// Unit test for AdmmQp: (1) inactive bounds -> matches unconstrained LSQ;
// (2) active bounds -> feasible and objective <= warm start objective.
#include "mpc_solver.hpp"
#include <cstdio>
#include <cmath>
#include <vector>
#include <numeric>

// dense A^T A + A^T c for least-squares problem min ||A u - c||^2
static void build_lsq(std::size_t m, std::size_t n, std::vector<double>& H,
                      std::vector<double>& g, double* solution_ref) {
    std::vector<double> A(m * n), c(m);
    std::srand(42);
    for (auto& x : A) x = (std::rand() % 2000 - 1000) / 1000.0;
    for (auto& x : c) x = (std::rand() % 2000 - 1000) / 1000.0;
    H.assign(n * n, 0.0);
    for (std::size_t i = 0; i < n; ++i)
        for (std::size_t j = 0; j < n; ++j)
            for (std::size_t k = 0; k < m; ++k) H[i * n + j] += A[k * n + i] * A[k * n + j];
    g.assign(n, 0.0);
    for (std::size_t i = 0; i < n; ++i)
        for (std::size_t k = 0; k < m; ++k) g[i] += A[k * n + i] * c[k];
    // reference (unconstrained) via normal equations: u = (A'A)^-1 A'c
    // solve dense 2x2 by hand for n=2
    if (n == 2) {
        double a = H[0], b = H[1], d = H[3], det = a * d - b * b;
        solution_ref[0] = (d * (-g[0]) - b * (-g[1])) / det;
        solution_ref[1] = (a * (-g[1]) - b * (-g[0])) / det;
    }
}

int main() {
    const std::size_t n = 2, m = 4;
    std::vector<double> H, g, lb(n, -1e6), ub(n, 1e6);
    double ref[2];
    build_lsq(m, n, H, g, ref);

    // (1) inactive bounds
    mpc::AdmmQp qp1(H, g, lb, ub, 2.0, 200);
    std::vector<double> u1(n, 0.0);
    qp1.solve(u1);
    double err = std::hypot(u1[0] - ref[0], u1[1] - ref[1]);
    std::printf("inactive-bounds: u=(%.4f, %.4f) ref=(%.4f, %.4f) err=%.2e\n",
                u1[0], u1[1], ref[0], ref[1], err);
    if (err > 1e-3) { std::printf("FAIL inactive\n"); return 1; }

    // (2) active bounds
    std::vector<double> lb2 = {-0.2, -0.2}, ub2 = {0.2, 0.2};
    mpc::AdmmQp qp2(H, g, lb2, ub2, 2.0, 200);
    std::vector<double> u2 = {0.0, 0.0};
    qp2.solve(u2);
    bool feas = true;
    for (std::size_t i = 0; i < n; ++i)
        if (u2[i] < lb2[i] - 1e-9 || u2[i] > ub2[i] + 1e-9) feas = false;
    double obj_sol = qp2.objective(u2), obj_ws = qp2.objective({0.0, 0.0});
    std::printf("active-bounds: u=(%.4f, %.4f) feasible=%d obj_sol=%.4f obj_ws=%.4f\n",
                u2[0], u2[1], (int)feas, obj_sol, obj_ws);
    if (!feas || obj_sol > obj_ws + 1e-9) { std::printf("FAIL active\n"); return 1; }

    std::printf("ALL TESTS PASSED\n");
    return 0;
}
