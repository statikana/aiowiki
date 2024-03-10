from dataclasses import dataclass
import datetime
from enum import EnumMeta
import logging
from types import NoneType
from typing import Any, Callable, TypeVar, Union, get_args, get_origin

from aiowiki.constants import PRIMITIVES
from aiowiki.models.enums import PlatformType

PlatformT = TypeVar("PlatformT", bound=PlatformType)


@dataclass(kw_only=True)
class InterfaceModel:
    "Represents any object which is a model to the API's object"

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)  # hmm

    @classmethod
    def from_json(cls, data: dict):
        logging.debug(
            f"BEGIN DESERIALIZATION [cls {cls.__name__}] FROM [keys {list(data)}]"
        )

        constructed = dict()

        for m_name, m_type in get_annotations(cls).items():

            method: Callable = None

            is_option = is_optional(m_type)

            if is_option:
                if data.get(m_name, None) is None:
                    constructed[m_name] = None
                    continue
                else:
                    typ = extract_typing(m_type)
            else:
                typ = m_type

            is_array = get_origin(typ) in (list, tuple)
            if is_array:
                typ = extract_typing(m_type)

            while (ori := get_origin(typ)) is not None:
                typ = ori

            # call the type directly to construct
            if typ in PRIMITIVES or issubclass(typ.__class__, EnumMeta):
                method = typ

            # custom behavior in .deserialize
            elif issubclass(typ, CustomDeserializer):
                method = typ.deserialize

            # another InterfaceModel
            elif issubclass(typ, InterfaceModel):
                method = typ.from_json

            # other standard uses
            elif issubclass(typ, datetime.datetime):
                method = datetime.datetime.fromisoformat

            elif issubclass(typ, datetime.date):
                method = lambda string: datetime.date(*map(int, string[:-1].split("-")))

            else:
                raise ValueError(
                    f"unimplemented deserialization source: "
                    f"{typ.__name__} ({typ.__class__}) in {cls.__name__} for attr {m_name}"
                )
            try:
                if is_option:
                    value = data.get(m_name, None)
                else:
                    value = data[m_name]
            except KeyError as e:
                logging.error(
                    f"KeyError: member {m_name} not found in {list(data.keys())} [cls {cls.__name__}]"
                )
                raise e

            if is_array:
                constructed[m_name] = [method(v) for v in value]
            else:
                constructed[m_name] = method(value)

        logging.debug(
            f"CONSTRUCTED [{cls.__name__}] FROM [{list(data.keys())}] TO [{list(constructed.keys())}"
        )
        return cls(**constructed)

    def __str__(self):
        return f"{self.__class__.__name__}({', '.join(f'{k}={v}' for k, v in self.__dict__.items())})"

    def __repr__(self):
        return self.__str__()


def extract_typing(typed: Any):
    return get_args(typed)[0]


def is_optional(typed: Any):
    return get_origin(typed) is Union and NoneType in get_args(typed)


def get_annotations(cls: InterfaceModel):
    if not hasattr(cls, "__annotations__"):
        return dict()
    annotations = cls.__annotations__.copy()
    if hasattr(cls, "__mro__"):
        for parent in cls.__mro__:
            if hasattr(parent, "__annotations__"):
                annotations.update(parent.__annotations__)

    return annotations


class CustomDeserializer:
    @classmethod
    def deserialize(cls, data: dict):
        raise NotImplementedError()
