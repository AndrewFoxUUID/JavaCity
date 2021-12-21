from method import Method

class Step():

    def __init__(self, action, var0=None, arg=None, var1=None, line=None):
        self.action = action
        self.var0 = var0
        self.arg = arg
        self.var1 = var1
        self.line = line

    def str(self, start=""):
        s = start + self.action.upper() + "(\n"
        lst = []
        if self.var0 is not None: lst.append(self.var0)
        if self.arg is not None: lst.append(self.arg)
        if self.var1 is not None: lst.append(self.var1)
        for item in lst:
            if type(item) == list and len(item) > 0:
                s += start + "  [\n"
                for step in item:
                    if isinstance(step, Step):
                        s += step.str(start + "    ") + ",\n"
                    else:
                        s += start + "    " + str(step) + ",\n"
                s += start + "  ],\n"
            else:
                if isinstance(item, Step):
                    s += item.str(start + "  ") + ",\n"
                elif isinstance(item, Method):
                    s += start + "  [\n"
                    for step in item.body:
                        if isinstance(step, Step):
                            s += step.str(start + "    ") + ",\n"
                        else:
                            s += start + "    " + str(step) + ",\n"
                    s += start + "  ],\n"
                else:
                    s += start + "  " + str(item) + ",\n"
        s += start + ")"
        return s

    def __str__(self):
        return self.str()