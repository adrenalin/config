"""
External source interface class

@author Arttu Manninen <arttu@kaktus.cc>
"""
from abc import ABC, abstractmethod

class ExternalInterface(ABC):
    """ External interface """
    def __init__(self):
        """ Constructor """

    @abstractmethod
    def load(self, config):
        """ Load external config """
