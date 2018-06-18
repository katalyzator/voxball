# -*- coding: utf-8 -*-
from uuid import UUID
import json


def json_list_from_string_list(_list):
    return list(map(json.loads, _list))


def int_or_none(value):
    if value:
        return int(value)
    return value
    

def empty_to_none(s):
    """
    :param s: String to be converted.
    :return: If string is empty returns None; otherwise returns string itself.
    """
    if s is not None:
        if len(s) == 0:
            return None
    return s
    

def integer_list(_list):
    return map(int, _list)


def zero_div(a, b):
    return a / b if b else 0


def valid_uuid4(uuid_string):
    try:
        UUID(uuid_string, version=4)
    except ValueError:
        return False
    return True


def handle_param(value, type1, type2=None, default=None):
    try:
        value = type1(value)
        if type2:
            value = type2(value)
    except:
        value = default
    return value
