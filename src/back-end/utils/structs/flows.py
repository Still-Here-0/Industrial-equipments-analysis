from typing import Optional



class Flowns:

    def __init__(
            self, 
            *, 
            Fs: list[Optional[float]],          # Inlet flows
            D: Optional[float],                 # Top outlet flow 
            B: Optional[float],                 # Bottom outlet flow
            Ss: Optional[list[Optional[float]]] # Outlet flow
        ) -> None:
        assert isinstance(Fs, list)

        self.Fs = Fs
        self.D  = D
        self.B  = B
        self.Ss = Ss