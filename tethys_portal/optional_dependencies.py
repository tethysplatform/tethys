from importlib import import_module


class MissingOptionalDependency(ImportError):
    pass


class FailedImport:
    def __init__(self, module, import_error):
        self.module_name = module
        self.error = import_error

    def __call__(self, *args, **kwargs):
        raise MissingOptionalDependency(
            f'Optional dependency "{self.module_name}" was not able to be imported because of the following error:\n'
            f"{self.error}."
        )

    def __getattr__(self, item):
        self.__call__()

    def __getitem__(self, item):
        self.__call__()


def _attempt_import(module, from_module, error_message):
    try:
        if from_module:
            from_module = import_module(from_module)
            return getattr(from_module, module)
        return import_module(module)
    except ImportError as e:
        return FailedImport(module, e)


def optional_import(module, from_module=None, error_message=None):
    if isinstance(module, (list, tuple)):
        return [_attempt_import(m, from_module, error_message) for m in module]
    else:
        return _attempt_import(module, from_module, error_message)


def verify_import(module, error_message=None):
    if isinstance(module, FailedImport):
        error_message = error_message or (
            f'Optional dependency "{module.module_name}" was not able to be imported because of the '
            f"following error:\n{module.error}."
        )
        raise MissingOptionalDependency(error_message)


def has_module(module, from_module=None):
    if isinstance(module, str):
        module = optional_import(module, from_module=from_module)
    return not isinstance(module, FailedImport)
