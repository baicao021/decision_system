import abc
from abc import *


class Component(metaclass=abc.ABCMeta):
    def __init__(self):
        self.namespace = None
        self.child_comp = None

    def run(self, namespace):
        self.namespace = namespace
        self.inner_run()
        if not self.is_endpoint:
            self.child_comp.run(self.namespace)

    @abstractmethod
    def inner_run(self):
        pass

    @property
    @abstractmethod
    def is_endpoint(self):
        return


class AnyToOneComponent(Component):
    def link(self, child_comp):
        assert isinstance(child_comp, Component)
        self.child_comp = child_comp

    @property
    def is_endpoint(self):
        return False

    @abstractmethod
    def inner_run(self):
        pass


class ZeroToOneComponent(Component):
    def link(self, child_comp):
        assert isinstance(child_comp, Component)
        self.child_comp = child_comp

    @property
    def is_endpoint(self):
        return False

    @abstractmethod
    def inner_run(self):
        pass


class AnyToZeroComponent(Component):
    @property
    def is_endpoint(self):
        return True

    @abstractmethod
    def inner_run(self):
        pass


class AnyToMultipleComponent(Component):
    def inner_run(self):
        self.child_comp = self.pick_child()

    def is_endpoint(self):
        return False

    @abstractmethod
    def pick_child(self):
        return


class Flow(metaclass=abc.ABCMeta):
    def __init__(self):
        self._start_node = self._init_start_node()
        self._end_node = self._init_end_node()
        self._namespace = None

    def run(self, namespace):
        self.namespace = namespace
        self._before_run()
        self.start_node.run(self.namespace)
        return self._after_run()

    @property
    def start_node(self):
        return self._start_node

    @property
    def end_node(self):
        return self._end_node

    @property
    def namespace(self):
        return self._namespace

    @namespace.setter
    def namespace(self, namespace):
        assert isinstance(namespace, dict)
        self._namespace = namespace

    @abstractmethod
    def _init_start_node(self):
        return

    @abstractmethod
    def _init_end_node(self):
        return

    @abstractmethod
    def _before_run(self):
        pass

    @abstractmethod
    def _after_run(self):
        return


class VarGenRule(object):
    def __init__(self, name, rule):
        self.name = name
        self.rule = rule
