from ..helpers import TemplateHelper



def create(supabase, organization_id: str, project_name: str, project_display_name: str):
    helper = TemplateHelper(supabase)
    helper.set_organization_id(organization_id)
    project = helper.create_project(project_name, project_display_name, start_date="2024-10-01", end_date="2024-12-31", budget="300000", work_day_duration=7)
    helper.set_project_id(project["id"])

    character = helper.create_entity_type("character", "👤 Character")
    prop = helper.create_entity_type("prop", "📦 Prop")
    environment = helper.create_entity_type("environment", "🌍 Environment")
    episode = helper.create_entity_type("episode", "📺 Episode")
    sequence = helper.create_entity_type("sequence", "🎬 Sequence")
    shot = helper.create_entity_type("shot", "🎥 Shot", {"type": "object", "properties": {
        "frame_start": {"type": "number"},
        "frame_end": {"type": "number"},
        "frame_count": {"type": "number"},
    }})

    human_resource = helper.create_resource_type("human_resource", "👥 Human Resource", {"type": "object", "properties": {"daily_rate": {"type": "number"}}})
    equipment = helper.create_resource_type("equipment", "💻 Equipment", {"type": "object", "properties": {"monthly_cost": {"type": "number"}}})

    modeling = helper.create_step("modeling")
    shading = helper.create_step("shading")
    rigging = helper.create_step("rigging")

    layout = helper.create_step("layout")
    lighting = helper.create_step("lighting")

    script = helper.create_step("script")
    storyboard = helper.create_step("storyboard")
    animation = helper.create_step("animation")
    montage = helper.create_step("montage")

    render = helper.create_step("render")
    compositing = helper.create_step("compositing")



    character_template = helper.create_entity_template("Character Template", [
        {"name": "modeling", "step_id": modeling["id"], "duration": "3 days"},
        {"name": "shading", "step_id": shading["id"], "duration": "3 days", "dependencies": ["modeling"]},
        {"name": "rigging", "step_id": rigging["id"], "duration": "5 days", "dependencies": ["modeling", "shading"]},
    ])

    prop_template = helper.create_entity_template("Prop Template", [
        {"name": "modeling", "step_id": modeling["id"], "duration": "1 day"},
        {"name": "shading", "step_id": shading["id"], "duration": "1 days", "dependencies": ["modeling"]},
        {"name": "rigging", "step_id": rigging["id"], "duration": "1 days", "dependencies": ["modeling", "shading"]},
    ])

    environment_template = helper.create_entity_template("Environment Template", [
        {"name": "modeling", "step_id": modeling["id"], "duration": "2 days"},
        {"name": "shading", "step_id": shading["id"], "duration": "3 days", "dependencies": ["modeling"]},
        {"name": "layout", "step_id": layout["id"], "duration": "5 days", "dependencies": ["modeling", "shading"], "dependencies_expression": "[entity.attributes.assets?].rigging?"},
        {"name": "lighting", "step_id": lighting["id"], "duration": "5 days", "dependencies": ["layout"]},
    ])

    episode_template = helper.create_entity_template("Episode Template", [
        {"name": "script", "step_id": script["id"], "duration": "10 days"},
        {"name": "storyboard", "step_id": storyboard["id"], "duration": "5 days", "dependencies": ["script"]},
    ])

    sequence_template = helper.create_entity_template("Sequence Template", [
        {"name": "layout", "step_id": layout["id"], "duration": "1 day", "dependencies_expression": "entity.attributes.episode.storyboard"},
        {"name": "animatic", "step_id": animation["id"], "duration": "1 day", "dependencies": ["layout"]},
    ])

    shot_template = helper.create_entity_template("Shot Template", [
        {"name": "animation", "step_id": animation["id"], "duration": "=entity.attributes.frame_count * 0.2", "dependencies": [], "dependencies_expression": "[entity.attributes.sequence].animatic,[entity.attributes.characters].rigging,entity.attributes.environment.layout"},
        {"name": "lighting", "step_id": lighting["id"], "duration": "1 day", "dependencies": ["animation"], "dependencies_expression": "entity.attributes.environment.lighting"},
        {"name": "render", "step_id": render["id"], "duration": "=entity.attributes.frame_count * 0.4", "dependencies": ["lighting"]},
        {"name": "compositing", "step_id": compositing["id"], "duration": "1 day", "dependencies": ["render"]},
    ])

    bob_character = helper.create_entity("Bob", character["id"], character_template["id"])
    alice_character = helper.create_entity("Alice", character["id"], character_template["id"])
    eve_character = helper.create_entity("Eve", character["id"], character_template["id"])

    tree_prop = helper.create_entity("Tree", prop["id"], prop_template["id"])
    house_prop = helper.create_entity("House", prop["id"], prop_template["id"])
    rock_prop = helper.create_entity("Rock", prop["id"], prop_template["id"])
    fish_prop = helper.create_entity("Fish", prop["id"], prop_template["id"])

    forest_environment = helper.create_entity("Forest", environment["id"], environment_template["id"], relations={
      "assets": [tree_prop["id"], rock_prop["id"]],
    })
    home_environment = helper.create_entity("Home", environment["id"], environment_template["id"], relations={
      "assets": [house_prop["id"]],
    })
    river_environment = helper.create_entity("River", environment["id"], environment_template["id"], relations={
      "assets": [rock_prop["id"], fish_prop["id"]],
    })

    episode_01 = helper.create_entity("E01", episode["id"], episode_template["id"], priority=300)
    episode_02 = helper.create_entity("E02", episode["id"], episode_template["id"], priority=200)
    episode_03 = helper.create_entity("E03", episode["id"], episode_template["id"], priority=100)

    sequence_e01sq01 = helper.create_entity("E01SQ01", sequence["id"], sequence_template["id"], priority=300, relations={
      "episode": [episode_01["id"]],
    })

    sequence_e01sq02 = helper.create_entity("E01SQ02", sequence["id"], sequence_template["id"], priority=300, relations={
      "episode": [episode_01["id"]],
    })

    sequence_e01sq03 = helper.create_entity("E01SQ03", sequence["id"], sequence_template["id"], priority=300, relations={
      "episode": [episode_01["id"]]
    })

    sequence_e02sq01 = helper.create_entity("E02SQ01", sequence["id"], sequence_template["id"], priority=100, relations={
      "episode": [episode_02["id"]],
    })

    sequence_e02sq02 = helper.create_entity("E02SQ02", sequence["id"], sequence_template["id"], priority=100, relations={
      "episode": [episode_02["id"]],
    })

    sequence_e02sq03 = helper.create_entity("E02SQ03", sequence["id"], sequence_template["id"], priority=100, relations={
      "episode": [episode_02["id"]]
    })

    sequence_e03sq01 = helper.create_entity("E03SQ01", sequence["id"], sequence_template["id"], priority=0, relations={
      "episode": [episode_03["id"]],
    })

    sequence_e03sq02 = helper.create_entity("E03SQ02", sequence["id"], sequence_template["id"], priority=0, relations={
      "episode": [episode_03["id"]],
    })

    sequence_e03sq03 = helper.create_entity("E03SQ03", sequence["id"], sequence_template["id"], priority=0, relations={
      "episode": [episode_03["id"]]
    })


    # Episode 01 Shots

    shot_e01sq01s01 = helper.create_entity("E01SQ01S01", shot["id"], shot_template["id"], {"frame_start": 1, "frame_end": 100, "frame_count": 100}, relations={
      "environment": [forest_environment["id"]],
      "episode": [episode_01["id"]],
      "sequence": [sequence_e01sq01["id"]],
      "characters": [bob_character["id"]],
    })
    shot_e01sq01s02 = helper.create_entity("E01SQ01S02", shot["id"], shot_template["id"], {"frame_start": 101, "frame_end": 200, "frame_count": 100}, relations={
      "environment": [forest_environment["id"]],
      "episode": [episode_01["id"]],
      "sequence": [sequence_e01sq01["id"]],
      "characters": [bob_character["id"]],
    })
    shot_e01sq01s03 = helper.create_entity("E01SQ01S03", shot["id"], shot_template["id"], {"frame_start": 201, "frame_end": 300, "frame_count": 100}, relations={
      "environment": [forest_environment["id"]],
      "episode": [episode_01["id"]],
      "sequence": [sequence_e01sq01["id"]],
      "characters": [bob_character["id"]],
    })



    shot_e01sq02s01 = helper.create_entity("E01SQ02S01", shot["id"], shot_template["id"], {"frame_start": 1, "frame_end": 100, "frame_count": 100}, relations={
      "environment": [home_environment["id"]],
      "episode": [episode_01["id"]],
      "sequence": [sequence_e01sq02["id"]],
      "characters": [bob_character["id"], alice_character["id"]],
    })
    shot_e01sq02s02 = helper.create_entity("E01SQ02S02", shot["id"], shot_template["id"], {"frame_start": 101, "frame_end": 200, "frame_count": 100}, relations={
      "environment": [home_environment["id"]],
      "episode": [episode_01["id"]],
      "sequence": [sequence_e01sq02["id"]],
      "characters": [bob_character["id"], alice_character["id"]],
    })



    shot_e01sq03s01 = helper.create_entity("E01SQ03S01", shot["id"], shot_template["id"], {"frame_start": 1, "frame_end": 100, "frame_count": 100}, relations={
      "environment": [forest_environment["id"]],
      "episode": [episode_01["id"]],
      "sequence": [sequence_e01sq03["id"]],
      "characters": [alice_character["id"]],
    })
    shot_e01sq03s02 = helper.create_entity("E01SQ03S02", shot["id"], shot_template["id"], {"frame_start": 101, "frame_end": 200, "frame_count": 100}, relations={
      "environment": [forest_environment["id"]],
      "episode": [episode_01["id"]],
      "sequence": [sequence_e01sq03["id"]],
      "characters": [alice_character["id"]],
    })


    # Episode 02 Shots

    shot_e02sq01s01 = helper.create_entity("E02SQ01S01", shot["id"], shot_template["id"], {"frame_start": 1, "frame_end": 100, "frame_count": 100}, relations={
      "environment": [forest_environment["id"]],
      "episode": [episode_02["id"]],
      "sequence": [sequence_e02sq01["id"]],
      "characters": [bob_character["id"], alice_character["id"]],
    })
    shot_e02sq01s02 = helper.create_entity("E02SQ01S02", shot["id"], shot_template["id"], {"frame_start": 101, "frame_end": 200, "frame_count": 100}, relations={
      "environment": [forest_environment["id"]],
      "episode": [episode_02["id"]],
      "sequence": [sequence_e02sq01["id"]],
      "characters": [bob_character["id"]],
    })
    shot_e02sq01s03 = helper.create_entity("E02SQ01S03", shot["id"], shot_template["id"], {"frame_start": 201, "frame_end": 300, "frame_count": 100}, relations={
      "environment": [forest_environment["id"]],
      "episode": [episode_02["id"]],
      "sequence": [sequence_e02sq01["id"]],
      "characters": [bob_character["id"]],
    })



    shot_e02sq02s01 = helper.create_entity("E02SQ02S01", shot["id"], shot_template["id"], {"frame_start": 1, "frame_end": 100, "frame_count": 100}, relations={
      "environment": [river_environment["id"]],
      "episode": [episode_02["id"]],
      "sequence": [sequence_e02sq02["id"]],
      "characters": [bob_character["id"], alice_character["id"]],
    })
    shot_e02sq02s02 = helper.create_entity("E02SQ02S02", shot["id"], shot_template["id"], {"frame_start": 101, "frame_end": 200, "frame_count": 100}, relations={
      "environment": [river_environment["id"]],
      "episode": [episode_02["id"]],
      "sequence": [sequence_e02sq02["id"]],
      "characters": [bob_character["id"], alice_character["id"]],
    })



    shot_e02sq03s01 = helper.create_entity("E02SQ03S01", shot["id"], shot_template["id"], {"frame_start": 1, "frame_end": 100, "frame_count": 100}, relations={
      "environment": [forest_environment["id"]],
      "episode": [episode_02["id"]],
      "sequence": [sequence_e02sq03["id"]],
      "characters": [alice_character["id"]],
    })
    shot_e02sq03s02 = helper.create_entity("E02SQ03S02", shot["id"], shot_template["id"], {"frame_start": 101, "frame_end": 200, "frame_count": 100}, relations={
      "environment": [forest_environment["id"]],
      "episode": [episode_02["id"]],
      "sequence": [sequence_e02sq03["id"]],
      "characters": [alice_character["id"]],
    })


    # Episode 03 Shots

    shot_e03sq01s01 = helper.create_entity("E03SQ01S01", shot["id"], shot_template["id"], {"frame_start": 1, "frame_end": 100, "frame_count": 100}, relations={
      "environment": [forest_environment["id"]],
      "episode": [episode_03["id"]],
      "sequence": [sequence_e03sq01["id"]],
      "characters": [bob_character["id"], alice_character["id"]],
    })
    shot_e03sq01s02 = helper.create_entity("E03SQ01S02", shot["id"], shot_template["id"], {"frame_start": 101, "frame_end": 200, "frame_count": 100}, relations={
      "environment": [forest_environment["id"]],
      "episode": [episode_03["id"]],
      "sequence": [sequence_e03sq01["id"]],
      "characters": [bob_character["id"]],
    })
    shot_e03sq01s03 = helper.create_entity("E03SQ01S03", shot["id"], shot_template["id"], {"frame_start": 201, "frame_end": 300, "frame_count": 100}, relations={
      "environment": [forest_environment["id"]],
      "episode": [episode_03["id"]],
      "sequence": [sequence_e03sq01["id"]],
      "characters": [bob_character["id"]],
    })



    shot_e03sq02s01 = helper.create_entity("E03SQ02S01", shot["id"], shot_template["id"], {"frame_start": 1, "frame_end": 100, "frame_count": 100}, relations={
      "environment": [river_environment["id"]],
      "episode": [episode_03["id"]],
      "sequence": [sequence_e03sq02["id"]],
      "characters": [bob_character["id"], alice_character["id"]],
    })
    shot_e03sq02s02 = helper.create_entity("E03SQ02S02", shot["id"], shot_template["id"], {"frame_start": 101, "frame_end": 200, "frame_count": 100}, relations={
      "environment": [river_environment["id"]],
      "episode": [episode_03["id"]],
      "sequence": [sequence_e03sq02["id"]],
      "characters": [bob_character["id"], alice_character["id"]],
    })



    shot_e03sq03s01 = helper.create_entity("E03SQ03S01", shot["id"], shot_template["id"], {"frame_start": 1, "frame_end": 100, "frame_count": 100}, relations={
      "environment": [forest_environment["id"]],
      "episode": [episode_03["id"]],
      "sequence": [sequence_e03sq03["id"]],
      "characters": [alice_character["id"]],
    })
    shot_e03sq03s02 = helper.create_entity("E03SQ03S02", shot["id"], shot_template["id"], {"frame_start": 101, "frame_end": 200, "frame_count": 100}, relations={
      "environment": [forest_environment["id"]],
      "episode": [episode_03["id"]],
      "sequence": [sequence_e03sq03["id"]],
      "characters": [alice_character["id"]],
    })


    script_artist = helper.create_resource("Script Artist 01", human_resource["id"], {"daily_rate": 250}, skills="script")
    storyboard_artist = helper.create_resource("Storyboard Artist 01", human_resource["id"], {"daily_rate": 250}, skills="storyboard")

    modeling_artist = helper.create_resource("Modeling Artist 01", human_resource["id"], {"daily_rate": 250}, skills="modeling")
    modeling_artist = helper.create_resource("Modeling Artist 02", human_resource["id"], {"daily_rate": 250}, skills="modeling")

    shading_artist = helper.create_resource("Shading Artist 01", human_resource["id"], {"daily_rate": 250}, skills="shading")
    shading_artist = helper.create_resource("Shading Artist 02", human_resource["id"], {"daily_rate": 250}, skills="shading")

    rigging_artist = helper.create_resource("Rigging Artist 01", human_resource["id"], {"daily_rate": 250}, skills="rigging")
    rigging_artist = helper.create_resource("Rigging Artist 02", human_resource["id"], {"daily_rate": 250}, skills="rigging")

    layout_artist = helper.create_resource("Layout Artist 01", human_resource["id"], {"daily_rate": 250}, skills="layout")

    animation_artist = helper.create_resource("Animation Artist 01", human_resource["id"], {"daily_rate": 250}, skills="animation")
    animation_artist = helper.create_resource("Animation Artist 02", human_resource["id"], {"daily_rate": 250}, skills="animation")

    lighting_artist = helper.create_resource("Lighting Artist 01", human_resource["id"], {"daily_rate": 250}, skills="lighting")
    lighting_artist = helper.create_resource("Lighting Artist 02", human_resource["id"], {"daily_rate": 250}, skills="lighting")

    render_artist = helper.create_resource("Render Artist 01", human_resource["id"], {"daily_rate": 250}, skills="render")
    render_artist = helper.create_resource("Render Artist 02", human_resource["id"], {"daily_rate": 250}, skills="render")

    montage_artist = helper.create_resource("Montage Artist 02", human_resource["id"], {"daily_rate": 250}, skills="montage")

    compositing_artist = helper.create_resource("Compositing Artist 01", human_resource["id"], {"daily_rate": 250}, skills="compositing")
    compositing_artist = helper.create_resource("Compositing Artist 02", human_resource["id"], {"daily_rate": 250}, skills="compositing")

    for i in range(12):
        helper.create_resource(f"Equipment {i+1:02d}", equipment["id"], {"monthly_cost": 150})
    helper.schedule()

    return project
