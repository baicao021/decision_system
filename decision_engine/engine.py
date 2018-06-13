from decision_engine.flow import Flow, BasicFlow
from typing import Mapping
import json


class Engine(object):
    def __init__(self, name, main_flow=None):
        self.policy_dict = {}
        self.score_rule_dict = {}
        self._main_flow = None  # Type Flow
        self._output_vars = []  # Type list
        self._input_vars = []  # Type list
        if main_flow is not None:
            self.main_flow = main_flow
        else:
            self.main_flow = BasicFlow()
        self._name = name
        self._namespace = None

    @property
    def name(self):
        return self._name

    @property
    def main_flow(self) -> Flow:
        return self._main_flow

    @main_flow.setter
    def main_flow(self, main_flow):
        assert isinstance(main_flow, Flow)
        self._main_flow = main_flow

    @property
    def output_vars(self):
        return self._output_vars

    @output_vars.setter
    def output_vars(self, output_vars):
        self._output_vars = output_vars

    @property
    def input_vars(self):
        return self._output_vars

    @input_vars.setter
    def input_vars(self, input_vars: Mapping[str, type]):
        self._input_vars = input_vars

    def var_exist_check(self):
        for var in self.input_vars:
            if var not in self._namespace:
                raise AttributeError

    def result_parser(self, result: dict):
        out_dict = {k: v for k, v in result.items() if k in self.output_vars}
        return json.dumps(out_dict)

    def run(self, namespace: dict) -> str:
        self._namespace = namespace
        self.main_flow.run(self._namespace)
        result = self.main_flow.namespace
        return self.result_parser(result)
