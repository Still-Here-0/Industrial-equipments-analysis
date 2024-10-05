from typing import Optional



class Compositions:

    def __init__(
            self, 
            *, 
            Zfs: list[Optional[float]],         # Composition of inlet flows
            Xd:  Optional[float],               # Fluid composition of top outlet flow 
            Xb:  Optional[float],               # Fluid composition of bottom outlet flow
            Xss: Optional[list[Optional[float]]]# Fluid composition of outlet flow
        ) -> None:
        
        self.Zfs = Zfs
        self.Xd = Xd
        self.Xb = Xb
        self.Xss = Xss