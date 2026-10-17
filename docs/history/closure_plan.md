# 结项倒排计划 2026-10-16

> 状态更新（2026-10-16）：本文件保留为 A1/A2 前期阶段资料。当前执行以[跨题型助手八周规划](../plan.md)和[新版交付清单](../delivery.md)为准；旧范围、倒排安排和完成状态不适用于新助手。

## 当前判断

原始 Timeline 的结题交付包括：最终流程文档、题库与模板库、原型、评估报告、答辩材料。A1/A2 主案例和主要量化实验已经完成，剩余两个月不适合再扩大实验范围，也不适合在没有合适受试者的情况下硬做正式 pilot。

当前结项策略是：冻结 A1/A2 主线，明确记录 formal pilot 暂缓，把已有证据整理成可提交、可复现、可演示的结项包。

## 必须交付

| 交付物 | 当前状态 | 结项前动作 |
|---|---|---|
| 最终研究报告 | 已形成 `report/final_report_v0.md` 正文初稿 | 导师审阅后补图表、格式和最终引用 |
| 最终流程文档 | 已形成 `report/final_workflow_guide_v0.md` | 用 A1/A2 实际 run 做一次外部可读性复核 |
| 题库与模板库 | 16 个正式条目，A1/A2 已闭环，A3/A4 已冻结首发条目 | 固定版本号、入口页和使用说明，不再用 rerun 扩充数量 |
| 原型 | CLI advisor demo 可用 | 准备 5 分钟演示脚本，锁定 A2 baseline + plain guidance 主线 |
| 评估报告 | A1/A2 metrics、summary、audit 已有 | 统一结果表、证据边界和失败案例说明 |
| 答辩材料 | 已形成 `report/defense_script_v0.md` 和 `report/defense_deck_outline_v0.md` | 排版结项 PPT，完成两次完整演练 |
| 复现与提交包 | 状态检查脚本可用 | 完成全仓库 QA、链接检查和最终提交清单 |

## 六周倒排

### 第 1 周：冻结范围和结果

- 固定最终研究问题：结构化 guidance 是否改善 LLM 生成代码的过程可检查性。
- 固定主案例：A1 Seam Carving、A2 低秩图像修复。
- 固定不做事项：不启动 formal participant pilot；A3/A4 不进入主结论。
- 运行 `python3 scripts/check_research_status.py`，保存通过结果。
- 完成 `report/final_results_summary_v0.md` 的数据核对。

验收：结项报告中不再出现“中期后再决定是否跑 pilot”的悬置表述。

### 第 2 周：完成最终流程文档（已完成初稿）

- 把 `report/prompt_template_library_v1.md`、`report/structured_modeling_checklist_v1.md` 和 `report/error_taxonomy_and_feedback_rules_v1.md` 串成一条流程。
- 明确 direct answer、plain guidance、CoE guided 的使用条件和输出要求。
- 加入一个 A1 示例和一个 A2 示例，说明如何从题目进入 task card、prompt、运行和回归。

验收：没有读过仓库的人可以只看流程文档理解输入、输出、检查点和记录方式。当前已完成 v0，待导师或外部读者复核。

### 第 3 周：完成最终报告正文（已完成 v0）

- 按 `report/final_report_outline_v0.md` 写完研究背景、方法、实验、结果、局限和结论。
- 所有定量结论回指 metrics；所有过程结论回指 run 或 audit。
- 明确 pilot 暂缓的原因，不把非正式反馈写成 participant 数据。

验收：`report/final_report_v0.md` 已形成可交给导师审阅的正文，不再是提纲。

### 第 4 周：完成原型和答辩演示（脚本和结构已完成）

- 锁定 `python3 run_research_case.py --demo advisor` 为主演示入口。
- 准备 5 分钟演示：题目、task card、prompt、run、metrics、结论边界。
- 准备 3 个追问答案：为什么没有学生 pilot、为什么 A2 指标没有差异、A3/A4 为什么没有进入主实验。

验收：CLI 已通过干净终端演示；当前待完成的是 PPT 排版和口头演练。

### 第 5 周：结项包 QA

- 运行状态检查和 CLI demo。
- 检查 README、最终报告、证据矩阵、题库、流程文档之间的数字和术语一致性。
- 检查所有报告链接、CSV、代表性输出和任务卡是否存在。
- 将 formal pilot task pack 标记为候选材料，不放入“已完成实验”清单。

验收：结项包能从 README 进入所有核心材料，且不存在相互冲突的阶段口径。

### 第 6 周：答辩准备和最终冻结

- 完成结项 PPT 和演示脚本。
- 进行至少两次完整口头演练。
- 根据导师反馈只修报告、图表和演示，不再新增高风险实验。
- 冻结版本号、提交清单和最终归档路径。

验收：报告、PPT、演示、代码和证据表可以作为一个完整成果包提交。

## 结项范围决策

### 保留为主成果

- A1/A2 两个可复查主案例。
- 结构化 guidance 的过程质量结论。
- bug-repair benchmark 和回归验证流程。
- 16 条中期题库骨架。
- CLI advisor demo 和状态检查脚本。

### 明确不包装成已完成成果

- 学生学习效果已经被证明。
- 初学者一定能独立完成当前任务。
- formal participant pilot 已完成。
- A3/A4 已完成固定协议实验。
- 结构化 guidance 显著提高了 A2 最终图像质量。

## 每周固定动作

- 每周运行一次 `python3 scripts/check_research_status.py`。
- 每周只更新一个结项交付物，避免同时改动报告、指标和协议口径。
- 每次新增结论必须绑定至少一个 `metrics/` 文件和一个 `report/` 或 `runs/` 文件。
