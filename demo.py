from meta_rule import *
from engine import Engine
from flow import BasicFlow, PolicyFlow
from component import *

# 1. init engine
engine = Engine()

# 2. config and register policies
policy = Policy(
    stage='preCheck',
    rule_id='R01',
    policy_id='ABC00001',
    reject_reason='年龄',
    public_reject_reason='准入不足',
    output_vars_list=['rules_hit'],
    engine=engine
)
policy.add_json_decode_rule(
    JsonDecodeRule('age', '$.core_source.age', 'float')
)
policy.add_bi_cond_rule(
    rule=lambda **k: k['age'] >= 24,
    true_var_gen_rules=[],
    false_var_gen_rules=[
       VarGenRule('rules_hit', lambda **k: k['rules_hit'] + [policy.rule_id])
    ]
)

# 3. init main flow
main_flow = BasicFlow()

# 4. register main flow
engine.register_main_flow(main_flow)

# 5. config var gen component
cur_comp = VarGenComponent()
main_flow.head_component = cur_comp
cur_comp.add_var_rule(VarGenRule('rules_hit', []))

# 6. link policy
cur_comp.link(SubFlowComponent(PolicyFlow(engine.policy_dict['R01']), ['rules_hit']))
cur_comp = cur_comp.child_comp

# 7. result summary
cur_comp.link(VarGenComponent())
cur_comp = cur_comp.child_comp
cur_comp.add_var('result', lambda **k: 'Approve' if len(k['rules_hit']) == 0 else 'Reject')
cur_comp.add_var('reject_reason', lambda **k: ','.join(k['rules_hit']))

# 8. flow end
cur_comp.link(OutComponent())

# 9. engine call
result = engine.run(['preCheck'], apply_json='{"core_source":{"age":"2"}}', output_var_list=['result', 'reject_reason'])
print(result)
