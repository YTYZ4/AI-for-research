# run 002 - template setup

日期：2026-03-25
阶段：官方模板环境与启动验证

## 执行命令
1. conda create -n mm26 python=3.12
2. conda activate mm26
3. pip install numpy matplotlib scikit-image scipy
4. python seam_carving.py

说明：在非交互终端中使用了等价方式 `conda run -n mm26 ...` 执行安装和启动。

## 环境是否成功
- 成功。
- 已创建 conda 环境：mm26（Python 3.12.13）。
- 已安装依赖：numpy、matplotlib、scikit-image、scipy（及其依赖）。

## 模板能不能启动
- 能启动。
- 首次失败原因：缺少 `../figs/original.png`（模板按相对路径读取图片）。
- 处理动作：补齐 `solutions/hw1_op1/figs/` 并复制官方 `figs` 资源。
- 二次启动结果：`seam_carving.py` 进程持续运行且 3 秒内无异常退出，符合 GUI 等待交互状态。

## 实际需要补哪些函数
- Python 模板核心 TODO 仅 1 个：`seam_carve_image(im, sz)`（位于 `solutions/hw1_op1/reference_template/seam_carving.py`）。
- 其余 GUI 交互（滑条、按钮、显示逻辑）已提供。

## 准备先走的最小路径
1. 先支持宽度缩小：循环删除 vertical seam，直到达到 target_w。
2. 高度缩小通过转置复用宽度逻辑，达到 target_h。
3. 先不做放大与扩展功能，先跑通基础版并生成对比结果（seam carving / crop / resize）。
