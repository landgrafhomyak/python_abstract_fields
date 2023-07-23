class RequiredFieldNotInitializedError(TypeError):
    __slots__ = ("__fname", "__ftype", "__abc", "__sub")

    def __init__(self, cls, fname, ftype, subcls):
        super(RequiredFieldNotInitializedError, self).__init__(
            f'Field {fname !r} (type {ftype !r}) required by abstract class {cls !r} not initialized in __new__ nor __init__ of subclass {subcls !r}'
        )
        self.__fname = fname
        self.__ftype = ftype
        self.__abc = cls
        self.__sub = subcls

    @property
    def field_name(self):
        return self.__fname

    @property
    def field_type(self):
        return self.__ftype

    @property
    def abstract_class(self):
        return self.__abc

    @property
    def failed_subclass(self):
        return self.__sub


class AbstractFieldInitializedWithWrongType(TypeError):
    __slots__ = ("__fname", "__abc", "__sub", "__expected", "__actual", "__value")

    def __init__(self, fname, abc, expected, value, subclass):
        super(AbstractFieldInitializedWithWrongType, self).__init__(
            f"Field {fname !r} must have type {expected !r}, got {type(value) !r} (required by abstract class {abc !r} inherited by {subclass !r})"
        )
        self.__fname = fname
        self.__abc = abc
        self.__sub = subclass
        self.__expected = expected
        self.__actual = type(value)
        self.__value = value

    @property
    def field_name(self):
        return self.__fname

    @property
    def abstract_class(self):
        return self.__abc

    @property
    def expected_type(self):
        return self.__expected

    @property
    def actual_type(self):
        return self.__actual

    @property
    def actual_value(self):
        return self.__value

    @property
    def failed_subclass(self):
        return self.__sub


class InheritanceTypeConflictError(TypeError):
    __slots__ = ("__fname", "__abc", "__sub", "__expected", "__actual")

    def __init__(self, fname, abc, subcls, expected, actual):
        super(InheritanceTypeConflictError, self).__init__(
            f"Overriding field {fname !r} with type {actual !r} which is not subtype of {expected !r} defined in {subcls !r} and overriden from {abc !r}"
        )
        self.__fname = fname
        self.__abc = abc
        self.__sub = subcls
        self.__expected = expected
        self.__actual = actual

    @property
    def base_abstract_class(self):
        return self.__abc

    @property
    def field_name(self):
        return self.__fname

    @property
    def derived_unwrapped_abstract_class(self):
        return self.__sub

    @property
    def base_field_type(self):
        return self.__expected

    @property
    def overriden_field_type(self):
        return self.__actual


class AbstractFieldsMeta(type):
    def __call__(cls, *args, **kwargs):
        obj = super(AbstractFieldsMeta, cls).__call__(*args, **kwargs)
        for attr, tp in cls.__fields.items():
            if not hasattr(obj, attr):
                raise RequiredFieldNotInitializedError(cls.__wrapper_class, attr, tp, cls)
            val = getattr(obj, attr)
            if not isinstance(val, tp):
                raise AbstractFieldInitializedWithWrongType(attr, cls.__wrapper_class, tp, val, cls)

        return obj

    # Python doesn't provide a comfortable mechanism like `internal` in kotlin or `friend` in c++, so some shit code here

    @staticmethod
    def _decorator(**fields):
        def _require_fields_decorator_instance(class_to_wrap):
            if isinstance(class_to_wrap, AbstractFieldsMeta) and class_to_wrap is class_to_wrap.__wrapper_class:
                raise TypeError("Only one @require_fields must be, it can consume several fields")

            if isinstance(class_to_wrap, AbstractFieldsMeta):
                meta_bases = (type(class_to_wrap),)
            else:
                meta_bases = (AbstractFieldsMeta, type(class_to_wrap))

            mcs = type(
                f'AbstractFieldsMeta[{class_to_wrap!r}, {type(class_to_wrap) !r}]',
                meta_bases,
                dict()
            )

            cls = mcs(
                f'AbstractFields[{class_to_wrap !r}]',
                (class_to_wrap,),
                dict()
            )

            if isinstance(class_to_wrap, AbstractFieldsMeta):
                for attr in fields.keys() & class_to_wrap.__fields.keys():
                    if not issubclass(fields[attr], class_to_wrap.__fields[attr]):
                        for abc in reversed(class_to_wrap.mro()):
                            if not isinstance(abc, AbstractFieldsMeta):
                                continue
                            if abc is abc.__wrapper_class:
                                if attr in abc.__fields:
                                    field_provider = abc
                                    break
                        else:
                            raise RuntimeError("Unreachable")
                        raise InheritanceTypeConflictError(attr, field_provider, class_to_wrap, class_to_wrap.__fields[attr], fields[attr])
                cls.__fields = class_to_wrap.__fields.copy()
                cls.__fields.update(fields)
            else:
                cls.__fields = fields
            cls.__wrapper_class = cls
            cls.__origin_class = class_to_wrap
            return cls

        return _require_fields_decorator_instance

    @staticmethod
    def _unwrap(cls):
        if not isinstance(cls, AbstractFieldsMeta):
            raise TypeError(f"{cls !r} is not wrapped with abstract fields checker")

        if cls is not cls.__wrapper_class:
            raise TypeError(f"{cls !r} inherits abstract fields checker wrapper, but not wrapper itself")

        return cls.__origin_class


require_fields = AbstractFieldsMeta._decorator
del AbstractFieldsMeta._decorator

_unwrap = AbstractFieldsMeta._unwrap
del AbstractFieldsMeta._unwrap
