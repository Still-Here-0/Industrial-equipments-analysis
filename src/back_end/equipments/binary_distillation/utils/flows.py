from ....sys_utils import PrintableClass
from typing import Optional


class FlowInput:

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

class SolvedFlow(PrintableClass):

    def __init__(
            self, 
            *, 
            Fs: list[float | int],          # Inlet flows
            D: float | int,                 # Top outlet flow 
            B: float | int,                 # Bottom outlet flow
            Ss: list[float | int] # Outlet flow
        ) -> None:

        self.Fs = Fs
        self.D  = D
        self.B  = B
        self.Ss = Ss
    