from utils.gekko_utils import init_gekko, get_value
from utils.structs import SolvedCompositions, InputOtherParam
from utils import get_eq_data

def min_reflux_ratio(C: SolvedCompositions, O: InputOtherParam, eq: bool) -> float:

    R_rmin: float = float('-inf')

    Xf:     float | int
    Yf:     float | int

    for Zf, beta_f in zip(C.Zfs, O.beta_fzs): # TODO: beta must be a array two

        if eq: # alpha can be calculated locally
            Xf, Yf, alpha = inlet_comp_by_eq_curve(Zf, beta_f)
        else: # alpha must be estimated by taking the mean of Antonie equations
            raise Exception("Not implemented yet!") # TODO

        if (C.Xd - Yf)/(Yf - Xf) > R_rmin:
            R_rmin = (C.Xd - Yf)/(Yf - Xf)

    return R_rmin

def inlet_comp_by_eq_curve(
        zf:     float | int, 
        beta_f: float | int
    ) -> tuple[float | int, float | int, float | int]:
    
    x_data, y_data = get_eq_data()

    engine = init_gekko()

    Zf = engine.Const(zf)       # type: ignore
    b  = engine.Const(beta_f)   # type: ignore

    alpha   = engine.Var(lb=0)
    Yf      = engine.Var(lb=0, ub=1)
    Xf      = engine.Var(lb=0, ub=1, value=Zf)

    engine.cspline(Xf, Yf, x_data, y_data)
    engine.Equation(Xf == Yf/(Yf + alpha*(1 - Yf)))
    engine.Equation(Zf == (1 - b)*(Xf) + b*Yf)

    engine.solve(disp=False)

    return get_value(Xf), get_value(Yf), get_value(alpha)

if __name__ == "__main__":

    print("inlet_comp_by_eq_curve TEST")
    # Test 1
    xf, yf, alpha = inlet_comp_by_eq_curve(0.5, 0)
    assert xf == 0.5 and yf == 0.73 and round(alpha, 3) == 2.704 # type: ignore
    print("## Passed T1")

    # Test 2
    xf, yf, alpha = inlet_comp_by_eq_curve(0.4, 0)
    assert xf == 0.4 and yf == 0.65 and round(alpha, 3) == 2.786 # type: ignore
    print("## Passed T2")

    # Test 3
    xf, yf, alpha = inlet_comp_by_eq_curve(0.7, 0.5)
    assert xf == 0.6 and yf == 0.8 and round(alpha, 3) == 2.667 # type: ignore
    print("## Passed T3")
    
    print("\n\nreflux_ratio TEST")
    # Test 1
    c = SolvedCompositions(Zfs=[0.5], Xd=0.95, Yd=None, Xb=0.05, Xss=None)
    o = InputOtherParam(beta_zs=[0], beta_d=0, beta_b=1)
    R_rmin = min_reflux_ratio(c, o, eq=True)
    assert round(R_rmin, 3) == 0.957
    print("## Passed T1")

    # Result
    beta_f = 0
    c = SolvedCompositions(Zfs=[0.5], Xd=0.95, Xb=0.05, Xss=None, Yd=None)
    o = InputOtherParam(beta_zs=[0], beta_d=0, beta_b=1)
    R_rmin = min_reflux_ratio(c, o, eq=True)
    print(f"Result: {R_rmin}")


