from web3.exceptions import (
    ValidationError,
)


def attach_modules(parent_module, module_definitions):
    for module_name, module_info in module_definitions.items():
        module_class = module_info[0]
        module_class.attach(parent_module, module_name)

        if len(module_info) == 2:
            submodule_definitions = module_info[1]
            module = getattr(parent_module, module_name)
            attach_modules(module, submodule_definitions)
        elif len(module_info) != 1:
            raise ValidationError("Module definitions can only have 1 or 2 elements.")
