from ..sys_utils import VaporModelType, LiquidModelType, EquilibriumModel
from ..equipments import Equipment
from logging import Logger


class BinarySystem(Equipment):

    def __init__(
            self, 
            log: Logger,
            # vapor_model: VaporModelType,
            # liquid_model: LiquidModelType,
            equilibrium_model: EquilibriumModel,
        ) -> None:

        super().__init__(log)

        self.vapor_model: VaporModelType
        self.liquid_model: LiquidModelType
        self.equilibrium_model = equilibrium_model
