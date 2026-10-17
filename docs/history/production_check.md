# 生产计划语义与不可行解释修正记录

2026 年 10 月 16 日，版本 0.2.0。修正整件产量的变量域、资源上限澄清和不可行解释。以下为针对已见问题的开发回归，不是保留测试集结果，也不用于宣称泛化正确率。

## 修改

- 整件实物默认整数并明示假设；质量和配比采用连续变量，用户明确要求连续近似时优先遵循。变量域依赖模型的语义理解，尚不保证所有新问题都判断正确。
- 缺少资源上限时询问“有限还是不限”；明确不限时省略容量约束，禁止用有限大数代替无穷大。
- 不可行时由程序分析模型：两变量等式消元可推导矛盾上下界；其他小模型用至多五秒的约束删除复验定位冲突组。保留原上下界和整数性，不保证找到约束条数最少的冲突组。大模型仅报告未定位冲突，不猜测原因。

## 真实调用结果

| 开发案例 | 结果 | 证据 |
|---|---|---|
| furniture | 整数变量；桌20、椅20；利润4000 | [报告](../../outputs/modeling_assistant/development_regression_v020/furniture/20261016_144133_282e2699/report.md) |
| electronics | 整数变量；手机40、电脑20；利润36000 | [报告](../../outputs/modeling_assistant/development_regression_v020/electronics/20261016_144135_4c30aa5e/report.md) |
| coal_missing | 询问煤的供应上限，明确可选择供应不限 | [报告](../../outputs/modeling_assistant/development_regression_v020/coal_missing/20261016_144136_eff7e712/report.md) |
| feed_infeasible | 连续配比；不可行；自动解释原料2比例至少50%但至多40% | [报告](../../outputs/modeling_assistant/development_regression_v020/feed_infeasible/20261016_144139_dc52fe65/report.md) |
| coal_unlimited | 首次失败：擅自增加1e18煤上限，虽数值4000但建模不合格 | [报告](../../outputs/modeling_assistant/development_regression_v020/coal_unlimited/20261016_144142_4bf16693/report.md) |
| explicit_continuous | 保留连续变量，遵循用户明确的近似要求 | [报告](../../outputs/modeling_assistant/development_regression_v020/explicit_continuous/20261016_144145_feccb7e0/report.md) |
| coal_unlimited_corrected | 补充禁止虚构上限的提示后，只保留电量约束；甲0、乙20；利润4000 | [报告](../../outputs/modeling_assistant/development_regression_v020/coal_unlimited_corrected/20261016_144204_4e75794e/report.md) |

共7次真实请求：6次初始回归和1次有针对性的修正复验；保留全部原始请求、响应、模型和 usage。最终追加的提示限制只对煤不限案例做了真实复验，其余案例的成功记录对应此前版本提示；23项本地自动测试在最终代码上通过。

## 本地验证

23项自动测试通过，新增覆盖：配方上下界冲突及可行邻近案例、变量顺序对换、仅因整数性造成的无解、无关约束剔除和原模型保持不变。原有测试仍覆盖最优解、API配置隔离和证书校验。

## 使用

仍使用 `.venv/bin/python -m assistant --backend deepseek --interactive`。不可行解释同时打印到终端并写入报告。需要澄清时，本版仍结束当前请求；用户将补充条件加入完整题目后重新运行，尚未实现持续多轮对话。

## 评测划分

用户提供的饲料混合已进入开发材料。原规划 OPT03 营养配餐与之可能同族，正式冻结保留题时必须重新划分或更换题族；不得把相似配比变体作为未见测试题。
