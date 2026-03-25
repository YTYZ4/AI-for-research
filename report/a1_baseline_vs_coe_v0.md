# A1 baseline vs CoE v0

## 实验设置
- 三个模式：direct_answer / plain_guidance / coe_guided。
- 固定测试图：bing1.png、original.png。
- 固定协议：report/a1_eval_protocol_v0.md（max_side=420，width/height shrink，统一对比项）。
- 同一执行环境：mm26（Python 3.12 + numpy/matplotlib/scikit-image/scipy）。

## 结果表

| mode | runnable | correct | fix_rounds | time_to_first_working_min | error_type | self_check |
|---|---:|---:|---:|---:|---|---:|
| direct_answer | 1 | 2 | 1 | 2.0 | other | 1 |
| plain_guidance | 1 | 2 | 0 | 3.5 | none | 2 |
| coe_guided | 1 | 2 | 0 | 4.2 | none | 2 |

## 观察
- 首轮稳定性：plain_guidance 与 coe_guided 均无首轮错误；direct_answer 首轮出现路径配置错误。
- 修复轮次：plain_guidance 与 coe_guided 为 0，direct_answer 为 1。
- 主动检查能力：coe_guided 在输出结构中最完整，明确覆盖 Reader/Planner/Coder/Reviewer/Experimenter，Reviewer 对 5 类错误逐项检查最到位。
- 运行耗时：本次实验中 coe_guided 版本整体耗时最高，说明结构化输出不等于更快执行。

## 结论 v0
- 在 A1 当前任务上，固定多角色结构（CoE）不必然提升算法最终正确性（3 模式均可达 correct=2），但能明显提升首轮输出的可检查性与纠错可追踪性。
- plain_guidance 已能显著减少 direct_answer 的首轮无关错误；coe_guided 在“检查覆盖度”上进一步增强。
- 下一轮应继续用同协议复跑，观察该趋势是否稳定，而不是立刻扩大结论范围。
