from .gekko_utils import init_gekko, get_value
from .sys_utils import get_eq_data
from abc import abstractmethod
from typing import Optional
from math import exp

class EquilibriumModel:
    
    def __init__(self) -> None:
        raise Exception("This class must not be initialized")

    @abstractmethod
    def get_XYA_from_Z(
            self,
            zf: float | int, 
            beta_f: float | int
        ) -> tuple[float | int, float | int, float | int]:
        ...
    
    @abstractmethod
    def get_XYA_from_XY(
            self,
            *,
            xi: Optional[float]=None,
            yi: Optional[float]=None,
        ) -> tuple[float | int, float | int, float | int]:
        ...
    
    def get_avg_alpha(self) -> float:
        ...

class IdealSystem(EquilibriumModel): # Antoine + Raoult

    def __init__(
            self, 
            A:tuple[float, float], 
            B: tuple[float, float], 
            C: tuple[float, float]
        ) -> None:
        
        self.A = A
        self.B = B
        self.C = C

    def _get_pressure(self, T: float) -> tuple[float, float]:
        assert T > 0

        P1 = exp(self.A[0] - self.B[0]/(T + self.C[0]))
        P2 = exp(self.A[1] - self.B[1]/(T + self.C[1]))

        return (P1, P2)

class EqGraph(EquilibriumModel):

    def __init__(self) -> None:
        ...
    
    def get_XYA_from_Z(
            self,
            zf: float | int, 
            beta_f: float | int
        ) -> tuple[float | int, float | int, float | int]:
        
        x_data, y_data = get_eq_data()

        engine = init_gekko()

        Zf = engine.Param(zf)
        b  = engine.Param(beta_f)

        alpha   = engine.Var(lb=0)
        Yf      = engine.Var(lb=0, ub=1)
        Xf      = engine.Var(lb=0, ub=1, value=Zf)

        engine.cspline(Xf, Yf, x_data, y_data)
        engine.Equation(Xf == Yf/(Yf + alpha*(1 - Yf)))
        engine.Equation(Zf == (1 - b)*(Xf) + b*Yf)

        engine.solve(disp=False)

        return get_value(Xf), get_value(Yf), get_value(alpha)

    def get_XYA_from_XY(
            self,
            *,
            xi: Optional[float]=None,
            yi: Optional[float]=None,
        ) -> tuple[float | int, float | int, float | int]:
        assert xi is not None or yi is not None
        assert xi is None or yi is None

        x_data, y_data = get_eq_data()

        engine = init_gekko(2)

        Xi  = engine.Var(lb=0, ub=1, value=0.5)
        Yi  = engine.Var(lb=0, ub=1, value=0.5)

        alpha   = engine.Var(lb=0)

        engine.cspline(Xi, Yi, x_data, y_data)
        engine.Equation(Xi == Yi/(Yi + alpha*(1 - Yi)))

        if xi is None:
            engine.Equation(Yi == yi)
        else:
            engine.Equation(Xi == xi)

        engine.solve(disp=False)

        return get_value(Xi), get_value(Yi), get_value(alpha)

    def get_avg_alpha(self) -> float:

        values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

        x_alphas = [self.get_XYA_from_XY(xi=v)[2] for v in values]
        y_alphas = [self.get_XYA_from_XY(yi=v)[2] for v in values]

        alphas = []
        alphas.extend(x_alphas)
        alphas.extend(y_alphas)

        avg_alpha = sum(alphas)/len(alphas)

        return avg_alpha