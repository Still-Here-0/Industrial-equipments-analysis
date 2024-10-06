from gekko.gk_operators import GK_Value
from typing import Optional


class InputFlowns:

    def __init__(
            self, 
            *, 
            Fs: list[Optional[float | GK_Value]],          # Inlet flows
            D: Optional[float | GK_Value],                 # Top outlet flow 
            B: Optional[float | GK_Value],                 # Bottom outlet flow
            Ss: Optional[list[Optional[float | GK_Value]]] # Outlet flow
        ) -> None:

        self.Fs = Fs
        self.D  = D
        self.B  = B
        self.Ss = Ss

class SolvedFlowns:

    def __init__(
            self, 
            *, 
            Fs: list[float | GK_Value],          # Inlet flows
            D: float | GK_Value,                 # Top outlet flow 
            B: float | GK_Value,                 # Bottom outlet flow
            Ss: Optional[list[float | GK_Value]] # Outlet flow
        ) -> None:

        self.Fs = Fs
        self.D  = D
        self.B  = B
        self.Ss = Ss
    
    def __str__(self) -> str:
        return f"Comp:\n\tFs - {self.Fs}\n\tD  - {self.D}\n\tB  - {self.B}\n\tSs - {self.Ss}"