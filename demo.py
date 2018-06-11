# 载入开发的模块
from decision_engine.engine import Engine
from decision_engine.flow import BasicFlow
from decision_engine.component import ConditionalComponent, VarGenComponent, BiConditionalComponent
from decision_engine.data_class import VarGenRule

# 初始化引擎，并给一个名字。等价于vincio新建一个project
engine = Engine(name="Pikachu wanna play outside!")

# engine预设入参检查，目前有简单的实现，确认变量是否存在
engine.input_vars = ['weather', 'time', 'mood']

# 引擎初始化会带一个默认flow，后续可以替换，不过一般没有必要。等价于鼠标选中了Main flow
flow = engine.main_flow

# flow 初始化之后会自动创建一个开始节点和结束节点。等价于选中了flow中的Start
cur_comp = flow.start_node

# flow的开始节点也有入参检查
cur_comp.input_vars = ['weather', 'time', 'mood']

# 创建一个条件分支组件
cond_comp = ConditionalComponent()

# 把开始节点和条件分支组件链接起来
cur_comp.link(cond_comp)

# 创建两个变量生成组件
var_true = VarGenComponent()
var_false = VarGenComponent()

# 给变量生成组件添加一点规则，（变量名称，值或者计算表达式）。这是一个固定值
var_true.add_var_rule(VarGenRule("result", True))

# 这是一个计算公式，动态计算，并创建或者覆盖一个变量
var_true.add_var_rule(VarGenRule("mood", lambda ns: ns["mood"] + 1))

var_false.add_var_rule(VarGenRule("result", True))
var_false.add_var_rule(VarGenRule("mood", lambda ns: ns["mood"] - 1))

# 把条件组件和一个变量生成组件链接在一起，入参为（规则表达式，组件）
cond_comp.add_cond_link(lambda ns: ns["weather"] in ["Sunny", "Thunderstorm"], var_true)

# 条件组件会遵循条件添加的顺序依次判断，一旦表达式为真则选择相应组件为下游
# 此外，Else的组件作为默认组件需要明确指定，如下一行所示
cond_comp.default_child = var_false

# 随便创建一个变量生成组件，用于归拢链接
cur_comp = VarGenComponent()
var_true.link(cur_comp)
var_false.link(cur_comp)

# 接下来创建另外一个规则, 变量名确定后续不再引用的情况下可以复用
# 下面这个组件是条件组件的变种，当条件分支只有两个分支时使用
cond_comp = BiConditionalComponent()

# 不要忘记链接
cur_comp.link(cond_comp)

# 可以使用这种方式快速创建变量生成组件，后续可以把常见的运算进行包装，进一步简化
var_true = VarGenComponent([
    VarGenRule('result', lambda ns: ns["result"] and True),
    VarGenRule('mood', lambda ns: ns["mood"] + 1),
])
var_false = VarGenComponent([
    VarGenRule('result', lambda ns: ns["result"] and False),
    VarGenRule('mood', lambda ns: ns["mood"] - 1),
])

# 看起来就像Excel 里的If函数
cond_comp.add_bi_rule_link(lambda ns: ns["time"] <= 18, var_true, var_false)

# 让我们结束flow
var_true.link(flow.end_node)
var_false.link(flow.end_node)

# 约束一下engine的返回值吧
engine.output_vars = ["result", "mood"]

# 好了，比卡丘要出去玩了
print(engine.run({"weather": "Sunny", "time": 10, "mood": 10}))
print(engine.run({"weather": "Sunny", "time": 19, "mood": 10}))
print(engine.run({"weather": "Rainy", "time": 20, "mood": 10}))
