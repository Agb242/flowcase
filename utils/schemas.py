from marshmallow import Schema, fields, validate

class RegisterUserSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    groups = fields.List(fields.Str(), required=True)

class UserCreateSchema(Schema):
    username = fields.Str(required=True)
    groups = fields.List(fields.Str(), required=True)

class DropletInstanceRequestSchema(Schema):
    droplet_id = fields.Int(required=True)
    resolution = fields.Str(required=False, allow_none=True)

class DropletCreateSchema(Schema):
    id = fields.Int(required=False, allow_none=True)
    description = fields.Str(allow_none=True)
    image_path = fields.Str(allow_none=True)
    display_name = fields.Str(required=True)
    droplet_type = fields.Str(required=True)
    container_docker_registry = fields.Str(allow_none=True)
    container_docker_image = fields.Str(allow_none=True)
    container_cores = fields.Float(allow_none=True)
    container_memory = fields.Float(allow_none=True)
    container_persistent_profile_path = fields.Str(allow_none=True)
    server_ip = fields.Str(allow_none=True)
    server_port = fields.Str(allow_none=True)
    server_username = fields.Str(allow_none=True)
    server_password = fields.Str(allow_none=True)

class GroupCreateSchema(Schema):
    id = fields.Int(required=False, allow_none=True)
    display_name = fields.Str(required=True)
    perm_admin_panel = fields.Bool(missing=False)
    perm_view_instances = fields.Bool(missing=False)
    perm_edit_instances = fields.Bool(missing=False)
    perm_view_users = fields.Bool(missing=False)
    perm_edit_users = fields.Bool(missing=False)
    perm_view_droplets = fields.Bool(missing=False)
    perm_edit_droplets = fields.Bool(missing=False)
    perm_view_registry = fields.Bool(missing=False)
    perm_edit_registry = fields.Bool(missing=False)
    perm_view_groups = fields.Bool(missing=False)
    perm_edit_groups = fields.Bool(missing=False)
    
    # Workshop permissions
    perm_view_workshops = fields.Bool(missing=False)
    perm_edit_workshops = fields.Bool(missing=False)
    perm_create_workshops = fields.Bool(missing=False)
    perm_manage_templates = fields.Bool(missing=False)
    perm_view_workshop_instances = fields.Bool(missing=False)

class RegistryCreateSchema(Schema):
    id = fields.Int(required=False, allow_none=True)
    url = fields.Str(required=True)
class DropletUpdateSchema(Schema):
    id = fields.Int(required=True)
    description = fields.Str(allow_none=True)
    image_path = fields.Str(allow_none=True)
    display_name = fields.Str(required=True)
    droplet_type = fields.Str(required=True)
    container_docker_registry = fields.Str(allow_none=True)
    container_docker_image = fields.Str(allow_none=True)
    container_cores = fields.Float(allow_none=True)
    container_memory = fields.Float(allow_none=True)
    container_persistent_profile_path = fields.Str(allow_none=True)
    server_ip = fields.Str(allow_none=True)
    server_port = fields.Str(allow_none=True)
    server_username = fields.Str(allow_none=True)
    server_password = fields.Str(allow_none=True)

class UserUpdateSchema(Schema):
    id = fields.Int(required=True)
    username = fields.Str(required=True)
    groups = fields.List(fields.Str(), required=True)

class GroupUpdateSchema(Schema):
    id = fields.Int(required=True)
    display_name = fields.Str(required=True)
    perm_admin_panel = fields.Bool(missing=False)
    perm_view_instances = fields.Bool(missing=False)
    perm_edit_instances = fields.Bool(missing=False)
    perm_view_users = fields.Bool(missing=False)
    perm_edit_users = fields.Bool(missing=False)
    perm_view_droplets = fields.Bool(missing=False)
    perm_edit_droplets = fields.Bool(missing=False)
    perm_view_registry = fields.Bool(missing=False)
    perm_edit_registry = fields.Bool(missing=False)
    perm_view_groups = fields.Bool(missing=False)
    perm_edit_groups = fields.Bool(missing=False)
    
    # Workshop permissions
    perm_view_workshops = fields.Bool(missing=False)
    perm_edit_workshops = fields.Bool(missing=False)
    perm_create_workshops = fields.Bool(missing=False)
    perm_manage_templates = fields.Bool(missing=False)
    perm_view_workshop_instances = fields.Bool(missing=False)

# Workshop schemas
class WorkshopTemplateCreateSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    category = fields.Str(required=True)
    thumbnail = fields.Str(allow_none=True)
    config_schema = fields.Str(allow_none=True)
    template_droplets = fields.Str(allow_none=True)
    estimated_duration = fields.Int(allow_none=True)
    difficulty_level = fields.Str(allow_none=True)
    is_public = fields.Bool(missing=True)

class WorkshopCreateSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    template_id = fields.Str(allow_none=True)
    is_public = fields.Bool(missing=False)

class UserWorkshopCreateSchema(Schema):
    workshop_id = fields.Str(required=True)
    template_id = fields.Str(allow_none=True)
    custom_config = fields.Str(allow_none=True)

class RegistryUpdateSchema(Schema):
    id = fields.Int(required=True)
    url = fields.Str(required=True)