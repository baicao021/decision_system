class JsonDecodeRule(object):
    def __init__(self, name, rule, data_type, default_val=None):
        self.name = name
        self.rule = rule
        self.data_type = data_type
        self.default_val = default_val

    def decode(self, apply_dict):
        val = apply_dict
        for key in self.rule.split('.')[1:]:
            val = val.get(key)

        if val is not None:
            if self.data_type == 'int':
                return int(val)
            elif self.data_type == 'float':
                return float(val)
            else:
                return val
        else:
            return self.default_val


class ConditionalRule(object):
    def __init__(self, rule, var_gen_rules):
        self.rule = rule
        self.var_gen_rules = var_gen_rules
        self.var_comp = var_gen_rules_to_var_gen_comp(var_gen_rules)


class DefaultRule(object):
    def __init__(self, var_gen_rules):
        self.var_gen_rules = var_gen_rules
        self.var_comp = var_gen_rules_to_var_gen_comp(var_gen_rules)


class Rule(object):
    def __init__(self):
        self.rule_list = []
        self.json_decode_rule_list = []
        self.derive_var_gen_rule_list = []
        self.default_rule = None
        self.output_vars_list = []

    def add_rule(self, rule, var_dict):
        self.rule_list.append((rule, var_dict))

    def add_default_rule(self, var_dict):
        self.default_rule = var_dict

    def add_bi_cond_rule(self, rule, true_var_gen_rules, false_var_gen_rules):
        self.rule_list.append(ConditionalRule(rule, true_var_gen_rules))
        self.default_rule = DefaultRule(false_var_gen_rules)

    def add_json_decode_rule(self, json_decode_rule):
        self.json_decode_rule_list.append(json_decode_rule)

    def add_derive_var_gen_rule(self, var_gen_rule):
        self.derive_var_gen_rule_list.append(var_gen_rule)


class Policy(Rule):
    def __init__(self, rule_id, stage, policy_id, reject_reason, public_reject_reason, engine, output_vars_list,
                 shunt_tuple=None):
        super(Policy, self).__init__()
        self.rule_id = rule_id
        self.stage = stage
        self.policy_id = policy_id
        self.reject_reason = reject_reason
        self.public_reject_reason = public_reject_reason
        self.output_vars_list = output_vars_list
        self.shunt_tuple = shunt_tuple
        engine.register_policy(self)


class ScoreRule(Rule):
    def __init__(self, rule_id, engine, output_vars_list):
        super(ScoreRule, self).__init__()
        self.rule_id = rule_id
        self.stage = 'scoreCard'
        self.output_vars_list = output_vars_list
        engine.register_score_rule(self)



