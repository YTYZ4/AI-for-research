# A1 replication run template

## Meta
- run_id: 2026-03-26_run_012
- case_id: A1
- mode: direct_answer
- replicate_id: rep3
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
- prompt_used.md: solutions/hw1_op1/generated/run_012_direct_answer_rep3/prompt_used.md
- model_raw_response.md: solutions/hw1_op1/generated/run_012_direct_answer_rep3/model_raw_response.md
- src path: solutions/hw1_op1/generated/run_012_direct_answer_rep3/src/
- outputs path: outputs/hw1_op1/run_012_direct_answer_rep3/

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
- final_working_time_min: 1.3

## Guidance metrics row to append
- CSV target: metrics/a1_guidance_eval_v0.csv
- row: 2026-03-26_run_012,A1,direct_answer,prompts/a1/baseline_direct_answer_v0.md,none,2,1,2,1,none,0,1.3,replication queue item 4

## Codegen performance rows to append
- CSV target: metrics/a1_codegen_perf_v0.csv
- row 1: 2026-03-26_run_012,bing1.png,direct_answer,18.7837,4.9949,24.4739,1,replication queue item 4
- row 2: 2026-03-26_run_012,original.png,direct_answer,36.6128,17.5688,55.1409,1,replication queue item 4

## Notes
- protocol deviation: none
- notable behavior: first pass runnable and complete under fixed protocol.
- comparison to prior runs: runtime is close to run_010 and much faster than run_011.
