from abstract_fields import require_fields, RequiredFieldNotInitializedError


@require_fields(field=str)
class Abstract7:
    ...


class J(Abstract7):
    def __init__(self):
        pass


try:
    j = J()
except RequiredFieldNotInitializedError as err:
    print(err.field_name)  # field
    print(err.field_type)  # <class 'str'>
    print(err.abstract_class)  # <class '__main__.Abstract6'>
    print(err.failed_subclass)  # <class '__main__.J'>

    raise