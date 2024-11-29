from ....sys_utils import PrintableClass
from typing import Optional

class CompositionInput:

    def __init__(
            self, 
            *, 
            Zfs: list[Optional[float | int]],                  # Composition of inlet flows
            Xd:  Optional[float | int],                        # Fluid composition of top outlet flow 
            Xb:  Optional[float | int],                        # Fluid composition of bottom outlet flow
            Xss: Optional[list[Optional[float | int]]] = None, # Fluid composition of outlet flow
            Yd:  Optional[float] = None,                            # Vapor composition of top outlet flow
        ) -> None:
        
        self.Zfs = Zfs
        self.Xd = Xd
        self.Yd = Yd
        self.Xb = Xb
        self.Xss = Xss

class SolvedComposition(PrintableClass):

    def __init__(
            self, 
            *, 
            Zfs: list[float | int],          # Composition of inlet flows
            Xd:  float | int,                # Fluid composition of top outlet flow 
            Xb:  float | int,                # Fluid composition of bottom outlet flow
            Xss: list[float | int],# Fluid composition of outlet flow
            Yd:  float | int,                # Vapor composition of top outlet flow
        ) -> None:
        
        self.Zfs = Zfs
        self.Xd = Xd
        self.Yd = Yd
        self.Xb = Xb
        self.Xss = Xss