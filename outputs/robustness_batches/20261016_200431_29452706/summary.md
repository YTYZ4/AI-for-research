# 修复后定向回归

本地数据检查：7/7；在线系统验收：9/10；tokens 26455。
本批为修复后定向测试，不覆盖或合并修复前64次结果。正确追问可能来自模型或本地护栏，分列如下。

| 场景 | 次数 | 系统结果 | 原模型状态 | 本地护栏 |
|---|---:|---|---|---|
| invalid_capacity | 1 | pass | needs_clarification | False |
| valid_logistic | 1 | pass | ready | False |
| cooling_units | 1 | pass | ready | False |
| logistic_units | 1 | fail | ready | False |
| path_units | 1 | pass | ready | False |
| invalid_capacity | 2 | pass | unsupported | False |
| valid_logistic | 2 | pass | ready | False |
| cooling_units | 2 | pass | ready | False |
| logistic_units | 2 | pass | ready | False |
| path_units | 2 | pass | ready | False |

数据质量是本地输入校验，不计LLM成功次数。两次通过不证明长期稳定。失败详情见results.json和每题API/评分证据。
