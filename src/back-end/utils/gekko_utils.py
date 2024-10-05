from gekko import GEKKO

def init_gekko() -> GEKKO:
    engine = GEKKO(remote=False)
    engine.options.IMODE = 1        #type: ignore
    engine.options.SOLVER = 1       #type: ignore

    return engine

if __name__ == "__main__":
    init_gekko()