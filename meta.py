import abc
from abc import *


class MetaComponent(metaclass=abc.ABCMeta):
    @abstractmethod
    def run(self, namespace):
        pass

    @abstractmethod
    def link(self, child_comp):
        pass


class Flow(object):
    def __init__(self):
        self.head_component = None

    def set_start_comp(self, comp):
        self.head_component = comp

    def run(self, **kwargs):
        return self.head_component.run(**kwargs)

