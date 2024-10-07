from typing import Optional



class InputOtherParam:

    def __init__(
            self,
            *, 
            beta_zs: list[float],               # Composition of inlet flows
            beta_d:  float,                     # Fluid composition of top outlet flow 
            beta_b:  float,                     # Fluid composition of bottom outlet flow
            beta_ss: Optional[list[float]]=None # Fluid composition of outlet flow
        ) -> None:
        
        self.beta_fzs = beta_zs
        self.beta_d  = beta_d
        self.beta_b  = beta_b
        self.beta_ss = beta_ss