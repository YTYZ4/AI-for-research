# A1 replication run template

## Meta
- run_id: 2026-03-26_run_013
- case_id: A1
- mode: plain_guidance
- replicate_id: rep1
- prompt_file: prompts/a1/baseline_plain_guidance_v0.md
- task_card_version: v1
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
- prompt_used.md: solutions/hw1_op1/generated/run_013_plain_guidance_rep1/prompt_used.md
- model_raw_response.md: solutions/hw1_op1/generated/run_013_plain_guidance_rep1/model_raw_response.md
- src path: solutions/hw1_op1/generated/run_013_plain_guidance_rep1/src/
- outputs path: outputs/hw1_op1/run_013_plain_guidance_rep1/

## First-pass assessment
- artifact_complete: 2
- runnable: 1
- correct: 2
- self_check: 2
- first_error_type: none
- first_error_summary: none

## Fix log
- fix_rounds: 0
- fix_step_1: none
- fix_step_2: none
- final_working_time_min: 3.6

## Guidance metrics row to append
- CSV target: metrics/a1_guidance_eval_v0.csv
- row: 2026-03-26_run_013,A1,plain_guidance,prompts/a1/baseline_plain_guidance_v0.md,v1,2,1,2,2,none,0,3.6,replication queue item 1

## Codegen performance rows to append
- CSV target: metrics/a1_codegen_perf_v0.csv
- row 1: 2026-03-26_run_013,bing1.png,plain_guidance,49.7853,14.3805,66.9598,1,replication queue item 1
- row 2: 2026-03-26_run_013,original.png,plain_guidance,96.7485,45.7774,144.9900,1,replication queue item 1

## Notes
- protocol deviation: none
- notable behavior: first pass runnable and complete, with explicit assertion-style self checks in raw response.
- comparison to prior runs: runtime is significantly higher than run_010 and run_016.
