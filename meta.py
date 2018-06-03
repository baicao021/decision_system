import abc
from abc import *


class Component(metaclass=abc.ABCMeta):
    def __init__(self):
        self.child_comp = None

    @abstractmethod
    def run(self):
        pass

    def link(self, child_comp):
        self.child_comp = child_comp


class Flow(object):
    def __init__(self):
        self.head_component = None

    def register_head_component(self, comp):
        self.head_component = comp

    def run(self, **kwargs):
        return self.head_component.run(**kwargs)

