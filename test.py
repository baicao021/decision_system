from decision_engine.component import *
from decision_engine.flow import *
from decision_engine.engine import Engine

'''
flow = BasicFlow()
comp = VarGenComponent()
comp.add_var_rule(VarGenRule('some', 2))
comp.add_var_rule(VarGenRule('a', lambda ns: ns['a']+2))
flow.start_node.link(comp)
comp.link(flow.end_node)

flow.run(namespace={"a": 1})
print(flow.namespace)
'''

'''
flow = BasicFlow(input_vars=["age"])
cond = ConditionalComponent()
flow.start_node.link(cond)
comp_true = VarGenComponent()
comp_false = VarGenComponent()
comp_true.add_var_rule(VarGenRule('result', True))
comp_false.add_var_rule(VarGenRule('result', False))
cond.add_cond_link(lambda ns: ns["age"] > 24, comp_true)
cond.default_child = comp_false
comp_true.link(flow.end_node)
comp_false.link(flow.end_node)
flow.run(namespace={"age": 20})
print(flow.namespace)
'''

flow = BasicFlow(input_vars=["age"])
cond = BiConditionalComponent()
flow.start_node.link(cond)
comp_true = VarGenComponent()
comp_false = VarGenComponent()
comp_true.add_var_rule(VarGenRule('result', True))
comp_false.add_var_rule(VarGenRule('result', False))
cond.add_bi_rule_link(lambda ns: ns["age"] > 24, comp_true, comp_false)
cond.default_child = comp_false
comp_true.link(flow.end_node)
comp_false.link(flow.end_node)

sub_flow_comp = SubFlowComponent()
sub_flow_comp.flow = flow
sub_flow_comp.output_vars = ['result', 'age']
flow = BasicFlow(input_vars=["age"])
flow.start_node.link(sub_flow_comp)
sub_flow_comp.link(flow.end_node)

engine = Engine("test")
engine.main_flow = flow
engine.input_vars = ["age"]
engine.output_vars = ["result", "age"]

print(engine.run(namespace={"age": 20}))
print(engine.run(namespace={"age": 50}))



