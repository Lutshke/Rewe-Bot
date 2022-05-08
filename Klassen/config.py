import yaml


def get_config() -> dict:
    with open("Config.yaml", "r") as config:
        return yaml.load(config, Loader=yaml.SafeLoader)
