# A1 replication run template

## Meta
- run_id: 2026-03-26_run_016
- case_id: A1
- mode: coe_guided
- replicate_id: rep1
- prompt_file: prompts/a1/coe_multi_role_v0.md
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
- prompt_used.md: solutions/hw1_op1/generated/run_016_coe_guided/prompt_used.md
- model_raw_response.md: solutions/hw1_op1/generated/run_016_coe_guided/model_raw_response.md
- src path: solutions/hw1_op1/generated/run_016_coe_guided/src/
- outputs path: outputs/hw1_op1/run_016_coe_guided/

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
- final_working_time_min: 1.2

## Guidance metrics row to append
- CSV target: metrics/a1_guidance_eval_v0.csv
- row: 2026-03-26_run_016,A1,coe_guided,prompts/a1/coe_multi_role_v0.md,v1,2,1,2,2,none,0,1.2,pilot replication 1

## Codegen performance rows to append
- CSV target: metrics/a1_codegen_perf_v0.csv
- row 1: 2026-03-26_run_016,bing1.png,coe_guided,18.2013,5.1697,24.5153,1,pilot replication 1
- row 2: 2026-03-26_run_016,original.png,coe_guided,33.8726,17.2976,52.3456,1,pilot replication 1

## Notes
- protocol deviation: none
- notable behavior: five-role output was present in model_raw_response and run was first-pass runnable.
- comparison to prior runs: runtime is much lower than run_008 coe_guided and close to run_010.
