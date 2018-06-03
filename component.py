from meta import Component, Flow


class ConditionalComponent(Component):
    def __init__(self):
        super(ConditionalComponent, self).__init__()
        self.link_list = []
        self.out_links = 0
        self.default_child = None

    def add_cond_link(self, rule, child_comp):
        self.link_list.append((rule, child_comp))
        self.out_links += 1

    def default_child(self, child_comp):
        self.default_child = child_comp

    def run(self, **kwargs):
        for rule, child_comp in self.link_list:
            if rule(**kwargs):
                return child_comp.run(**kwargs)
        return self.default_child.run(**kwargs)


class BiConditionalComponent(ConditionalComponent):
    def __init__(self):
        super(BiConditionalComponent, self).__init__()

    def bi_rule_link(self, rule, true_comp, false_true_comp):
        self.link_list.append((rule, true_comp))
        self.link_list.append((lambda k: True, false_true_comp))
        self.out_links += 2


class VarGenComponent(Component):
    def __init__(self, **kwargs):
        super(VarGenComponent, self).__init__()
        self.args = kwargs
        self.child_comp = None
        self.var_func_list = []

    def add_var(self, var_name, var_func):
        if type(var_func).__name__ == 'function':
            self.var_func_list.append((var_name, var_func))
        else:
            self.var_func_list.append((var_name, lambda **k: var_func))

    def run(self, **kwargs):
        for var_name, var_func in self.var_func_list:
            kwargs[var_name] = var_func(**kwargs)
        return self.child_comp.run(**kwargs)


class OutComponent(Component):
    def __init__(self):
        super(OutComponent, self).__init__()

    def run(self, **kwargs):
        return kwargs


class SubFlowComponent(Component):
    def __init__(self, flow, output_vars):
        super(SubFlowComponent, self).__init__()
        if isinstance(flow, Flow):
            self.flow = flow
        else:
            raise Exception
        self.output_vars = output_vars

    def run(self, **kwargs):
        args_cp = {k: v for k, v in kwargs.items()}
        result_space = self.flow.run(**args_cp)
        for var in self.output_vars:
            kwargs[var] = result_space[var]
        return self.child_comp.run(**kwargs)