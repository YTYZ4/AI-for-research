# 不支持任务缺少拒绝说明：契约修复与定向回归

助手v0.11.7，deepseek-flash。本轮原最小费用流及两种改写9/9原始通过，均有非空的任务范围说明；多商品流和时变任务6/6也不再缺说明。全批42次三层34/42、34/42、40/42，保留两项方向追问失败。没有重跑完整开发集，历史失败不覆盖。

## 共因与改动

旧3条原响应完全相同：unsupported、questions=[]、model=null。实际请求Schema的三个字段相互独立，不能表达“ready时空questions、非ready时必须有说明”的状态关系。questions的名称又容易被理解成仅存放追问，从而在“不需追问”的拒绝中留空。旧图说明还称“完整题返回ready”，provider在Schema后再次追加“完整问题必须返回ready”和资源供应追问示例，与“条件完整但任务范围不支持”冲突。

本次：
- 图说明改为先判断任务范围，再检查信息完整性；明确questions是兼容名称的面向用户说明列表，拒绝原因也放在其中。
- DeepSeek图请求Schema增加互斥状态分支：ready必须空questions且有原始图；非ready必须model=null、至少一条非空白说明。
- 图请求不再追加通用ready指令及无关资源追问示例。
- 本地validate_envelope强化拒绝空字符串、纯空白、混入空白项的说明列表。空原因仍失败，不由程序编造理由，不升级ready，也不自动再调用API。

DeepSeek JSON mode不强制执行Schema，因此仍保留本地验证。OpenAI严格输出路径保留兼容Schema形状，未发送新增根层组合约束；本轮未作OpenAI真实回归，不宣称该后端效果。

graph_units、graph_quotes、capacity_conflict、parameter_policy、dimension_policy、missing_capacity、source_quotes、format_repair八个护栏模块与v0.11.6快照逐字相同。model模块仅强化非ready的空白说明检查，数值护栏未变。

以上是可定位的契约缺口与指令冲突；没有消融实验，不能确定每项修改的独立因果贡献。

## 本地测试与旧失败

210项本地测试通过（此前204项，新增6个测试方法，含多个子案例）。覆盖：
- 空数组、空字符串、纯空白、有效说明混入空白、状态/model不一致。
- 正确拒绝和追问保持原样，拒绝不自动提升。
- 实际请求不再包含冲突后缀；其他后端保持原Schema形状。
- 独立评分拒绝泛泛“不支持”、仅重复题名、编造JSON限制、建议忽略费用及错误ready。
- 既有数值、单位、引用和误放行测试全部继续通过。

旧3条空说明响应离线重放均仍被拒绝；新请求状态Schema也判无效。零新增API，不计入42次。没有给旧响应补理由并改写旧统计。

## 冻结真实API回归

协议refusal_contract_v1，14场景各3次，共42次；单次请求不重试，批中未改代码/题目/评分。260个冻结文件与快照及工作区哈希一致。81,621 tokens，usage未知0，不估算货币费用。

| 累计口径 | 通过 | 比例 |
|---|---:|---:|
| 原始通过 | 34/42 | 80.95% |
| 格式修复后累计通过 | 34/42 | 80.95% |
| 本地处理后累计通过 | 40/42 | 95.24% |

三个数不可相加。格式修复0、引用修复0，必要数值/未知转换护栏6次。图请求36次均通过实际发送的状态Schema独立检查，但Schema通过不代表业务正确；另6次走通用路径（Logistic及未命中图关键词的成本目标改写）。

| 子集 | 调用数 | 原始 | 格式后累计 | 本地后累计 |
|---|---:|---:|---:|---:|
| 最小费用流原题及两种改写 | 9 | 9 | 9 | 9 |
| 多商品流、时变网络 | 6 | 6 | 6 | 6 |
| 合法图及费用否定对照 | 15 | 15 | 15 | 15 |
| 非整数容量、未知转换 | 6 | 0 | 0 | 6 |
| 缺方向 | 3 | 1 | 1 | 1 |
| Logistic禁止改值对照 | 3 | 3 | 3 | 3 |

合法图包含正反向单位换算、原单位、混合单位，以及“费用数据无关，不要求最小费用流，只求普通最大流”。后者3/3原始通过，未因出现费用关键词就拒绝。非法转换仍由程序阻止，不计为原始通过。

## 保留失败与说明质量问题

两项自动失败均为flow_missing_direction：
- 第1次返回needs_clarification，并询问“从哪个节点指向哪个节点”，语义正确；旧评分只匹配“方向”而误判。本轮保持冻结结果，不回写通过率。
- 第2次把缺少方向误判为unsupported；应询问方向，这是实际状态错误。
- 第3次正常追问，通过。

开发助手复核还发现：
- 多商品流第3次正确指出不支持多商品流，但额外声称缺少节点/边/容量不准确，原题已给S到T及容量。自动检查未覆盖该附加断言，单独记录为说明质量问题。
- 部分拒绝附带“若只需最大流，请移除费用要求”等改变任务的建议；均保持unsupported且model=null，没有静默执行替代模型，但这些建议超出必要拒绝说明，后续宜精简。

因此本轮解决的是空说明问题，不代表拒绝解释全部语义正确，也不代表不支持/缺信息分类已经稳定。独立评分是有限规则检查，助手复核不冒充独立人工评价。

## 证据与复跑

- [批次摘要](../../outputs/refusal_contract_regressions/20261016_225944_e764b376/summary.md)、[逐次CSV](../../outputs/refusal_contract_regressions/20261016_225944_e764b376/results.csv)
- [共因分析](../../outputs/refusal_contract_regressions/20261016_225944_e764b376/root_cause_analysis.json)、[语义复核](../../outputs/refusal_contract_regressions/20261016_225944_e764b376/semantic_review.json)
- [旧失败离线重放](../../outputs/refusal_contract_regressions/20261016_225944_e764b376/offline_replay.json)、[实际请求状态检查](../../outputs/refusal_contract_regressions/20261016_225944_e764b376/request_state_audit.json)
- [测试日志](../../outputs/refusal_contract_regressions/20261016_225944_e764b376/local_tests.log)、[冻结清单](../../outputs/refusal_contract_regressions/20261016_225944_e764b376/manifest.json)、[完整性](../../outputs/refusal_contract_regressions/20261016_225944_e764b376/snapshot_integrity.json)、[护栏核对](../../outputs/refusal_contract_regressions/20261016_225944_e764b376/guard_integrity.json)
- [固定协议](../../protocols/refusal_contract_v1.md)

运行 `.venv/bin/python -m evaluation.refusal_contract` 会新增42次真实请求。开发失败子集和变体不代表独立新题泛化；三个口径保持原定义，不与历史批次合并。
