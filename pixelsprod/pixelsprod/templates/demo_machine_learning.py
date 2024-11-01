from ..helpers import TemplateHelper

DOCUMENT_CHUNK_SIZE = 1000

def create_documents_entities(helper, display_name, entity_type_id, template_id, count, concepts=[], patients=None, offset=0):
    entities = []
    relations = {"concepts": concepts}
    if patients:
        relations["patients"] = [patients]
    for i, start in enumerate(range(0, count, DOCUMENT_CHUNK_SIZE)):
        chunk_size = min(DOCUMENT_CHUNK_SIZE, count - start)
        entities.append(helper.create_entity(display_name.format(i+offset+1), entity_type_id, template_id, {"documents_count": chunk_size}, relations=relations))
    return entities

def create(supabase, organization_id: str, project_name: str, project_display_name: str):
    helper = TemplateHelper(supabase)
    helper.set_organization_id(organization_id)
    project = helper.create_project(project_name, project_display_name, start_date="2025-01-01", end_date="2028-05-01", budget="5000000", work_day_duration=7)
    helper.set_project_id(project['id'])

    # Create entity types
    patients = helper.create_entity_type("patients", "😷 Patients", {"type": "object", "properties": {
        "patients_count": {"type": "number", "display_name": "Patients Count"},
    }})

    concepts = helper.create_entity_type("concepts", "🔖 Concepts", {"type": "object", "properties": {
        "concepts_count": {"type": "number", "display_name": "Concepts Count"},
        "categories_count": {"type": "number", "display_name": "Categories Count"},
    }})

    documents = helper.create_entity_type("documents", "📝 Documents", {"type": "object", "properties": {
        "documents_count": {"type": "number", "display_name": "Documents Count"},
    }})

    # Create resource types
    human_resource = helper.create_resource_type("human_resource", "👥 Human Resource", {"type": "object", "properties": {"daily_rate": {"type": "number"}}})
    equipment = helper.create_resource_type("equipment", "💻 Equipment", {"type": "object", "properties": {"monthly_cost": {"type": "number"}}})

    # Create steps
    data_extract = helper.create_step("data_extract")
    data_analysis = helper.create_step("data_analysis")
    data_visualization = helper.create_step("data_visualization")

    expert_specifications = helper.create_step("expert_specifications")
    expert_labeling = helper.create_step("expert_labeling")
    expert_review = helper.create_step("expert_review")

    auto_labeling = helper.create_step("auto_labeling")


    # Create templates
    population_template = helper.create_entity_template("Population", [
        {"name": "population_definition", "step_id": expert_specifications["id"], "duration": 14, "description": "Define poputation criteria"},
        {"name": "population_extract", "step_id": data_extract["id"], "duration": 7, "dependencies": ["population_definition"], "description": "Extract population data"},
    ])

    concepts_template = helper.create_entity_template("Concepts", [
        {"name": "concepts_definition", "step_id": expert_specifications["id"], "duration": 14, "description": "Define labeling concepts"},
        {"name": "concepts_extract", "step_id": data_extract["id"], "duration": 7, "dependencies": ["concepts_definition"], "description": "Extract and structure concepts data"},
    ])

    documents_labeling = helper.create_entity_template("Documents Labeling", [
        {"name": "auto_label_categories", "step_id": auto_labeling["id"], "duration": "=entity.attributes.documents_count * durationToHours(\"1 min\") / 100.0", "dependencies_expression": "[entity.attributes.concepts].concepts_extract,entity.attributes.patients.population_extract", "description": "Automatically label data with concepts categories"},
        {"name": "clean_label_categories", "step_id": expert_labeling["id"], "duration": "=entity.attributes.documents_count * durationToHours(\"5 min\")", "dependencies": ["auto_label_categories"], "description": "Manually Review and correct categories auto labeling"},
        {"name": "auto_label_concepts", "step_id": auto_labeling["id"], "duration": "=entity.attributes.documents_count * durationToHours(\"1 min\") / 100.0", "dependencies": ["clean_label_categories"], "description": "Automatically label data with concepts"},
        {"name": "clean_label_concepts", "step_id": expert_labeling["id"], "duration": "=entity.attributes.documents_count * durationToHours(\"15 min\")", "dependencies": ["auto_label_concepts"], "description": "Manually Review and correct auto labeling"},
    ])

    # Create entities
    patients_paris = helper.create_entity("Patients Paris", patients["id"], population_template["id"], {"patients_count": 5000})
    patients_lyon = helper.create_entity("Patients Lyon", patients["id"], population_template["id"], {"patients_count": 3500})
    patients_marseille = helper.create_entity("Patients Marseille", patients["id"], population_template["id"], {"patients_count": 3500})
    patients_toulouse = helper.create_entity("Patients Toulouse", patients["id"], population_template["id"], {"patients_count": 3000})
    patients = [patients_paris, patients_lyon, patients_marseille, patients_toulouse]

    concepts_medical_history = helper.create_entity("Concepts Medical History", concepts["id"], concepts_template["id"], {"concepts_count": 500, "categories_count": 10})
    concepts_family_history = helper.create_entity("Concepts Family History", concepts["id"], concepts_template["id"], {"concepts_count": 300, "categories_count": 8})
    concepts_symptoms = helper.create_entity("Concepts Symptoms", concepts["id"], concepts_template["id"], {"concepts_count": 150, "categories_count": 15})
    concepts_physical_caracteristics = helper.create_entity("Concepts Physical Caracteristics", concepts["id"], concepts_template["id"], {"concepts_count": 200, "categories_count": 12})

    for i, patients_entity in enumerate(patients):
        consultation_reports = create_documents_entities(helper, "Consultation Reports {:03d}", documents["id"], documents_labeling["id"], 10000, concepts=[concepts_medical_history["id"], concepts_family_history["id"]], patients=patients_entity["id"], offset=i*100)
        radiology_reports = create_documents_entities(helper, "Radiology Reports {:03d}", documents["id"], documents_labeling["id"], 3000, concepts=[concepts_symptoms["id"], concepts_physical_caracteristics["id"]], patients=patients_entity["id"], offset=i*100)
        lab_reports = create_documents_entities(helper, "Lab Reports {:03d}", documents["id"], documents_labeling["id"], 3000, concepts=[concepts_family_history["id"]], patients=patients_entity["id"], offset=i*100)
        genetic_reports = create_documents_entities(helper, "Genetic Reports {:03d}", documents["id"], documents_labeling["id"], 1000, concepts=[concepts_family_history["id"], concepts_physical_caracteristics["id"]], patients=patients_entity["id"], offset=i*100)

    # Create resources
    for i in range(10):
        helper.create_resource(f"Data Scientist {i+1}", human_resource["id"], {"daily_rate": 700}, skills="data_*")

    for i in range(10):
        helper.create_resource(f"Medical Expert {i+1}", human_resource["id"], {"daily_rate": 1800}, skills="expert_*")

    for i in range(15):
        helper.create_resource(f"No Human {i+1}", human_resource["id"], {"daily_rate": 0}, skills="auto_*")

    for i in range(20):
        helper.create_resource(f"Workstation {i+1}", equipment["id"], {"monthly_cost": 200})

    # Schedule
    helper.schedule()
    return project
