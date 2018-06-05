from decision_engine.component import *
from decision_engine.meta import Flow


class BasicFlow(Flow):
    def __init__(self, input_vars=None, output_vars=None):
        self._input_vars = input_vars if input_vars is not None else []
        self._output_vars = output_vars if output_vars is not None else []
        super(BasicFlow, self).__init__()

    def _init_start_node(self) -> StartComponent:
        return StartComponent(self._input_vars)

    def _init_end_node(self):
        return OutComponent(self._output_vars)

    def _before_run(self):
        pass

    def _after_run(self):
        return self.end_node.namespace

