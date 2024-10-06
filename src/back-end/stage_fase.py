from utils.structs import SolvedFlowns, SolvedCompositions, InputOtherParam
from utils.gekko_utils import init_gekko, get_value
from gekko.gk_operators import GK_Value
from utils import get_eq_data


def number_of_teorical_stages(
        X_sec: list[float | GK_Value], 
        lin_coef: list[float | GK_Value], 
        ang_coef: list[float | GK_Value], 
        C: SolvedCompositions
    ) -> tuple[list[float | GK_Value], list[float | GK_Value]]:
    
    if C.Yd is None:    # Total condenser 
        Xs, Ys = solve_for_total_condenser(X_sec, lin_coef, ang_coef, C)
    else:               # Parcial condenser
        ...

    return Xs, Ys

def solve_for_total_condenser(
        X_sec: list[float | GK_Value],
        lin_coef: list[float | GK_Value],
        ang_coef: list[float | GK_Value],
        C: SolvedCompositions
    ) -> tuple[list[float | GK_Value], list[float | GK_Value]]:

    Xs = [C.Xd]
    Ys = [C.Xd]

    while True:

        Xi, _, _ = eq_curve(None, Ys[-1]) # type: ignore
        Yi = Ys[-1]
        Xs.append(Xi)
        Ys.append(Yi)

        for id, X_sec_i in enumerate(X_sec):

            if Xi > X_sec_i:
                Xi = Xs[-1]
                Yi = lin_coef[id] + ang_coef[id]*Xi
                Ys.append(Yi)
                Xs.append(Xi)
                break
        else:
            break

    return Xs, Ys
    
def eq_curve(xi:float | None, yi:float | None) -> tuple[GK_Value | float, GK_Value | float, GK_Value | float]:
    assert xi is not None or yi is not None
    assert xi is None or yi is None
    
    x_data, y_data = get_eq_data()

    engine = init_gekko(2)

    Xi  = engine.Var(lb=0, ub=1, value=0.5)   #type: ignore
    Yi  = engine.Var(lb=0, ub=1, value=0.5)   #type: ignore

    alpha   = engine.Var(lb=0)

    engine.cspline(Xi, Yi, x_data, y_data)
    engine.Equation(Xi == Yi/(Yi + alpha*(1 - Yi)))

    if xi is None:
        engine.Equation(Yi == yi)
    else:
        engine.Equation(Xi == xi)

    engine.solve(disp=False)

    return get_value(Xi), get_value(Yi), get_value(alpha)

if __name__ == "__main__":
    print("Eq. test 1:", eq_curve(0.5, None))
    print("Eq. test 2:", eq_curve(0.98, None))
    print("Eq. test 3:", eq_curve(None, 0.73))
    print("Eq. test 4:", eq_curve(None, 0.3))

    X_sec = [0.75, 0.05]
    ang_coef = [0.5876288659793814, 1.4123711340206186]
    lin_coef = [0.3917525773195876, -0.020618556701030927]
    c = SolvedCompositions(Zfs= [0.5 ], Xd= 0.95, Xb=0.05,  Xss=None, Yd=None)

    Xs, Ys = number_of_teorical_stages(X_sec, lin_coef, ang_coef, c) # type: ignore

    import matplotlib.pyplot as plt
    import numpy as np

    x, y = get_eq_data()
    engine = init_gekko(2)
    par = engine.Param(value=np.linspace(0, 1))
    v = engine.Var()
    engine.cspline(par, v, x, y)
    engine.solve(disp=False)

    r1_x = np.linspace(0, 1) 
    r1_y = ang_coef[0]*r1_x + lin_coef[0]
    r2_x = np.linspace(0, 1) 
    r2_y = ang_coef[1]*r2_x + lin_coef[1]

    plt.plot(par, v, 'b:', label='spline') # type: ignore
    plt.plot([0, 1], [0, 1], 'k--', label="suporte")
    plt.plot(r1_x, r1_y, 'm--', label="R1")
    plt.plot(r2_x, r2_y, 'y--', label="R2")
    plt.plot(x, y, 'g.', label='data')
    # plt.plot(Xs, Ys, 'ro')
    plt.legend()
    plt.grid()
    plt.show()
