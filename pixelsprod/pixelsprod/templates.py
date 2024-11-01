from typing import Optional

from .schema import (TaskTemplate,
                     EntityTemplate,
                     Requirement,
                     HumanResource,
                     HardwareResource,
                     ExpressionAttribute)


character_modeling_task = TaskTemplate(name="modeling", step="modeling", duration="=10+2")
character_modeling_task.requirements.append(Requirement(rtype=HumanResource, filter=lambda x: character_modeling_task.step in x.skills))
character_modeling_task.requirements.append(Requirement(rtype=HardwareResource))

character_shading_task = TaskTemplate(name="shading", step="shading", duration=5, upstream=[character_modeling_task])
character_shading_task.requirements.append(Requirement(rtype=HumanResource, filter=lambda x: character_shading_task.step in x.skills))
character_shading_task.requirements.append(Requirement(rtype=HardwareResource))

character_rigging_task = TaskTemplate(name="rigging", step="rigging", duration=10, upstream=[character_modeling_task, character_shading_task])
character_rigging_task.requirements.append(Requirement(rtype=HumanResource, filter=lambda x: character_rigging_task.step in x.skills))
character_rigging_task.requirements.append(Requirement(rtype=HardwareResource))

character_task_template = EntityTemplate(name="character")
character_task_template.tasks = [character_modeling_task,
                                 character_shading_task,
                                 character_rigging_task]

prop_modeling_task = TaskTemplate(name="modeling", step="modeling", duration=7)
prop_modeling_task.requirements.append(Requirement(rtype=HumanResource, filter=lambda x: prop_modeling_task.step in x.skills))
prop_modeling_task.requirements.append(Requirement(rtype=HardwareResource))

prop_shading_task = TaskTemplate(name="shading", step="shading", duration=5, upstream=[prop_modeling_task])
prop_shading_task.requirements.append(Requirement(rtype=HumanResource, filter=lambda x: prop_shading_task.step in x.skills))
prop_shading_task.requirements.append(Requirement(rtype=HardwareResource))

prop_task_template = EntityTemplate(name="prop")
prop_task_template.tasks = [prop_modeling_task,
                            prop_shading_task]

environment_modeling_task = TaskTemplate(name="modeling", step="modeling", duration=10)
environment_modeling_task.requirements.append(Requirement(rtype=HumanResource, filter=lambda x: environment_modeling_task.step in x.skills))
environment_modeling_task.requirements.append(Requirement(rtype=HardwareResource))

environment_shading_task = TaskTemplate(name="shading", step="shading", duration=5, upstream=[environment_modeling_task])
environment_shading_task.requirements.append(Requirement(rtype=HumanResource, filter=lambda x: environment_shading_task.step in x.skills))
environment_shading_task.requirements.append(Requirement(rtype=HardwareResource))

environment_layout_task = TaskTemplate(name="layout", step="layout", duration=8, upstream=[environment_modeling_task, environment_shading_task])
environment_layout_task.requirements.append(Requirement(rtype=HumanResource, filter=lambda x: environment_layout_task.step in x.skills))
environment_layout_task.requirements.append(Requirement(rtype=HardwareResource))

environment_task_template = EntityTemplate(name="environment")
environment_task_template.tasks = [environment_modeling_task,
                                   environment_shading_task,
                                   environment_layout_task]

shot_layout_task = TaskTemplate(name="layout", step="layout", duration=8)
shot_layout_task.requirements.append(Requirement(rtype=HumanResource, filter=lambda x: shot_layout_task.step in x.skills))
shot_layout_task.requirements.append(Requirement(rtype=HardwareResource))

shot_animation_task = TaskTemplate(name="animation", step="animation", duration="=0.2*entity.attributes.frame_count", upstream=[shot_layout_task])
shot_animation_task.requirements.append(Requirement(rtype=HumanResource, filter=lambda x: shot_animation_task.step in x.skills))
shot_animation_task.requirements.append(Requirement(rtype=HardwareResource))

shot_render_task = TaskTemplate(name="render", step="render", duration=8, upstream=[shot_layout_task, shot_animation_task])
shot_render_task.requirements.append(Requirement(rtype=HardwareResource))

shot_compositing_task = TaskTemplate(name="compositing", step="compositing", duration=8, upstream=[shot_layout_task, shot_animation_task, shot_render_task])
shot_compositing_task.requirements.append(Requirement(rtype=HumanResource, filter=lambda x: shot_compositing_task.step in x.skills))
shot_compositing_task.requirements.append(Requirement(rtype=HardwareResource))

shot_task_template = EntityTemplate(name="shot")
shot_task_template.tasks = [shot_layout_task,
                            shot_animation_task,
                            shot_render_task,
                            shot_compositing_task]


TASK_TEMPLATES = {}
TASK_TEMPLATES["Prop"] = prop_task_template
TASK_TEMPLATES["Character"] = character_task_template
TASK_TEMPLATES["Environment"] = environment_task_template
TASK_TEMPLATES["Shot"] = shot_task_template
