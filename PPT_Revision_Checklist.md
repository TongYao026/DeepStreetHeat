# PPT 修改清单 (发给负责 PPT 的同学)

这是一份基于最终版学术报告（v4）与当前 PPT 内容的详细核对修改清单。请逐页核对并修改以下文字细节，以防答辩时被老师抓到逻辑漏洞或术语不一致。

---

### 🚨 优先级：最高（逻辑错误，必改）

#### **1. Slide 17: 残差方向的逻辑写反了**
*   **位置**: "Under-Prediction in High-Density Areas" 下方的说明文字。
*   **原句**: Commercial cores exhibit large **negative** residuals, indicating models systematically underestimate...
*   **修改为**: Commercial cores exhibit large **positive** residuals, indicating models systematically underestimate...
*   **修改原因**: 我们的残差公式是 `Residual = True LST - Predicted LST`。如果模型“低估 (underestimate)”了温度，说明真实值比预测值大，那么减出来的残差必须是 **正数 (positive)**。原句写成 negative 在逻辑上是矛盾的，这是老师最容易扣分的硬伤。

---

### 🟡 优先级：中等（术语对齐，避免被问）

#### **2. Slide 10: 特征变量名称混淆**
*   **位置**: "The 'Texture' Factor" 下方的说明文字。
*   **原句**: Higher Image Entropy (**h_std**) — representing complex urban surfaces...
*   **修改为**: Higher Image Entropy (**entropy**) — representing complex urban surfaces...
*   **修改原因**: 在我们的代码和数据中，“图像熵”这个变量名叫 `entropy`，而 `h_std` 是指“色调标准差”。把 Entropy 括注为 `h_std` 是概念混淆。为了和最终报告统一，请改为 `(entropy)`。

#### **3. Slide 12: 同样是特征名称混淆**
*   **位置**: "Texture Sensitivity" 下方的说明文字。
*   **原句**: The impact of Image Texture (**h_std**) confirms that visual clutter contributes si...
*   **修改为**: The impact of Image Texture (**entropy**) confirms that visual clutter contributes si...
*   **修改原因**: 同上，保持全文对复杂度和纹理的统一定义，一律使用 `entropy`。

#### **4. Slide 18: SHAP 术语突然出现**
*   **位置**: "Vegetation Cooling Effects" 下方的说明文字。
*   **原句**: **SHAP values** reveal vegetation indices show non-linear cooling effects...
*   **修改为**: **Partial Dependence Plots (PDP)** reveal vegetation indices show non-linear cooling effects...
*   **修改原因**: 在我们的最终版报告正文中，解释非线性关系的核心方法是 **PDP (部分依赖图)**，并没有专门介绍 SHAP 算法。如果 PPT 里突然冒出一个 SHAP，而方法论没提，评委很可能会追问。改成 PDP 就能和报告里的图 (如图 8) 完美对应。

---

### 🟢 优先级：低（学术严谨性拔高，建议补充）

#### **5. Slide 6: SegFormer 的实验设置说明**
*   **位置**: "Dual-Engine Pipeline" 下方对比深度学习与传统视觉的文字。
*   **建议**: 在这一页用小字（或备注里）补充一句：**"SegFormer-B0 model with ADE20K pre-trained weights (Zero-shot Inference)"**。
*   **补充原因**: 我们的结果是传统视觉 (R²=0.17) 吊打了深度学习 (R²=0.04)。如果不写清楚深度学习是“无微调直接推理 (Zero-shot)”，老师会觉得我们在贬低深度学习。加上这句，就显得我们非常严谨：是因为没有 fine-tuning 且热特征与语义类别不匹配，才导致深度学习在这里表现不佳。

#### **6. Slide 2: 摘要因果推断过于绝对**
*   **位置**: 可以在口头汇报时注意，或者微调 PPT 文字。如果 PPT 某处写了“证明了 POI 导致升温” (Proving that...)。
*   **建议**: 改为 **"Suggesting / Indicating a significant association..."** (表明/提示显著关联)。
*   **修改原因**: 最终版报告已经把“证明了”改成了“表明/提示”，因为相关性不等于因果性，学术汇报用词要留有余地。