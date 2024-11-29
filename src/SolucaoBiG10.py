from back_end.equipments.binary_distillation.utils import ChargeInput, CompositionInput, FlowInput, ColumnInput, TotalCondenser, PartialReboiler
from back_end.equipments import BinaryDistillation
from back_end.sys_utils import EqGraph
from logging import Logger

S = ColumnInput(TotalCondenser, PartialReboiler)
C = CompositionInput(Zfs=[0.5], Xd=0.95, Xb=0.05)
O = ChargeInput(beta_zs=[0], beta_d=0, beta_b=1)
Q = FlowInput(Fs=[1000], D=None, B=None, Ss=[100])
EqModel = EqGraph()

log = Logger("teste")

# Assumindo correlação de 1.5 entre refluxo mínimo teórico e refluxo de operação
equipment = BinaryDistillation(log, S, C, O, Q, EqModel, 1.5)

equipment.solve()
equipment.plot_result()
equipment.real_stages(0.007, 0.652)
equipment.opt_reflux("3_000/n", "n**2")

print(f"Número ótimo de pratos: {equipment.num_teo_stages:.3f}")
print(f"Número de estágios reais de acordo com o método de O'Connell: {equipment.num_real_stages:.3f}")
print(f"\nNúmero ótimo de estágios na coluna (gekko): {equipment.gekko_stages:.3f}")
print(f"\nNúmero ótimo de estágios pela minimização do valor gasto (scipy):")
print(f"\t - Razão de refluxo op/teo: {equipment.mini_opt["corr"]:.3f}")
print(f"\t - Estágios:                {equipment.mini_opt["stages"]:.3f}")
print(f"\t - Preço:                   {equipment.mini_opt["price"]:.3f}")
print(f"\nNúmero ótimo de estágios pela pela correlação gekko-scipy:")
print(f"\t - Razão de refluxo op/teo: {equipment.root_opt["corr"]:.3f}")
print(f"\t - Estágios:                {equipment.root_opt["stages"]:.3f}")
print(f"\t - Preço:                   {equipment.root_opt["price"]:.3f}")