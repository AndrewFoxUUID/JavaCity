class Method():

    def __init__(self, name, args=[], body=[], static=False, final=False):
        self.name = name
        self.args = args
        self.body = body
        self.static = static
        self.final = final

    def __eq__(self, other):
        eq = self.name == other.name
        eq = eq and len(self.args) == len(other.args)
        for i, arg in enumerate(other.args):
            eq = eq and self.args[i].type == arg.type
        return eq

    def __hash__(self):
        return hash(self.name) + hash(len(self.args))

    def __iter__(self):
        return self.body.__iter__()

    def __str__(self):
        return str(self.name) + "(" + ", ".join([arg.type + " " + arg.name for arg in self.args]) + ")"

class MethodSet():

    def __init__(self, name):
        self.name = name
        self.methods = []

    def add(self, method):
        if method not in self:
            self.methods.append(method)
        return self

    def __iter__(self):
        return self.methods.__iter__()

    def __getitem__(self, args):
        name, params = args
        for method in self.methods:
            if method.name == name and len(method.args) == len(params):
                found = True
                for i, param in enumerate(params):
                    if param.type != method.args[i].type and method.args[i].type != "Object":
                        found = False
                        break
                if found:
                    return method
        raise NameError(f"Method {name} with parameters ({', '.join([param.type for param in params])}) not found")

    def __str__(self):
        return "{" + ", ".join([str(method) for method in self.methods]) + "}"
