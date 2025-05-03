def load_config():
    import json
    try:
        with open("config.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_config(config):
    import json
    with open("config.json", "w") as file:
        json.dump(config, file, indent=4)