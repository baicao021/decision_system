from decision_engine.flow import Flow
from decision_engine.meta_rule import Policy, ScoreRule
import json


class Engine(object):
    def __init__(self):
        self.policy_dict = {}
        self.score_rule_dict = {}
        self.main_flow = None

    def register_policy(self, policy):
        assert isinstance(policy, Policy)
        assert policy.rule_id not in self.policy_dict, 'duplicate policy register: ' + policy.rule_id
        self.policy_dict[policy.rule_id] = policy

    def register_score_rule(self, score_rule):
        assert isinstance(score_rule, ScoreRule)
        assert score_rule.rule_id not in self.score_rule_dict, 'duplicate score_rule register: ' + score_rule.rule_id
        self.score_rule_dict['score_rule.rule_id'] = score_rule

    def register_main_flow(self, flow):
        assert isinstance(flow, Flow)
        assert self.main_flow is None
        self.main_flow = flow

    def run(self, stage, apply_json, output_var_list):
        flow_result = self.main_flow.run(stage_list=stage, apply_dict=json.loads(apply_json))
        result = {k: v for k, v in flow_result.items() if k in output_var_list}
        return json.dumps(result)

