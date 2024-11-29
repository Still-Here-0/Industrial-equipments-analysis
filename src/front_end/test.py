from back_end.equipments.binary_distillation.utils import ChargeInput, CompositionInput, FlowInput, ColumnInput, TotalCondenser, PartialReboiler
from back_end.equipments import BinaryDistillation
from back_end.sys_utils import EqGraph

from logging import Logger

S = ColumnInput(TotalCondenser, PartialReboiler)
C = CompositionInput(Zfs=[0.5], Xd=0.95, Xb=0.05)
O = ChargeInput(beta_zs=[0], beta_d=0, beta_b=1)
Q = FlowInput(Fs=[1000], D=None, B=None)
EqModel = EqGraph()

log = Logger("teste")
equipament = BinaryDistillation(log, S, C, O, Q, EqModel, 2.5)

equipament.solve()
equipament.plot_result()
