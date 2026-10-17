# 正实数容量边界重复评测

原始通过36/36；格式修复后累计36/36；含护栏最终36/36。
已知tokens 132310；usage未知0。

| 场景 | 通过次数 |
|---|---:|
| zero | 3/3 |
| negative | 3/3 |
| missing | 3/3 |
| fraction | 3/3 |
| small | 3/3 |
| zero_initial | 3/3 |
| above_capacity | 3/3 |
| above_paraphrase | 3/3 |
| above_symbols | 3/3 |
| above_reordered | 3/3 |
| equal_capacity | 3/3 |
| near_above | 3/3 |

每场景3次独立请求，无重试，固定开发边界；不能证明长期稳定或保留题泛化。追问文字规则另行人工复核，原始响应保留；未覆盖的措辞可能误判。
