class Variable():

    def __init__(self, name, t='', static=False, final=False):
        self.name = name
        self.type = t
        self.static = static
        self.final = final

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return self.name.__hash__()

    def __str__(self):
        return "VAR_" + str(self.name) + "_" + str(self.type)