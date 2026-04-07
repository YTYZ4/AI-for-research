# A1 replication run template

## Meta
- run_id: 2026-03-26_run_015
- case_id: A1
- mode: plain_guidance
- replicate_id: rep3
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
- prompt_used.md: solutions/hw1_op1/generated/run_015_plain_guidance_rep3/prompt_used.md
- model_raw_response.md: solutions/hw1_op1/generated/run_015_plain_guidance_rep3/model_raw_response.md
- src path: solutions/hw1_op1/generated/run_015_plain_guidance_rep3/src/
- outputs path: outputs/hw1_op1/run_015_plain_guidance_rep3/

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
- final_working_time_min: 5.5

## Guidance metrics row to append
- CSV target: metrics/a1_guidance_eval_v0.csv
- row: 2026-03-26_run_015,A1,plain_guidance,prompts/a1/baseline_plain_guidance_v0.md,v1,2,1,2,2,none,0,5.5,replication queue item 6

## Codegen performance rows to append
- CSV target: metrics/a1_codegen_perf_v0.csv
- row 1: 2026-03-26_run_015,bing1.png,plain_guidance,18.8012,5.1230,24.6274,1,replication queue item 6
- row 2: 2026-03-26_run_015,original.png,plain_guidance,35.0429,17.6436,53.6999,1,replication queue item 6

## Notes
- protocol deviation: none
- notable behavior: first pass runnable and complete under fixed protocol.
- comparison to prior runs: runtime is much faster than run_013 and run_014 plain_guidance.
