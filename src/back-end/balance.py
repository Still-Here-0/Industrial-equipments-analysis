from utils.structs import SolvedFlowns, InputFlowns, SolvedCompositions, InputCompositions
from utils.gekko_utils import init_gekko, get_value


def total_mass(Q: InputFlowns, C: InputCompositions) -> tuple[SolvedFlowns, SolvedCompositions]:
    
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

    Q_solved = SolvedFlowns( 
        Fs = [get_value(Fi) for Fi in Fs],
        D  = get_value(D),
        B  = get_value(B),
        Ss = [get_value(Si) for Si in Ss],
    )

    C_solved = SolvedCompositions(
        Zfs = [get_value(Zfi) for Zfi in Zfs],
        Xd  = get_value(Xd),
        Xb  = get_value(Xb),
        Xss = [get_value(Xsi) for Xsi in Xss],
        Yd  = C.Yd if C.Yd is None else get_value(C.Yd)
    )

    return Q_solved, C_solved

if __name__ == "__main__":

    # Test 1
    q = InputFlowns      (Fs= [1000], D= None, B= None, Ss= None)
    c = InputCompositions(Zfs=[0.5 ], Xd=0.95, Xb=0.05, Xss=None)
    Q, C = total_mass(q, c)
    assert Q.D == 500 and Q.B == 500
    print("## Passed T1")

    # Test 3
    q = InputFlowns      (Fs= [1000], D= None, B= None, Ss= [150.0])
    c = InputCompositions(Zfs=[0.5 ], Xd=0.95, Xb=0.05, Xss=[ 0.8 ])
    Q, C = total_mass(q, c)
    assert Q.D == 375 and Q.B == 475
    print("\n## Passed T2")

    # Test 2
    q = InputFlowns      (Fs= [1000, 200], D= None, B= None, Ss= [150])
    c = InputCompositions(Zfs=[0.5 , 0.5], Xd=0.95, Xb=0.05, Xss=[0.8])
    Q, C = total_mass(q, c)
    assert Q.D == 475 and Q.B == 575
    print("\n## Passed T3")

    # Result
    q = InputFlowns      (Fs=[1000], D= None, B= None, Ss= None)
    c = InputCompositions(Zfs=[0.5], Xd=0.95, Xb=0.05, Xss=None)
    Q, C = total_mass(q, c)
    print(Q, C, sep='\n')