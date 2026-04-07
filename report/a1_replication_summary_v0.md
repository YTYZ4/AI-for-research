# A1 replication summary v0

## Scope
- target runs: run_010 to run_018
- case_id: A1
- protocol_file: report/a1_eval_protocol_v0.md
- fixed setup: bing1.png + original.png, max_side=420, shrink-only

## 已完成
- completed in replication track: run_010, run_011, run_012, run_013, run_014, run_015, run_016, run_017, run_018
- baseline anchor runs included for context: run_006, run_007, run_008
- current data source: metrics/a1_guidance_eval_v0.csv (12 rows total)

### 当前统计（基于已回填 12 条）
1) Runnable success count by mode
- direct_answer: 4/4
- plain_guidance: 4/4
- coe_guided: 4/4

2) correct=2 count by mode
- direct_answer: 4/4
- plain_guidance: 4/4
- coe_guided: 4/4

3) fix_rounds median by mode
- direct_answer: 0
- plain_guidance: 0
- coe_guided: 0

4) time_to_first_working_min median by mode
- direct_answer: 1.65
- plain_guidance: 4.50
- coe_guided: 1.45

5) self_check=2 count by mode
- direct_answer: 0/4
- plain_guidance: 4/4
- coe_guided: 4/4

## 未完成
- pending replication runs: none
- required immediate backfill per run:
	- runs/<run_doc>.md
	- metrics/a1_guidance_eval_v0.csv (1 row)
	- metrics/a1_codegen_perf_v0.csv (2 rows: bing1.png + original.png)

## 初步观察
- 在当前样本下，三种模式的 runnable 和 correct 均为 100%，说明协议与实现链路基本可复现。
- plain_guidance 与 coe_guided 的 self_check 记录明显优于 direct_answer（plain 4/4, coe 4/4 vs direct 0/4）。
- direct_answer 的 time_to_first_working 当前更快，但出现过额外修复轮次；该差异仍需完整 replication 才能判断稳定性。
- coe_guided 在样本补齐后保持较低的 time_to_first_working 中位数（1.45），与 direct_answer 接近。

## Interpretation boundary
- This is a fixed-protocol replication snapshot, not an expanded-scope final conclusion.
- Full run_010 to run_018 replication is complete; conclusions remain scoped to this fixed protocol.
