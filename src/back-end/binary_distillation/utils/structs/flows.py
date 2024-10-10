from typing import Optional



class InputFlowns:

    def __init__(
            self, 
            *, 
            Fs: list[Optional[float | int]],                   # Inlet flows
            D: Optional[float | int],                          # Top outlet flow 
            B: Optional[float | int],                          # Bottom outlet flow
            Ss: Optional[list[Optional[float | int]]] = None   # Outlet flow
        ) -> None:

        self.Fs = Fs
        self.D  = D
        self.B  = B
        self.Ss = Ss

class SolvedFlowns:

    def __init__(
            self, 
            *, 
            Fs: list[float | int],          # Inlet flows
            D: float | int,                 # Top outlet flow 
            B: float | int,                 # Bottom outlet flow
            Ss: Optional[list[float | int]] # Outlet flow
        ) -> None:

        self.Fs = Fs
        self.D  = D
        self.B  = B
        self.Ss = Ss
    
    def __str__(self) -> str:
        return f"Comp:\n\tFs - {self.Fs}\n\tD  - {self.D}\n\tB  - {self.B}\n\tSs - {self.Ss}"