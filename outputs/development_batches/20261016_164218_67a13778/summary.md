# 八题开发基线评测

模式：deepseek；已完成 8/8；自动检查通过 8/8。
已知总tokens：21521；usage未知：0例；未知不计作0，金额以账单为准。
每题一次，不自动重试或修复。固定开发题，不代表保留题泛化、稳定成功率或对照实验效果。
自动通过涵盖数值与部分结构检查；中文含义、单位和假设仍需人工审核。离线模式不计为LLM实验。

| 题号 | 类别 | 结果 | 失败分类 | tokens | 秒 |
|---|---|---|---|---:|---:|
| OPT01 | optimization | pass |  | 2714 | 1.944 |
| OPT02 | optimization | pass |  | 3169 | 3.127 |
| FIT01 | fitting | pass |  | 2591 | 1.581 |
| FIT02 | fitting | pass |  | 2616 | 1.730 |
| DYN01 | dynamics | pass |  | 2581 | 1.623 |
| DYN02 | dynamics | pass |  | 2513 | 1.392 |
| NET01 | graph | pass |  | 2720 | 1.997 |
| NET02 | graph | pass |  | 2617 | 1.643 |

## 失败分析

当前没有自动检查失败。仍需审查语义与评测覆盖边界。

## 文件说明

manifest.json 固定协议、模型名和输入/代码哈希；snapshot/ 保存本轮输入与代码。每题目录先保存原始API响应（不含密钥），再保存求解与评分。results.csv 可用于统计；不依据退出码或optimal状态直接判成功。
失败分类：generation_error（网络/HTTP/响应解析或模型格式）、needs_clarification、unsupported、solver_error、verification_failed、evaluation_failed（原题评分不通过）、evaluator_error（评分器异常）。评分器异常不算模型答错，需单独修复并保留原记录。

## 运行后语义抽查

Codex逐份复核单位、变量描述和假设：FIT01发现1处说明文字警告——模型称“不输出拟合系数”，而本地报告实际展示系数；数值结果及固定一阶协议通过。其余7题未发现实质性语义问题。这不是独立人工双评，也不是完整14分评分。详见 semantic_review.json。原自动结果与原API响应保持不变。
