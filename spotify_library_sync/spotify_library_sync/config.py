from dynaconf import Dynaconf

# default
settings = Dynaconf(settings_files=[
    "settings.toml",
    "*.yaml",
    "/config/settings.yaml"
])

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
