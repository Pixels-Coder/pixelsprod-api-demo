import requests
import os
from .duration import Duration


class TemplateHelper(object):

    def __init__(self, supabase):
        super(TemplateHelper, self).__init__()
        self.supabase = supabase
        self._organization_id = None
        self._project = None
        self._project_id = None

    def set_organization_id(self, organization_id):
        self._organization_id = organization_id

    def set_project_id(self, project_id):
        self._project_id = project_id
        self._project = self.supabase.table("projects").select("*").eq("id", project_id).single().execute().data
        if self._project is None:
            raise ValueError(f"Project with ID {project_id} not found")
        Duration.push_context_work_day_duration(self._project["work_day_duration"])

    def create_project(self, project_name, project_display_name, description=None, start_date=None, end_date=None, budget=None, work_day_duration=None):
        if self._organization_id is None:
            raise ValueError("Organization ID is not set")
        # Create project
        project_data = {
            'organization_id': self._organization_id,
            'name': project_name,
            'display_name': project_display_name,
        }
        if description:
            project_data['description'] = description
        if start_date:
            project_data['start_date'] = start_date + "T00:00:00Z"
        if end_date:
            project_data['end_date'] = end_date + "T00:00:00Z"
        if budget:
            project_data['budget'] = budget
        if work_day_duration:
            project_data['work_day_duration'] = work_day_duration
        project = self.supabase.table("projects").insert([project_data]).execute().data[0]
        return project

    def create_entity_type(self, name, display_name, attributes_schema=None):
        if self._organization_id is None:
            raise ValueError("Organization ID is not set")
        if self._project_id is None:
            raise ValueError("Project ID is not set")
        # Create entity type
        entity_type_data = {
            'project_id': self._project_id,
            'name': name,
            'display_name': display_name,
        }
        if attributes_schema is not None:
            entity_type_data['attributes_schema'] = attributes_schema
        entity_type = self.supabase.table("entity_types").insert([entity_type_data]).execute().data[0]
        return entity_type

    def create_resource_type(self, name, display_name, attributes_schema=None):
        if self._organization_id is None:
            raise ValueError("Organization ID is not set")
        if self._project_id is None:
            raise ValueError("Project ID is not set")
        # Create resource type
        resource_type_data = {
            'project_id': self._project_id,
            'name': name,
            'display_name': display_name,
        }
        if attributes_schema is not None:
            resource_type_data['attributes_schema'] = attributes_schema
        resource_type = self.supabase.table("resource_types").insert([resource_type_data]).execute().data[0]
        return resource_type

    def create_step(self, name):
        if self._organization_id is None:
            raise ValueError("Organization ID is not set")
        if self._project_id is None:
            raise ValueError("Project ID is not set")
        # Create step
        step_data = {
            'project_id': self._project_id,
            'name': name,
        }
        step = self.supabase.table("steps").insert([step_data]).execute().data[0]
        return step

    def create_entity_template(self, name, task_templates):
        if self._organization_id is None:
            raise ValueError("Organization ID is not set")
        if self._project_id is None:
            raise ValueError("Project ID is not set")
        # Create entity template
        entity_template_data = {
            'project_id': self._project_id,
            'name': name,
        }
        entity_template = self.supabase.table("entity_templates").insert([entity_template_data]).execute().data[0]
        task_templates_rows = {}
        for task_template_data in task_templates:
            task_template = self._create_task_template(
              task_template_data['name'],
              entity_template['id'],
              task_template_data['step_id'],
              task_template_data['duration'],
              dependencies_expression=task_template_data.get('dependencies_expression', None),
              description=task_template_data.get('description', None),
            )
            task_templates_rows[task_template_data['name']] = task_template

        dependencies_rows = []
        for task_template_data in task_templates:
            task_template = task_templates_rows[task_template_data['name']]
            for dependency in task_template_data.get('dependencies', []):
                dependencies_rows.append({
                    'task_template_id': task_template['id'],
                    'upstream_task_template_id': task_templates_rows[dependency]['id'],
                })
        if len(dependencies_rows):
            self.supabase.table("tasks_templates_dependencies").insert(dependencies_rows).execute()
        return entity_template

    def _create_task_template(self, name, entity_template_id, step_id, duration, dependencies_expression=None, description=None):
        if self._organization_id is None:
            raise ValueError("Organization ID is not set")
        if self._project_id is None:
            raise ValueError("Project ID is not set")
        # Create task template
        task_template_data = {
            # 'project_id': self._project_id,
            'name': name,
            'entity_template_id': entity_template_id,
            'step_id': step_id,
            'dependencies_expression': dependencies_expression,
        }
        if description:
            task_template_data['description'] = description
        if isinstance(duration, str):
            if duration.startswith("="):
              task_template_data['duration_expression'] = duration[1:]
            else:
              task_template_data['duration'] = Duration(duration).total_hours
        else:
            task_template_data['duration'] = duration
        task_template = self.supabase.table("task_templates").insert([task_template_data]).execute().data[0]
        return task_template

    def create_entity(self, name, entity_type_id, entity_template_id=None, attributes=None, priority=None, relations=None):
        if self._organization_id is None:
            raise ValueError("Organization ID is not set")
        if self._project_id is None:
            raise ValueError("Project ID is not set")
        # Create entity
        entity_data = {
            'project_id': self._project_id,
            'entity_type_id': entity_type_id,
            'name': name,
        }
        if attributes is not None:
            entity_data['attributes'] = attributes
        if priority is not None:
            entity_data['priority'] = priority
        entity = self.supabase.table("entities").insert([entity_data]).execute().data[0]
        if relations is not None:
            for key, related_entity_ids in relations.items():
                self.create_entity_relations(entity['id'], related_entity_ids, key)
        if entity_template_id is not None:
            self.supabase.rpc("apply_entity_template", {"target_entity_id": entity['id'], "template_id": entity_template_id}).execute()
        return entity

    def create_entity_relation(self, entity_id, related_entity_id, key):
        if self._organization_id is None:
            raise ValueError("Organization ID is not set")
        if self._project_id is None:
            raise ValueError("Project ID is not set")
        # Create entity relation
        entity_relation_data = {
            'entity_id': entity_id,
            'related_entity_id': related_entity_id,
            'key': key,
        }
        entity_relation = self.supabase.table("entities_entities_relation").insert([entity_relation_data]).execute().data[0]
        return entity_relation

    def create_entity_relations(self, entity_id, related_entity_ids, key):
        if self._organization_id is None:
            raise ValueError("Organization ID is not set")
        if self._project_id is None:
            raise ValueError("Project ID is not set")
        # Create entity relations
        entity_relations_data = []
        for related_entity_id in related_entity_ids:
            entity_relations_data.append({
                'entity_id': entity_id,
                'related_entity_id': related_entity_id,
                'key': key,
            })
        entity_relations = self.supabase.table("entities_entities_relation").insert(entity_relations_data).execute().data
        return entity_relations

    def create_resource(self, name, resource_type_id, attributes=None, skills=None):
        if self._organization_id is None:
            raise ValueError("Organization ID is not set")
        if self._project_id is None:
            raise ValueError("Project ID is not set")
        # Create resource
        resource_data = {
            'project_id': self._project_id,
            'resource_type_id': resource_type_id,
            'name': name,
            'skills': skills,
        }
        if attributes is not None:
            resource_data['attributes'] = attributes
        resource = self.supabase.table("resources").insert([resource_data]).execute().data[0]
        return resource

    def schedule(self):
        pixelsprod_api_url = os.environ["PIXELSPROD_API_URL"]
        res = requests.post(f"{pixelsprod_api_url}/project/{self._project_id}/_schedule")
        res.raise_for_status()
        print(res.json())
