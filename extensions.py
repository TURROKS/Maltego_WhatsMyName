from maltego_trx.decorator_registry import TransformRegistry, TransformSet

registry = TransformRegistry(
        owner="Mario Rojas",
        author="Mario Rojas <mario.rojas-chinchilla@outlook.com>",
        host_url="https://transforms.acme.com",
        seed_ids=["demo"]
)

# The rest of these attributes are optional

whatsmyname_set = TransformSet("WhatsMyName", "WhatsMyName Transforms")

# metadata
registry.version = "0.1"

# global settings
# from maltego_trx.template_dir.settings import api_key_setting
# registry.global_settings = [api_key_setting]

# transform suffix to indicate datasource
# registry.display_name_suffix = " [ACME]"

# reference OAuth settings
# registry.oauth_settings_id = ['github-oauth']
