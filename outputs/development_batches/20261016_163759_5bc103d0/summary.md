# 八题开发基线评测

模式：reference；已完成 8/8；自动检查通过 8/8。
已知总tokens：0；usage未知：0例；未知不计作0，金额以账单为准。
每题一次，不自动重试或修复。固定开发题，不代表保留题泛化、稳定成功率或对照实验效果。
自动通过涵盖数值与部分结构检查；中文含义、单位和假设仍需人工审核。离线模式不计为LLM实验。

| 题号 | 类别 | 结果 | 失败分类 | tokens | 秒 |
|---|---|---|---|---:|---:|
| OPT01 | optimization | pass |  | 0 | 0.012 |
| OPT02 | optimization | pass |  | 0 | 0.002 |
| FIT01 | fitting | pass |  | 0 | 0.003 |
| FIT02 | fitting | pass |  | 0 | 0.003 |
| DYN01 | dynamics | pass |  | 0 | 0.003 |
| DYN02 | dynamics | pass |  | 0 | 0.003 |
| NET01 | graph | pass |  | 0 | 0.001 |
| NET02 | graph | pass |  | 0 | 0.001 |

## 失败分析

当前没有自动检查失败。仍需审查语义与评测覆盖边界。

## 文件说明

manifest.json 固定协议、模型名和输入/代码哈希；snapshot/ 保存本轮输入与代码。每题目录先保存原始API响应（不含密钥），再保存求解与评分。results.csv 可用于统计；不依据退出码或optimal状态直接判成功。
失败分类：generation_error（网络/HTTP/响应解析或模型格式）、needs_clarification、unsupported、solver_error、verification_failed、evaluation_failed（原题评分不通过）、evaluator_error（评分器异常）。评分器异常不算模型答错，需单独修复并保留原记录。
