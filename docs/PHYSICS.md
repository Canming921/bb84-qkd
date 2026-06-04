# BB84 协议的物理机制解析

> 本文档对应代码核心逻辑，使用狄拉克符号给出态制备、测量与窃听攻击的完整推导。
> 公式在 GitHub 上以 LaTeX 渲染（`$...$` 行内，`$$...$$` 独占行）。

---

## 1. 量子比特与两组互无偏基

BB84 用单量子比特的两组**互无偏基 (mutually unbiased bases, MUB)** 编码信息。

**直角基 / 计算基 (Z, "+")：**

$$|0\rangle = \begin{pmatrix}1\\0\end{pmatrix}, \qquad |1\rangle = \begin{pmatrix}0\\1\end{pmatrix}$$

**对角基 (X, "×")：** 由 Hadamard 变换 $H=\tfrac{1}{\sqrt2}\begin{pmatrix}1&1\\1&-1\end{pmatrix}$ 作用于计算基得到：

$$|+\rangle = H|0\rangle = \tfrac{1}{\sqrt2}\big(|0\rangle+|1\rangle\big), \qquad
|-\rangle = H|1\rangle = \tfrac{1}{\sqrt2}\big(|0\rangle-|1\rangle\big)$$

"互无偏"指任一基的态在另一基下展开时各分量等概率：

$$\big|\langle 0|+\rangle\big|^2 = \big|\langle 1|+\rangle\big|^2 = \big|\langle 0|-\rangle\big|^2 = \big|\langle 1|-\rangle\big|^2 = \tfrac12$$

这是协议安全性的物理根基：**在错误的基下，对方得不到任何关于比特的确定信息。**

代码对应：`bb84/qubit.py` 中的 `KET_0, KET_1, KET_PLUS, KET_MINUS`。

---

## 2. Alice 的态制备

Alice 随机抽取比特 $a\in\{0,1\}$ 与基 $\theta\in\{Z,X\}$，制备：

| 比特 \\ 基 | $Z$ | $X$ |
|:---:|:---:|:---:|
| $a=0$ | $\lvert0\rangle$ | $\lvert+\rangle$ |
| $a=1$ | $\lvert1\rangle$ | $\lvert-\rangle$ |

代码对应：`Alice.transmit()` → `prepare(bit, basis)`。

---

## 3. 投影测量与玻恩定则

在基 $\{|e_0\rangle,|e_1\rangle\}$ 下测量态 $|\psi\rangle$，得到结果 $k$ 的概率由**玻恩定则**给出：

$$P(k) = \big|\langle e_k|\psi\rangle\big|^2, \qquad |\psi\rangle \xrightarrow{\text{测量}} |e_k\rangle$$

测量后态**坍缩**到对应本征态，原始叠加信息不可逆地丢失。

- **基匹配**（测量基 = 制备基）：例如对 $|1\rangle$ 在 $Z$ 基测量，$P(1)=|\langle1|1\rangle|^2=1$，结果**确定**。
- **基失配**：例如对 $|0\rangle$ 在 $X$ 基测量，$P(\pm)=|\langle\pm|0\rangle|^2=\tfrac12$，结果**纯随机**，且态坍缩，原信息丢失。

代码对应：`measure()` 用 `p0 = |<e0|psi>|^2 = abs(np.vdot(e0, state))**2` 严格实现玻恩定则——25% 的误码率是**涌现**出来的，并非写死。

---

## 4. 对基筛选 (Sifting)

传输后，Alice 与 Bob 通过**公开经典信道**比对各自用的基（只公布基，不公布比特值），仅保留基相同的位置，得到**筛后密钥 (sifted key)**。

由于 Bob 独立随机选基，基匹配概率为 $\tfrac12$，故约一半比特被丢弃：

$$\text{筛后密钥长度} \approx \tfrac12 \times n$$

无窃听时，保留下来的位置都满足基匹配 → 测量确定 → **Alice 与 Bob 的筛后密钥完全一致，QBER $=0$**。

代码对应：`run_bb84()` 中 `sift_mask = alice.bases == bob.bases`。

---

## 5. Eve 的截获-重发攻击 (Intercept-Resend)

Eve 不知道 Alice 用的基。她在随机基 $\phi\in\{Z,X\}$ 下测量截获的量子比特（导致坍缩），再把坍缩后的态重新发给 Bob。

**关键约束——不可克隆定理：** 未知量子态无法被完美复制：

$$\nexists\,\hat U:\quad \hat U\,|\psi\rangle|0\rangle = |\psi\rangle|\psi\rangle \quad \forall|\psi\rangle$$

因此 Eve 无法"复制后放行"，只能测量，而测量必然以一定概率扰动态——这正是窃听被探测的物理来源。

代码对应：`Eve.intercept()` —— 测量 → 坍缩 → 重发坍缩态。

---

## 6. QBER 推导（全程窃听）

只在**筛后位置**（Alice 基 = Bob 基 $\equiv\theta$）分析，逐情况计算 Bob 出错概率。

**情形 A：Eve 基 $\phi=\theta$（概率 $\tfrac12$）。**
Eve 在正确基下测量，得到 Alice 的比特并重发正确态，Bob 在 $\theta$ 下测得正确值。
$$P(\text{error}\mid \phi=\theta)=0$$

**情形 B：Eve 基 $\phi\neq\theta$（概率 $\tfrac12$）。**
Eve 重发的是**另一基**的本征态。Bob 在 $\theta$ 下测量该失配态，结果等概率：
$$P(\text{error}\mid \phi\neq\theta)=\tfrac12$$

合并：

$$\boxed{\;\text{QBER} = \tfrac12\cdot 0 + \tfrac12\cdot\tfrac12 = \tfrac14 = 25\%\;}$$

**部分窃听**（Eve 以概率 $p$ 截获）线性缩放：

$$\text{QBER}(p) = \frac{p}{4}$$

代码对应：`BB84Result.theoretical_qber` 返回 $p_{eve}/4$；仿真结果（$n=5\times10^4$）为 $0.2499$ 与 $0.1253$，与理论 $0.25 / 0.125$ 高度吻合。

---

## 7. 安全判据

无噪理想信道下，任何 $\text{QBER}>0$ 都暴露窃听。考虑实际信道噪声，BB84 配合常用纠错+隐私放大方案的安全阈值约为 **11%**：

$$\text{QBER} \lesssim 11\% \;\Rightarrow\; \text{可提取安全密钥}; \qquad \text{QBER} > 11\% \;\Rightarrow\; \text{丢弃密钥}$$

全程截获-重发产生 25% $\gg$ 11%，故该攻击必然被发现——这就是 BB84 "可探测窃听"的核心保证。

---

## 符号—代码对照表

| 物理量 / 步骤 | 数学表达 | 代码位置 |
|---|---|---|
| 计算基 / 对角基 | $\lvert0\rangle,\lvert1\rangle$ / $\lvert\pm\rangle$ | `qubit.py: KET_*` |
| 态制备 | $a,\theta \mapsto \lvert\psi\rangle$ | `qubit.prepare` |
| 玻恩定则测量 | $P(k)=\lvert\langle e_k\rvert\psi\rangle\rvert^2$ | `qubit.measure` |
| 对基筛选 | 保留 $\theta_A=\theta_B$ | `protocol.run_bb84` |
| 截获-重发 | 测量→坍缩→重发 | `parties.Eve.intercept` |
| 误码率 | $\text{QBER}=p/4$ | `protocol`, `theoretical_qber` |
