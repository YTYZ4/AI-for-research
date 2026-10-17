# 前期材料

这里保存 A1/A2 阶段的代码、结果、试用表、过程记录和汇报材料。它们属于前期探索，不混入当前建模助手的实验结果。

| 文件 | 内容 |
|---|---|
| `a1.tar.gz` | A1 原始实验输出 |
| `a2.tar.gz` | 旧课程工程和 `solutions` 中的代码与结果 |
| `a2_runs.tar.gz` | A2 原始实验输出 |
| `notes.tar.gz` | 旧报告、任务卡、提示词、指标、试用包、运行记录和汇报文件 |
| `index.json` | 归档内文件的原路径和 SHA-256 |

归档内保留原目录结构，压缩后逐文件核对过内容。需要查旧材料时，解压到另一个目录，不要覆盖当前项目：

```bash
mkdir -p /tmp/a1a2
for file in archive/*.tar.gz; do tar -xzf "$file" -C /tmp/a1a2; done
```

旧入口在解压目录中的 `run_research_case.py`。旧代码与旧 README 原样保留，所需依赖按当时说明安装。新研究不再从这个入口运行。
