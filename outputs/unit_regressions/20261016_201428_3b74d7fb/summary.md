# 原始参数与确定性单位换算回归

通过10/12；已知tokens 37047；未知usage 0。
每题三次，无重试；仅验证两个动态题族，不代表其他任务的单位都已自动处理。

| 场景 | 次数 | 结果 | 失败分类 |
|---|---:|---|---|
| cooling_control | 1 | pass |  |
| logistic_control | 1 | pass |  |
| cooling_units | 1 | fail | evaluation_failed |
| logistic_units | 1 | pass |  |
| cooling_control | 2 | pass |  |
| logistic_control | 2 | pass |  |
| cooling_units | 2 | pass |  |
| logistic_units | 2 | pass |  |
| cooling_control | 3 | pass |  |
| logistic_control | 3 | pass |  |
| cooling_units | 3 | fail | generation_error |
| logistic_units | 3 | pass |  |

评分同时核对原题未换算参数、程序换算记录、原题解析轨迹。失败详情见results.json；source_model.json和unit_conversion.json在每次运行目录。
