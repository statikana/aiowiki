import datetime
import logging
from dataclasses import dataclass, field
from enum import EnumMeta
from types import NoneType, UnionType
from typing import TYPE_CHECKING, Any, Never, TypeVar, get_args, get_origin

from awiki.constants import PRIMITIVES
from awiki.models.enums import PlatformType

if TYPE_CHECKING:
    from collections.abc import Callable

PlatformT = TypeVar("PlatformT", bound=PlatformType)
ModelT = TypeVar("ModelT", bound="InterfaceModel")


@dataclass(kw_only=True)
class InterfaceModel:
    "Represents any object which is a model to the API's object"

    __prefix_schema__: dict[str, str] = field(default_factory=lambda: {})

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)  # hmm

    @classmethod
    def _from_json(cls: ModelT, data: dict) -> ModelT:
        logging.debug(
            f"BEGIN DESERIALIZATION [cls {cls.__name__}] FROM [keys {list(data)}]"
        )
        
        constructed = {}

        for m_name, m_type in get_annotations(cls).items():
            method: Callable = None

            typ: type = m_type

            primary_is_array = get_origin(typ) in (list, tuple)
            primary_is_option = is_optional(typ)

            if data.get(m_name) is None:
                if primary_is_option:
                    constructed[m_name] = None
                    continue
                else:
                    raise ValueError(f"In attr {m_name} of {cls.__name__}, data received is None but expected structure {typ}.")

            while typ != (extracted := extract_typing(typ)):
                typ = extracted

            # call the type directly to construct
            if typ in PRIMITIVES or issubclass(typ.__class__, EnumMeta):
                method = typ

            # custom behavior in .deserialize
            elif issubclass(typ, CustomDeserializer):
                method = typ.deserialize

            # another InterfaceModel
            elif issubclass(typ, InterfaceModel):
                method = typ._from_json

            # other standard uses
            elif issubclass(typ, datetime.datetime):
                method = datetime.datetime.fromisoformat

            elif issubclass(typ, datetime.date):
                def method(string):
                    return datetime.date(*map(int, string[:-1].split("-")))

            else:
                raise ValueError(
                    f"unimplemented deserialization source: "
                    f"{typ.__name__} ({typ.__class__}) in {cls.__name__} for attr {m_name}"
                )
            
            value = data.get(m_name)

            if value is None:
                if primary_is_option:
                    constructed[m_name] = None
                    continue
                else:
                    raise ValueError(f"expected a value in {m_name} of {cls.__name__} of type {m_type}, got None.")
            
            if m_name in getattr(cls, "__prefix_schema__", {}):
                value = cls.__prefix_schema__[m_name] + value
                
            if primary_is_array:
                constructed[m_name] = [method(v) for v in value]
            else:
                constructed[m_name] = method(value)

        logging.debug(
            f"CONSTRUCTED [{cls.__name__}] FROM [{list(data.keys())}] TO [{list(constructed.keys())}"
        )
        return cls(**constructed)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(f'{k}={v}' for k, v in self.__dict__.items())})"

    def __repr__(self) -> str:
        return self.__str__()


def extract_typing(typed: Any, safe: bool = True) -> type:
    try:
        return get_args(typed)[0]
    except (TypeError, IndexError) as e:
        if safe:
            return typed
        raise TypeError(f"expected a typing object, got {typed}") from e

def is_optional(typed: Any) -> bool:
    return get_origin(typed) is UnionType and NoneType in get_args(typed)


def get_annotations(cls: ModelT) -> dict[str, type]:
    if not hasattr(cls, "__annotations__"):
        return {}
    annotations = cls.__annotations__.copy()
    if hasattr(cls, "__mro__"):
        for parent in cls.__mro__:
            if hasattr(parent, "__annotations__"):
                annotations.update(parent.__annotations__)
    return {k:v for k, v in annotations.items() if not k.startswith("_")}


class CustomDeserializer:
    @classmethod
    def deserialize(cls, data: dict) -> Never:
        raise NotImplementedError()
