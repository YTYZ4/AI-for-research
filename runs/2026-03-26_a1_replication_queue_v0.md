# A1 replication queue v0

固定执行顺序（remaining 7）：
1. run_013 (plain_guidance rep1)
2. run_011 (direct_answer rep2)
3. run_014 (plain_guidance rep2)
4. run_017 (coe_guided rep2)
5. run_012 (direct_answer rep3)
6. run_015 (plain_guidance rep3)
7. run_018 (coe_guided rep3)

状态：
- run_010: completed
- run_016: completed
- run_013: pending
- run_011: pending
- run_014: pending
- run_017: pending
- run_012: pending
- run_015: pending
- run_018: pending

执行纪律：
- 只变会话，不变协议。
- 固定 bing1.png / original.png、max_side=420、shrink-only。
- 完成每次 run 后立刻回填 runs + guidance CSV + codegen perf CSV。
