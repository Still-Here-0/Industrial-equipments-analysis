from logging import Logger



class Equipment:

    def __init__(self, log: Logger) -> None:
        self.log = log
        self.log.info("Initializing")


    def solve(self):
        self.log.info("Solving")
        