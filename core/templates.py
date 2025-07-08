import yaml

def load_template(name):
    with open(f"templates/{name}.yaml") as f:
        return yaml.safe_load(f) 