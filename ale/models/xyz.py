# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from ale.models.base_model_ import Model
from ale import util


class XYZ(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self):  # noqa: E501
        """XYZ - a model defined in OpenAPI

        """
        self.openapi_types = {
        }

        self.attribute_map = {
        }

    @classmethod
    def from_dict(cls, dikt) -> 'XYZ':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The XYZ of this XYZ.  # noqa: E501
        :rtype: XYZ
        """
        return util.deserialize_model(dikt, cls)