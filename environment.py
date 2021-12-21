from value import Value
from variable import Variable
from step import Step
from object import Object
from method import Method, MethodSet

class Environment():

    def __init__(self, upper, variables):
        self.upper = upper
        self.vars = variables

    def copy(self):
        variables = {}
        for k in self.vars:
            variables[k] = self.vars[k]
        return Environment(self.upper, variables)

    def define(self, var):
        if type(var) == Step and var.action == 'dot':
            parent = self[var.var0]
            if type(parent) == Environment:
                parent.define(var.arg)
            else:
                try:
                    parent.env[Variable('this')].define(var.arg)
                except UnboundLocalError:
                    parent.env.define(var.arg)
        elif var not in self.vars:
            self.vars[var] = Value(None, var.type)
        else:
            raise NameError("Variable " + str(var) + " already defined in scope")

    def __setitem__(self, var, val):
        if type(var) == Step and var.action == 'dot':
            parent = self[var.var0]
            if isinstance(parent, Environment):
                parent[var.arg] = val
            else:
                try:
                    parent.env[Variable('this')][var.arg] = val
                except UnboundLocalError:
                    parent.env[var.arg] = val
        elif self.contains(var, False):
            if var.final and self.vars[var] != Value(None, "Object"):
                raise TypeError(f"Cannot modify final variable {var.name}")
            self.vars[var] = val
        elif self.upper is not None:
            self.upper[var] = val
        else:
            raise UnboundLocalError(f"Variable {var.name if type(var) == Variable else str(var)} is not defined in scope")

    def __getitem__(self, args):
        if type(args) == tuple:
            var, params = args[0], args[1]
        else:
            var, params = args, None

        if type(var) == Step and var.action == 'dot':
            parent = self[var.var0]
            if isinstance(parent, Environment):
                return parent[var.arg]
            else:
                try:
                    return parent.env[Variable('this')][var.arg]
                except UnboundLocalError:
                    return parent.env[var.arg]
        elif self.contains(var, False):
            if params is not None:
                try:
                    return self.vars[var][var, params]
                except Exception:
                    pass
            else:
                return self.vars[var]
        if self.upper is not None:
            return self.upper[var, params]
        else:
            if var in javascope:
                if params is not None and isinstance(javascope[var], Object):
                    return javascope[var][var][var, params]
                elif params is not None:
                    return javascope[var][var, params]
                return javascope[var]
            raise UnboundLocalError(f"Variable {var} not found")

    def contains(self, item, checkupper=True):
        if item in self.vars:
            return True

        if checkupper and self.upper is not None:
            return self.upper.contains(item)
        
        return False

    def __iter__(self):
        return self.vars.__iter__()

    def __str__(self):
        s = "{"
        if self.upper is not None:
            u = str(self.upper)
            for line in u.split("\n"):
                s += "\n  " + line
        for var in self.vars:
            s += "\n  " + str(var) + " = " + ("Environment" if type(self.vars[var]) == Environment else str(self.vars[var]))
        return s + "\n}"


javascope = {
    Variable('System', 'Object', True, True): Object(
        name='System',
        env=Environment(None, {
            Variable('out', 'Object', True, True): Object(
                name='out',
                env=Environment(None, {
                    Variable('println', 'void', True, True): MethodSet(Variable('println', 'void')).add(
                        Method(
                            Variable('println', 'void', True, True),
                            [
                                Variable('val', 'Object')
                            ],
                            [
                                Step('print', Variable('val'))
                            ],
                            True
                        )
                    )
                })
            )
        })
    ),
    Variable('Integer', 'Object', True, True): Object(
        name='Integer',
        env=Environment(None, {
            Variable('Integer', 'Integer', True, True): MethodSet(Variable('Integer', 'Integer', True, True)).add(
                Method(
                    Variable('Integer', 'Integer', True, True),
                    [
                        Variable('inner', 'int')
                    ],
                    [
                        Step('def', Step('dot', Variable('this', 'Integer'), Variable('inner', 'int'))),
                        Step('set', Step('dot', Variable('this', 'Integer'), Variable('inner', 'int')), Variable('inner', 'int'))
                    ]
                )
            ),
            Variable('parseInt', 'int', True, True): MethodSet(Variable('parseInt', 'int', True, True)).add(
                Method(
                    Variable('parseInt', 'int', True, True),
                    [
                        Variable('val', 'Object')
                    ],
                    [
                        Step('return', Step('cast', Variable('val', 'Object'), 'int'))
                    ]
                )
            ),
            Variable('toString', 'String', True, True): MethodSet(Variable('toString', 'String', True, True)).add(
                Method(
                    Variable('toString', 'String', True, True),
                    [],
                    [
                        Step('return', Step('cast', Variable('inner', 'int'), 'String'))
                    ]
                )
            )
        })
    ),
    Variable('Double', 'Object', True, True): Object(
        name='Double',
        env=Environment(None, {
            Variable('Double', 'Double', True, True): MethodSet(Variable('Double', 'Double', True, True)).add(
                Method(
                    Variable('Double', 'Double', True, True),
                    [
                        Variable('inner', 'double')
                    ],
                    [
                        Step('def', Step('dot', Variable('this', 'Double'), Variable('inner', 'double'))),
                        Step('set', Step('dot', Variable('this', 'Double'), Variable('inner', 'double')), Variable('inner', 'double'))
                    ]
                )
            ),
            Variable('parseDouble', 'double', True, True): MethodSet(Variable('parseDouble', 'double', True, True)).add(
                Method(
                    Variable('parseDouble', 'double', True, True),
                    [
                        Variable('val', 'Object')
                    ],
                    [
                        Step('return', Step('cast', Variable('val', 'Object'), 'double'))
                    ]
                )
            ),
            Variable('toString', 'String', True, True): MethodSet(Variable('toString', 'String', True, True)).add(
                Method(
                    Variable('toString', 'String', True, True),
                    [],
                    [
                        Step('return', Step('cast', Variable('inner', 'double'), 'String'))
                    ]
                )
            )
        })
    ),
    Variable('Boolean', 'Object', True, True): Object(
        name='Boolean',
        env=Environment(None, {
            Variable('Boolean', 'Boolean', True, True): MethodSet(Variable('Boolean', 'Boolean', True, True)).add(
                Method(
                    Variable('Boolean', 'Boolean', True, True),
                    [
                        Variable('inner', 'boolean')
                    ],
                    [
                        Step('def', Step('dot', Variable('this', 'Boolean'), Variable('inner', 'boolean'))),
                        Step('set', Step('dot', Variable('this', 'Boolean'), Variable('inner', 'boolean')), Variable('inner', 'boolean'))
                    ]
                )
            ),
            Variable('parseBoolean', 'boolean', True, True): MethodSet(Variable('parseBoolean', 'boolean', True, True)).add(
                Method(
                    Variable('parseBoolean', 'boolean', True, True),
                    [
                        Variable('val', 'Object')
                    ],
                    [
                        Step('return', Step('cast', Variable('val', 'Object'), 'boolean'))
                    ]
                )
            ),
            Variable('toString', 'String', True, True): MethodSet(Variable('toString', 'String', True, True)).add(
                Method(
                    Variable('toString', 'String', True, True),
                    [],
                    [
                        Step('return', Step('cast', Variable('inner', 'boolean'), 'String'))
                    ]
                )
            )
        })
    ),
    Variable('Character', 'Object', True, True): Object(
        name='Character',
        env=Environment(None, {
            Variable('Character', 'Character', True, True): MethodSet(Variable('Character', 'Character', True, True)).add(
                Method(
                    Variable('Character', 'Character', True, True),
                    [
                        Variable('inner', 'char')
                    ],
                    [
                        Step('def', Step('dot', Variable('this', 'Character'), Variable('inner', 'char'))),
                        Step('set', Step('dot', Variable('this', 'Character'), Variable('inner', 'char')), Variable('inner', 'char'))
                    ]
                )
            ),
            Variable('toString', 'String', True, True): MethodSet(Variable('toString', 'String', True, True)).add(
                Method(
                    Variable('toString', 'String', True, True),
                    [],
                    [
                        Step('return', Step('cast', Variable('inner', 'char'), 'String'))
                    ]
                )
            )
        })
    ),
    Variable('String', 'Object', True, True): Object(
        name='String',
        env=Environment(None, {
            Variable('String', 'String', True, True): MethodSet(Variable('String', 'String', True, True)).add(
                Method(
                    Variable('String', 'String', True, True),
                    [
                        Variable('inner', 'String')
                    ],
                    [
                        Step('def', Step('dot', Variable('this', 'String'), Variable('inner', 'String'))),
                        Step('set', Step('dot', Variable('this', 'String'), Variable('inner', 'String')), Variable('inner', 'String'))
                    ]
                )
            ),
            Variable('charAt', 'char', False, True): MethodSet(Variable('charAt', 'char', False, True)).add(
                Method(
                    Variable('charAt', 'char', False, True),
                    [
                        Variable('index', 'int')
                    ],
                    [
                        Step('return', Step('substring', Variable('inner', 'String'), Variable('index', 'int'), Step('eval', Variable('index', 'int'), '+', Value(1, 'int'))))
                    ]
                )
            ),
            Variable('substring', 'String', False, True): MethodSet(Variable('substring', 'String', False, True)).add(
                Method(
                    Variable('substring', 'String', False, True),
                    [
                        Variable('start', 'int')
                    ],
                    [
                        Step('return', Step('substring', Variable('inner', 'String'), Variable('start', 'int'), Step('length', Variable('inner', 'String'))))
                    ]
                ),
                Method(
                    Variable('substring', 'String', False, True),
                    [
                        Variable('start', 'int'),
                        Variable('end', 'int')
                    ],
                    [
                        Step('return', Step('substring', Variable('inner', 'String'), Variable('start', 'int'), Variable('end', 'int')))
                    ]
                )
            ),
            Variable('length', 'int', False, True): MethodSet(Variable('length', 'int', False, True)).add(
                Method(
                    Variable('length', 'int', False, True),
                    [],
                    [
                        Step('return', Step('length', Variable('inner', 'String')))
                    ]
                )
            )
        })
    )
}