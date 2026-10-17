# 生产计划建模与求解报告

运行时间：2026-10-16T14:45:34.894187+08:00。输入来源：deepseek。

验证仅针对已生成模型；请对照原题核对遗漏条件、单位和假设。离线模板结果不属于大模型实验。


## 阶段 1 初始模型

### 数学模型

最大化 500*x_phone + 800*x_computer（元）

- x_phone：每天生产的手机数量；整数；下界 0；上界 无限制；单位 部
- x_computer：每天生产的电脑数量；整数；下界 0；上界 无限制；单位 台

约束：

- chip_supply：2*x_phone + 1*x_computer <= 100（个）
- screen_supply：1*x_phone + 2*x_computer <= 80（块）
- assembly_hours：1*x_phone + 3*x_computer <= 120（小时）
- market_strategy：1*x_computer + -1*x_phone <= 0（台）

假设：

- 手机和电脑的产量按整件实物计，变量为非负整数。
- 每天芯片、屏幕和组装工时供应上限分别为100个、80块和120小时。
- 所有生产数量均不超过对应资源约束决定的可行范围。
- 市场策略约束为电脑产量不超过手机产量。

求解状态：optimal。

Optimization terminated successfully. (HiGHS Status 7: Optimal)

- x_phone = 40
- x_computer = 20
- 目标值：36000 元
- 可行性与目标复算：通过

| 检查 | 左值 | 关系 | 右值 | 通过 |
|---|---:|---|---:|---|
| x_phone 下界 |  |  |  | 是 |
| x_phone 整数性 |  |  |  | 是 |
| x_computer 下界 |  |  |  | 是 |
| x_computer 整数性 |  |  |  | 是 |
| chip_supply | 100.0 | <= | 100 | 是 |
| screen_supply | 80.0 | <= | 80 | 是 |
| assembly_hours | 100.0 | <= | 120 | 是 |
| market_strategy | -20.0 | <= | 0 | 是 |
| 目标值复算 |  |  |  | 是 |
