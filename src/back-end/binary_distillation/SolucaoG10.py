from utils.structs import OtherOperatinalParam, InputCompositions, InputFlowns, System, BoilerType, CondenserType, EqType
from min_reflux_ratio import min_reflux_ratio
from utils.gekko_utils import init_gekko
from section_fase import section_fase
from stage_fase import stages_points
import matplotlib.pyplot as plt
from balance import total_mass
from utils import get_eq_data
import numpy as np


O = OtherOperatinalParam(beta_zs=[0], beta_d=0, beta_b=1)
C = InputCompositions(Zfs=[0.5], Xd=0.95, Xb=0.05)
Q = InputFlowns(Fs=[1000], D= None, B= None)
S = System(CondenserType.Total, BoilerType.Total, EqType.EqCurve)

Q, C = total_mass(Q, C)

print(f"AVG alpha: {S.get_avg_alpha()}")

C.Yd = C.Xd # Condensador total

R_min = min_reflux_ratio(C, O, S)

corrs = [1.5, 1.4, 1.3, 1.2]

fig, axs = plt.subplots(2, 2)
coords = [[0, 0], [0, 1], [1, 0], [1, 1]]

for corr, c in zip(corrs, coords):
    X_sec, Y_sec, ang_coef, lin_coef = section_fase(R_min, corr, Q, O, C)

    Xs, Ys = stages_points(X_sec, Y_sec, lin_coef, ang_coef, C, S)

    eq_x, eq_y = get_eq_data()
    engine = init_gekko(2)
    par = engine.Param(value=np.linspace(0, 1))
    v = engine.Var()
    engine.cspline(par, v, eq_x, eq_y)
    engine.solve(disp=False)


    axs[c[0], c[1]].plot(par, v, 'b:', label='Eq. curve') # type: ignore
    axs[c[0], c[1]].plot(eq_x, eq_y, 'g.', label='Eq. data')
    axs[c[0], c[1]].plot([0, 1], [0, 1], 'k--', label="Suport line")

    last_x_sec = 1
    for R, (ang, lin, x_sec) in enumerate(zip(ang_coef, lin_coef, X_sec)):
        r_x = np.linspace(x_sec, last_x_sec)
        r_y = ang*r_x + lin
        axs[c[0], c[1]].plot(r_x, r_y, '--', label=f"R{R}")
        last_x_sec = x_sec

    axs[c[0], c[1]].plot(Xs, Ys, 'r-', label="Operation points")
    axs[c[0], c[1]].set_title(f"R_rop = R_rmin*{corr}")
    axs[c[0], c[1]].grid()

plt.legend()
plt.show()