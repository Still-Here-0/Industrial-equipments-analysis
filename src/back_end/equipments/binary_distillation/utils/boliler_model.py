from abc import abstractmethod
from copy import deepcopy

from . import CompositionInput


class ReboilerModel:
    
    @abstractmethod
    def solve(self, C: CompositionInput) -> CompositionInput:
        ...

class TotalReboiler(ReboilerModel):

    def solve(self, C: CompositionInput) -> CompositionInput:
        ...
    
class PartialReboiler(ReboilerModel):

    def solve(self, C: CompositionInput) -> CompositionInput:
        return C