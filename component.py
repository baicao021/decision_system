from meta import *
from meta_rule import VarGenRule


class StartComponent(ZeroToOneComponent):
    def __init__(self, input_vars=None):
        super(StartComponent, self).__init__()
        self._input_vars = input_vars

    @property
    def input_vars(self):
        return self._input_vars

    @input_vars.setter
    def input_vars(self, input_vars):
        assert self.input_vars is None
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
        for rule, child in self.link_list:
            if rule(self.namespace):
                return child
        return self.default_child


class BiConditionalComponent(ConditionalComponent):
    def add_bi_rule_link(self, rule, true_comp, false_true_comp):
        self.add_cond_link(rule, true_comp)
        self.default_child = false_true_comp


class VarGenComponent(AnyToOneComponent):
    def __init__(self, var_gen_rules=list()):
        super(VarGenComponent, self).__init__()
        self.child_comp = None
        self.var_gen_rules = var_gen_rules

    def inner_run(self):
        for var_gen_rule in self.var_gen_rules:
            if type(var_gen_rule.rule).__name__ == 'function':
                self.namespace[var_gen_rule.name] = var_gen_rule.rule(self.namespace)
            else:
                self.namespace[var_gen_rule.name] = var_gen_rule.rule

    def add_var_rule(self, var_gen_rule):
        assert isinstance(var_gen_rule, VarGenRule)
        self.var_gen_rules.append(var_gen_rule)


class SubFlowComponent(AnyToOneComponent):
    def __init__(self, flow=None, output_vars=None):
        super(SubFlowComponent, self).__init__()
        if isinstance(flow, Flow):
            self.flow = flow
        else:
            raise Exception
        self.output_vars = output_vars

    def set_flow(self, flow):
        assert isinstance(flow, Flow)
        self.flow = flow

    def set_output_vars(self, output_vars):
        self.output_vars = output_vars

    def inner_run(self, **kwargs):
        ns_cp = {k: v for k, v in self.namespace.items()}
        result = self.flow.run(ns_cp)
        for var in self.output_vars:
            self.namespace[var] = result[var]
