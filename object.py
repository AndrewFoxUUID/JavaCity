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
        return f"<{self.type} object at {self.addr}>"

    def __getitem__(self, key):
        return self.env.__getitem__(key)

    def __bool__(self):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] != 0
        else:
            return True

    def __lt__(self, other):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] < other
        else:
            raise TypeError(f"Cannot compare '{other.type if type(other) == Object else other.type}' to '{self.type}'")

    def __le__(self, other):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] <= other
        else:
            raise TypeError(f"Cannot compare '{other.type if type(other) == Object else other.type}' to '{self.type}'")

    def __gt__(self, other):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] > other
        else:
            raise TypeError(f"Cannot compare '{other.type if type(other) == Object else other.type}' to '{self.type}'")

    def __ge__(self, other):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] >= other
        else:
            raise TypeError(f"Cannot compare '{other.type if type(other) == Object else other.type}' to '{self.type}'")

    def __eq__(self, other):
        return self.type == other.type and self.addr == other.addr

    def __ne__(self, other):
        return self.type != other.type or self.addr != other.addr

    def __abs__(self):
        if self.type == "Integer":
            return abs(self.env[Variable("this", "Integer")][Variable("inner", "int")])
        else:
            return self

    def __neg__(self):
        if self.type == "Integer":
            return -(self.env[Variable("this", "Integer")][Variable("inner", "int")])
        else:
            return self

    def __pos__(self):
        if self.type == "Integer":
            return +(self.env[Variable("this", "Integer")][Variable("inner", "int")])
        else:
            return self

    def __add__(self, other):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] + other
        else:
            raise TypeError(f"Cannot add '{other.type if type(other) == Object else other.type}' to '{self.type}'")

    def __sub__(self, other):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] - other
        else:
            raise TypeError(f"Cannot subtract '{other.type if type(other) == Object else other.type}' from '{self.type}'")

    def __mul__(self, other):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] * other
        else:
            raise TypeError(f"Cannot multiply '{other.type if type(other) == Object else other.type}' by '{self.type}'")

    def __truediv__(self, other):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] // other
        else:
            raise TypeError(f"Cannot divide '{self.type}' by '{other.type if type(other) == Object else other.type}'")

    def __mod__(self, other):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] % other
        else:
            raise TypeError(f"Cannot get modulus '{self.type}' of '{other.type if type(other) == Object else other.type}'")

    def __pow__(self, other):
        if self.type == "Integer":
            return self.env[Variable("this", "Integer")][Variable("inner", "int")] ** other
        else:
            raise TypeError(f"Cannot raise '{self.type}' to '{other.type if type(other) == Object else other.type}'")

    def __iadd__(self, other):
        if self.type == "Integer":
            self.env[Variable("this", "Integer")][Variable("inner", "int")] += other
        else:
            raise TypeError(f"Cannot add '{other.type if type(other) == Object else other.type}' to '{self.type}'")

    def __isub__(self, other):
        if self.type == "Integer":
            self.env[Variable("this", "Integer")][Variable("inner", "int")] -= other
        else:
            raise TypeError(f"Cannot subtract '{other.type if type(other) == Object else other.type}' from '{self.type}'")