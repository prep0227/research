# deploy/cpp — 嵌入式 ADMM 求解器（P3 部署就绪）

`mpc_solver.hpp`：header-only C++17 稠密 ADMM 盒约束 QP 求解器，无外部依赖
（手写 Cholesky + ADMM），可直接嵌入工控机/MCU 侧 C++ 项目。

## 用法
```cpp
#include "mpc_solver.hpp"
// min 0.5 u' H u + g' u  s.t. lb <= u <= ub
mpc::AdmmQp qp(H, g, lb, ub, /*rho=*/2.0, /*iters=*/60);
std::vector<double> u(H_size, 0.0);
qp.solve(u);              // warm start via u
```
与 Python `sim/controllers.py` 的 `ADMMSolver` 算法一致（同一 `H=AᵀA, g=−Aᵀc` 构造）。

## 测试
```bash
g++ -O2 -std=c++17 test_mpc_solver.cpp -o test_mpc_solver && ./test_mpc_solver
```
覆盖：非活跃约束 → 与无约束最小二乘一致；活跃约束 → 可行且目标不增。

## 集成到自瞄（P3）
1. 在主机侧把 MPC 的 `A,c`（由延迟感知预测矩阵 `T,b` 构造）填入 `H,g`。
2. 每控制周期调用 `solve()`（P99 预期 <1ms @36 维，远优于 Python 4.9ms）。
3. 与 `tools/delay_profiler/` 的 `latency_profile.yaml` 配合设置 `d_steps`（输入延迟步数）。
