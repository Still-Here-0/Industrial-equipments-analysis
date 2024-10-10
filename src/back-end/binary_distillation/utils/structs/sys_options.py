from ..gekko_utils import init_gekko, get_value
from ..utils import get_eq_data
from typing import Optional
from enum import Enum
# TODO: refedine names

class CondenserType(Enum):
    
    Partial = 0       # TODO: NOT IMPLEMENTED
    Total = 1

class BoilerType(Enum):
    
    Partial = 0       # TODO: NOT IMPLEMENTED
    Total = 1

class EqType(Enum):

    Antoine = 0         # TODO: NOT IMPLEMENTED
    EqCurve = 1
    PengRobinson = 2    # TODO: NOT IMPLEMENTED

class System: # TODO: All vars must be inside system

    def __init__(
            self,
            CondState: CondenserType,
            RefeState: BoilerType,
            eq_curve: EqType
        ) -> None:
        
        self._cond_state = CondState
        self._refe_state = RefeState
        self._eq_curve = eq_curve

    # region PUBLIC
    def get_eq_data(self, *, xi:Optional[float]=None, yi:Optional[float]=None) -> tuple[int | float, int | float, int | float]:
        assert xi is not None or yi is not None
        assert xi is None or yi is None
        
        if self._eq_curve == EqType.EqCurve:
            Xi, Yi, alpha = self._get_eq_data_by_curve(xi, yi)
        elif self._eq_curve == EqType.Antoine:
            raise Exception(f"Type not implemented")
        elif self._eq_curve == EqType.PengRobinson:
            raise Exception(f"Type not implemented")

        else:
            raise Exception(f"No equation type mached with {self._eq_curve}")

        return get_value(Xi), get_value(Yi), get_value(alpha)

    def get_avg_alpha(self):

        xs = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        alphas = []

        for xi in xs:
            _, _, alpha = self.get_eq_data(xi=xi)
            alphas.append(alpha)

        return sum(alphas)/len(alphas)

    # endregion 

    # region PRIVATE

    def _get_eq_data_by_curve(self, xi:Optional[float], yi:Optional[float]):
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

    # endregion

if __name__ == "__main__": # TODO: can not be tested here
    s = System(CondenserType.Total, BoilerType.Total, EqType.EqCurve)

    print("Eq. test 1:", s.get_eq_data(xi=0.5))
    print("Eq. test 2:", s.get_eq_data(xi=0.98))
    print("Eq. test 3:", s.get_eq_data(yi=0.73))
    print("Eq. test 4:", s.get_eq_data(yi=0.3))
