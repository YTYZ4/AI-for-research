# A1 replication run template

## Meta
- run_id: 2026-03-26_run_014
- case_id: A1
- mode: plain_guidance
- replicate_id: rep2
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
- prompt_used.md: solutions/hw1_op1/generated/run_014_plain_guidance_rep2/prompt_used.md
- model_raw_response.md: solutions/hw1_op1/generated/run_014_plain_guidance_rep2/model_raw_response.md
- src path: solutions/hw1_op1/generated/run_014_plain_guidance_rep2/src/
- outputs path: outputs/hw1_op1/run_014_plain_guidance_rep2/

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
- final_working_time_min: 5.4

## Guidance metrics row to append
- CSV target: metrics/a1_guidance_eval_v0.csv
- row: 2026-03-26_run_014,A1,plain_guidance,prompts/a1/baseline_plain_guidance_v0.md,v1,2,1,2,2,none,0,5.4,replication queue item 2

## Codegen performance rows to append
- CSV target: metrics/a1_codegen_perf_v0.csv
- row 1: 2026-03-26_run_014,bing1.png,plain_guidance,72.9664,20.5696,95.5802,1,replication queue item 2
- row 2: 2026-03-26_run_014,original.png,plain_guidance,148.3295,74.2918,225.4836,1,replication queue item 2

## Notes
- protocol deviation: none
- notable behavior: completed under fixed protocol and generated both case outputs with runtime_metrics.csv.
- comparison to prior runs: runtime is higher than run_013 plain_guidance rep1.
