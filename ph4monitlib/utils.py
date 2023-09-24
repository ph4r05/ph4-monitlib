import json

import yaml

from ph4monitlib import has_yaml_ext


def load_config_fh(fh, is_yaml=False):
    return yaml.safe_load(fh) if is_yaml else json.load(fh)


def load_config_data(data, is_yaml=False):
    return yaml.safe_load(data) if is_yaml else json.loads(data)


def load_config_file(fpath):
    with open(fpath, "r+") as fh:
        return load_config_fh(fh, has_yaml_ext(fpath))
