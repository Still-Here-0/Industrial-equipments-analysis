from gekko.gk_operators import GK_Value
from typing import Optional


class InputCompositions:

    def __init__(
            self, 
            *, 
            Zfs: list[Optional[float | GK_Value]],          # Composition of inlet flows
            Xd:  Optional[float | GK_Value],                # Fluid composition of top outlet flow 
            Xb:  Optional[float | GK_Value],                # Fluid composition of bottom outlet flow
            Xss: Optional[list[Optional[float | GK_Value]]],# Fluid composition of outlet flow
            Yd:  Optional[float] = None,                    # Vapor composition of top outlet flow
        ) -> None:
        
        self.Zfs = Zfs
        self.Xd = Xd
        self.Yd = Yd
        self.Xb = Xb
        self.Xss = Xss

class SolvedCompositions:

    def __init__(
            self, 
            *, 
            Zfs: list[float | GK_Value],          # Composition of inlet flows
            Xd:  float | GK_Value,                # Fluid composition of top outlet flow 
            Xb:  float | GK_Value,                # Fluid composition of bottom outlet flow
            Xss: Optional[list[float | GK_Value]],# Fluid composition of outlet flow
            Yd:  Optional[float],                 # Vapor composition of top outlet flow
        ) -> None:
        
        self.Zfs = Zfs
        self.Xd = Xd
        self.Yd = Yd
        self.Xb = Xb
        self.Xss = Xss
    
    def __str__(self) -> str:
        return f"Comp:\n\tZfs - {self.Zfs}\n\tXd  - {self.Xd}\n\tXb  - {self.Xb}\n\tXss - {self.Xss}"