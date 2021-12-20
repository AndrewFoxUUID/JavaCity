from variable import Variable

class Object():
    
    def __init__(self, name, env, addr=None):
        self.type = name
        self.env = env
        self.addr = addr

    def __setitem__(self, var, val):
        self.env[var] = val
        return val

    def copy(self):
        return Object(self.type, self.env.copy())

    def __str__(self):
        if self.type == "Integer":
            return str(self.env[Variable("this", "Integer")][Variable("inner", "int")])
        elif self.type == "Double":
            return str(self.env[Variable("this", "Double")][Variable("inner", "double")])
        elif self.type == "Boolean":
            return str(self.env[Variable("this", "Boolean")][Variable("inner", "boolean")])
        elif self.type == "Character":
            return str(self.env[Variable("this", "Character")][Variable("inner", "char")])
        elif self.type == "String":
            return str(self.env[Variable("this", "String")][Variable("inner", "String")])
        else:
            return f"<{self.type} object at {self.addr}>"

    def __getitem__(self, key):
        return self.env.__getitem__(key)

    def __bool__(self):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] != 0
        elif self.type == "Double":
            return self.env[Variable("this", "Double")][Variable("inner", "double")] != 0.0
        elif self.type == "Boolean":
            return self.env[Variable("this", "Boolean")][Variable("inner", "boolean")]
        elif self.type == "String":
            return len(self.env[Variable("this", "String")][Variable("inner", "String")]) != 0
        else:
            return True

    def __lt__(self, other):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] < other
        elif self.type == "Double":
            return self.env[Variable("this", "Double")][Variable("inner", "double")] < other
        elif self.type == "Character":
            return self.env[Variable("this", "Character")][Variable("inner", "char")] < other
        elif self.type == "String":
            return self.env[Variable("this", "String")][Variable("inner", "String")] < other
        else:
            raise TypeError(f"Cannot compare '{other.type if type(other) == Object else other.type}' to '{self.type}'")

    def __le__(self, other):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] <= other
        elif self.type == "Double":
            return self.env[Variable("this", "Double")][Variable("inner", "double")] <= other
        elif self.type == "Character":
            return self.env[Variable("this", "Character")][Variable("inner", "char")] <= other
        elif self.type == "String":
            return self.env[Variable("this", "String")][Variable("inner", "String")] <= other
        else:
            raise TypeError(f"Cannot compare '{other.type if type(other) == Object else other.type}' to '{self.type}'")

    def __gt__(self, other):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] > other
        elif self.type == "Double":
            return self.env[Variable("this", "Double")][Variable("inner", "double")] > other
        elif self.type == "Character":
            return self.env[Variable("this", "Character")][Variable("inner", "char")] > other
        elif self.type == "String":
            return self.env[Variable("this", "String")][Variable("inner", "String")] > other
        else:
            raise TypeError(f"Cannot compare '{other.type if type(other) == Object else other.type}' to '{self.type}'")

    def __ge__(self, other):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] >= other
        elif self.type == "Double":
            return self.env[Variable("this", "Double")][Variable("inner", "double")] >= other
        elif self.type == "Character":
            return self.env[Variable("this", "Character")][Variable("inner", "char")] >= other
        elif self.type == "String":
            return self.env[Variable("this", "String")][Variable("inner", "String")] >= other
        else:
            raise TypeError(f"Cannot compare '{other.type if type(other) == Object else other.type}' to '{self.type}'")

    def __eq__(self, other):
        return self.addr == other.addr

    def __ne__(self, other):
        return self.addr != other.addr

    def __abs__(self):
        if self.type == "Integer":
            return abs(self.env[Variable("this", "Integer")][Variable("inner", "int")])
        elif self.type == "Integer":
            return abs(self.env[Variable("this", "Double")][Variable("inner", "double")])
        else:
            return self

    def __neg__(self):
        if self.type == "Integer":
            return -(self.env[Variable("this", "Integer")][Variable("inner", "int")])
        elif self.type == "Double":
            return -(self.env[Variable("this", "Double")][Variable("inner", "double")])
        else:
            return self

    def __pos__(self):
        if self.type == "Integer":
            return +(self.env[Variable("this", "Integer")][Variable("inner", "int")])
        elif self.type == "Double":
            return +(self.env[Variable("this", "Double")][Variable("inner", "double")])
        else:
            return self

    def __add__(self, other):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] + other
        elif self.type == "Double":
            return self.env[Variable("this", "Double")][Variable("inner", "double")] + other
        elif self.type == "Character":
            return self.env[Variable("this", "Character")][Variable("inner", "char")] + other
        elif self.type == "String":
            return self.env[Variable("this", "String")][Variable("inner", "String")] + other
        else:
            raise TypeError(f"Cannot add '{other.type if type(other) == Object else other.type}' to '{self.type}'")

    def __sub__(self, other):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] - other
        elif self.type == "Double":
            return self.env[Variable("this", "Double")][Variable("inner", "double")] - other
        elif self.type == "Character":
            return self.env[Variable("this", "Character")][Variable("inner", "char")] - other
        else:
            raise TypeError(f"Cannot subtract '{other.type if type(other) == Object else other.type}' from '{self.type}'")

    def __mul__(self, other):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] * other
        elif self.type == "Double":
            return self.env[Variable("this", "Double")][Variable("inner", "double")] * other
        elif self.type == "String":
            return self.env[Variable("this", "String")][Variable("inner", "String")] * other
        else:
            raise TypeError(f"Cannot multiply '{other.type if type(other) == Object else other.type}' by '{self.type}'")

    def __truediv__(self, other):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] // other
        elif self.type == "Double":
            return self.env[Variable("this", "Double")][Variable("inner", "double")] // other
        else:
            raise TypeError(f"Cannot divide '{self.type}' by '{other.type if type(other) == Object else other.type}'")

    def __mod__(self, other):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] % other
        elif self.type == "Double":
            return self.env[Variable("this", "Double")][Variable("inner", "double")] % other
        else:
            raise TypeError(f"Cannot get modulus '{self.type}' of '{other.type if type(other) == Object else other.type}'")

    def __pow__(self, other):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] ** other
        elif self.type == "Double":
            return self.env[Variable("this", "Double")][Variable("inner", "double")] ** other
        else:
            raise TypeError(f"Cannot raise '{self.type}' to '{other.type if type(other) == Object else other.type}'")

    def __iadd__(self, other):
        if self.type == "Integer":
            self.env[Variable("this", "Integer")][Variable("inner", "int")] += other
        elif self.type == "Double":
            self.env[Variable("this", "Double")][Variable("inner", "double")] += other
        elif self.type == "Character":
            self.env[Variable("this", "Character")][Variable("inner", "char")] += other
        elif self.type == "String":
            self.env[Variable("this", "String")][Variable("inner", "String")] += other
        else:
            raise TypeError(f"Cannot add '{other.type if type(other) == Object else other.type}' to '{self.type}'")

    def __isub__(self, other):
        if self.type == "Integer":
            self.env[Variable("this", "Integer")][Variable("inner", "int")] -= other
        elif self.type == "Double":
            self.env[Variable("this", "Double")][Variable("inner", "double")] -= other
        else:
            raise TypeError(f"Cannot subtract '{other.type if type(other) == Object else other.type}' from '{self.type}'")