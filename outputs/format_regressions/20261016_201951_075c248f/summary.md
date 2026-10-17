# 原始参数与确定性单位换算回归

通过12/12；已知tokens 36961；未知usage 0。
每题三次，无重试；仅验证两个动态题族，不代表其他任务的单位都已自动处理。

| 场景 | 次数 | 结果 | 失败分类 |
|---|---:|---|---|
| cooling_control | 1 | pass |  |
| logistic_control | 1 | pass |  |
| cooling_units | 1 | pass |  |
| logistic_units | 1 | pass |  |
| cooling_control | 2 | pass |  |
| logistic_control | 2 | pass |  |
| cooling_units | 2 | pass |  |
| logistic_units | 2 | pass |  |
| cooling_control | 3 | pass |  |
| logistic_control | 3 | pass |  |
| cooling_units | 3 | pass |  |
| logistic_units | 3 | pass |  |

评分同时核对原题未换算参数、程序换算记录、原题解析轨迹。失败详情见results.json；source_model.json和unit_conversion.json在每次运行目录。

## 格式与系统结果分开统计

原始schema通过 12/12；本地格式修复 0 条；拒绝修复 0 条。
schema通过不等于原题正确；系统通过仍要求原值提取、程序换算和独立数值评分。所有格式修复均为本地单次操作，不新增API请求。

| 场景 | 次数 | 原schema通过 | 格式处理 | 系统结果 |
|---|---:|---|---|---|
| cooling_control | 1 | True | not_needed | pass |
| logistic_control | 1 | True | not_needed | pass |
| cooling_units | 1 | True | not_needed | pass |
| logistic_units | 1 | True | not_needed | pass |
| cooling_control | 2 | True | not_needed | pass |
| logistic_control | 2 | True | not_needed | pass |
| cooling_units | 2 | True | not_needed | pass |
| logistic_units | 2 | True | not_needed | pass |
| cooling_control | 3 | True | not_needed | pass |
| logistic_control | 3 | True | not_needed | pass |
| cooling_units | 3 | True | not_needed | pass |
| logistic_units | 3 | True | not_needed | pass |
