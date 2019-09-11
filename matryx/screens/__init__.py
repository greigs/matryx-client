import pkgutil
import importlib


def get_available_screens():
    for _, name, _ in pkgutil.iter_modules(__path__):
        yield name


def get_screen_class(screen_name):
    if screen_name not in get_available_screens():
        raise ValueError(f"{screen_name} not found.")

    screen_module = importlib.import_module(f".{screen_name}", package=__package__)
    screen_class = screen_module.screen_class

    return screen_class
