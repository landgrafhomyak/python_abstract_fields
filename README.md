[![Python](https://img.shields.io/badge/Python-3-blue.svg?logo=python)](http://python.org)
![Github stable release](https://img.shields.io/github/v/release/landgrafhomyak/python_abstact_fields?label=Stable%20release)
![Github latest release](https://img.shields.io/github/v/release/landgrafhomyak/python_abstact_fields?include_prereleases&label=Latest%20release)

# Abstract fields

Addition to python's `abc` package for making abstract fields:

## Installing

#### Build from sources

```shell
pip install git+https://github.com/LandgrafHomyak/python_abstract_fields.git@v0.1
```

#### Install from wheel

```shell
pip install https://github.com/LandgrafHomyak/python_abstract_fields/releases/download/v0.1/abstract_fields-0.1-py3-none-any.whl
```

## Examples

Simple usage:

```python
from abstract_fields import require_fields


@require_fields(field=str)
class Abstract1:
    ...


class A(Abstract1):
    def __init__(self):
        self.field = "Hello world"


class B(Abstract1):
    def __init__(self):
        self.field = b"Hello world"


class C(Abstract1):
    def __init__(self):
        pass


a = A()  # ok
b = B()  # abstract_fields.AbstractFieldInitializedWithWrongType(TypeError): expected str, got bytes
c = C()  # abstract_fields.RequiredFieldNotInitializedError(TypeError): "field" not initialized
```

It can be combined with any other
[metaclasses](https://docs.python.org/3/reference/datamodel.html#metaclasses)
(usually
[`abc.ABCMeta`](https://docs.python.org/3/library/abc.html#abc.ABCMeta)
provided by inheriting from
[`abc.ABC`](https://docs.python.org/3/library/abc.html#abc.ABC)
):

```python
import abc
from abstract_fields import require_fields


@require_fields(field=str)
class Abstract2(abc.ABC):
    @abc.abstractmethod
    def function(self): ...


class D(Abstract2):
    def __init__(self):
        self.field = "Hello world"

    def function(self): ...


class E(Abstract2):
    def __init__(self):
        pass

    def function(self): ...


class F(Abstract2):
    def __init__(self):
        self.field = "Hello world"


d = D()  # ok
e = E()  # abstract_fields.RequiredFieldNotInitializedError(TypeError): "field" not initialized
f = F()  # TypeError from ABCMeta: abstract method not defined
```

It can be combined with other classes with abstract fields as well:

```python
from abstract_fields import require_fields


@require_fields(field3=str)
class Abstract3:
    ...


@require_fields(field4=str)
class Abstract4(Abstract3):
    ...

@require_fields(field3=int) # abstract_fields.InheritanceTypeConflictError(TypeError): int is not subclass of str
class Abstract5(Abstract3):
    ...


class G(Abstract3):
    def __init__(self):
        self.field3 = "3"


class H(Abstract4):
    def __init__(self):
        self.field3 = "3"


class I(Abstract4):
    def __init__(self):
        self.field3 = "3"
        self.field4 = "4"


g = G()  # ok
h = H()  # abstract_fields.RequiredFieldNotInitializedError: "field4" not initialized
i = I()  # ok
```

> **Be sure, that decorator creates and returns a new class wrapped with new metaclass
> so if your class should be registered by `__init_subclass__` or metaclass, you will have issues**

Decorators that will register this class must be written before (above) this decorator:

```python
from abstract_fields import require_fields


def register_class(cls): ...


@register_class
@require_fields(field3=str)
class Abstract6:
    ...
```

This module is debug-friendly!

Generated classes have a name that shows from which class they inherited:

```python
print(Abstract1)  # <class 'abstract_fields.AbstractFields[<class '__main__.Abstract1'>]'>
print(type(Abstract1))  # <class 'abstract_fields.AbstractFieldsMeta[<class '__main__.Abstract1'>, <class 'type'>]'>

print(Abstract2)  # <class 'abstract_fields.AbstractFields[<class '__main__.Abstract2'>]'>
print(type(Abstract2))  # <class 'abstract_fields.AbstractFieldsMeta[<class '__main__.Abstract2'>, <class 'abc.ABCMeta'>]'>

print(Abstract3)  # <class 'abstract_fields.AbstractFields[<class '__main__.Abstract3'>]'>
print(type(Abstract3))  # <class 'abstract_fields.AbstractFieldsMeta[<class '__main__.Abstract3'>, <class 'type'>]'>
print(Abstract4)  # <class 'abstract_fields.AbstractFields[<class '__main__.Abstract4'>]'>
print(type(Abstract4))  # <class 'abstract_fields.AbstractFieldsMeta[<class '__main__.Abstract4'>, <class 'type'>]'>
```

If you're forgotten to initialize field, raised error will show you in the debugger a lot of useful information:

```python
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
    print(err.abstract_class)  # <class 'abstract_fields.AbstractFields[<class '__main__.Abstract7'>]'>
    print(err.failed_subclass)  # <class '__main__.J'>

    raise
```

And error will look like:

```
Traceback (most recent call last):
  File "...", line 15, in <module>
    j = J()  # ok
  File "...", line X, in ...
    ...
abstract_fields.RequiredFieldNotInitializedError: Field 'field' (type <class 'str'>) required by abstract class <class '__main__.Abstract6'> not initialized in __new__ nor __init__ of subclass <class '__main__.J'>
```

Other errors and their fields can be checked in [type hints file](./abstract_fields/__init__.pyi).

Also, there is an inspection method for unwrapping; it shouldn't be used in production code:

```python
from abstract_fields import require_fields, RequiredFieldNotInitializedError, _unwrap


@require_fields()
class Abstract8:
    ...


print(Abstract8)  # <class 'abstract_fields.AbstractFields[<class '__main__.Abstract7'>]'>
print(_unwrap(Abstract8))  # <class '__main__.Abstract7'>
```

## FAQ

### Why not annotation?

Not all annotations will be used for marking abstract fields (e.g., abstract class defines some fields by itself or inherits them),
so there should be wrapper like `field: AbstractField[str]`, but linters don't know what to do with them and will break.

And, of course, annotations in python can be used not only for type checking;
in this case, abstract fields will conflict with other frameworks and libraries that use annotations in this way.