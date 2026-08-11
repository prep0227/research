# Methods 数学稿（v0.2 对应实现）

## 1. 目标运动模型与 IMM
- CV：x=[x,y,z,vx,vy,vz]，F=I+dt·[0 I;0 0]。
- CT（地面）：x=[x,y,vx,vy,ω]，
  - vx' = −ω·vy，vy' = ω·vx，ω'≈0；离散精确传播（ω≠0 分支）。
- IMM：两模型加权 μ=[μ_CV, μ_CT]，Markov 转移 p_switch；输出预测 `p̂(t+τ) = Σ μ_i p̂_i(t+τ)`。
- OOSM 延迟测量：滤波器维护内部时间 t_f；测量 z 在 t_meas 有效 → `propagate(t_meas − t_f)` → 更新 → `propagate(t_now − t_meas)`。

## 2. 延迟链
```
τ_total = τ_cam + τ_proc + τ_serial + τ_gimbal + τ_fire + τ_flight
```
- 每段 τ_i(t) = τ̄_i + δ_i(t)，|δ_i| ≤ Δ_i；在线滑动窗估计 τ̄_i、Δ_i = P95 − mean。
- 瞄准参考：`r(t) = az/el( p̂(t + τ_fire + τ_flight(t)) )`。

## 3. 云台模型（离散，dt）
```
g(k+1) = g(k) + dt·ω(k)
ω(k+1) = clip( ω(k) + dt·u(k − d), ±ω_max ),   d = round(τ_gimbal/dt)
|u| ≤ u_max,  |u(k) − u(k−1)| ≤ du_max
```

## 4. MPC（滚动时域）
```
min_{u(0..H−1)}  Σ_k ‖r(k) − g(k)‖²_Q + ‖Δu(k)‖²_R + ‖r(H−1) − g(H−1)‖²_Q_T
s.t. 增广动力学（含输入延迟缓冲），盒约束，斜率约束
```
- 线性预测映射：`g_flat = T·u_flat + b`（b 含当前角度/角速度与延迟缓冲历史）。
- 解析梯度 `∇J = 2(AᵀA u − Aᵀc)`；SLSQP 求解（论文用 ADMM/OSQP 版本报告实时性）。

## 5. 发弹决策
```
fire 当且仅当  ‖r(0) − g(0)‖ + k·σ_impact < θ_hit(距离)，且冷却期/弹药允许
θ_hit = atan(armor_half / dist)
```

## 6. 指标
- 命中率 = hits/shots（真值：仿真=命中几何；真机=裁判系统）。
- 角误差 RMSE = RMS‖ang_diff(g(t), true_azel(t))‖。
- 配对检验：`t = mean(d)/(std(d)/√n)`；效应量 `d = mean(d)/std(d)`。

## 4.1 ADMM 求解器（v0.3，论文版）
QP: `min_u ½uᵀHu + gᵀu s.t. lb ≤ u ≤ ub`，H=2AᵀA, g=−2Aᵀc。
ADMM：`u ← (H+ρI)⁻¹(ρ(z−w)−g)`，`z ← clip(u+w, lb, ub)`，`w ← w+u−z`；热启动（上一拍解平移）。
Python 实现 P99=4.8ms（保守上界；C++/代码生成可到 μs 级）。

## 5.1 时延不确定性约束收紧（v0.3）
fire 条件：`‖r(0)−g(0)‖ + κ·v̂·(Δ_vision+Δ_gimbal)/dist < θ_hit`
其中 Δ_i = P95 − mean（在线滑动窗）；v̂ 为 IMM 速度估计。收紧在延迟漂移/抖动下提供一致的小幅命中率增益（仿真 A6 消融）。

## 1.1 模型集合选择（补充）
- 主配置：IMM{CV, CT}。实现另有 IMM{CV, CT, CA}（CAKF 恒加速度 9 维）。
- 实验：CA 改善 S 形 drift（+5.4pp）但使变速 drift 回退 20pp → 场景依赖，留作自适应模型集未来工作。
