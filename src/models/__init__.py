###
# File:   src\models\__init__.py
# Date:   2025-01-21 / 08:58
# Author: alexrjs
###


# imports
from re import match
from types import SimpleNamespace


# constants


# variables


# functions/classes
class ExtendedNamespaceOld(SimpleNamespace):
    """ Extended version from SimpleNamespace """

    def set(self, attribute_:str=None, value_:object=None) -> None:
        """
        Sets an attribute on the ExtendedNamespace dynamically.

        Parameters:
        attribute_ (str): The name of the attribute to set.
        value_ (object): The value to assign to the attribute.
        """

        if attribute_ is None:
            print("Problem: No attribute name given!")
            return None

        _name = attribute_.replace(" ", "_")
        if not match(r'^[\w]{1}$', _name):
            raise ValueError("Attribute name contains unallowed special characters.")
        
        setattr(self, attribute_, value_)

    def get(self, attribute_:str=None) -> object:
        """
        Gets the value of an attribute on the ExtendedNamespace dynamically.

        Parameters:
        attribute_name (str): The name of the attribute to retrieve.

        Returns:
        Optional[Any]: The value of the attribute, or None if the attribute does not exist.
        """

        if attribute_ is None:
            print("Problem: No attribute name given!")
            return None

        _name = attribute_.replace(" ", "_")
        if not match(r'^[\w]{1}$', _name):
            raise ValueError("Attribute name contains unallowed special characters.")
        
        return getattr(self, attribute_, None)
