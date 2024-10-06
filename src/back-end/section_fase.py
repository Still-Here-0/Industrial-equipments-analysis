from utils.structs import SolvedFlowns, SolvedCompositions, InputOtherParam
from gekko.gk_operators import GK_Value

def section_fase(
        R_rmin: float, 
        corr: float,
        Q: SolvedFlowns, 
        O: InputOtherParam, 
        C: SolvedCompositions
    ) -> tuple[list[float | GK_Value], list[float], list[float]]:
    
    R_rop = corr*R_rmin
    
    # First stage
    stage = 0
    Ls: list[float] = [R_rop*Q.D]
    Vs: list[float] = [Q.D*(R_rop + 1)]
    ang_coef_s: list[float] = [Ls[0]/Vs[0]]
    in_and_outs: list[float] = [-Q.D*C.Xd] # TODO: assumindo condensador total Xd == Yd
    lin_coef_s: list[float] = [-(1/Vs[0])*sum(in_and_outs[:1])]

    # Outlet stages TODO: confirmar se os calculos dessa parte estao corretas
    if Q.Ss is not None and O.beta_ss is not None and C.Xss is not None and False: # TODO: Not implemented
        for Si, Xsi, beta_sxi in zip(Q.Ss, C.Xss, O.beta_ss):
            
            Ls.append(Ls[stage] - (1 - beta_sxi)*Si)
            Vs.append(Vs[stage] + beta_sxi*Si)
            
            stage += 1
            ang_coef_s.append(Ls[stage]/Vs[stage])
            in_and_outs.append(-Si*Xsi)
            lin_coef_s.append(-(1/Vs[0])*sum(in_and_outs[:stage + 1]))
    
    # Inlet stages
    for Fi, Zfi, beta_fzi in zip(Q.Fs, C.Zfs, O.beta_fzs):
            
        Ls.append(Ls[stage] + (1 - beta_fzi)*Fi)
        Vs.append(Vs[stage] - beta_fzi*Fi)
        
        stage += 1
        ang_coef_s.append(Ls[stage]/Vs[stage])
        in_and_outs.append(Fi*Zfi)
        lin_coef_s.append(-(1/Vs[0])*sum(in_and_outs[:stage + 1]))
    
    X_sec_s: list[float | GK_Value] = []
    # Y_sec_s: list[float | None] = [None] TODO: Rever se o Y é realmente necessario
    
    a = 1
    while a <= stage:
        X_sec_s.append((Vs[a]*in_and_outs[a - 1] - Vs[a - 1]*in_and_outs[a])/(Ls[a - 1]*Vs[a] - Ls[a]*Vs[a - 1]))

        # if a < stage:
        #     Y_sec_s.append((Ls[a]*in_and_outs[a - 1] - Ls[a - 1]*in_and_outs[a])/(Ls[a - 1]*Vs[a] - Ls[a]*Vs[a - 1]))

        a += 1

    # Y_sec_s.append(None)
    X_sec_s.append(C.Xb) #type: ignore
    # Y_sec_s.append(None)

    return X_sec_s, ang_coef_s, lin_coef_s

if __name__ == "__main__":
    q = SolvedFlowns      (Fs=  [1000], D=  500 , B= 500 ,  Ss= None)
    c = SolvedCompositions(Zfs= [0.5 ], Xd= 0.95, Xb=0.05,  Xss=None, Yd=None)
    o = InputOtherParam   (beta_zs=[0], beta_d=0, beta_b=1, beta_ss=None)

    R_min = 0.957
    corr = 1.5

    X_sec, ang_coef, lin_coef = section_fase(0.95, 1.5, q, o, c)
    print(f"X sections:    {X_sec}")
    print(f"Angular Coef.: {ang_coef}")
    print(f"Linear Coef.:  {lin_coef}")