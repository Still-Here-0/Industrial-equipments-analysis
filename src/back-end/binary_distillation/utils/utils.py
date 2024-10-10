from pathlib import Path
import pandas as pd
import os


def get_eq_data() -> tuple[list[float], list[float]]:
    DIR = str(Path(os.path.dirname(__file__)).parent.parent.parent) + "\\data\\equilibrium_curve.csv"
    eq_data = pd.read_csv(DIR)
    x_data = list(eq_data['x'])
    y_data = list(eq_data['y'])

    return x_data, y_data

if __name__ == "__main__":
    from gekko_utils import init_gekko
    import matplotlib.pyplot as plt
    import numpy as np

    x, y = get_eq_data()
    engine = init_gekko(2)
    par = engine.Param(value=np.linspace(0, 1))
    v = engine.Var()
    engine.cspline(par, v, x, y)
    engine.solve(disp=False)

    plt.plot(par, v, label='spline') # type: ignore
    plt.plot(x, y, 'bo', label='data')
    plt.legend()
    plt.grid()
    plt.show()