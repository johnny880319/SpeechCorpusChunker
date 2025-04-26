from pathlib import Path
import os
import yaml
from dacite import from_dict

# my module
from .types import AppConfig, PathsConfig, VADConfig, PipelineConfig


def load_config(path: str="configs/default.yaml") -> AppConfig:
    # conpute project root path
    PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
    
    # load config file
    with open(os.path.join(PROJECT_ROOT, path), "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    
    # compute absolute path for all paths in config
    for key, val in cfg["paths"].items():
        cfg["paths"][key] = os.path.join(PROJECT_ROOT, val)
    
    # create directories if not exist
    for p in cfg["paths"].values():
        os.makedirs(p, exist_ok=True)
    
    # automatically instantiate dataclasses from config dict
    return from_dict(data_class=AppConfig, data=cfg)
