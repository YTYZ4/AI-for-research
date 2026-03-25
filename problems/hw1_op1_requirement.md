# hw1 op1 requirement

目标：实现内容感知的图像缩放，而不是普通 resize/crop。

输入：原图 im，目标尺寸 sz=(target_h, target_w)

输出：缩放后的图像，实验报告，代码

报告必须包含：
1. 算法基本原理
2. 缩小长度/宽度的结果
3. 与 crop / resize 的对比
4. 结果说明

本次暂不做：
1. 放大
2. content amplification
3. 多语言版本

补充说明：
- 本次作业核心是实现 Seam Carving，并在报告中展示算法原理、宽度/高度缩放结果、与截断/伸缩的对比、结果说明。
- 课程提供了 Python 模板，允许用自己的实现，但当前优先使用模板以最快完成基础版。
- Image Enlarging、Content Amplification 等扩展项暂不进入本轮范围，除非基础版全部完成。
