from dataclasses import dataclass, fields
from enum import Enum
from functools import partial
from types import NoneType
from typing import Any, Callable, Optional, Union, get_args, get_origin

from aiowiki.constants import PRIMITIVES


@dataclass(kw_only=True)
class InterfaceModel:
    "Represents any object which is a model to the API's object"

    def __init__(self, **kwargs):
        for m_name, m_type in self.__annotations__.items():
            if m_name not in kwargs:
                raise ValueError(
                    f"missing required argument {m_name} of type {m_type} in {self.__class__.__name__}"
                )
            setattr(self, m_name, kwargs[m_name])

    @classmethod
    def from_json(cls, data: dict):
        # cls should be the class that is calling this method
        # not the InterfaceModel class

        constructed = dict()

        for m_name, m_type in cls.__annotations__.items():

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

            is_array = typ in (list, tuple)

            if is_array:
                typ = extract_typing(m_type)

            # call the type directly to construct
            if typ in (*PRIMITIVES, Enum):
                method = typ

            # custom behavior in .deserialize
            elif typ is CustomDeserializer:
                method = typ.deserialize

            # another InterfaceModel
            elif issubclass(typ, InterfaceModel):
                method = typ.from_json

            else:
                raise ValueError(
                    f"unimplemented deserialization source: {typ} in {cls.__name__} for {m_name}"
                )

            if is_option:
                value = data.get(m_name, None)
            else:
                value = data[m_name]

            if is_array:
                constructed[m_name] = [method(v) for v in value]
            else:
                constructed[m_name] = method(value)
        return cls(**constructed)


def extract_typing(typed: Any):
    return get_args(typed)[0]


def is_optional(typed: Any):
    return get_origin(typed) is Union and NoneType in get_args(typed)


class CustomDeserializer:
    @classmethod
    def deserialize(cls, data: dict):
        raise NotImplementedError()
