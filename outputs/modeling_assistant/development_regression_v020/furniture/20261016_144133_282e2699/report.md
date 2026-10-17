# 生产计划建模与求解报告

运行时间：2026-10-16T14:41:33.214450+08:00。输入来源：deepseek。

验证仅针对已生成模型；请对照原题核对遗漏条件、单位和假设。离线模板结果不属于大模型实验。


## 阶段 1 初始模型

### 数学模型

最大化 120*x_table + 80*x_chair（元）

- x_table：每周生产的桌子数量；整数；下界 0；上界 无限制；单位 张
- x_chair：每周生产的椅子数量；整数；下界 0；上界 无限制；单位 把

约束：

- carpentry_hours：4*x_table + 2*x_chair <= 120（小时）
- painting_hours：2*x_table + 3*x_chair <= 100（小时）

假设：

- 桌子、椅子为整件实物产品，生产数量取非负整数。
- 每周木工可用工时上限为120小时，油漆工可用工时上限为100小时。
- 利润单位为元，工时单位为小时。

求解状态：optimal。

Optimization terminated successfully. (HiGHS Status 7: Optimal)

- x_table = 20
- x_chair = 20
- 目标值：4000 元
- 可行性与目标复算：通过

| 检查 | 左值 | 关系 | 右值 | 通过 |
|---|---:|---|---:|---|
| x_table 下界 |  |  |  | 是 |
| x_table 整数性 |  |  |  | 是 |
| x_chair 下界 |  |  |  | 是 |
| x_chair 整数性 |  |  |  | 是 |
| carpentry_hours | 120.0 | <= | 120 | 是 |
| painting_hours | 100.0 | <= | 100 | 是 |
| 目标值复算 |  |  |  | 是 |
