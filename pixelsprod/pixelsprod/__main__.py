import click
import time
import os
import copy
import openai
from .prompts import PROJECT_PROMPT
from pprint import pprint
import requests
import tempfile
import datetime
import shutil

import random

from dotenv import load_dotenv

load_dotenv()


from .supabase_client import supabase_client

SHOTGRID_URL = os.environ.get("SHOTGRID_URL")
SCRIPT_NAME = os.environ.get("SHOTGRID_SCRIPT_URL")
API_KEY = os.environ.get("SHOTGRID_API_KEY")


OPENAI_API_KEY = os.environ.get("OPENAPI_KEY")
openai.api_key = OPENAI_API_KEY
def get_connection():
    from shotgun_api3 import Shotgun
    sg = Shotgun(SHOTGRID_URL, SCRIPT_NAME, API_KEY)
    return sg

@click.group()
def main():
    pass

SG_ASSET_FIELDS = ["id", "code", "sg_asset_type", "sg_status_list", "description"]


BATTERY_PROMPT = """A highly detailed 3D rendering of a makeshift battery in a style similar to Pixar and Fallout. The battery is cobbled together from various scavenged materials, such as old electronics and rusted metal parts. It has visible wires and connectors, with a weathered and aged appearance. The battery is placed on a small patch of dirt and grass, with a few scattered leaves and small rocks around it, creating a realistic yet whimsical scene, perfect for use as a thumbnail in a production tracker."""
BROKENLAPTOP_PROMPT = """A highly detailed 3D rendering of a broken laptop in a style similar to Pixar and Fallout. The laptop is visibly damaged, with cracks on the screen, missing keys, and exposed wires. The scene is realistic yet whimsical, perfect for use as a thumbnail in a production tracker."""
LIGHTBULB_PROMPT = """A highly detailed 3D rendering of a light bulb in a style similar to Pixar and Fallout. The light bulb is slightly worn and has a vintage look, with visible filaments inside. It is placed on a small patch of dirt and grass, with a few scattered leaves and small rocks around it. The scene is realistic yet whimsical, perfect for use as a thumbnail in a production tracker."""
@main.command()
@click.option("--project-id", type=int, help="Project Id")
@click.argument("asset_name_or_id", required=False)
def generate_thumbnail(project_id: int, asset_name_or_id: str=None):
    sg = get_connection()
    if asset_name_or_id is None:
        assets = sg.find("Asset", [["project", "is", {"type": "Project", "id": project_id}], ["image", "is", None]], SG_ASSET_FIELDS)
        for asset in assets:
            generate_asset_thumnail(sg, asset)
    else:
        print(f"Generating thumbnail for {asset_name_or_id}")
        try:
            asset_id = int(asset_name_or_id)
            asset = sg.find_one("Asset", [["project", "is", {"type": "Project", "id": project_id}], ["code", "is", asset_id]], SG_ASSET_FIELDS)
        except ValueError:
            asset = sg.find_one("Asset", [["project", "is", {"type": "Project", "id": project_id}], ["code", "is", asset_name_or_id]], SG_ASSET_FIELDS)
        generate_asset_thumnail(sg, asset)

def generate_asset_thumnail(sg, asset):
    print(asset)
    messages = [
        {"role": "system", "content": PROJECT_PROMPT},
        {"role": "system", "content": "You are an assistant writing prompts for Dale-E to generate thumbnails for assets in the project. Don't output anything else, just the prompt. The prompt must be written like an image description."},
        {"role": "system", "content": "Rendering style, pixar, 3d animation. fallout, forest, abandoned human objects, post-apocalyptic, ultra realistic"},
        {"role": "user", "content": "Make me a prompt for the asset Battery with description: Makeshift battery to store solar energy."},
        {"role": "assistant", "content": BATTERY_PROMPT},
        {"role": "user", "content": "Make me a prompt for the asset BrokenLaptop with description: Old, broken laptop."},
        {"role": "assistant", "content": BROKENLAPTOP_PROMPT},
        {"role": "user", "content": "Make me a prompt for the asset LightBulb with description: Light bulb to test the solar setup."},
        {"role": "assistant", "content": LIGHTBULB_PROMPT},
        {"role": "user", "content": f"Make me a prompt for the asset {asset['code']} with description: {asset['description']}"},
    ]
    response = openai.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
    )
    image_prompt = response.choices[0].message.content
    print(image_prompt)

    response = openai.images.generate(
        model="dall-e-3",
        prompt=image_prompt,
        n=1,
        size="1024x1024",
        # seed=5000,
    )
    print(response.data[0].url)
    # Download the image

    r = requests.get(response.data[0].url)
    tmp_dir = tempfile.mkdtemp()
    try:
        with open(f"{tmp_dir}/{asset['code']}.png", "wb") as f:
            f.write(r.content)
        sg.upload_thumbnail("Asset", asset["id"], f"{tmp_dir}/{asset['code']}.png")
    finally:
        shutil.rmtree(tmp_dir)

def sg_entity_to_ref(entity):
    return f"{entity['type']}:{entity['name']}"


DELIVERABLES = [
    {"id": 1, "name": "ep001", "entities": ["Episode:ep001"], "order": 1, "due_date": "2024-12-16"},
    {"id": 2, "name": "ep002", "entities": ["Episode:ep002"], "order": 2, "due_date": "2025-12-21"},
    {"id": 3, "name": "ep003", "entities": ["Episode:ep003"], "order": 3, "due_date": "2024-12-21"},
]

@main.command()
@click.argument("organization_name")
@click.argument("organization_display_name")
def create_organization(organization_name, organization_display_name):
    response = (
        supabase_client.table("organizations")
        .select("*")
        .eq("name", organization_name)
        .execute()
    )
    organization = response.data[0] if response.data else None

    if organization:
        print(f"Organization {organization_name} already exists")
        return
    else:
        response = (
            supabase_client.table("organizations")
            .insert(
                {"name": organization_name, "display_name": organization_display_name}
            )
            .execute()
        )

        if response.data:
            organization = response.data[0]
            print(
                f"Created organization {organization['name']} with id {organization['id']}"
            )
        else:
            print("Failed to create the organization.")


@main.command()
@click.argument("project_name")
@click.argument("display_name")
@click.argument("description")
@click.option("--template-id", type=str, help="Project Template", default=None)
@click.option("--template-name", type=str, help="Project Template", default=None)
def create_project(project_name: str, display_name: str, description: str, template_id: str=None, template_name=None):
    template_project = None
    if template_id:
        template_project = supabase_client.table("projects").select("*").eq("id", template_id).limit(1).single().execute().data
    elif template_name:
        template_project = supabase_client.table("projects").select("*").eq("name", template_name).limit(1).single().execute().data
    if template_project:
        # CREATE OR REPLACE FUNCTION copy_project(source_project_id UUID, dest_name TEXT, dest_display_name TEXT, dest_description TEXT, dest_is_template BOOLEAN)
        response = supabase_client.rpc("copy_project", {"source_project_id": template_project["id"], "dest_name": project_name, "dest_display_name": display_name, "dest_description": description, "dest_is_template": False}).execute()
    else:
        response = supabase_client.table("projects").insert({
            "name": project_name,
            "display_name": display_name,
            "description": description
        }).execute()
    project = response.data
    print(project)

@main.command()
@click.argument("project_name")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def delete_project(project_name: str, yes: bool):
    response = supabase_client.table("projects").select("*").eq("name", project_name).limit(1).single().execute()
    project = response.data

    print(project)
    if not yes:
        print("Are you sure you want to delete the following project?")
        response = input("Y/N")
        if response.lower() != "y":
            print("Aborted")
            return
    response = supabase_client.table("projects").delete().eq("name", project_name).execute()
    print(response)

@main.command()
@click.option("--shotgrid-project-id", type=int, help="Shotgrid Project Id")
@click.argument("project-name", type=str)
def shotgrid_import(shotgrid_project_id: int, project_name: str):
    sg = get_connection()
    response = supabase_client.table("projects").select("*").eq("name", project_name).limit(1).single().execute()
    project = response.data
    response = supabase_client.table("entity_types").select("*").eq("project_id", project["id"]).execute()
    entity_types = response.data
    entity_type_names = [et["name"] for et in entity_types]
    sg_assets = sg.find("Asset", [["project", "is", {"type": "Project", "id": shotgrid_project_id}]], ["id", "code", "sg_asset_type", "description", "assets"])
    default_entity_types = ["Shot", "Sequence", "Scene", "Episode"]
    sg_entity_types = []
    asset_types = []
    for et in default_entity_types:
        et_name = display_name_to_name(et)
        if et_name not in entity_type_names:
            sg_entity_types.append(et)
    for asset in sg_assets:
        if asset["sg_asset_type"] not in asset_types:
            asset_types.append(asset["sg_asset_type"])
        if asset["sg_asset_type"] not in sg_entity_types:
            name = display_name_to_name(asset["sg_asset_type"])
            if name in entity_type_names:
                continue
            sg_entity_types.append(asset["sg_asset_type"])
    if len(sg_entity_types) > 0:
        response = supabase_client.table("entity_types").upsert([{"name": display_name_to_name(t), "display_name": t, "project_id": project["id"]} for t in sg_entity_types]).execute()
        inserted_entity_types = response.data
        print(inserted_entity_types)

    # Update entity types
    response = supabase_client.table("entity_types").select("*").eq("project_id", project["id"]).execute()
    entity_types = response.data
    entity_types_by_names = {et["name"]: et for et in entity_types}
    entity_types_by_id = {et["id"]: et for et in entity_types}
    sg_entities = copy.copy(sg_assets)
    sg_entities += sg.find("Episode", [["project", "is", {"type": "Project", "id": shotgrid_project_id}]], ["id", "code", "description", "sequences", "assets"])
    sg_entities += sg.find("Sequence", [["project", "is", {"type": "Project", "id": shotgrid_project_id}]], ["id", "code", "description", "shots", "assets", "sg_scenes"])
    sg_entities += sg.find("Shot", [["project", "is", {"type": "Project", "id": shotgrid_project_id}]], ["id", "code", "description", "assets", "sg_scene", "sg_cut_duration"])
    sg_entities += sg.find("Scene", [["project", "is", {"type": "Project", "id": shotgrid_project_id}]], ["id", "code", "description", "sg_cut_duration", "assets"])
    sg_entities_by_ref = {}
    sg_entities_by_id = {}
    entities_insert = []
    for sg_entity in sg_entities:
        if sg_entity['type'] == 'Asset':
            entity_type_name = display_name_to_name(sg_entity["sg_asset_type"])
            key = f"{display_name_to_name(sg_entity['sg_asset_type'])}:{sg_entity['code']}"
        else:
            entity_type_name = display_name_to_name(sg_entity["type"])
            key = f"{display_name_to_name(sg_entity['type'])}:{sg_entity['code']}"
        sg_entities_by_ref[key] = sg_entity
        sg_entities_by_id[f"{sg_entity['type']}:{sg_entity['id']}"] = sg_entity
        et = entity_types_by_names[entity_type_name]
        attributes = {}
        if sg_entity["type"] == "Shot":
            attributes["duration"] = sg_entity["sg_cut_duration"]
            attributes["start_frame"] = 101
            attributes["end_frame"] = 101 + sg_entity["sg_cut_duration"]
        entities_insert.append({
            "name": sg_entity["code"],
            "description": sg_entity["description"],
            "entity_type_id": et["id"],
            "project_id": project["id"],
            "attributes": attributes,
        })

    response = supabase_client.table("entities").insert(entities_insert).execute()
    inserted_entities = response.data
    print(len(inserted_entities))
    response = supabase_client.table("entities").select("id,name,description,entity_type:entity_types(id,name,display_name)").eq("project_id", project["id"]).execute()
    entities = response.data
    print(entities[0])
    insert_entities_relations = []
    entities_by_ref = {f"{e['entity_type']['name']}:{e['name']}": e for e in entities}
    for entity in entities:
        if entity['entity_type']['display_name'] in asset_types:
            sg_entity = sg_entities_by_ref[f"{entity['entity_type']['name']}:{entity['name']}"]
            for sg_sub_asset in sg_entity["assets"]:
                sg_sub_asset = sg_entities_by_id[f"{sg_sub_asset['type']}:{sg_sub_asset['id']}"]
                sub_asset = entities_by_ref[f"{display_name_to_name(sg_sub_asset['sg_asset_type'])}:{sg_sub_asset['code']}"]
                insert_entities_relations.append({
                    "entity_id": entity["id"],
                    "related_entity_id": sub_asset["id"],
                    "key": "assets",
                })
        elif entity["entity_type"]["name"] == "scene":
            sg_entity = sg_entities_by_ref[f"{entity['entity_type']['name']}:{entity['name']}"]
            for sg_sub_asset in sg_entity["assets"]:
                sg_sub_asset = sg_entities_by_id[f"Scene:{sg_sub_asset['id']}"]
                sub_asset = entities_by_ref[f"scene:{sg_sub_asset['code']}"]
                insert_entities_relations.append({
                    "entity_id": entity["id"],
                    "related_entity_id": sub_asset["id"],
                    "key": "assets",
                })
        elif entity["entity_type"]["name"] == "episode":
            sg_entity = sg_entities_by_ref[f"{entity['entity_type']['name']}:{entity['name']}"]
            for sg_sub_asset in sg_entity["sequences"]:
                sg_sub_asset = sg_entities_by_id[f"Sequence:{sg_sub_asset['id']}"]
                sub_asset = entities_by_ref[f"sequence:{sg_sub_asset['code']}"]
                insert_entities_relations.append({
                    "entity_id": entity["id"],
                    "related_entity_id": sub_asset["id"],
                    "key": "sequences",
                })
            for sg_sub_asset in sg_entity["assets"]:
                sg_sub_asset = sg_entities_by_id[f"{sg_sub_asset['type']}:{sg_sub_asset['id']}"]
                sub_asset = entities_by_ref[f"{display_name_to_name(sg_sub_asset['sg_asset_type'])}:{sg_sub_asset['code']}"]
                insert_entities_relations.append({
                    "entity_id": entity["id"],
                    "related_entity_id": sub_asset["id"],
                    "key": "assets",
                })
        elif entity["entity_type"]["name"] == "sequence":
            sg_entity = sg_entities_by_ref[f"{entity['entity_type']['name']}:{entity['name']}"]
            for sg_sub_asset in sg_entity["shots"]:
                sg_sub_asset = sg_entities_by_id[f"Shot:{sg_sub_asset['id']}"]
                sub_asset = entities_by_ref[f"shot:{sg_sub_asset['code']}"]
                insert_entities_relations.append({
                    "entity_id": entity["id"],
                    "related_entity_id": sub_asset["id"],
                    "key": "shots",
                })
            for sg_sub_asset in sg_entity["assets"]:
                sg_sub_asset = sg_entities_by_id[f"{sg_sub_asset['type']}:{sg_sub_asset['id']}"]
                sub_asset = entities_by_ref[f"{display_name_to_name(sg_sub_asset['sg_asset_type'])}:{sg_sub_asset['code']}"]
                insert_entities_relations.append({
                    "entity_id": entity["id"],
                    "related_entity_id": sub_asset["id"],
                    "key": "assets",
                })
        elif entity["entity_type"]["name"] == "shot":
            sg_entity = sg_entities_by_ref[f"{entity['entity_type']['name']}:{entity['name']}"]
            for sg_sub_asset in sg_entity["assets"]:
                sg_sub_asset = sg_entities_by_id[f"{sg_sub_asset['type']}:{sg_sub_asset['id']}"]
                sub_asset = entities_by_ref[f"{display_name_to_name(sg_sub_asset['sg_asset_type'])}:{sg_sub_asset['code']}"]
                insert_entities_relations.append({
                    "entity_id": entity["id"],
                    "related_entity_id": sub_asset["id"],
                    "key": "assets",
                })
            if sg_entity["sg_scene"]:
                sg_sub_asset = sg_entity["sg_scene"]
                sg_sub_asset = sg_entities_by_id[f"Scene:{sg_sub_asset['id']}"]
                sub_asset = entities_by_ref[f"scene:{sg_sub_asset['code']}"]
                insert_entities_relations.append({
                    "entity_id": entity["id"],
                    "related_entity_id": sub_asset["id"],
                    "key": "scenes",
                })

    response = supabase_client.table("entities_entities_relation").insert(insert_entities_relations).execute()


def display_name_to_name(display_name: str):
    return display_name.lower().replace(" ", "_")


@main.command()
@click.argument("template_name")
@click.argument("organization_name")
@click.argument("project_name")
@click.argument("project_display_name")
@click.option("--replace", "-r", is_flag=True, help="Replace project if it already exists")
def create_project_from_script(template_name, organization_name: str, project_name, project_display_name, replace=False):
    from .utils import import_object
    template_func = import_object(f"{template_name}:create")
    organization = supabase_client.table("organizations").select("*").eq("name", organization_name).single().execute().data
    if replace:
        supabase_client.table("projects").delete().eq("organization_id", organization["id"]).eq("name", project_name).execute()
    project = template_func(supabase_client, organization["id"], project_name, project_display_name)
    print(f"Created project {project['name']} with id {project['id']}")



