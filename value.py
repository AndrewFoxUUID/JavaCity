class Value():

    def __init__(self, val, t):
        if val is None:
            self.val = None
        elif t == 'int':
            self.val = int(val)
        elif t == 'double':
            self.val = float(val)
        elif t == 'boolean':
            self.val = bool(val)
        elif t == 'char':
            self.val = str(val)[0]
        elif t == 'String':
            self.val = str(val)
        else:
            self.val = val
        self.type = t

    def __str__(self):
        if self.val is None:
            return 'null'
        elif self.val == True and self.type == 'boolean':
            return 'true'
        elif self.val == False and self.type == 'boolean':
            return 'false'
        else:
            return str(self.val)

    def __bool__(self):
        if self.val == None:
            return False
        elif self.type == 'int' or self.type == 'double':
            return self.val != 0
        elif self.type == 'boolean':
            return self.val
        elif self.type == 'String':
            return len(self.val) > 0
        else:
            return bool(self.val)

    def __len__(self):
        if self.val == None or self.val == False:
            return 0
        elif self.type == 'int' or self.type == 'double':
            return len(str(self.val))
        elif self.type == 'boolean':
            return 1
        elif self.type == 'String':
            return len(self.val)
        else:
            return len(self.val)

    def __contains__(self, other):
        return Value(self.val.__contains__(other), 'boolean')

    def __getitem__(self, other):
        return Value(self.val.__getitem__(other), 'Object')

    def __setitem__(self, other, val):
        return Value(self.val.__setitem__(other, val), 'Object')

    def __delitem__(self, other):
        return Value(self.val.__delitem__(other), 'Object')

    def __lt__(self, other):
        return Value(self.val.__lt__(other.val), 'boolean')

    def __le__(self, other):
        return Value(self.val.__le__(other.val), 'boolean')

    def __eq__(self, other):
        if not isinstance(other, Value):
            return False
        return Value(self.val == other.val and self.type == other.type, 'boolean')

    def __ne__(self, other):
        if not isinstance(other, Value):
            return True
        return Value(self.val != other.val or self.type != other.type, 'boolean')

    def __ge__(self, other):
        return Value(self.val.__ge__(other.val), 'boolean')

    def __gt__(self, other):
        return Value(self.val.__gt__(other.val), 'boolean')

    def __and__(self, other):
        return Value(self.val.__and__(other.val), 'boolean')

    def __or__(self, other):
        return Value(self.val.__or__(other.val), 'boolean')

    def __xor__(self, other):
        return Value(self.val.__xor__(other.val), 'boolean')

    def __index__(self):
        return Value(self.val.__index__(), 'int')

    def __abs__(self):
        return Value(self.val.__abs__(), self.type)

    def __neg__(self):
        return Value(self.val.__neg__(), self.type)

    def __pos__(self):
        return Value(self.val.__pos__(), self.type)

    def __add__(self, other):
        if isinstance(other, Value):
            val = other.val
        else:
            val = str(other)

        if self.type == 'String':
            val = str(val)
            
        return Value(self.val.__add__(val), self.type)

    def __sub__(self, other):
        return Value(self.val.__sub__(other.val), self.type)

    def __mul__(self, other):
        return Value(self.val.__mul__(other.val), self.type)

    def __floordiv__(self, other):
        return Value(self.val.__floordiv__(other.val), self.type)

    def __truediv__(self, other):
        return Value(self.val.__truediv__(other.val), self.type)

    def __mod__(self, other):
        return Value(self.val.__mod__(other.val), self.type)

    def __pow__(self, other):
        return Value(self.val.__pow__(other.val), self.type)

    def __iadd__(self, other):
        self.val = self.val.__add__(other.val)
        return self

    def __isub__(self, other):
        self.val = self.val.__sub__(other.val)
        return self

    def __hash__(self):
        return hash(self.val)