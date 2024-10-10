from .antoine import Antoine
from typing import Optional


class OtherOperatinalParam:

    def __init__(
            self,
            *, 
            beta_zs: list[float],               # Composition of inlet flows
            beta_d:  float,                     # Fluid composition of top outlet flow 
            beta_b:  float,                     # Fluid composition of bottom outlet flow
            beta_ss: Optional[list[float]]=None,# Fluid composition of outlet flow
            A_antonie: Optional[float]=None,
            B_antonie: Optional[float]=None,
            C_antonie: Optional[float]=None,
            mean_alpha: Optional[float]=None,
        ) -> None:
        
        self.beta_fzs = beta_zs
        self.beta_d  = beta_d
        self.beta_b  = beta_b
        self.beta_ss = beta_ss
        self.mean_alpha = mean_alpha

        # Antoine equation
        self.antonie = Antoine(A_antonie, B_antonie, C_antonie)