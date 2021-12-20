class Step():

    def __init__(self, innerlist, line):
        self.innerlist = innerlist
        self.line = line
    
    def __getitem__(self, indices):
        return self.innerlist.__getitem__(indices)

    def __setitem__(self, indices, values):
        return self.innerlist.__setitem__(indices, values)

    def str(self, start=""):
        s = start + self.innerlist[0].upper() + "(\n"
        for item in self.innerlist[1:]:
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
                else:
                    s += start + "  " + str(item) + ",\n"
        s += start + ")"
        return s

    def __str__(self):
        return self.str()

    def __len__(self):
        return self.innerlist.__len__()