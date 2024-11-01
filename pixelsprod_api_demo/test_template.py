from pixelsprod.helpers import TemplateHelper

def create(supabase, organization_id: str, project_name: str, project_display_name: str):
    helper = TemplateHelper(supabase)
    helper.set_organization_id(organization_id)
    project = helper.create_project(project_name, project_display_name, start_date="2025-01-01", end_date="2028-05-01", budget="5000000", work_day_duration=7)
    helper.set_project_id(project['id'])

    # Create entity types
    parts = helper.create_entity_type("parts", "Parts", {"type": "object", "properties": {
        "complexity": {"type": "number", "display_name": "Complexity"},
    }})

    products = helper.create_entity_type("products", "Products", {"type": "object", "properties": {}})

    # Create resource types
    human_resource = helper.create_resource_type("human_resource", "👥 Human Resource", {"type": "object", "properties": {"daily_rate": {"type": "number"}}})
    equipment = helper.create_resource_type("equipment", "💻 Equipment", {"type": "object", "properties": {"monthly_cost": {"type": "number"}}})

    # Create steps
    modeling = helper.create_step("modeling")
    shading = helper.create_step("shading")
    assembly = helper.create_step("assembly")
    render = helper.create_step("render")


    # Create templates
    part_template = helper.create_entity_template("Part Template", [
        {"name": "modeling", "step_id": shading["id"], "duration": "1 day", "description": "Model part"},
        {"name": "shading", "step_id": shading["id"], "duration": "1 day", "dependencies": ["modeling"], "description": "Shade part"},
    ])

    product_template = helper.create_entity_template("Product Template", [
        {"name": "assembly", "step_id": assembly["id"], "duration": "1 day", "description": "Assemble product"},
        {"name": "render", "step_id": render["id"], "duration": "1 day", "dependencies": ["assembly"], "description": "Render product"},
    ])

    

    # Create entities
    for i in range(100):
        helper.create_entity(f"Part {i+1:03d}", parts["id"], part_template["id"], {"complexity": 1})
    
    for i in range(10):
        helper.create_entity(f"Product {i+1}", products["id"], product_template["id"])


    # Create resources
    for i in range(4):
        helper.create_resource(f"Modeling Artist {i+1}", human_resource["id"], {"daily_rate": 400}, skills="modeling")

    for i in range(4):
        helper.create_resource(f"Shading Artist {i+1}", human_resource["id"], {"daily_rate": 400}, skills="shading")
    
    for i in range(4):
        helper.create_resource(f"Assembly Artist {i+1}", human_resource["id"], {"daily_rate": 400}, skills="assembly")
    
    for i in range(4):
        helper.create_resource(f"Redering Artist {i+1}", human_resource["id"], {"daily_rate": 400}, skills="render")

    for i in range(20):
        helper.create_resource(f"Workstation {i+1}", equipment["id"], {"monthly_cost": 200})

    # Schedule
    helper.schedule()
    return project
