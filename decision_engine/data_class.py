from decision_engine.meta_func import MetaFunc, auto_parser


class VarGenRule(object):
    def __init__(self, name, rule):
        self.name = name
        if isinstance(rule, MetaFunc):
            self.rule = rule  # type: MetaFunc
        else:
            self.rule = auto_parser(rule)




