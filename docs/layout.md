# 目录整理记录

整理日期：2026-10-17。这里只调整结构、名字、路径和文档入口，不改变数学检查规则，不新增API实验。

## 备份

修改前已完整备份到桌面 `AIresearch_backup_20261017_150537`。`project.tar.gz` 包含整个原目录、未提交改动、Git历史和本地环境；`backup.json`记录压缩包哈希。已逐文件核对37847个文件。备份不参与Git提交，后续整理未修改它。

## 新结构

- `assistant`：原 `modeling_assistant`，运行命令改为 `python -m assistant`。
- `lab/production`：原 `research/production_pilot`，运行命令改为 `python -m lab.production.experiment`。
- `evaluation`：保留评分功能，去掉文件名中重复的 `regression`，完整回归入口为 `python -m evaluation.full`。
- `docs`：当前计划、清单、评分和实验报告；历史回归报告集中在 `history`。
- `protocols`：原 `task_cards`，缩短文件名并保留协议版本号。
- `examples`：保留开发题，去掉文件夹名中重复的 `boundaries`。
- `requirements.txt` / `requirements.lock`：依赖范围和已验证的固定版本。
- `archive`：旧 A1/A2 工程、记录、材料与结果压缩归档，恢复方法见其README。

完整改名表见 [paths.json](paths.json)。历史重评分入口会利用该表定位当前文件。

## 删除和保留

直接删除Python缓存、Finder元数据和迁移后空目录。前期材料不是无用数据，移入可恢复归档后才删除原来的散落目录；归档已按原文件哈希核对。桌面完整备份仍保留原始状态。

`.venv`保留以便继续使用。原始API响应、失败证据、批次号、冻结快照及其内部文件名不改写；原题内容和数学参数没有修改。旧记录中的路径是当时路径，需用对应表查当前位置。当前源码已经改名，因此旧快照与当前工作区的源码哈希不同是预期现象；冻结快照自身内容未变。

## 验证与同步

本地测试通过；新CLI入口可加载；当前文档链接检查通过。整理期间没有调用真实API，也没有把新的结果合并到历史统计。发布前检查本机配置密钥未出现在待提交代码、记录或归档中。GitHub提交不包含虚拟环境、缓存或本机密钥配置。
