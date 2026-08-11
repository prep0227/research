# III. Method

This section summarizes the main components (full formulation in the supplementary material).

## A. System architecture

The closed loop is: camera -> detection -> PnP pose -> multi-model estimator -> online latency estimator -> delay-aware MPC (gimbal trajectory) -> firing decision -> serial -> MCU -> gimbal/launcher -> projectile (Fig.~\ref{fig:arch}). The estimator and the MPC are the two blocks we modify relative to the baselines; detection/PnP are shared.

## B. Target state estimation (multi-model, MMAE-style)

We maintain a two-model Bayesian multi-model estimator with a CV Kalman filter on 3D Cartesian state and a CT EKF on the ground-plane state $[x,y,v_x,v_y,\omega]$, weighting model outputs by posterior mode probabilities as in [R16] (MMAE-style: we use the mode-probability weighting without interactive mixing, the common simplification used by RoboMaster trackers). Measurements arrive with delay; each filter tracks its internal time $t_f$ and performs out-of-sequence updates following [R17]: propagate to the measurement time $t_m$, update, propagate to now. The mode probabilities follow a two-state Markov prior, and the predicted position at any horizon is the weighted mixture $\hat p(t+\tau)=\sum_i \mu_i\,\hat p_i(t+\tau)$.

## C. Online latency estimation

A sliding-window estimator records per-segment latency samples (from timestamps, Section V) and maintains the mean $\bar\tau$ and the uncertainty bound $\Delta = p95 - \mathrm{mean}$ for the vision and actuation segments. The vision estimate determines the measurement-time alignment in the filters; the actuation estimate sets the input-delay steps $d=\mathrm{round}(\bar\tau_g/\Delta t)$ of the MPC model; $\Delta$ enters the firing margin (III-E). Table~\ref{tab:de_a} quantifies estimator accuracy (settling time in Table~\ref{tab:de_b}): under fixed delay the causal estimate is within $0.4$~ms MAE; under $\pm15$~ms jitter the per-step error is dominated by the jitter itself (MAE $\approx10$~ms), which $\Delta$ is designed to cover in the firing tightening; under drift the causal estimate lags by $\approx5$~ms (half-window $\times$ drift rate).

## D. Delay-aware MPC

The gimbal is modeled per axis as a double integrator with input delay: $\omega(k+1)=\omega(k)+\Delta t\, u(k-d)$, with acceleration bound $|u|\le u_{\max}$ and rate bound $|\dot\omega|\le \omega_{\max}$. The aim reference is the azimuth/elevation of the predicted target at $t+\tau_{\mathrm{fire}}+\tau_{\mathrm{flight}}(t)$ (lead point). At each control step we solve

\begin{multline*}
\min_{u(0:H-1)} \sum_{k=0}^{H-1} \|r(k)-g(k)\|_Q^2 + \|\Delta u(k)\|_R^2 \\
+ \|r(H-1)-g(H-1)\|_{Q_T}^2
\end{multline*}

subject to the input-delay-augmented linear dynamics and box constraints, using a warm-started ADMM solver for a box-constrained QP (SLSQP fallback). The prediction map $g_{\mathrm{flat}}=T u_{\mathrm{flat}}+b$ is built from the current angles/rates and the delayed-input buffer.

## E. Firing decision with delay-uncertainty tightening

We fire when the predicted pointing error plus a delay-uncertainty margin is below a conservative angular firing threshold:

$$
\|r(0)-g(0)\| + \kappa\,\hat v\,(\Delta_{\mathrm{vision}}+\Delta_{\mathrm{gimbal}})/\mathrm{dist} < \theta_{\mathrm{fire}},
$$

where $\hat v$ is the multi-model speed estimate and $\theta_{\mathrm{fire}}=0.05$~rad is a fixed conservative threshold ($\approx\arctan(\mathrm{armor\_half}/1.6~\mathrm{m})$, so that over the nominal 1--8~m engagement range we fire only on near-tolerance errors). The margin term (with $\kappa=1$) prevents firing when the latency estimate is unreliable (e.g., during drift or jitter). Hits are scored in the metrics against the distance-adaptive tolerance $\theta_{\mathrm{hit}}=\arctan(\mathrm{armor\_half}/\mathrm{dist})$.

## F. Baselines

- **B0** (community baseline): empirical lead $Kt+B$ + cascade PID, mirroring RMVL practice [R1], driven by the same multi-model predictor as our method (a stronger-than-typical baseline). Its lead parameters are set to the ground-truth values (the static lead $B=\tau_{\mathrm{gimbal}}=0.06$~s equals the true nominal actuation latency, and the flight-time term $Kt$ uses the exact projectile flight time $t=\mathrm{dist}/v_{\mathrm{bullet}}$), an oracle, hence favorable, setting for the baseline.
- **B1** (delay-unaware MPC): the same MPC but with the input-delay model disabled (d=0); it uses only nominal latency constants in the aim horizon and does not model the time-varying/uncertain chain [R3].
- **B2** (upper bound): our controller under a zero-delay profile (simulation only).
