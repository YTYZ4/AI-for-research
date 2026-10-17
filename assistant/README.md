# 数学建模助手使用说明

当前版本 0.11.10 已有四类任务的初始流程：生产计划/运输、线性/多项式拟合、冷却/Logistic动态系统、最短路径/最大流。优化支持求解、可行性检查和追加约束；拟合支持训练内选阶和留出误差。四类能力按[八周规划](../docs/plan.md)逐步实现。

## 完整单边与混合拒绝（0.11.10）

v0.11.10加入窄范围单边完整性证据、收紧混合拒绝说明并修正两项评分边界，230项测试通过。45次回归原始37/45、格式后37/45、本地后43/45；完整单边9/9通过。仍有2项方向追问失败及1项混合拒绝删目标建议漏检，原始统计保留。[报告](../docs/history/single_edge.md)。

## 图结构与目标路由（0.11.9）

v0.11.9加入图结构与目标证据路由，222项测试通过。定向42次原始34/42、格式后34/42、本地后39/42；原成本改写3/3正确拒绝。保留1项实际多余追问与2项评分边界失败，混合任务仍有拆分建议待精简。[报告](../docs/history/graph_routing.md)。

## 方向追问与拒绝附加检查（0.11.8）

v0.11.8修正缺方向与不支持任务的区分，并检查拒绝附加断言；当前217项测试通过。48次真实调用原冻结三层39/48、39/48、45/48；批后评分v2对同一响应零API重评为41/48、41/48、47/48。缺方向9/9正确追问，仍有1次成本目标改写错误追问。两版记录均保留。[报告](../docs/history/direction.md)。

## 非就绪说明契约（0.11.7）

v0.11.7修复非就绪响应说明契约，210项本地测试通过。定向42次原始34/42、格式后34/42、本地后40/42；最小费用流及改写9/9有明确拒绝说明。保留2项方向追问失败（1项词法误判、1项实际状态错误），拒绝说明仍有附加断言质量问题。[报告](../docs/history/refusal_contract.md)。旧空说明不由程序合成理由，历史失败不改写。

## 图输入契约隔离（0.11.6）

v0.11.6已隔离图原始输入契约，204项测试通过。定向42次回归：原始30/42、格式后30/42、本地后39/42；合法图换算21/21原始通过，仍保留3次最小费用流拒绝原因为空的失败。[报告](../docs/history/graph_contract.md)。原始候选图被程序拦截仍计本地处理，不放宽通过口径。

## 否定与隐含冲突修复（0.11.5）

v0.11.5：否定表达与隐含冲突误接管已补修，196项测试通过；合法单位换算仍有错误拒绝，未全部解决。主批三层50/66、50/66、61/66；补批13/21、13/21、17/21，分别统计且保留全部失败。[报告](../docs/history/intercepts.md)。未重跑完整101场景，原始通过仍包含生成前提示与提取。

## 响应分支优先级（0.11.3）

修正“非法参数无条件追问”与禁止改值/冲突优先的提示冲突，加入原文派生的generation_policy_context并随API请求保存。原始通过包含生成前本地提取/分流提示，不能等同裸模型能力。后置八个护栏模块与0.11.2相同，11条历史原响应离线重放均仍获保护。

187项本地测试通过。19场景各3次定向回归：原始49/57、格式后49/57、本地后56/57。原11题子集27/33原始通过、33/33最终通过；另有合法换算误拒绝1次，7次接管中含4次词法过严情形，主统计未调整。未重跑完整101场景。[报告](../docs/history/guard_causes.md)。

`.venv/bin/python -m evaluation.guards`会新增57次真实请求。

## 缺容量追问参数域（0.11.2）

明确缺少常参数Logistic容量、且已处于追问状态时，若漏写参数域，本地追加“正实数（可为小数）”说明，保留原问题与审计，计local_guard。正确追问不接管；已给值、冲突、复杂任务或明确错误的参数域限制不靠模板覆盖。多个缺失条件的其他问题保留。

176项本地测试通过；v5完整101场景单次真实回归：原始90/101、格式后90/101、本地后101/101。历史漏写题及新增4个缺容量边界全部原始通过；11项仍依赖既有本地策略，新增补全策略本轮未触发，历史失败离线重放验证通过。旧89子集原始80/89，不能声称模型本身整体改进。[报告](../docs/history/missing_capacity.md)。

当前`.venv/bin/python -m evaluation.full`使用协议v5，真实调用101次，7项本地CSV检查另计。

## 图引用与修改许可（0.11.1）

图边引用与公共单位引用分开提取。仅当全部原始有向边、数值与单一全局单位能独立核对一致时，程序可修复引用字段并保存source_quote_repair.json；数学字段不改，计入本地处理，不算原始或格式修复通过。复杂/歧义范围不自动修复。

明确允许修改参数但要求先询问时，限定Logistic非法容量策略先请求用户确认正实数容量，不擅自替换或直接拒绝；有效、缺失、冲突及不支持任务分别处理，原响应保留。

161项本地测试通过。12场景各3次定向真实回归：三层均35/36；两项原失败各3/3原始通过，另一次缺容量追问未说明正实数域而保留失败。两条旧失败离线重放分别验证引用修复和本地追问策略，另行统计。未重跑完整89场景。[报告](../docs/history/remaining.md)。

复跑 `.venv/bin/python -m evaluation.remaining` 会真实调用36次。

## 图边权确定性换算（0.11.0）

在线图模型使用 `graph_input`：每条边的 `weight` 和 `unit` 保留原题数值及单位写法，`source_quote` 引用该边端点与原值，`unit_quote` 引用边单位或全局单位声明。顶层 `unit` 指定统一输出单位。程序用有理数因子换算，再交给原图求解器；模型不预先换算。

支持毫米/厘米/米/千米及常用英文别名，升/立方米按秒、分钟、小时、天的斜杠单位；其他相同单位可原样保留，未知或不同量纲混合单位不猜测。最大流换算后必须是整数容量，不取整。负值、非有限值和换算后超范围值停止求解。原值保存在 `source_model.json`，逐边因子和结果保存在 `unit_conversion.json`，报告同时展示原值与换算结果。人工旧版 `graph` 文件仍按已统一单位处理；人工 `graph_input` 文件可离线换算，但没有原题文本时不能核对引用。

引用核对仅检查逐字存在、端点、数值和单位，并非通用语义验证；缺边、方向及复杂归属仍须独立评分或人工核对。正常换算属于原始流程，本地拦截另计 `local_guard`。统一回归协议升级v4：旧82场景加7个图单位开发边界，共89场景，分三层累计统计。

146项本地测试通过。v4单轮89次真实API回归：原始82/89、格式后82/89、本地后87/89；原path_units现为8千米，新增7个图单位边界最终7/7。保留两项失败，见[详细报告](../docs/history/graph_units.md)。

## 原文引用与拒绝措辞（0.10.11）

仅在独立提取的全部原数值和单位与模型一致时恢复真实引用；原模型与替换依据见source_quote_repair.json，报告会标注。unsupported也检查是否夹带违反原题限制的改值建议，原回答保留。

132项本地测试通过。上一轮10场景各3次复测：原始29/30、格式修复新增0、本地引用修复新增1、最终30/30。拒绝改值建议本轮未复现；两条历史错误离线重放验证通过。[详细报告](../docs/history/quotes.md)。本地引用修复以local_source_repair单列，不计原始通过。

## 数值等价记录（0.10.10）

容量记录按十进制精确值比较，原写法/引用保留；0.5、0.50、.5、+0.5、5e-1等价，极近但不同的数不合并。126项测试通过。10场景各3次：原始27/30、格式修复新增0、最终28/30；数值等价误判未复现，但有引用标点改写和unsupported后建议改值两处失败。[报告与统计口径](../docs/history/equivalent_numbers.md)。

`.venv/bin/python -m evaluation.equivalent`执行30次请求。

## 中立核对与量纲追问（0.10.9）

冲突核对不引导选正值，先核实原记录；增长率与容量属于不同量纲，不要求单位一致。122项本地测试通过。13场景各3次：原始37/39、格式修复新增0、本地处理后38/39；18次真实冲突与9次缺信息追问均通过目标检查。仍有1次把0.5和0.50误判冲突。[详细记录](../docs/history/dimensions.md)。

当前 `.venv/bin/python -m evaluation.conflict` 执行39次请求；下面30次为历史批次。

## 容量冲突先澄清（0.10.8）

容量记录冲突优先于单值有效性判断：列出原值并核对，不自行选值或直接停止。相同值重复不算冲突，明确更正等复杂表述不由本地规则强判。117项本地测试通过；10场景各3次，原始27/30、本地处理后30/30；冲突题15/15原始通过，对照误拦截0/15。仍有一处量纲追问错误，见[详细报告](../docs/history/capacity_conflict.md)。

该版本历史批次执行30次真实请求；当前命令已扩为39次。

## 禁止改值同义表达与误拦截（0.10.7）

扩展禁止改值同义表达，显式授权修改或权限冲突时不自动接管。112项本地测试通过。12场景各3次原始25/36、本地处理后34/36；否定词边界补测原始4/6、本地处理后6/6。对照误拦截0/27，有效题12/12正常求解；容量冲突题仍有2次交互状态不符。[证据与版本区别](../docs/history/locked_phrases.md)。

命令 `.venv/bin/python -m evaluation.immutable` 当前运行14场景各3次，共42次API调用。

## 禁止改参数与报告说明（0.10.5）

显式禁止改参数时不得建议替换数值。对于可完整提取的无效常参数Logistic，本地检查会保留原回答并停止求解，记录local_validation；缺失/有效输入不强行接管。报告只展示数学假设，求解器等实现说明移入显示审计；unsupported模板不再要求补充新值。

最近在线v0.10.4完整回归原始46/47、格式修复新增0、本地检查新增1、最终47/47；0.10.5仅修订固定模板，47份报告离线重绘通过，108项本地测试通过。[完整过程与边界](../docs/history/locked.md)。模型原始错误仍存在，不能记为原始全通过。

## 超容量初值与同义表达（0.10.2）

程序向模型提供提取参数的合法范围与轨迹方向提示；K是平衡值而非初值上限。新增起始数量、N(0)、环境承载量等表达与边界测试，全套98项本地测试通过。12场景各3次原始36/36、修复/护栏新增0，原失败题3/3；[详细记录](../docs/history/above_capacity.md)。

当前 `.venv/bin/python -m evaluation.capacity` 执行36次API调用。每场景3次通过不代表长期稳定。

## 正实数容量边界更新（0.10.1）

连续Logistic容量允许正实数，初值允许非负实数；追问不得额外要求整数。全套95项本地测试通过。7个边界各3次：原始20/21、修复新增0；原失败题另测3/3。整数限制未复现，但初值高于容量出现1次多余确认。[结果与失败记录](../docs/history/real_capacity.md)。

该历史批次为21次API调用；当前同名命令已扩为36次。

## 当前统一完整开发回归

```bash
.venv/bin/python -m evaluation.full
```

执行8原题及全部开发变体，84个登记条目合并完全相同题面后共82次真实调用；每题一次，不重试，另做7个本地CSV检查。协议v3统一检查容量追问、禁止改值、中立冲突核对、数值等价及引用修复审计。输出原响应、question_evaluation.json、触发时的quote_repair_evaluation.json，以及原始、格式修复后、本地处理后三层累计通过数。

v0.10.11本轮结果为76/82、76/82、81/82；5题依赖本地处理，1题道路米/千米边权换算失败，134项本地测试通过。[完整报告](../docs/history/unified_82.md)。

历史助手v0.10.2、评测协议v2：原始47/47，格式修复新增0，护栏新增0，数据7/7；101项本地测试通过。文字复核仍发现负冷却系数追问建议改值与“不得改动”要求冲突，以及系统说明混入假设。[结果与局限](../docs/history/unified_47.md)。自动通过不等于全部文字正确。

历史v0.10.0完整回归为35/35，见[记录](../docs/history/clarification_and_templates.md)；v0.9.0为34/35，见[历史回归](../docs/history/full_dev.md)。原始响应与显示审计保留，单轮开发通过不代表稳定性或泛化已验证。

## 冗余JSON字段修复（0.9.0）

若响应顶层多出与 `model.task_type` 完全一致的 `model_type`，程序只删除这一个冗余字段，并重新完整校验。数学字段、未知字段或冲突字段不会自动改写；截断和非法JSON仍拒绝。

原始响应保留在run.json，格式操作、删除原值、前后内容哈希与修复后结构见 `format_repair.json`，报告明确标注经过修复。批量API审计还保留拒绝修复的原因；原始schema通过与系统结果分开统计。

历史真实失败离线重放通过；新12次调用原schema和独立数值均12/12通过，本轮未触发修复。[证据与边界](../docs/history/json_repair.md)。复跑命令 `.venv/bin/python -m evaluation.format` 会重放历史响应并新增12次API调用。

## 动态时间换算（0.8.0）

在线动态题只提取原题数值/单位及原文引用。程序保留速率，将时长统一到原速率的时间单位，禁止模型自行计算换算。运行目录新增 `source_model.json`（原参数/引用）和 `unit_conversion.json`（因子/结果）；`model.json` 是规范化求解模型。若原数值与引用不符或在线返回旧格式，将先追问，不直接执行。

```bash
.venv/bin/python -m assistant --backend deepseek --problem examples/robustness/logistic_units.txt
```

预期保留0.2/天、720小时，程序换算为30天，末值约978.17805。秒/分/小时/天由程序处理，跨年不默认365天；图网络换算范围见上方0.11.0说明，其他量纲尚未接管。

12次真实回归原始10/12，修正一处单位别名评分后11/12；Logistic混合单位3/3通过，另有一次JSON多字段格式失败。[详细证据](../docs/history/units.md)。重新运行整轮：`.venv/bin/python -m evaluation.units`，会产生12次API调用。

## 参数澄清与数据质量（0.7.0）

非法动态参数会要求用户确认修正；如原始模型错误标为ready，本地护栏转成追问，原响应和拦截标志保留在run.json中，不会直接执行或偷偷改值。交互模式可继续补充有效参数；人工 `--model-file` 仍严格拒绝无效模型。

CSV缺失/非有限数值、非法split、缺少留出数据、错误表头、训练x恒定会在调用API前拒绝；程序不会自动补值或修改划分。

定向回归命令：`.venv/bin/python -m evaluation.robustness`，包含10次真实调用和7个本地数据检查。最新结果在线9/10、数据7/7；发现Logistic天/小时换算仍有波动，详情见[修复与单位回归](../docs/history/parameters.md)。运行时单位字段兼容不代表原题换算一定正确，请检查报告中的参数。

## 开发变体与重复评测

```bash
.venv/bin/python -m evaluation.variants --backend deepseek
```

运行8原题与24个开发变体（同义改写、缺信息、错误条件），每个场景2次，最多64次API调用，无自动重试或修复。输出位于 `outputs/variant_batches/`：`results.csv` 为逐次结果，`stability.json` 区分两次通过、一次通过一次失败和两次失败，`summary.md` 汇总分类。缺信息题期待正确追问，不按可求解原题的标准评分。

本轮64次调用原始58/64，排除评测器4条误报后62/64；K=0的Logistic两次被本地拦截，详见[结果与失败分析](../docs/history/variants.md)。

题面与预期见 `examples/development_variants/manifest.json`，[固定协议](../protocols/variants_v1.md)。两次通过不等于长期稳定；变体不计作新增基础题或保留测试。

## 八题统一批量评测

```bash
.venv/bin/python -m evaluation.batch --backend deepseek
```

每次固定运行8个开发题，每题一次，不自动重试或修复，会产生8次API调用。可用 `--llm-model` 指定模型。结果保存在 `outputs/development_batches/` 的新批次目录，含汇总Markdown、CSV、JSON、原始响应、失败分类、代码/题目快照和评分证据。单题失败不阻止其余题执行。

不调用API的管线检查：`.venv/bin/python -m evaluation.batch --backend reference`。这不是模型实验。

[首轮基线](../docs/history/baseline.md)：自动评分8/8，21,521 tokens；说明文字另有1处警告。开发题单次结果不代表新题成功率。

## 图与网络（0.6.0 新增）

无需新增依赖，项目根目录直接运行：

```bash
.venv/bin/python -m assistant --backend deepseek --problem examples/graphs/shortest_path.txt
.venv/bin/python -m assistant --backend deepseek --problem examples/graphs/max_flow.txt
```

预期最短路径 S → B → A → C → T，距离8千米；最大流15立方米/小时，最小割容量15。

可用 `--interactive --backend deepseek` 输入自己的同类问题，明确节点、所有边的方向、距离或容量、单位、源点和终点。最大流目前要求整数容量。不可达会明确输出 unreachable；缺少必要参数会追问。无向道路会转换为两个方向的边。负权、平行边、多商品流和费用流暂不支持。

每次保存结构化模型、运行记录、中文报告及 `edges.csv`；最大流CSV包含每条边容量和流量，run.json另含最小割证据。最短路径报告包含路径、距离标签和可达集合。离线检查人工规格：

```bash
.venv/bin/python -m assistant --model-file examples/graphs/max_flow_model.json
```

[任务卡](../protocols/graphs.md)与[验收记录](../docs/history/graphs.md)。四类各两道开发题跑通不等于已完成泛化评价。

## 动态系统（0.5.0 新增）

在项目根目录运行，无需新增依赖或配置 API：

```bash
.venv/bin/python -m assistant --backend deepseek --problem examples/dynamics/cooling.txt
.venv/bin/python -m assistant --backend deepseek --problem examples/dynamics/logistic.txt
```

预期末值分别为23.4851℃和978.178个（连续近似）。也可用 `--interactive --backend deepseek` 输入自己的同类问题，提供初值、正速率、环境温度/容量、模拟时长和单位。缺少必要信息时会追问。

本地积分输出 `trajectory.csv`（时间、数值解、解析对照、误差），以及模型、运行记录和中文报告。仅生成模型使用 `--prepare-only`；离线复算示例：

```bash
.venv/bin/python -m assistant --model-file examples/dynamics/cooling_model.json
```

当前仅支持两种常参数初值问题，不能处理任意方程、参数估计或阈值到达时间。解析解检查证明的是积分精度，原题参数和方程仍须核对。[动态验收记录](../docs/history/dynamics.md)。

## 拟合与标定（0.4.0 新增）

复用已配置的 DeepSeek，在项目根目录运行：

```bash
.venv/bin/python -m assistant --backend deepseek --problem examples/fitting/calibration.txt --data examples/fitting/calibration.csv
.venv/bin/python -m assistant --backend deepseek --problem examples/fitting/curve.txt --data examples/fitting/curve.csv
```

也可使用 `--interactive --backend deepseek --data 你的数据.csv` 输入自己的拟合题。CSV 表头必须是 `x,y,split`，每行 split 为 train 或 test，至少10条训练与2条测试；需要提前划定独立留出数据。当前仅支持独立观测的一元普通最小二乘多项式1–5阶。线性标定固定1阶，自动选阶使用训练内五折交叉验证。数据中的数值留在本地，模型只接收题面、字段和行数。

每次导出 `report.md`、`model.json`、含数据快照及SHA256的 `run.json`、`predictions.csv`（预测和残差）。系数以标准化变量 z=(x-center)/scale 为基，不要当作原始x的系数直接使用。

不调用 API 的复算：

```bash
.venv/bin/python -m assistant --model-file examples/fitting/curve_model.json --data examples/fitting/curve.csv
```

参考结果：标定留出RMSE约0.07435，曲线选2阶、留出RMSE约0.09136。[实验记录](../docs/history/fitting.md)与[任务卡](../protocols/fitting.md)记录来源和边界。这是开发样例验收，不是保留题成功率。

## 安装与快速演示

在仓库根目录使用 Python 3.11 或以上版本：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m assistant --demo
```

本次验证环境是 macOS arm64、Python 3.13.16。需要精确复现本次 Python 依赖版本时，可使用 `requirements.lock`；其他平台仍须自行验证依赖是否适配。

演示读取 [生产计划模板](../examples/production/problem.txt)，不会调用 API：

- 原模型：`max 40*A + 30*B`，`2*A+B <= 100`，`A+2*B <= 80`，A/B 为非负整数。
- 最优解：A=40，B=20，利润 2200 元。
- 自动追加 `A <= 20` 后：A=20，B=30，利润 1700 元。
- 每次运行新建独立目录，保存输入、数学模型、求解结果、逐项检查与中文报告。

默认输出目录为 `outputs/modeling_assistant/<时间戳_随机ID>/`。`--output` 可改变父目录，不会覆盖已有运行。

## 离线输入格式

`template` 是严格模板解析器，不是大模型，不支持任意自由表述。每行必须符合以下格式，空行允许；任何无法解析的内容都会报错，避免漏掉限制。

```text
目标：利润最大化。
产品 A：单位利润 40 元；产量为非负整数。
产品 B：单位利润 30 元；产量为非负整数。
资源 工时：上限 100；A 每件消耗 2；B 每件消耗 1。
资源 原料：上限 80；A 每件消耗 1；B 每件消耗 2。
约束：A + B <= 50。
```

模板支持任意 ASCII 产品标识符、多个产品和资源，可将“整数”改为“实数”。每个资源必须明确列出所有产品消耗，不消耗时填 0。模板中的资源单位由用户保持一致，当前不自动换算单位。若输入缺少资源/产品等必要信息，返回待澄清问题，不猜测数值。

```bash
.venv/bin/python -m assistant --problem examples/production/problem.txt
.venv/bin/python -m assistant --problem examples/production/problem.txt --add-constraint 'A <= 20'
.venv/bin/python -m assistant --problem examples/production/problem.txt --add-constraint 'A >= 60'
```

追加约束支持加减、常数乘系数、`<=` / `>=` / `=`，例如 `A + 2*B <= 40`。可重复指定，按顺序累加，每阶段重新求解；不修改原始模型。条件更新只支持追加，删除或替换原约束请编辑模型 JSON。

## 检查和编辑数学模型

先只建模、不求解：

```bash
.venv/bin/python -m assistant --problem examples/production/problem.txt --prepare-only
```

打开输出目录中的 `model.json` 和 `report.md`，核对原题条件、假设和单位。编辑后，把实际文件路径代入：

```bash
.venv/bin/python -m assistant --model-file /absolute/path/to/model.json
.venv/bin/python -m assistant --model-file /absolute/path/to/model.json --add-constraint 'A <= 20'
```

模型包含 `variables`、`objective`、`constraints`、`assumptions`；格式定义在 `model.py`。支持 max/min、整数/连续变量、上下界与线性约束。`stage_2_model.json` 等文件可用于从变更后的模型继续求解。

## 使用 DeepSeek 自由表述建模

DeepSeek 官方密钥可通过独立向导配置，不需要 OpenAI 密钥：

```bash
.venv/bin/python -m assistant.configure --provider deepseek
.venv/bin/python -m assistant.configure --provider deepseek --check
```

粘贴密钥时输入不可见；模型 ID 默认 `deepseek-flash`，直接回车使用。[DeepSeek 当前官方接入文档](https://api-docs.deepseek.com/zh-cn/)列出的调用地址为 `https://api.deepseek.com`，本项目请求 `/chat/completions`。配置保存在 `~/.config/aiforresearch/deepseek.json`（权限 600，非加密本地文件），与 OpenAI 配置独立，不进入项目或 iCloud。

模型 ID 可自行填写有权限的型号。环境变量方式使用 `DEEPSEEK_API_KEY` 和 `DEEPSEEK_MODEL`；DeepSeek 后端不会读取 OpenAI 的密钥或模型环境变量。`--llm-model` 可以覆盖本次模型 ID。

真实调用一次自由表述示例：

```bash
.venv/bin/python -m assistant --backend deepseek --problem examples/production/problem_freeform.txt
```

直接输入自己的问题：

```bash
.venv/bin/python -m assistant --backend deepseek --interactive
```

可以输入多行，空行结束；也可以用 `--text '完整问题'`。加 `--prepare-only` 可先检查数学模型，再离线求解。

DeepSeek 使用 JSON Output，并在本地严格校验数学模型结构；这与服务端强制符合 JSON Schema 不同。空内容、截断、格式错误和非法模型均停止求解，不自动重试。[官方 JSON Output 文档](https://api-docs.deepseek.com/guides/json_mode/)

当前请求关闭 thinking，输出上限 6000 token、连接超时 60 秒。请求、响应、实际返回模型、usage 和耗时保存在运行记录，密钥不进入日志。402 表示余额不足，401 检查密钥，404 检查模型 ID，429 检查限流。真实请求会产生 API 费用。

此配置适用于 DeepSeek 官方密钥；第三方平台提供的 DeepSeek 模型需要该平台的地址、模型 ID 与接口协议，不能把第三方密钥发往官方地址。

当前验收：20 项测试通过。2026 年 10 月 16 日已完成一次真实 DeepSeek 自由表述建模→求解→验证，正确得到 A=40、B=20、利润 2200。对返回模型追加产量上限后离线求解得到 A=20、B=30、利润 1700。参见[真实验收记录](../docs/history/production.md)。单题通过不代表跨题型正确率已验证。

HTTPS 使用 truststore 加载操作系统信任证书，保留证书和主机名校验。若旧环境出现证书错误，先安装更新后的 requirements.txt；不要关闭证书校验。

## 使用 OpenAI 自由表述建模

在线适配器使用 OpenAI Responses API 的结构化输出，将题目转为同一数学模型数据；它不会生成或执行任意 Python 代码。接口依据[官方结构化输出文档](https://developers.openai.com/api/docs/guides/structured-outputs/)实现。

推荐使用本机配置向导（仅保存配置，不发送 API 请求）：

```bash
.venv/bin/python -m assistant.configure
.venv/bin/python -m assistant.configure --check
```

先在 [OpenAI API 控制台](https://platform.openai.com/api-keys)创建自己的 API Key，并确认 API 账户的计费与可用额度。向导隐藏密钥输入，将配置保存在 `~/.config/aiforresearch/openai.json`，权限 600；该文件不加密，但位于项目和 iCloud 目录之外。密钥不要发到聊天或写入仓库。向导建议 `gpt-4.1-mini` 作为首轮接通用模型，可修改为你有访问权限的其他模型。[官方模型页](https://developers.openai.com/api/docs/models/gpt-4.1-mini)确认其支持结构化输出；具体账户访问权限仍需真实请求验证。

也可以继续设置环境变量 `OPENAI_API_KEY` 和 `MODEL_ASSISTANT_MODEL`。优先级为：`--llm-model` 覆盖模型环境变量，环境变量覆盖本地配置。`--backend openai` 固定连接 OpenAI 官方 Responses API，DeepSeek 请显式选择 `--backend deepseek`。

首次运行自由表述示例（产生一次真实模型请求）：

```bash
.venv/bin/python -m assistant --backend openai --problem examples/production/problem_freeform.txt
```

核对生成模型包含两条资源约束、非负整数变量和利润最大化目标；正确转录时求解结果应为 A=40、B=20、利润 2200。仅看该数值不能证明建模完整，仍需核对报告中的模型。

直接输入自己的问题（多行输入，空行结束）：

```bash
.venv/bin/python -m assistant --backend openai --interactive
```

或使用 `--text '完整问题文本'`。需要先审阅模型、不立即求解时：

```bash
.venv/bin/python -m assistant --backend openai --problem examples/production/problem_freeform.txt --prepare-only
```

在线调用会发送题目文本，产生 API 费用。默认最多 6000 输出 token、60 秒连接超时，不自动重试。原始请求（不含密钥）、响应、模型名称、usage 和耗时保存在运行记录中。检查生成的模型后，可通过 `--model-file` 离线求解；去掉 `--prepare-only` 会直接求解并生成报告。

**验收状态：20 项自动测试通过；DeepSeek 已完成上述单题真实验收，OpenAI 路径仍仅有模拟测试。尚未开展批量建模正确率实验。** 不配置 API 仍可使用模板或人工模型文件完整运行求解流程。

常见错误：401 表示密钥无效；403 表示权限或地区访问问题；404 检查模型 ID 和访问权限；429 检查额度、计费及限流；400 检查模型是否支持当前结构化输出。`--check` 仅检查本地字段是否齐全，不联网、不证明账户可调用。请勿发送包含密钥的截图或配置文件。

## 输出与状态解释

| 文件或状态 | 含义 |
|---|---|
| `run.json` | 输入、后端、版本、原模型、各阶段结果和检查 |
| `model.json` | 初始模型，供查看和编辑 |
| `stage_N_model.json` | 各阶段的独立模型，可重放 |
| `report.md` | 数学模型、产量、目标值、约束检查和变化说明 |
| `optimal` | 求解器报告给定模型最优，另做可行性复算 |
| `infeasible` | 给定约束下无可行方案，不输出虚构产量 |
| `unbounded` | 给定模型目标无界，需要检查是否遗漏上限 |
| `needs_clarification` | 必要信息缺失；不求解 |
| `unsupported` | 在线模型判断超出当前支持范围；不求解 |
| `limit_reached` | 求解超时/资源限制；即使有候选解也不称最优 |
| `verification_failed` | 候选解未通过本地复算 |

CLI 退出码：0 表示已得到确定求解状态或完成准备（不可行/无界也属于正常求解结论）；2 表示输入、配置或连接错误；3 表示需澄清/不支持；4 表示求解未正常完成或验证失败。批量评测应读取 JSON 的 `status`，不能把退出码 0 都当作题目求解成功。

当前验证器检查变量完整性、有限数值、上下界、整数性、约束和目标复算；不能证明原题条件全部被正确转录，也不独立证明全局最优。开发案例的最优值另外通过测试中的独立穷举核对。

## 测试与本周剩余任务

```bash
.venv/bin/python -m unittest discover -s tests -v
python3 scripts/check_research_status.py
```

第一条检查新助手；第二条只核验旧 A1/A2 资产。新测试覆盖最优解、追加约束、整数/连续差异、不可行/无界、错误解检测、缺失信息、未识别文本、模型重放和 API 响应校验。测试不读取任何保留题，也不算正式模型实验。

本周剩余：配置实际模型后验收自由表述、检查条件转录、记录一次真实 API 成本；将开发题评分细则固化。自动修复、网页界面和其余题型尚未实现。

## 语义判断与不可行解释更新

整件实物默认整数并写明假设；质量和配比保持连续，用户明确要求连续近似时遵循用户设定。资源上限未知时询问是否有限制，明确不限时不设虚构大数上限。上述判断通过提示约束模型，仍须检查新问题的数学模型。

不可行结果现在附带程序推导的上下界矛盾，或保持变量上下界/整数要求时已验证的冲突约束组。无法定位时明确说明，不自动修改业务限制。

[23项本地测试及真实开发回归记录](../docs/history/production_check.md)。0.3.0已支持交互式澄清：直接回答提示即可，默认最多2轮补充，每次提交答案会再次调用API；留空或 /quit 退出。非交互输入仍直接保存待澄清结果。

## 连续澄清与运输分配

交互模式输入问题后，如果模型询问资源上限，可直接输入“煤供应不限”。补充答案为一行，无需再输入整道题；默认最多2轮，可用 `--max-clarifications 0` 禁用。每次答案触发一次付费模型请求，所有已返回响应分别保存，最终记录通过 clarification_history 回指前轮。

新增运输示例：

```bash
.venv/bin/python -m assistant --backend deepseek --problem examples/transport/problem.txt
```

正确建模时，W1→S1为20吨、W1→S3为20吨、W2→S2为30吨，其他为0，运费170元。供给上限、恰好需求和连续单位均应在模型中保留。

最新验收：31项本地测试、5次真实模型请求；[详细记录](../docs/history/transport.md)。旧版验收段落保留历史计数，当前以本节为准。
