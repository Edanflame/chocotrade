""""""
from dotenv import set_key

from ..base.plugin import CHOCO_ENV_FILE, PLUGINS
from ..utilities import safe_import_module


class PluginManager:
    """"""
    def __init__(self):
        """"""
        data_path = PLUGINS["tushare"]["module_path"]
        self.datasource = safe_import_module(data_path[0], data_path[1]).TushareDataSource()
        self.plugins = {}

    def get_datasource(self):
        return self.datasource

    def get_gateway(self):
        """"""
        pass

    def load_plugin(self, plugin_name):
        """"""
        name = PLUGINS[plugin_name]["name"]
        if name not in self.plugins:
            data_path = PLUGINS[plugin_name]["module_path"]
            module = safe_import_module(data_path[0], data_path[1])
            loaded_plugin = getattr(module, PLUGINS[plugin_name]["class"])()
            self.plugins[name] = loaded_plugin
        else:
            loaded_plugin = self.plugins[name]

        return loaded_plugin

    def load_config(self, plugin_name):
        """"""
        data_path = PLUGINS[plugin_name]["module_path"]
        module = safe_import_module(data_path[0], data_path[1])
        auth_fields = PLUGINS[plugin_name]["auth_fields"]
        config = {}

        for field in auth_fields:
            config[field] = getattr(
                getattr(module, PLUGINS[plugin_name]["class"]
            ).config_class(), field)

        return config

    def save_config(self, plugin_name, config):
        """"""
        data_path = PLUGINS[plugin_name]["module_path"]
        module = safe_import_module(data_path[0], data_path[1])
        env_prefix = getattr(
            module, PLUGINS[plugin_name]["class"]
        ).config_class().model_config.get("env_prefix", "")
        for key, value in config.items():
            full_key = f"{env_prefix}{key.upper()}"
            set_key(str(CHOCO_ENV_FILE), full_key, value)
