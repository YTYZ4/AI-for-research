# A1 replication run template

## Meta

- run_id: 2026-03-26_run_011
- case_id: A1
- mode: direct_answer
- replicate_id: rep2
- prompt_file: prompts/a1/baseline_direct_answer_v0.md
- task_card_version: none
- protocol_file: report/a1_eval_protocol_v0.md
- env: mm26

## Fixed protocol checklist

- [x] test images = bing1.png, original.png
- [x] max_side = 420
- [x] shrink only
- [x] width shrink done
- [x] height shrink done
- [x] compare output generated

## Prompt and raw output

- prompt_used.md: solutions/hw1_op1/generated/run_011_direct_answer_rep2/prompt_used.md
- model_raw_response.md: solutions/hw1_op1/generated/run_011_direct_answer_rep2/model_raw_response.md
- src path: solutions/hw1_op1/generated/run_011_direct_answer_rep2/src/
- outputs path: outputs/hw1_op1/run_011_direct_answer_rep2/

## First-pass assessment

- artifact_complete: 2
- runnable: 1
- correct: 2
- self_check: 1
- first_error_type: none
- first_error_summary: none

## Fix log

- fix_rounds: 0
- fix_step_1: none
- fix_step_2: none
- final_working_time_min: 5.2

## Guidance metrics row to append

- CSV target: metrics/a1_guidance_eval_v0.csv
- row: 2026-03-26_run_011,A1,direct_answer,prompts/a1/baseline_direct_answer_v0.md,none,2,1,2,1,none,0,5.2,replication queue item 2

## Codegen performance rows to append

- CSV target: metrics/a1_codegen_perf_v0.csv
- row 1: 2026-03-26_run_011,bing1.png,direct_answer,73.7054,19.4438,95.2078,1,replication queue item 2
- row 2: 2026-03-26_run_011,original.png,direct_answer,140.3213,70.5032,213.7220,1,replication queue item 2

## Notes

- protocol deviation: none
- notable behavior: completed under fixed protocol and generated both case outputs with runtime_metrics.csv.
- comparison to prior runs: runtime is substantially slower than run_010 pilot replication.
