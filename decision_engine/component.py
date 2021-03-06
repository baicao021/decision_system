from decision_engine.meta import *
from decision_engine.data_class import VarGenRule
from decision_engine.basic_data_class import Val


class StartComponent(ZeroToOneComponent):
    def __init__(self, input_vars=None):
        super(StartComponent, self).__init__()
        self._input_vars = input_vars

    @property
    def input_vars(self):
        return self._input_vars

    @input_vars.setter
    def input_vars(self, input_vars):
        assert self.input_vars is not None
        self._input_vars = input_vars

    def var_exist_check(self):
        for var in self.input_vars:
            if var not in self.namespace:
                raise AttributeError

    def inner_run(self):
        self.var_exist_check()


class OutComponent(AnyToZeroComponent):
    def __init__(self, output_vars=None):
        super(OutComponent, self).__init__()
        self._output_vars = output_vars

    @property
    def output_vars(self):
        return self._output_vars

    @output_vars.setter
    def output_vars(self, output_vars):
        assert self.output_vars is None
        self._output_vars = output_vars

    def inner_run(self):
        if self.output_vars is not None:
            self.namespace = {k: self.namespace[k] for k in self.output_vars}


class ConditionalComponent(AnyToMultipleComponent):
    def __init__(self):
        super(ConditionalComponent, self).__init__()
        self.link_list = []
        self._default_child = None

    def add_cond_link(self, rule, child_comp):
        self.link_list.append((rule, child_comp))

    @property
    def default_child(self):
        return self._default_child

    @default_child.setter
    def default_child(self, child_comp):
        self._default_child = child_comp

    def pick_child(self):
        for cond_rule, child in self.link_list:
            if cond_rule(self.namespace):
                return child
        return self.default_child


class BiConditionalComponent(ConditionalComponent):
    def add_bi_rule_link(self, cond_rule, true_comp, false_true_comp):
        self.add_cond_link(cond_rule, true_comp)
        self.default_child = false_true_comp


class VarGenComponent(AnyToOneComponent):
    def __init__(self, var_gen_rules=None):
        super(VarGenComponent, self).__init__()
        self.child_comp = None
        self.var_gen_rules = var_gen_rules if var_gen_rules is not None else []

    def inner_run(self):
        for var_gen_rule in self.var_gen_rules:
            self.namespace[var_gen_rule.name] = var_gen_rule.rule(self.namespace)

    def add_var_rule(self, var_gen_rule: VarGenRule):
        assert isinstance(var_gen_rule, VarGenRule)
        self.var_gen_rules.append(var_gen_rule)


class SubFlowComponent(AnyToOneComponent):
    def __init__(self, flow=None, output_vars=None):
        super(SubFlowComponent, self).__init__()
        self._flow = None  # Type Flow
        if flow is not None:
            if isinstance(flow, Flow):
                self._flow = flow
            else:
                raise Exception
        self._output_vars = output_vars if output_vars is not None else []

    @property
    def flow(self):
        return self._flow

    @flow.setter
    def flow(self, flow):
        assert isinstance(flow, Flow)
        self._flow = flow

    @property
    def output_vars(self):
        return self._output_vars

    @output_vars.setter
    def output_vars(self, output_vars):
        self._output_vars = output_vars

    def inner_run(self):
        ns_cp = {k: v for k, v in self.namespace.items()}
        self.flow.run(ns_cp)
        for var in self.output_vars:
            self.namespace[var] = self.flow.namespace[var]

