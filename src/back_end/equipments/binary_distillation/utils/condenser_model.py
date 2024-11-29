from abc import abstractmethod
from copy import deepcopy

from . import CompositionInput


class CondenserModel:
    
    @abstractmethod
    def solve(self, C: CompositionInput) -> CompositionInput:
        ...

class TotalCondenser(CondenserModel):

    def solve(self, C: CompositionInput) -> CompositionInput:
        
        new_C = deepcopy(C)
        new_C.Yd = C.Xd
        return new_C # Xd == Yd
    
class PartialCondenser(CondenserModel):

    def solve(self, C: CompositionInput) -> CompositionInput:
        ... # Sabe-se Yd -> Deve-se calcular 