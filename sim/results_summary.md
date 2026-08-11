# Phase-2/3 Simulation Results (v0.3, ADMM solver)

Config: dt=0.02s, T=6.0s, H=18, tau_fire=0.08s, tau_vision=0.03s, tau_gimbal=0.06s, estimator=IMM(CV+CT), solver=ADMM, seeds=10, wall=0s

## 1. Primary matrix (hit_rate, mean over 10 seeds)

| scenario | delay | B0 | B1 | Ours | ours_vs_B0 (pp, p, d) | ours_vs_B1 (pp, p, d) |
|---|---|---|---|---|---|---|
| line | fixed | 0.076 | 0.227 | 0.500 | +42.4pp p=0.000 d=+3.90 | +27.3pp p=0.000 d=+2.14 |
| line | gamma | 0.086 | 0.219 | 0.505 | +41.9pp p=0.000 d=+4.35 | +28.6pp p=0.000 d=+2.13 |
| line | drift | 0.057 | 0.106 | 0.450 | +39.3pp p=0.000 d=+4.72 | +34.4pp p=0.000 d=+2.48 |
| circle | fixed | 0.196 | 0.426 | 0.501 | +30.6pp p=0.000 d=+2.75 | +7.6pp p=0.024 d=+0.85 |
| circle | gamma | 0.211 | 0.435 | 0.496 | +28.5pp p=0.000 d=+2.42 | +6.1pp p=0.017 d=+0.92 |
| circle | drift | 0.123 | 0.277 | 0.468 | +34.4pp p=0.000 d=+2.54 | +19.1pp p=0.000 d=+1.74 |
| s | fixed | 0.009 | 0.128 | 0.141 | +13.1pp p=0.000 d=+2.48 | +1.3pp p=0.591 d=+0.18 |
| s | gamma | 0.021 | 0.115 | 0.154 | +13.3pp p=0.002 d=+1.33 | +4.0pp p=0.129 d=+0.53 |
| s | drift | 0.000 | 0.074 | 0.111 | +11.1pp p=0.000 d=+2.01 | +3.8pp p=0.138 d=+0.51 |
| accel | fixed | 0.095 | 0.409 | 0.761 | +66.6pp p=0.000 d=+5.44 | +35.2pp p=0.000 d=+2.91 |
| accel | gamma | 0.134 | 0.408 | 0.773 | +64.0pp p=0.000 d=+3.48 | +36.5pp p=0.000 d=+2.51 |
| accel | drift | 0.082 | 0.148 | 0.713 | +63.1pp p=0.000 d=+3.77 | +56.5pp p=0.000 d=+3.09 |

## 2. B2 zero-delay upper bound (Ours, hit_rate)

| scenario | B2 |
|---|---|
| line | 0.560 |
| circle | 0.587 |
| s | 0.186 |
| accel | 0.815 |

## 3. Ablations (drift mode, hit_rate)

| scenario | Ours(IMM) | A1 no-delay-model(B1) | A2 no-lead | A4 CV-est | A6 no-tighten | A5 CV% |
|---|---|---|---|---|---|---|
| line | 0.450 | 0.106 | 0.064 | 0.450 | 0.408 | 20.2% |
| circle | 0.468 | 0.277 | 0.239 | 0.460 | 0.439 | 17.9% |
| s | 0.111 | 0.074 | 0.118 | 0.111 | 0.104 | 47.2% |
| accel | 0.713 | 0.148 | 0.487 | 0.768 | 0.702 | 15.0% |

> v0.3 说明：Ours=时延感知 MPC(IMM+在线时延估计+ADMM 盒约束+时延不确定性约束收紧)；B1=无时延建模 MPC；B0=Kt+B+PID。
> 出口准则：Ours 在 >=2 类轨迹显著优于 B0/B1 且 P99 求解耗时 < 控制周期。