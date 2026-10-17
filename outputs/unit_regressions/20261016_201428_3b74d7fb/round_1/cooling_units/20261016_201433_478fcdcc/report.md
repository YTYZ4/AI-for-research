# 动态系统建模与求解报告

牛顿冷却模拟

方程：dT/dt = -k(T−T_env)；t=0 时状态为 90.0 celsius。
速率：0.1 1/min；平衡参数（环境温度或容量）：20.0 celsius。
时间区间：[0, 30.0] min；输出101个等距采样点。

假设：液体温度均匀，牛顿冷却定律适用；冷却系数k恒定，环境温度恒定为20摄氏度；模拟从t=0开始，持续0.5小时

单位检查仅核对结构化速率与时间的兼容性；需人工核对原题换算、参数、初值和方程。解析解对照验证数值积分，不证明题意建模正确。

## 原题参数与程序换算

原速率：0.1 1/min（保持不变）。
原时长：0.5 hour。
程序换算：时长 × 60 = 30.0 min。
原题引用：{'initial': '初始90摄氏度', 'equilibrium': '恒温环境20摄氏度', 'rate': '冷却系数k=0.1每分钟', 'duration': '0到0.5小时'}
原始参数见source_model.json，换算审计见unit_conversion.json；引用核对不等于完整语义理解正确。

状态：simulated；末时刻值：23.48509479 celsius。
解析解对照最大绝对误差：1.86767e-08；容差：9e-06。

| 检查 | 通过 |
|---|---|
| initial_condition | 是 |
| analytic_agreement | 是 |
| physical_bounds | 是 |
| monotonic_toward_equilibrium | 是 |

完整轨迹见 trajectory.csv。当前为常参数初值问题，不支持参数估计、事件时间求解或任意微分方程。
