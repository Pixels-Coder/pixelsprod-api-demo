import json
from  pixelsprod.supabase_client import supabase_client

"""
Run with
dotenv -f ../.env run poetry run python scripts/dump_project.py a0000001-0000-0000-0000-000000000000 project.sql

To dump from the local supabase instance
Otherwise, set the SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables
"""

def escape_value(value):
  if type(value) is str:
    return f"'{value.replace("'", "''")}'"
  if value is None:
    return "NULL"
  if type(value) is int:
    return str(value)
  if type(value) is bool:
    return "TRUE" if value else "FALSE"
  if type(value) is float:
     return str(value)
  if type(value) is dict:
    return escape_value(json.dumps(value))
  return str(value)

def dump_row(table_name:str , row: dict):
  return f"INSERT INTO {table_name} ({','.join(row.keys())}) VALUES ({','.join([ escape_value(v) for v in row.values()])});"

def dump_rows(table_name:str , rows: list[dict]):
  return "\n".join([dump_row(table_name, row) for row in rows])

# Dump a table containing a project_id column
def dump_project_table(project_id: str, table_name:str):
  rows = supabase_client.table(table_name).select("*").eq("project_id", project_id).execute().data
  return dump_rows(table_name, rows)

def get_project_table(project_id: str, table_name:str):
  return supabase_client.table(table_name).select("*").eq("project_id", project_id).execute().data

def dump_project(project_id: str, output_file : str):
  projects = supabase_client.table("projects").select("*").eq("id", project_id).execute()
  if len(projects.data) != 1:
    raise Exception("Project not found")
    
  project = projects.data[0]
  with open(output_file, 'w') as f:
    f.write(dump_row("projects", project))
    f.write("\n")
    # Dump user relations
    f.write(dump_project_table(project_id, "projects_users_relation"))
    f.write("\n")
    # Dump transactions categories
    f.write(dump_project_table(project_id, "transactions_categories"))
    f.write("\n")
    # Dump transactions 
    transactions = get_project_table(project_id, "transactions")
    f.write(dump_rows( "transactions", transactions))
    f.write("\n")
    # Dump transactions_categories_transactions_relation
    for transaction in transactions:
      f.write(dump_rows("transactions_categories_transactions_relation", supabase_client.table("transactions_categories_transactions_relation").select("*").eq("transaction_id", transaction["id"]).execute().data))
      f.write("\n")
    # Dump resources
    f.write(dump_project_table(project_id, "resources"))
    f.write("\n")
    # Dump resources transactions relation
    for transaction in transactions:
      f.write(dump_rows("resources_transactions_relation", supabase_client.table("resources_transactions_relation").select("*").eq("transaction_id", transaction["id"]).execute().data))
      f.write("\n")
    # Dump entity types 
    f.write(dump_project_table(project_id, "entity_types"))
    f.write("\n")
    # Dump steps
    steps = get_project_table(project_id, "steps")
    f.write(dump_rows("steps", steps))
    f.write("\n")


    # Dump entity templates
    f.write(dump_project_table(project_id, "entity_templates"))
    f.write("\n")

    # dump task_templates
    task_templates = []
    for step in steps :
      task_templates.extend(supabase_client.table("task_templates").select("*").eq("step_id", step["id"]).execute().data)
    f.write(dump_rows("task_templates", task_templates ))
    f.write("\n")

    # Dump tasks_templates_dependencies
    for task_template in task_templates:
      f.write(dump_rows("tasks_templates_dependencies", supabase_client.table("tasks_templates_dependencies").select("*").eq("task_template_id", task_template["id"]).execute().data))
      f.write("\n")

    # Dump entities
    entities = get_project_table(project_id, "entities")
    f.write(dump_rows("entities", entities))
    f.write("\n")

    # Dump enities entities relation
    for entity in entities:
      f.write(dump_rows("entities_entities_relation", supabase_client.table("entities_entities_relation").select("*").eq("entity_id", entity["id"]).execute().data))
      f.write("\n")

    # Dump tasks
    tasks = get_project_table(project_id, "tasks")
    f.write(dump_rows("tasks", tasks))
    f.write("\n")
    # Dump resources tasks relation
    for task in tasks:
      f.write(dump_rows("resources_tasks_relation", supabase_client.table("resources_tasks_relation").select("*").eq("task_id", task["id"]).execute().data))
      f.write("\n")


# dump_project("a0000001-0000-0000-0000-000000000000", 'project.sql')
if __name__ == "__main__":
  import sys
  import os
  if len(sys.argv) != 3 or sys.argv[1] == "--help":
    print("Dump a project to a sql file")
    print("Please set the following environment variables:")
    print("SUPABASE_URL")
    print("SUPABASE_SERVICE_KEY")
    print()
    print("Usage: dump_project.py project_id output_file")
  else:
    dump_project(sys.argv[1], sys.argv[2])