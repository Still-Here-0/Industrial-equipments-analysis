from utils.structs import SolvedCompositions, System, CondenserType, EqType
from utils.gekko_utils import init_gekko, get_value
from utils import get_eq_data


def stages_points(
        X_sec: list[float | int], 
        Y_sec: list[float | int], 
        lin_coef: list[float | int], 
        ang_coef: list[float | int], 
        C: SolvedCompositions,
        S: System
    ) -> tuple[list[float | int], list[float | int]]:
    
    pinch = check_for_pinch(X_sec, Y_sec, S)

    if pinch:
        print("System PINCHED")
        return [], []
    elif S._cond_state == CondenserType.Total:
        Xs, Ys = solve_for_total_condenser(X_sec, lin_coef, ang_coef, C, S)
    else:               # TODO: Parcial condenser
        ...

    return Xs, Ys

def check_for_pinch(X_sec: list[float | int], Y_sec: list[float | int], S: System):
    
    for xi, yi in zip(X_sec, Y_sec):

        _, y_eq, _ = S.get_eq_data(xi=xi)

        if y_eq < yi:
            return True
    
    return False

def solve_for_total_condenser(
        X_sec: list[float | int],
        lin_coef: list[float | int],
        ang_coef: list[float | int],
        C: SolvedCompositions,
        S: System
    ) -> tuple[list[float | int], list[float | int]]:

    Xs = [C.Xd]
    Ys = [C.Xd]

    while True:

        Xi, _, _ = S.get_eq_data(yi=Ys[-1])
        Yi = Ys[-1]
        Xs.append(get_value(Xi))
        Ys.append(Yi)

        for id, X_sec_i in enumerate(X_sec):

            if Xi >= X_sec_i:
                Xi = Xs[-1]
                Yi = lin_coef[id] + ang_coef[id]*Xi
                Ys.append(Yi)
                Xs.append(Xi)
                break
        else:
            Xi = Xs[-1]
            Yi = lin_coef[id] + ang_coef[id]*Xi
            Ys.append(Yi)
            Xs.append(Xi)
            break

    return Xs, Ys

if __name__ == "__main__":
    from utils.structs import CondenserType, BoilerType, EqType

    X_sec =    [0.5, 0.05]
    Y_sec =    [0.6848214285714286]
    ang_coef = [0.5876288659793814, 1.4123711340206186]
    lin_coef = [0.3917525773195876, -0.020618556701030927]
    c = SolvedCompositions(Zfs= [0.5 ], Xd= 0.95, Xb=0.05,  Xss=None, Yd=0.95)
    s = System(CondenserType.Total, BoilerType.Total, EqType.EqCurve)

    Xs, Ys = stages_points(X_sec, Y_sec, lin_coef, ang_coef, c, s)

    import matplotlib.pyplot as plt
    import numpy as np

    x, y = get_eq_data()
    engine = init_gekko(2)
    par = engine.Param(value=np.linspace(0, 1))
    v = engine.Var()
    engine.cspline(par, v, x, y)
    engine.solve(disp=False)

    r1_x = np.linspace(0.5, 1) 
    r1_y = ang_coef[0]*r1_x + lin_coef[0]
    r2_x = np.linspace(0, 0.5) 
    r2_y = ang_coef[1]*r2_x + lin_coef[1]

    plt.plot(par, v, 'b:', label='spline') # type: ignore
    plt.plot([0, 1], [0, 1], 'k--', label="suporte")
    plt.plot(r1_x, r1_y, 'm--', label="R1")
    plt.plot(r2_x, r2_y, 'y--', label="R2")
    plt.plot(x, y, 'g.', label='data')
    plt.plot(Xs, Ys, 'ro')
    plt.legend()
    plt.grid()
    plt.show()
