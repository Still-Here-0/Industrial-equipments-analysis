from .utils import ColumnInput, CompositionInput, ChargeInput, FlowInput, SolvedFlow, SolvedComposition
from ...sys_utils.gekko_utils import init_gekko, get_value
from ...sys_utils import EquilibriumModel, get_eq_data
from ...systems.binary_system import BinarySystem

from scipy.optimize import root_scalar, minimize_scalar
import matplotlib.pyplot as plt
from logging import Logger
import pandas as pd
import numpy as np
import math

class BinaryDistillation(BinarySystem):
    
    def __init__(
            self,
            log: Logger,
            column_input: ColumnInput, 
            composition_input: CompositionInput,
            charge_input: ChargeInput,
            flow_input: FlowInput,
            eq_model: EquilibriumModel,
            correlacao: float
        ) -> None:
        super().__init__(log, eq_model)

        # INIT
        self.column_input = column_input
        self.composition_input = composition_input
        self.charge_input = charge_input
        self.flow_input = flow_input
        self.corr = correlacao

        # 0
        self.solved_composition: SolvedComposition
        self.solved_flow: SolvedFlow

        # 1
        self.R_teo: float
        
        # 2
        self.R_op: float
        self.ang_coef_s: list[float | int]
        self.lin_coef_s: list[float | int]
        self.X_sec_s: list[float | int]
        self.Y_sec_s: list[float | int]

        # 3
        self.Xs: list[float | int]
        self.Ys: list[float | int]
        self.num_teo_stages: float

        # Real
        self.perc_efficiency: float
        self.num_real_stages: float

        # Optimization
        self.gekko_stages: float | int
        self.mini_opt: dict
        self.root_opt: dict

    def solve(self):
        super().solve()

        self.composition_input = self.column_input.solve_for_preriferics(self.composition_input)

        # Initial
        self._balance()
        self._min_reflux_ratio()
        
        # Solving for R_op
        (self.R_op, self.X_sec_s, self.Y_sec_s, self.ang_coef_s, self.lin_coef_s) = self._section_fase(self.corr)
        (self.Xs, self.Ys, self.num_teo_stages) = self._stage_fase(self.X_sec_s, self.Y_sec_s, self.ang_coef_s, self.lin_coef_s)

    def real_stages(self, vicosity_A: float, vicosity_B: float):
        """
        Where A is the componente with higher volatility than B
        OBS: Same compenente that Zf refers
        """
        assert hasattr(self, "num_teo_stages")

        avg_zf = sum(self.solved_composition.Zfs)/len(self.solved_composition.Zfs)

        mix_viscosity = avg_zf*vicosity_A + (1 - avg_zf)*vicosity_B

        avg_alpha = self.equilibrium_model.get_avg_alpha()

        self.perc_efficiency = 49.2*(avg_alpha*mix_viscosity)**(-0.245)

        self.num_real_stages = self.num_teo_stages/(self.perc_efficiency/100)

    def plot_result(self):
        eq_x, eq_y = get_eq_data()
        engine = init_gekko(2)
        par = engine.Param(value=np.linspace(0, 1))
        v = engine.Var()
        engine.cspline(par, v, eq_x, eq_y)
        engine.solve(disp=False)


        plt.plot(par, v, 'b:', label='Eq. curve') # type: ignore
        plt.plot(eq_x, eq_y, 'g.', label='Eq. data')
        plt.plot([0, 1], [0, 1], 'k--', label="Suport line")

        last_x_sec = 1
        for R, (ang, lin, x_sec) in enumerate(zip(self.ang_coef_s, self.lin_coef_s, self.X_sec_s)):
            r_x = np.linspace(x_sec, last_x_sec)
            r_y = ang*r_x + lin
            plt.plot(r_x, r_y, '--', label=f"R{R}")
            last_x_sec = x_sec

        plt.plot(self.Xs, self.Ys, 'r-', label="Operation points")
        plt.title(f"R_rop = R_rmin*{self.corr:.3f} -> Stages: {self.num_teo_stages:.3f}")
        plt.xlabel("X (%)")
        plt.ylabel("Y (%)")
        plt.legend()
        plt.grid()
        plt.show()

    def opt_reflux(self, CAPEX_math_equation: str, OPEX_math_equation: str):
        """
        Optimize the correlation between teoricial reflux and operational reflux

        CAPEX: A string that represents a function where 'n' is the number of stages in the tower
        
        OPEX: A string that represents a function where 'n' is the number of stages in the tower
        """
        assert len(self.solved_flow.Fs) == 1 and len(self.solved_composition.Zfs) == 1 and len(self.charge_input.beta_fzs) == 1
        assert sum(self.solved_flow.Ss) == 0 and sum(self.solved_composition.Xss) == 0 and self.charge_input.beta_ss is None

        engine = init_gekko(3)
        
        n = engine.Var(value=self.num_teo_stages, lb=1, ub=100)

        operations = [
            "abs",
            "sum",
            "sin",
            "cos",
            "tan",
            "exp",
            "asin",
            "acos",
            "atan",
            "sinh",
            "cosh",
            "atanh",
            "log",
            "log10",
            "sqrt",    
        ]
        for operation in operations:
            CAPEX_math_equation = CAPEX_math_equation.replace(operation, f"engine.{operation}")
            OPEX_math_equation = OPEX_math_equation.replace(operation, f"engine.{operation}")
            
            if operation not in ["sum", "abs"]:
                CAPEX_math_equation = CAPEX_math_equation.replace(operation, f"math.{operation}")
                OPEX_math_equation = OPEX_math_equation.replace(operation, f"math.{operation}")

        CAPEX = engine.Intermediate(eval(CAPEX_math_equation))
        OPEX = engine.Intermediate(eval(OPEX_math_equation))

        engine.Minimize(CAPEX + OPEX)
        engine.solve(False)

        self.gekko_stages = get_value(n)

        # f(corr) -> plate_number {if plate_number == opt_plate_number: corr => opt_corr}
        def _optimization_f(corr: float):
            (_, X_sec_s, Y_sec_s, ang_coef_s, lin_coef_s) = self._section_fase(corr)
            (_, _, num_teo_stages) = self._stage_fase(X_sec_s, Y_sec_s, ang_coef_s, lin_coef_s)
            return num_teo_stages

        # find minimum value where f(corr) -> result_plate_number -> price
        def mini_f(corr: float) -> float:
            num_plates = str(_optimization_f(corr))
            return eval(CAPEX_math_equation.replace("n", num_plates)) + eval(OPEX_math_equation.replace("n", num_plates))
        
        mini_res = minimize_scalar(mini_f, bounds=(1.001, 10))
        self.mini_opt = {
            "corr": mini_res.x,                         #type: ignore
            "stages": _optimization_f(mini_res.x),      #type: ignore
            "price": mini_res.fun,                      #type: ignore
        }

        # find root with f(corr) -> {result_plate_number - opt_plate_number}
        root_f = lambda corr: self.gekko_stages - _optimization_f(corr)
        root_res = root_scalar(root_f, bracket=[1.001, 10], method='brentq')
        self.root_opt = {
            "corr": root_res.root,                          #type: ignore
            "stages": _optimization_f(root_res.root),       #type: ignore
            "price": mini_res.fun,                          #type: ignore
        }

    # region Private

    def _balance(self):
        engine = init_gekko()

        B   = engine.Var(lb=0)       if self.flow_input.B  is None else engine.Const(self.flow_input.B)    #type: ignore
        Xb  = engine.Var(lb=0, ub=1) if self.composition_input.Xb is None else engine.Const(self.composition_input.Xb)   #type: ignore
        D   = engine.Var(lb=0)       if self.flow_input.D  is None else engine.Const(self.flow_input.D)    #type: ignore
        Xd  = engine.Var(lb=0, ub=1) if self.composition_input.Xd is None else engine.Const(self.composition_input.Xd)   #type: ignore

        if self.flow_input.Fs is not None and self.composition_input.Zfs is not None:
            Fs  = [engine.Var(lb=0)       if Fi  is None else engine.Const(Fi)  for Fi  in self.flow_input.Fs ] #type: ignore
            Zfs = [engine.Var(lb=0, ub=1) if Xfi is None else engine.Const(Xfi) for Xfi in self.composition_input.Zfs] #type: ignore
        else:
            Fs  = [engine.Const(0)]
            Zfs = [engine.Const(0)]

        if self.flow_input.Ss is not None and self.composition_input.Xss is not None:
            Ss  = [engine.Var(lb=0)       if Si  is None else engine.Const(Si)  for Si  in self.flow_input.Ss ] #type: ignore
            Xss = [engine.Var(lb=0, ub=1) if Xsi is None else engine.Const(Xsi) for Xsi in self.composition_input.Xss] #type: ignore
        else:
            Ss  = [engine.Const(0)]
            Xss = [engine.Const(0)]

        flow_in  = engine.Intermediate(engine.sum(Fs))
        flow_out = engine.Intermediate(engine.sum(Ss) + D + B)

        comp_flow_in = engine.Intermediate(engine.sum([Fi*xi for Fi, xi in zip(Fs, Zfs)]))
        comp_flow_out = engine.Intermediate(
            engine.sum([Si*xi for Si, xi in zip(Ss, Xss)]) + D*Xd + B*Xb
        )

        engine.Equation(flow_in == flow_out)
        engine.Equation(comp_flow_in == comp_flow_out)

        engine.solve(disp=False)

        self.solved_flow = SolvedFlow( 
            Fs = [get_value(Fi) for Fi in Fs],
            D  = get_value(D),
            B  = get_value(B),
            Ss = [get_value(Si) for Si in Ss],
        )

        self.solved_composition = SolvedComposition(
            Zfs = [get_value(Zfi) for Zfi in Zfs],
            Xd  = get_value(Xd),
            Xb  = get_value(Xb),
            Xss = [get_value(Xsi) for Xsi in Xss],
            Yd  = get_value(self.composition_input.Yd)
        )

    def _min_reflux_ratio(self):
        
        R_teo = float('-inf')

        Xf: float | int
        Yf: float | int

        for Zf, beta_f in zip(self.solved_composition.Zfs, self.charge_input.beta_fzs):
            
            Xf, Yf, _ = self.equilibrium_model.get_XYA_from_Z(Zf, beta_f)

            R_teo_new = (self.solved_composition.Yd - Yf)/(Yf - Xf)

            if R_teo_new > R_teo:
                R_teo = R_teo_new
        
        self.R_teo = R_teo

    def _section_fase(self, corr: float) -> tuple[float, list[float], list[float], list[float], list[float]]:
        assert hasattr(self, "R_teo")

        R_op = self.R_teo*corr

        # First stage

        stage = 0
        Ls: list[float | int] = [R_op*self.solved_flow.D]
        Vs: list[float | int] = [self.solved_flow.D*(R_op + 1)]
        in_and_outs: list[float | int] = [-self.solved_flow.D*self.solved_composition.Yd]
        
        ang_coef_s = [Ls[0]/Vs[0]]
        lin_coef_s = [-(1/Vs[0])*sum(in_and_outs[:1])]

        # Outlet stages
        if self.solved_flow.Ss is not None and self.charge_input.beta_ss is not None and self.solved_composition.Xss is not None:
            for Si, Xsi, beta_sxi in zip(self.solved_flow.Ss, self.solved_composition.Xss, self.charge_input.beta_ss):
                
                Ls.append(Ls[stage] - (1 - beta_sxi)*Si)
                Vs.append(Vs[stage] + beta_sxi*Si)
                
                stage += 1
                ang_coef_s.append(Ls[stage]/Vs[stage])
                in_and_outs.append(-Si*Xsi)
                lin_coef_s.append(-(1/Vs[stage])*sum(in_and_outs[:stage + 1]))
        
        # Inlet stages
        for Fi, Zfi, beta_fzi in zip(self.solved_flow.Fs, self.solved_composition.Zfs, self.charge_input.beta_fzs):
                
            Ls.append(Ls[stage] + (1 - beta_fzi)*Fi)
            Vs.append(Vs[stage] - beta_fzi*Fi)
            
            stage += 1
            ang_coef_s.append(Ls[stage]/Vs[stage])
            in_and_outs.append(Fi*Zfi)
            lin_coef_s.append(-(1/Vs[stage])*sum(in_and_outs[:stage + 1]))
        
        X_sec_s = []
        Y_sec_s = []

        intersection = 1
        while intersection <= stage:
            X_sec_s.append((Vs[intersection]*sum(in_and_outs[:intersection]) - Vs[intersection - 1]*sum(in_and_outs[:intersection + 1]))/(Ls[intersection - 1]*Vs[intersection] - Ls[intersection]*Vs[intersection - 1]))

            Y_sec_s.append((Ls[intersection]*sum(in_and_outs[:intersection]) - Ls[intersection - 1]*sum(in_and_outs[:intersection + 1]))/(Ls[intersection - 1]*Vs[intersection] - Ls[intersection]*Vs[intersection - 1]))

            intersection += 1
        
        Y_sec_s.append(self.solved_composition.Xb)
        X_sec_s.append(self.solved_composition.Xb)

        df = pd.DataFrame({'X': X_sec_s, 'Y': Y_sec_s, 'ang': ang_coef_s, 'lin': lin_coef_s})
        df.sort_values('X')

        X_sec_s: list[float] = list(df['X'])
        Y_sec_s: list[float] = list(df['Y'])
        ang_coef_s: list[float] = list(df['ang'])
        lin_coef_s: list[float] = list(df['lin'])

        return R_op, X_sec_s, Y_sec_s, ang_coef_s, lin_coef_s

    def _stage_fase(
            self, 
            X_sec_s: list[float], 
            Y_sec_s: list[float],
            ang_coef_s: list[float],
            lin_coef_s: list[float]
        ) -> tuple[list[float], list[float], float]:
        
        for xi, yi in zip(X_sec_s, Y_sec_s):

            _, y_eq, _ = self.equilibrium_model.get_XYA_from_XY(xi=xi)

            if y_eq < yi:
                self.log.error("System PINCHED")
                return [], [], 0
        
        Xs = [self.solved_composition.Xd]
        Ys = [self.solved_composition.Xd]
        num_teo_stages = 0

        while True:

            Xi, _, _ = self.equilibrium_model.get_XYA_from_XY(yi=Ys[-1])
            Yi = Ys[-1]

            Xs.append(get_value(Xi))
            Ys.append(Yi)
            num_teo_stages += 1

            for id, X_sec_i in enumerate(X_sec_s):

                if Xi >= X_sec_i:
                    Xi = Xs[-1]
                    Yi = lin_coef_s[id] + ang_coef_s[id]*Xi
                    Ys.append(Yi)
                    Xs.append(Xi)
                    break
            else:
                Xi = Xs[-1]
                Yi = lin_coef_s[id] + ang_coef_s[id]*Xi
                Ys.append(Yi)
                Xs.append(Xi)
                break
        
        num_teo_stages -= (X_sec_s[-1] - Xs[-2])/(Xs[-3] - Xs[-2])

        return Xs, Ys, num_teo_stages

    # endregion