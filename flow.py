from component import *
from meta import Flow


class BasicFlow(Flow):
    def __init__(self):
        super(BasicFlow, self).__init__()


class ConditionalFlow(Flow):
    def __init__(self, json_decode_rules, var_gen_rules, cond_rules, default_rule):
        super(ConditionalFlow, self).__init__()
        self.var_predefine_comp = VarGenComponent()
        for json_decode_rule in json_decode_rules:
            self.var_predefine_comp.add_var(json_decode_rule.name, lambda **k: json_decode_rule.decode(k['apply_dict']))

        for var_gen_rule in var_gen_rules:
            self.var_predefine_comp.add_var(var_gen_rule.name, var_gen_rule.rule)

        self.rule_comp = ConditionalComponent()
        self.var_predefine_comp.link(self.rule_comp)
        self.out_comp = OutComponent()

        for cond_rule in cond_rules:
            self.add_rule(cond_rule.rule, cond_rule.var_comp)

        self.add_default_child(default_rule.var_comp)
        self.set_start_comp(self.var_predefine_comp)

    def add_rule(self, rule, child_var):
        self.rule_comp.add_cond_link(rule, child_var)
        child_var.link(self.out_comp)

    def add_default_child(self, child_var):
        self.rule_comp.default_child = child_var
        child_var.link(self.out_comp)


class PolicyFlow(Flow):
    def __init__(self, policy):
        super(PolicyFlow, self).__init__()
        self.out_comp = OutComponent()
        self.router_checker = BiConditionalComponent()
        cond_flow = ConditionalFlow(policy.json_decode_rule_list, policy.derive_var_gen_rule_list, policy.rule_list,
                                    policy.default_rule)
        self.cond_flow_comp = SubFlowComponent(cond_flow, policy.output_vars_list)
        self.router_checker.bi_rule_link(lambda **k: router_check(stage=policy.stage,
                                                                  rule_id=policy.rule_id,
                                                                  shunt_tuple=policy.shunt_tuple, **k),
                                         self.cond_flow_comp, self.out_comp)
        self.out_comp = OutComponent()
        self.cond_flow_comp.link(self.out_comp)
        self.set_start_comp(self.router_checker)


class ScoreFlow(Flow):
    def __init__(self, score_rule):
        super(ScoreFlow, self).__init__()
        conditional_flow = ConditionalFlow(score_rule.json_decode_rule_list, score_rule.derive_var_gen_rule_list)
        self.conditional_flow_comp = SubFlowComponent(conditional_flow, score_rule.output_vars_list)
        self.out_comp = OutComponent()
        self.conditional_flow_comp.link(self.out_comp)
        self.set_start_comp(self.conditional_flow_comp)


def router_check(stage, rule_id, shunt_tuple, **kwargs):
    if stage not in kwargs['stage_list']:
        return False
    if 'rule_list' in kwargs and rule_id not in kwargs['rule_list']:
        return False
    elif shunt_tuple is not None:
        for valid_list, shunt_id in zip(shunt_tuple, kwargs['shunt_tuple']):
            if shunt_id not in valid_list:
                return False
    return True

