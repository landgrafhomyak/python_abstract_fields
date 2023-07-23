from typing import TypeVar, Callable, Generic

import sys

if sys.version_info >= (3, 10):
    Type = type
else:
    from typing import Type

_T = TypeVar("_T", bound=type)
_V = TypeVar("_V")


def require_fields(**fields: type) -> Callable[[_T], _T]: ...


def _unwrap(cls: type) -> type: ...


class RequiredFieldNotInitializedError(TypeError):
    @property
    def field_name(self) -> str: ...

    @property
    def field_type(self) -> type: ...

    @property
    def abstract_class(self) -> type: ...

    @property
    def failed_subclass(self) -> type: ...


class AbstractFieldInitializedWithWrongType(TypeError, Generic[_V]):
    @property
    def field_name(self) -> str: ...

    @property
    def abstract_class(self) -> type: ...

    @property
    def expected_type(self) -> type: ...

    @property
    def actual_type(self) -> Type[_V]: ...

    @property
    def actual_value(self) -> _V: ...

    @property
    def failed_subclass(self) -> type: ...


class InheritanceTypeConflictError(TypeError, Generic[_T]):
    @property
    def base_abstract_class(self) -> _T: ...

    @property
    def field_name(self) -> str: ...

    @property
    def derived_unwrapped_abstract_class(self) -> _T: ...

    @property
    def base_field_type(self) -> type: ...

    @property
    def overriden_field_type(self) -> type: ...
