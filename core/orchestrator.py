import json

def load_config():
    config_path = "config.json"

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            dict_config = json.load(f)

            if not isinstance(dict_config, dict):
                raise TypeError("dict_config must be a dict type!")

            return dict_config
        
    except Exception as e:
        raise Exception(f"Unable to load config --> dict: {e}")

