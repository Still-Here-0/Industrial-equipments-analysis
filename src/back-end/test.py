from utils.structs import InputOtherParam, InputCompositions, InputFlowns
from min_reflux_ratio import min_reflux_ratio
from utils.gekko_utils import init_gekko
from section_fase import section_fase
from stage_fase import stages_points
import matplotlib.pyplot as plt
from balance import total_mass
from utils import get_eq_data
import numpy as np


O = InputOtherParam(beta_zs=[0], beta_d=0, beta_b=1)
C = InputCompositions(Zfs=[0.5], Xd=0.95, Xb=0.05)
Q = InputFlowns(Fs=[1000], D= None, B= None)

Q, C = total_mass(Q, C)

R_min = min_reflux_ratio(C, O, True)

corrs = [1.5, 1.4, 1.3, 1.2]

fig, axs = plt.subplots(2, 2)
coords = [[0, 0], [0, 1], [1, 0], [1, 1]]

for corr, c in zip(corrs, coords):
    X_sec, ang_coef, lin_coef = section_fase(R_min, corr, Q, O, C)

    Xs, Ys = stages_points(X_sec, lin_coef, ang_coef, C)

    eq_x, eq_y = get_eq_data()
    engine = init_gekko(2)
    par = engine.Param(value=np.linspace(0, 1))
    v = engine.Var()
    engine.cspline(par, v, eq_x, eq_y)
    engine.solve(disp=False)

    r1_x = np.linspace(0.5, 1) 
    r1_y = ang_coef[0]*r1_x + lin_coef[0]
    r2_x = np.linspace(0, 0.5) 
    r2_y = ang_coef[1]*r2_x + lin_coef[1]

    axs[c[0], c[1]].plot(par, v, 'b:', label='Eq. curve') # type: ignore
    axs[c[0], c[1]].plot(eq_x, eq_y, 'g.', label='Eq. data')
    axs[c[0], c[1]].plot([0, 1], [0, 1], 'k--', label="Suport line")
    axs[c[0], c[1]].plot(r1_x, r1_y, 'm--', label="R1")
    axs[c[0], c[1]].plot(r2_x, r2_y, 'y--', label="R2")
    axs[c[0], c[1]].plot(Xs, Ys, 'r-', label="Operation points")
    axs[c[0], c[1]].set_title(f"R_rop = R_rmin*{corr}")
    axs[c[0], c[1]].grid()

plt.legend()
plt.show()