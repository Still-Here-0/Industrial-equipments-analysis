from . import CondenserModel, ReboilerModel, CompositionInput

class ColumnInput:

    def __init__(
            self,
            condenser_model: type[CondenserModel],
            boiler_model: type[ReboilerModel],
        ) -> None:
        
        self._conden = condenser_model()
        self._boiler = boiler_model()
    
    def solve_for_preriferics(self, C: CompositionInput) -> CompositionInput:

        C = self._conden.solve(C)
        C = self._boiler.solve(C)

        return C
