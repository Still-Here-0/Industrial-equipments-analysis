from utils.structs import SolvedFlowns, SolvedCompositions, OtherOperatinalParam
import pandas as pd


def section_fase(
        R_rmin: float, 
        corr: float,
        Q: SolvedFlowns, 
        O: OtherOperatinalParam, 
        C: SolvedCompositions
    ) -> tuple[list[float | int], list[float | int], list[float | int], list[float | int]]:
    
    R_rop = corr*R_rmin
    
    # First stage
    stage = 0
    Ls: list[float | int] = [R_rop*Q.D]
    Vs: list[float | int] = [Q.D*(R_rop + 1)]
    ang_coef_s: list[float | int] = [Ls[0]/Vs[0]]
    in_and_outs: list[float | int] = [-Q.D*C.Xd] # TODO: assumindo condensador total Xd == Yd
    lin_coef_s: list[float | int] = [-(1/Vs[0])*sum(in_and_outs[:1])]

    # Outlet stages TODO: confirmar se os calculos dessa parte estao corretas
    if Q.Ss is not None and O.beta_ss is not None and C.Xss is not None: # TODO: Not implemented
        for Si, Xsi, beta_sxi in zip(Q.Ss, C.Xss, O.beta_ss):
            
            Ls.append(Ls[stage] - (1 - beta_sxi)*Si)
            Vs.append(Vs[stage] + beta_sxi*Si)
            
            stage += 1
            ang_coef_s.append(Ls[stage]/Vs[stage])
            in_and_outs.append(-Si*Xsi)
            lin_coef_s.append(-(1/Vs[stage])*sum(in_and_outs[:stage + 1]))
    
    # Inlet stages
    for Fi, Zfi, beta_fzi in zip(Q.Fs, C.Zfs, O.beta_fzs):
            
        Ls.append(Ls[stage] + (1 - beta_fzi)*Fi)
        Vs.append(Vs[stage] - beta_fzi*Fi)
        
        stage += 1
        ang_coef_s.append(Ls[stage]/Vs[stage])
        in_and_outs.append(Fi*Zfi)
        lin_coef_s.append(-(1/Vs[stage])*sum(in_and_outs[:stage + 1]))
    
    X_sec_s: list[float | int] = []
    Y_sec_s: list[float | int] = []
    
    intersession = 1
    while intersession <= stage:
        X_sec_s.append((Vs[intersession]*sum(in_and_outs[:intersession]) - Vs[intersession - 1]*sum(in_and_outs[:intersession + 1]))/(Ls[intersession - 1]*Vs[intersession] - Ls[intersession]*Vs[intersession - 1]))

        Y_sec_s.append((Ls[intersession]*sum(in_and_outs[:intersession]) - Ls[intersession - 1]*sum(in_and_outs[:intersession + 1]))/(Ls[intersession - 1]*Vs[intersession] - Ls[intersession]*Vs[intersession - 1]))

        intersession += 1

    X_sec_s.append(C.Xb)
    Y_sec_s.append(C.Xb)

    df = pd.DataFrame({'X': X_sec_s, 'Y': Y_sec_s, 'ang': ang_coef_s, 'lin': lin_coef_s})
    df.sort_values('X')

    X_sec_s = list(df['X'])
    Y_sec_s = list(df['Y'])
    ang_coef_s = list(df['ang'])
    lin_coef_s = list(df['lin'])

    return X_sec_s, Y_sec_s, ang_coef_s, lin_coef_s

if __name__ == "__main__":
    q = SolvedFlowns      (Fs=  [1000], D=  500 , B= 500 ,  Ss= None)
    c = SolvedCompositions(Zfs= [0.5 ], Xd= 0.95, Xb=0.05,  Xss=None, Yd=0.95)
    o = OtherOperatinalParam   (beta_zs=[0], beta_d=0, beta_b=1, beta_ss=None)

    R_min = 0.957
    corr = 1.5

    X_sec, Y_sec, ang_coef, lin_coef = section_fase(R_min, corr, q, o, c)
    print(f"X sections:    {X_sec}")
    print(f"Y sections:    {Y_sec}")
    print(f"Angular Coef.: {ang_coef}")
    print(f"Linear Coef.:  {lin_coef}")