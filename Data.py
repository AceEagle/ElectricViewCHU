

class Data:
    def __init__(self, globalParameters=None):
        if globalParameters is not None:
            self.parameters = {"parameter1": globalParameters["parameter1"],
                               "parameter2": globalParameters["parameter2"],
                               "parameter3": globalParameters["parameter3"],
                               "parameter4": globalParameters["parameter4"],
                               "parameter5": globalParameters["parameter5"],
                               "parameter6": globalParameters["parameter6"],
                               "parameter7": globalParameters["parameter7"],
                               "parameter8": globalParameters["parameter8"]}

        self.graphics = {"Tension": 1,
                         "Puissance (Full)": 0,
                         "Puissance (1t)": 0,
                         "Lissajoue": 0,
                         "graph5": 0,
                         "graph6": 0,}

