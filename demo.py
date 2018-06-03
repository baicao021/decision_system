from meta_rule import *
from engine import Engine
from meta_flow import BasicFlow, PolicyFlow
from meta_component import *

engine = Engine()

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
    JsonDecodeRule('age', '$.core_source.age', 'int')
)
policy.add_bi_rule(
    rule=lambda **k: k['age'] >= 24,
    true_var_gen_rules=[],
    false_var_gen_rules=[
       VarGenRule('rules_hit', lambda **k: k['rules_hit'] + [policy.rule_id])
    ]
)

main_flow = BasicFlow()
engine.register_main_flow(main_flow)
main_flow.head_component = SubFlowComponent(PolicyFlow(engine.policy_dict['R01']), ['rules_hit'])
result_summary_comp = VarGenComponent()
result_summary_comp.add_var('result', lambda **k: 'Approve' if len(k['rules_hit']) == 0 else 'Reject')
result_summary_comp.add_var('reject_reason', lambda **k: ','.join(k['rules_hit']))
main_flow.head_component.link(result_summary_comp)
output_comp = OutComponent()
result_summary_comp.link(output_comp)

engine.run(['preCheck'], apply_json='{"core_source":{"age":"15"}}', output_var_list=['result', 'reject_reason'])
