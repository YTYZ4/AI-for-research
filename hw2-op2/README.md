# hw2-op2

本目录是 A2 低秩图像修复任务的独立工程本体。

它回答的是：“A2 这个图像修复项目本身怎么运行？”

在主研究仓库里，A2 已收束到 `src/chapter5_rslt.py::rslt_inpainting(...)` 作为主案例。其他章节保留为算法背景、对比实验和报告材料。

## Layout

| path | purpose |
|---|---|
| `src/` | A2 各章节算法代码，主案例是 `chapter5_rslt.py` |
| `run_all.py` | 执行 A2 全部章节实验的入口 |
| `gui.py` | 图形界面 demo 入口 |
| `data/` | 可选自定义图像/视频素材说明 |
| `results/` | A2 工程内部章节实验结果 |
| `report/` | A2 工程自己的 LaTeX/PDF 报告和报告插图 |
| `gui_demos/` | GUI demo 示例输出 |
| `requirements.txt` | pip 依赖 |
| `environment.yml` | conda 环境 |

## Relation To The Main Research Repo

| main repo path | role |
|---|---|
| `hw2-op2/src/chapter5_rslt.py` | A2 主案例 gold reference |
| `solutions/hw2_op2/generated/` | 模型生成的 A2 版本 |
| `solutions/hw2_op2/failure_cases/` | A2 bug-repair benchmark |
| `outputs/hw2_op2/` | A2 fixed protocol、expanded-scope 和 fresh-generation 输出 |
| `metrics/a2_*` | A2 结构化评分和恢复指标 |
| `runs/2026-04-12_run_*a2*` | A2 每次运行记录 |

## Common Commands

```bash
cd hw2-op2
python run_all.py
python gui.py
```

