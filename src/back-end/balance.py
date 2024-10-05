from utils.gekko_utils import init_gekko
from utils.structs import Compositions, Flowns
from typing import Optional


def global_b(
        B:  Optional[float], 
        D:  Optional[float], 
        Si: Optional[list[float]], 
        Fi: Optional[list[float]]
    ):
    ...

def comp_b(
        B:   Optional[float],
        xb:  Optional[float],
        D:   Optional[float],
        xd:  Optional[float],
        Si:  Optional[list[float]], 
        xsi: Optional[list[float]], 
        Fi:  Optional[list[float]],
        xfi: Optional[list[float]]
    ):
    ...

def total_mass(
        Q: Flowns,
        C: Compositions
    ):
    
    engine = init_gekko()

    B   = engine.Var(lb=0)       if Q.B  is None else engine.Const(Q.B)    #type: ignore
    Xb  = engine.Var(lb=0, ub=1) if C.Xb is None else engine.Const(C.Xb)   #type: ignore
    D   = engine.Var(lb=0)       if Q.D  is None else engine.Const(Q.D)    #type: ignore
    Xd  = engine.Var(lb=0, ub=1) if C.Xd is None else engine.Const(C.Xd)   #type: ignore

    if Q.Fs is not None and C.Zfs is not None:
        Fs  = [engine.Var(lb=0)       if Fi  is None else engine.Const(Fi)  for Fi  in Q.Fs ] #type: ignore
        Zfs = [engine.Var(lb=0, ub=1) if Xfi is None else engine.Const(Xfi) for Xfi in C.Zfs] #type: ignore
    else:
        Fs  = [engine.Const(0)]
        Zfs = [engine.Const(0)]

    if Q.Ss is not None and C.Xss is not None:
        Ss  = [engine.Var(lb=0)       if Si  is None else engine.Const(Si)  for Si  in Q.Ss ] #type: ignore
        Xss = [engine.Var(lb=0, ub=1) if Xsi is None else engine.Const(Xsi) for Xsi in C.Xss] #type: ignore
    else:
        Ss  = [engine.Const(0)]
        Xss = [engine.Const(0)]

    flow_in  = engine.Intermediate(engine.sum(Fs))
    flow_out = engine.Intermediate(engine.sum(Ss) + D + B)

    comp_flow_in = engine.Intermediate(engine.sum([Fi*xi for Fi, xi in zip(Fs, Zfs)]))
    comp_flow_out = engine.Intermediate(
        engine.sum([Si*xi for Si, xi in zip(Ss, Xss)]) + D*Xd + B*Xb
    )

    engine.Equation(flow_in == flow_out)
    engine.Equation(comp_flow_in == comp_flow_out)

    engine.solve(disp=False)

    # Q_solved = Flowns(Fs=Fs.VALUE, )

if __name__ == "__main__":
    q = Flowns      (Fs= [1000], D= None, B= None, Ss= None)
    c = Compositions(Zfs=[0.5 ], Xd=0.95, Xb=0.05, Xss=None)
    total_mass(q, c)