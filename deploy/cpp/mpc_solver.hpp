// mpc_solver.hpp -- header-only dense ADMM solver for box-constrained QP
//   min_u  0.5 u' H u + g' u   s.t.  lb <= u <= ub
// C++17, no external dependencies. For embedded RoboMaster deployment (P3).
// Usage:
//   AdmmQp qp(H, g, lb, ub, rho, iters);
//   qp.solve(u0.data());          // warm start optional
#pragma once
#include <cmath>
#include <cstddef>
#include <vector>
#include <algorithm>

namespace mpc {

class AdmmQp {
public:
    AdmmQp(const std::vector<double>& H, const std::vector<double>& g,
           const std::vector<double>& lb, const std::vector<double>& ub,
           double rho = 2.0, int iters = 60)
        : n_(g.size()), H_(H), g_(g), lb_(lb), ub_(ub), rho_(rho), iters_(iters) {
        // factor L L' = H + rho I (dense Cholesky)
        L_.assign(n_ * n_, 0.0);
        for (std::size_t i = 0; i < n_; ++i) {
            for (std::size_t j = 0; j <= i; ++j) {
                double s = H_[i * n_ + j] + (i == j ? rho_ : 0.0);
                for (std::size_t k = 0; k < j; ++k)
                    s -= L_[i * n_ + k] * L_[j * n_ + k];
                L_[i * n_ + j] = (i == j) ? std::sqrt(std::max(s, 1e-12)) : s / L_[j * n_ + j];
            }
        }
    }

    // u: in = warm start (optional, may be all zeros), out = solution
    void solve(std::vector<double>& u) const {
        std::vector<double> z(u), w(n_, 0.0), tmp(n_), b(n_);
        for (int it = 0; it < iters_; ++it) {
            // b = rho*(z - w) - g
            for (std::size_t i = 0; i < n_; ++i) b[i] = rho_ * (z[i] - w[i]) - g_[i];
            // solve (H + rho I) u = b via Cholesky
            for (std::size_t i = 0; i < n_; ++i) {         // forward: L y = b
                double s = b[i];
                for (std::size_t k = 0; k < i; ++k) s -= L_[i * n_ + k] * tmp[k];
                tmp[i] = s / L_[i * n_ + i];
            }
            for (std::size_t i = n_; i-- > 0;) {           // backward: L' u = y
                double s = tmp[i];
                for (std::size_t k = i + 1; k < n_; ++k) s -= L_[k * n_ + i] * u[k];
                u[i] = s / L_[i * n_ + i];
            }
            for (std::size_t i = 0; i < n_; ++i) z[i] = std::clamp(u[i] + w[i], lb_[i], ub_[i]);
            for (std::size_t i = 0; i < n_; ++i) w[i] += u[i] - z[i];
        }
        u.swap(z);
    }

    double objective(const std::vector<double>& u) const {
        double v = 0.0;
        for (std::size_t i = 0; i < n_; ++i) {
            double hu = 0.0;
            for (std::size_t j = 0; j < n_; ++j) hu += H_[i * n_ + j] * u[j];
            v += 0.5 * u[i] * hu + g_[i] * u[i];
        }
        return v;
    }

    std::size_t n() const { return n_; }
private:
    std::size_t n_;
    std::vector<double> H_, g_, lb_, ub_, L_;
    double rho_;
    int iters_;
};

} // namespace mpc
