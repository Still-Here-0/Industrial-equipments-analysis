from math import exp



class Antoine:

    def __init__(self, A: float, B: float, C: float) -> None:
        
        self.A = A
        self.B = B
        self.C = C

    def get_pressure(self, T: float):
        assert T > 0

        return exp(self.A - self.B/(T + self.C))