# BB84 量子密钥分发协议全链路仿真

> 课题三：用 Python 仿真 BB84 协议中的 Alice（发送方）、Bob（接收方）与 Eve（窃听者），
> 演示随机比特/基生成、对基筛选过程，并计算截获-重发攻击下的量子误码率 (QBER)。

[![CI](https://github.com/Canming921/bb84-qkd/actions/workflows/ci.yml/badge.svg)](https://github.com/Canming921/bb84-qkd/actions)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 核心结论

| 信道状态 | 仿真 QBER | 理论值 | 含义 |
|---|---|---|---|
| 无窃听 | `0.00%` | `0` | 筛后密钥完全一致 |
| Eve 全程截获-重发 | `≈25.0%` | `1/4` | 远超 11% 阈值，窃听必被发现 |
| Eve 截获 50% | `≈12.5%` | `p/4` | QBER 随窃听强度线性增长 |

> 误码率 25% 由玻恩定则 $P(k)=|\langle e_k|\psi\rangle|^2$ **涌现**，而非硬编码。
> 完整狄拉克符号推导见 [`docs/PHYSICS.md`](docs/PHYSICS.md)。

---

## 快速开始

```bash
# 1) 安装依赖
pip install -r requirements.txt

# 2) 干净信道（无窃听）
python main.py -n 2048 --seed 7

# 3) 全程截获-重发攻击
python main.py --eve -n 2048 --seed 7

# 4) Eve 只截获一半量子比特
python main.py --eve --p-eve 0.5

# 5) 生成 QBER vs 窃听强度 曲线 (qber_sweep.png)
python main.py --sweep

# 6) 运行测试
pytest -q
```

### 示例输出

```
--- First 24 transmitted qubits (basis reconciliation) ---
idx | A-bit A-basis | B-basis B-result | sifted | error
  0 |   1      Z    |    Z       1      |  kept  |
  1 |   0      X    |    Z       1      |   --   |
 ...
=============== SUMMARY ===============
Qubits transmitted   : 2048
Sifted key length    : 1027  (50.1% retained)
Eavesdropper present : True  (intercepts 100%)
Measured QBER        : 0.2230  (22.30%)
Theoretical QBER     : 0.2500  (25.00%)
QBER exceeds the ~11% security threshold -> eavesdropper detected.
```

---

## 项目结构

```
bb84-qkd/
├── bb84/                # 核心库（模块化）
│   ├── qubit.py         # 态矢量 + 玻恩定则投影测量
│   ├── parties.py       # Alice / Bob / Eve 三角色
│   └── protocol.py      # 全链路编排：传输→筛选→QBER
├── tests/test_bb84.py   # pytest 自动化测试（兼作物理正确性检验）
├── docs/PHYSICS.md       # 物理机制推导（狄拉克符号）
├── main.py              # 命令行演示 + 绘图
├── requirements.txt
├── AI-Collaboration.md  # AI 协同日志
└── .github/workflows/ci.yml   # 持续集成
```

---

## 协议流程

1. **态制备** — Alice 随机选比特 $a$ 与基 $\theta\in\{Z,X\}$，制备对应单量子比特态。
2. **量子传输** — 量子比特经信道送往 Bob；存在 Eve 时被其截获-重发。
3. **测量** — Bob 随机选基测量并记录结果。
4. **对基筛选** — 双方公开比对基（不公开比特值），仅保留基一致的位置 → 筛后密钥。
5. **QBER 估计** — 在筛后密钥上统计不一致比例；超过 ~11% 即判定信道被窃听并丢弃密钥。

## License
MIT
