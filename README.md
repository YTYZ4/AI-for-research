# 数学建模实验

用大模型把题目转成数学模型，再用本地程序求解和检查。目前支持优化、拟合、动态系统和图网络，命令行助手版本为 **0.11.10**。

现在的重点是研究：**同一份初稿下，程序检查反馈是否比 AI 自查更容易修好错误？** 暂不扩题，也不继续逐条打补丁。

生产计划小实验已完成。两组都修好了三个错误版本，暂未观察到程序反馈的额外收益。这里只用了一个开发题，不能作为新题泛化结论。详见[实验报告](docs/pilot.md)和[实验协议](protocols/pilot_v1.md)。

## 从这里看

| 目录 | 内容 |
|---|---|
| `assistant` | 建模助手、求解器和检查逻辑 |
| `lab/production` | 生产计划双组修复实验 |
| `evaluation` | 开发回归和评分程序 |
| `examples` | 开发题、数据和边界样例 |
| `tests` | 本地测试 |
| `docs` | 计划、报告、评分说明；旧回归报告在 `history` |
| `protocols` | 实验和回归协议 |
| `outputs` | 原始响应、结果、失败记录与冻结快照 |
| `archive` | 前期 A1/A2 材料的可恢复归档 |

## 使用

在项目根目录执行；本机已有 `.venv` 可以直接使用。新安装使用 Python 3.13（本机验证版本）：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
```

自由输入题目（会调用 API）：

```bash
.venv/bin/python -m assistant --backend deepseek --interactive
```

读取问题文件（会调用 API）：

```bash
.venv/bin/python -m assistant --backend deepseek --problem examples/transport/problem.txt
```

[使用说明](assistant/README.md)包含配置与更多输入方式。本机 API 配置保存在项目之外，整理目录不会改变它；密钥不提交 GitHub。

## 检查和实验

本地测试，不调用真实 API：

```bash
.venv/bin/python -m unittest discover -s tests -q
```

生产计划修复实验（固定 48 次真实调用；每次另建结果目录）：

```bash
.venv/bin/python -m lab.production.experiment
```

完整开发回归（会真实调用 API）：

```bash
.venv/bin/python -m evaluation.full
```

[最近实验的证据](outputs/research_pilots/20261017_003738_6f89af40/summary.md)保留每次请求、响应、模型差异和独立评分。程序直接修正与 AI 反馈修复分开统计；历史回归的原始、格式修复后、本地处理后三个口径也不合并。

## 文档与旧材料

- [当前计划](docs/plan.md)、[交付清单](docs/delivery.md)、[题库说明](docs/tasks.md)、[评分规则](docs/scoring.md)
- [历史回归报告](docs/history/README.md)
- [旧 A1/A2 材料及恢复方法](archive/README.md)
- [目录整理说明](docs/layout.md)、[旧路径对应表](docs/paths.json)

原始证据中的批次号、文件名和内容保持原样。它们记录当时的运行环境，不随当前目录改名而改写；阅读旧路径时可查对应表。
