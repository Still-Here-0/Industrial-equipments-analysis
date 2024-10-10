from typing import Optional
from math import exp



class Antoine:

    def __init__(self, A: Optional[float], B: Optional[float], C: Optional[float]) -> None:
        
        self.A = A
        self.B = B
        self.C = C

    def get_pressure(self, T: float):
        assert T > 0
    
        if self.A is not None and self.B is not None and self.C is not None:
            return exp(self.A - self.B/(T + self.C))

        raise Exception(f"No Antoine data {self.A=}, {self.B=}, {self.C=}")