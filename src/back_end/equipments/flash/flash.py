from back_end.sys_utils.equilibrium_model_types import EquilibriumModel
from ...systems.binary_system import BinarySystem
from .utils import InputInlet, InputOutlet

from logging import Logger
from typing import Optional


class Flash(BinarySystem):
    
    def __init__(
            self, 
            log: Logger, 
            eq_model: EquilibriumModel,
            botton_outlet: InputOutlet,
            top_outlet: InputOutlet,
            inlet: InputInlet,
            beta: Optional[float]
        ) -> None:
        super().__init__(log, eq_model)

        self.b_outlet = botton_outlet
        self.t_outlet = top_outlet
        self.inlet = inlet
        self.beta = beta
    
    def solve(self):
        super().solve()

    def balance(self):
        ...