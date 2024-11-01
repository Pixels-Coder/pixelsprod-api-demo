from ..helpers import TemplateHelper

def create(supabase, organization_id: str, project_name: str, project_display_name: str):
    helper = TemplateHelper(supabase)
    helper.set_organization_id(organization_id)
    project = helper.create_project(project_name, project_display_name)
    helper.set_project_id(project['id'])

    # Create entity types
    user_story = helper.create_entity_type("user_story", "User Story")
    feature = helper.create_entity_type("feature", "Feature")
    issue = helper.create_entity_type("issue", "Issue")
    release = helper.create_entity_type("release", "Release")

    # Create resource types
    human_resource = helper.create_resource_type("human_resource", "Human Resource")
    equipment = helper.create_resource_type("equipment", "Equipment")

    # Create steps for user stories
    user_story_analysis = helper.create_step("analysis", user_story["id"])
    user_story_design = helper.create_step("design", user_story["id"])
    user_story_implementation = helper.create_step("implementation", user_story["id"])
    user_story_testing = helper.create_step("testing", user_story["id"])
    user_story_documentation = helper.create_step("documentation", user_story["id"])

    # Create steps for features
    feature_planning = helper.create_step("planning", feature["id"])
    feature_design = helper.create_step("design", feature["id"])
    feature_implementation = helper.create_step("implementation", feature["id"])
    feature_testing = helper.create_step("testing", feature["id"])
    feature_documentation = helper.create_step("documentation", feature["id"])

    # Create steps for issues
    issue_triage = helper.create_step("triage", issue["id"])
    issue_investigation = helper.create_step("investigation", issue["id"])
    issue_fix = helper.create_step("fix", issue["id"])
    issue_testing = helper.create_step("testing", issue["id"])
    issue_documentation = helper.create_step("documentation", issue["id"])

    # Create steps for releases
    release_planning = helper.create_step("planning", release["id"])
    release_integration = helper.create_step("integration", release["id"])
    release_testing = helper.create_step("testing", release["id"])
    release_documentation = helper.create_step("documentation", release["id"])
    release_deployment = helper.create_step("deployment", release["id"])

    # Create templates with updated durations
    user_story_template = helper.create_entity_template("User Story Template", [
        {"name": "Analysis", "step_id": user_story_analysis["id"], "duration": 16},
        {"name": "Design", "step_id": user_story_design["id"], "duration": 24, "dependencies": ["Analysis"]},
        {"name": "Implementation", "step_id": user_story_implementation["id"], "duration": 40, "dependencies": ["Design"]},
        {"name": "Testing", "step_id": user_story_testing["id"], "duration": 16, "dependencies": ["Implementation"]},
        {"name": "Documentation", "step_id": user_story_documentation["id"], "duration": 8, "dependencies": ["Testing"]},
    ])

    feature_template = helper.create_entity_template("Feature Template", [
        {"name": "Planning", "step_id": feature_planning["id"], "duration": 24},
        {"name": "Design", "step_id": feature_design["id"], "duration": 40, "dependencies": ["Planning"]},
        {"name": "Implementation", "step_id": feature_implementation["id"], "duration": 80, "dependencies": ["Design"]},
        {"name": "Testing", "step_id": feature_testing["id"], "duration": 32, "dependencies": ["Implementation"]},
        {"name": "Documentation", "step_id": feature_documentation["id"], "duration": 16, "dependencies": ["Testing"]},
    ])

    issue_template = helper.create_entity_template("Issue Template", [
        {"name": "Triage", "step_id": issue_triage["id"], "duration": 4},
        {"name": "Investigation", "step_id": issue_investigation["id"], "duration": 16, "dependencies": ["Triage"]},
        {"name": "Fix", "step_id": issue_fix["id"], "duration": 24, "dependencies": ["Investigation"]},
        {"name": "Testing", "step_id": issue_testing["id"], "duration": 8, "dependencies": ["Fix"]},
        {"name": "Documentation", "step_id": issue_documentation["id"], "duration": 4, "dependencies": ["Testing"]},
    ])

    release_template = helper.create_entity_template("Release Template", [
        {"name": "Planning", "step_id": release_planning["id"], "duration": 40},
        {"name": "Integration", "step_id": release_integration["id"], "duration": 80, "dependencies": ["Planning"]},
        {"name": "Testing", "step_id": release_testing["id"], "duration": 60, "dependencies": ["Integration"]},
        {"name": "Documentation", "step_id": release_documentation["id"], "duration": 24, "dependencies": ["Testing"]},
        {"name": "Deployment", "step_id": release_deployment["id"], "duration": 16, "dependencies": ["Documentation"]},
    ])

    # Create entities for a Notion-like app

    # User Stories
    helper.create_entity("US1: Create and Edit Pages", user_story["id"], user_story_template["id"])
    helper.create_entity("US2: Organize Pages in Hierarchies", user_story["id"], user_story_template["id"])
    helper.create_entity("US3: Add Rich Media Content", user_story["id"], user_story_template["id"])
    helper.create_entity("US4: Collaborate in Real-time", user_story["id"], user_story_template["id"])
    helper.create_entity("US5: Search Across All Content", user_story["id"], user_story_template["id"])
    helper.create_entity("US6: Create and Manage Tasks", user_story["id"], user_story_template["id"])
    helper.create_entity("US7: Customize Workspace Layout", user_story["id"], user_story_template["id"])
    helper.create_entity("US8: Export and Import Data", user_story["id"], user_story_template["id"])

    # Features
    helper.create_entity("F1: WYSIWYG Editor", feature["id"], feature_template["id"])
    helper.create_entity("F2: Page Hierarchy and Navigation", feature["id"], feature_template["id"])
    helper.create_entity("F3: Media Embedding", feature["id"], feature_template["id"])
    helper.create_entity("F4: Real-time Collaboration", feature["id"], feature_template["id"])
    helper.create_entity("F5: Full-text Search", feature["id"], feature_template["id"])
    helper.create_entity("F6: Kanban Board", feature["id"], feature_template["id"])
    helper.create_entity("F7: Customizable Layouts", feature["id"], feature_template["id"])
    helper.create_entity("F8: Data Import/Export", feature["id"], feature_template["id"])
    helper.create_entity("F9: User Authentication", feature["id"], feature_template["id"])
    helper.create_entity("F10: Permissions and Sharing", feature["id"], feature_template["id"])

    # Issues
    helper.create_entity("I1: Editor Performance Issues", issue["id"], issue_template["id"])
    helper.create_entity("I2: Sync Conflicts in Real-time Collaboration", issue["id"], issue_template["id"])
    helper.create_entity("I3: Search Indexing Delays", issue["id"], issue_template["id"])
    helper.create_entity("I4: Mobile Responsiveness", issue["id"], issue_template["id"])
    helper.create_entity("I5: Data Import Failures", issue["id"], issue_template["id"])

    # Releases
    helper.create_entity("R1: MVP Launch", release["id"], release_template["id"])
    helper.create_entity("R2: Collaboration Update", release["id"], release_template["id"])
    helper.create_entity("R3: Mobile App Release", release["id"], release_template["id"])
    helper.create_entity("R4: Enterprise Features", release["id"], release_template["id"])

    # Create resources
    for i in range(5):
        helper.create_resource(f"Frontend Developer {i+1}", human_resource["id"], {"daily_rate": 400})
    for i in range(3):
        helper.create_resource(f"Backend Developer {i+1}", human_resource["id"], {"daily_rate": 450})
    for i in range(2):
        helper.create_resource(f"UX Designer {i+1}", human_resource["id"], {"daily_rate": 380})
    for i in range(2):
        helper.create_resource(f"QA Engineer {i+1}", human_resource["id"], {"daily_rate": 350})
    helper.create_resource("Product Manager", human_resource["id"], {"daily_rate": 500})
    helper.create_resource("DevOps Engineer", human_resource["id"], {"daily_rate": 480})

    for i in range(15):
        helper.create_resource(f"Development Workstation {i+1}", equipment["id"], {"monthly_cost": 10})
    helper.create_resource("CI/CD Server", equipment["id"], {"monthly_cost": 50})
    helper.create_resource("Staging Environment", equipment["id"], {"monthly_cost": 100})

    return project