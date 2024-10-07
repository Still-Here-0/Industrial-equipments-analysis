from gekko.gk_operators import GK_Operators, GK_Intermediate
from gekko.gk_variable import GKVariable
from gekko import GEKKO
from typing import Any

def init_gekko(mode=None) -> GEKKO:
    engine = GEKKO(remote=False)
    engine.options.IMODE = 1 if mode is None else mode #type: ignore
    engine.options.SOLVER = 1                          #type: ignore

    return engine

def get_value(var: GK_Operators | GKVariable | Any) -> float | int:

    if var is None:
        raise Exception("Value can not be None")
    elif isinstance(var, GKVariable):
        return var.VALUE[0]
    elif isinstance(var, GK_Intermediate):
        return var.VALUE[0]
    elif isinstance(var, GK_Operators):
        return var.VALUE.value
    
    return float(var)


if __name__ == "__main__":
    init_gekko()