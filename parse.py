import os, sys

from scan import *
from variable import Variable
from value import Value
from program import Program
from step import Step

class Parser():

    def __init__(self, scanner):
        self.scanner = scanner
        self.t = scanner.getToken()
        self.className = None
        while self.t.type in ['whitespace', 'singleline comment', 'multiline comment']:
            self.t = scanner.getToken()

    def eat(self, expected):
        if self.t == expected:
            self.t = self.scanner.getToken()
            while self.t.type in ['whitespace', 'singleline comment', 'multiline comment']:
                self.t = self.scanner.getToken()
        else:
            raise ValueError("Attempted to eat " + str(expected) + " but found " + str(self.t))

    def parse1(self): # grouping
        line = self.t.line
        if self.t == Token('operator', ';'):
            return self.eat(self.t)
        elif self.t == Token('( block opener', '('):
            self.eat(self.t)
            expression = self.parse7()
            self.eat(Token('( block closer', ')'))
            return expression
        elif self.t.type == 'variable':
            var = Variable(self.t.val)
            self.eat(self.t)
            if self.t.type == '( block opener':
                self.eat(self.t)
                params = []
                while self.t.type != '( block closer':
                    params.append(self.parse7())
                    if self.t.type != '( block closer':
                        self.eat(Token('operator', ','))
                self.eat(Token('( block closer', ')'))
                return Step(['exec', var, params], line)
            else:
                if self.t.type == 'special operator':
                    operator = self.t.val
                    self.eat(self.t)
                    return Step(['eval', var, operator, ''], line)
                elif self.t == Token('operator', '.'):
                    vars = [var]
                    while self.t.val == '.':
                        self.eat(self.t)
                        vars.append(Variable(self.t.val))
                        self.eat(self.t)
                        if self.t == Token('( block opener', '('):
                            self.eat(self.t)
                            params = []
                            while self.t != Token('( block closer', ')'):
                                params.append(self.parse7())
                                if self.t == Token('operator', ','):
                                    self.eat(self.t)
                                else:
                                    break
                            self.eat(Token('( block closer', ')'))
                            vars[-1] = (vars[-1], params)
                    if type(vars[0]) == tuple: vars[0] = Step(['exec', vars[0][0], vars[0][1]])
                    var = Step(['dot', vars[0], vars[1]], line)
                    if type(vars[1]) == tuple:
                        params = var[2][1]
                        var[2] = var[2][0]
                        var = Step(['exec', var, params], line)

                    for v in vars[::-1][:-2]:
                        if type(v) == tuple:
                            var = Step(['exec', Step(['dot', var, v[0]], line), v[1]], line)
                        else:
                            var = Step(['dot', var, v], line)
                return var
        elif self.t == Token('operator', '!'):
            self.eat(self.t)
            return Step(['eval', '', 'not', self.parse1()], line)
        elif self.t == Token('key word', 'new'):
            self.eat(self.t)
            objectName = self.t.val
            self.eat(self.t)
            self.eat(Token('( block opener', '('))
            params = []
            while self.t.type != '( block closer':
                params.append(self.parse7())
                if self.t.type != '( block closer':
                    self.eat(Token('operator', ','))
            self.eat(Token('( block closer', ')'))
            return Step(['new', objectName, params], line)
        else:
            if self.t.type == 'int':
                val = Value(int(self.t.val), 'int')
            elif self.t.type == 'double':
                val = Value(float(self.t.val), 'double')
            elif self.t.type == 'boolean':
                val = Value(False if self.t.val == 'false' else True, 'boolean')
            elif self.t.type == 'char':
                val = Value(str(self.t.val)[1], 'char')
            elif self.t.type == 'String':
                val = Value(str(self.t.val)[1:-1], 'String')
            else:
                val = Value(self.t.val, 'Object')
            self.eat(self.t)
            return val
        t = self.t
        self.eat(self.t)
        return t

    def parse2(self): # multiplicative operators
        line = self.t.line
        factor = self.parse1()
        while self.t.type == 'operator' and self.t.val in ['*', '/', '%']:
            operator = self.t.val
            self.eat(self.t)
            factor = Step(['eval', factor, operator, self.parse1()], line)
        return factor

    def parse3(self): # additive operators
        line = self.t.line
        term = self.parse2()
        while self.t.type == 'operator' and self.t.val in ['+', '-']:
            operator = self.t.val
            self.eat(self.t)
            term = Step(['eval', term, operator, self.parse2()], line)
        return term

    def parse4(self): # relational operators
        line = self.t.line
        term = self.parse3()
        while self.t.type == 'operator' and self.t.val in ['<', '>', '<=', '>=']:
            operator = self.t.val
            self.eat(self.t)
            term = Step(['eval', term, operator, self.parse3()], line)
        return term

    def parse5(self): # equality operators
        line = self.t.line
        term = self.parse4()
        while self.t.type == 'operator' and self.t.val in ['==', '!=']:
            operator = self.t.val
            self.eat(self.t)
            term = Step(['eval', term, operator, self.parse4()], line)
        return term

    def parse6(self): # and operator
        line = self.t.line
        term = self.parse5()
        while self.t == Token('operator', '&&'):
            self.eat(self.t)
            term = Step(['eval', term, 'and', self.parse5()], line)
        return term

    def parse7(self): # or operator
        line = self.t.line
        term = self.parse6()
        while self.t == Token('operator', '||'):
            self.eat(self.t)
            term = Step(['eval', term, 'or', self.parse6()], line)
        return term

    def parseBlock(self): # method/statement body
        line = self.t.line
        if self.t == Token('{ block opener', '{'):
            self.eat(self.t)
            steps = []
            while self.t != Token('{ block closer', '}'):
                block = self.parseBlock()
                for step in block:
                    steps.append(step)
            self.eat(self.t)
            return steps
        elif self.t.type == 'statement opener':
            statementType = self.t.val
            self.eat(self.t)

            if statementType == 'if':
                self.eat(Token('( block opener', '('))
                condition = self.parse7()
                self.eat(Token('( block closer', ')'))
                body = self.parseBlock()

                if self.t == Token('statement opener', 'else'):
                    self.eat(self.t)
                    if self.t == Token('statement opener', 'if'):
                        self.eat(self.t)
                        self.eat(Token('( block opener', '('))
                        condition2 = self.parse7()
                        self.eat(Token('( block closer', ')'))
                        body2 = self.parseBlock()

                        if self.t == Token('statement opener', 'else'):
                            self.eat(self.t)
                            return [Step(['if', condition, body, [
                                Step(['if', condition2, body2, self.parseBlock()], line)
                            ]], line)]
                        else:
                            return [Step(['if', condition, body, [
                                Step(['if', condition2, body2], line)
                            ]], line)]
                    else:
                        return [Step(['if', condition, body, self.parseBlock()], line)]
                else:
                    return [Step(['if', condition, body], line)]
            elif statementType == 'for':
                self.eat(Token('( block opener', '('))
                itype = self.t.val
                self.eat(self.t)
                iname = self.t.val
                self.eat(self.t)
                self.eat(Token('assignment operator', '='))
                istartval = self.parse7()
                self.eat(Token('operator', ';'))
                endcondition = self.parse7()
                self.eat(Token('operator', ';'))
                iadvancer = self.parse1()
                self.eat(Token('( block closer', ')'))
                body = self.parseBlock()
                return [Step(['for', Variable(iname, itype), istartval, endcondition, iadvancer, body], line)]
            elif statementType == 'while':
                self.eat(Token('( block opener', '('))
                condition = self.parse7()
                self.eat(Token('( block closer', ')'))
                body = self.parseBlock()
                return [Step(['while', condition, body], line)]
            elif statementType == 'do':
                body = self.parseBlock()
                self.eat(Token('statement opener', 'while'))
                self.eat(Token('( block opener', '('))
                condition = self.parse7()
                self.eat(Token('( block closer', ')'))
                self.eat(Token('operator', ';'))
                return [*body, Step(['while', condition, body], line)]
            else:
                raise ValueError(f"Parsing Error: Invalid Token '{self.t}'")
        elif self.t == Token('key word', 'return'):
            self.eat(self.t)
            if self.t == Token('operator', ';'):
                self.eat(self.t)
                return [Step(['return', Value(None, 'Object')], line)]
            else:
                val = self.parse7()
                self.eat(Token('operator', ';'))
                return [Step(['return', val], line)]
        else:
            if self.t.type == 'access modifier':
                self.eat(self.t)

            static = False
            if self.t == Token('var modifier', 'static'):
                self.eat(self.t)
                static = True

            final = False
            if self.t == Token('var modifier', 'final'):
                self.eat(self.t)
                final = True

            t1 = self.t

            if t1.type == 'type': # definition
                self.eat(self.t)
                if self.t == Token('( block opener', '('):
                    varname = t1.val
                else:
                    varname = self.t.val
                    self.eat(self.t)
                    
                if self.t == Token('operator', ';'):
                    self.eat(self.t)
                    return [Step(['def', Variable(varname, t1.val, static, final)], line)]
                elif self.t.type == 'assignment operator':
                    operator = self.t.val
                    self.eat(self.t)
                    val = self.parse7()
                    self.eat(Token('operator', ';'))
                    var = Variable(varname, t1.val, static, final)
                    steps = [Step(['def', var], line)]
                    if len(operator) == 1:
                        steps.append(Step(['set', var, val], line))
                    else:
                        steps.append(Step(['set', var, Step(['eval', var, operator[0], val], line)], line))
                    return steps
                elif self.t == Token('( block opener', '('):
                    self.eat(self.t)
                    params = []
                    while self.t != Token('( block closer', ')'):
                        type = self.t.val
                        self.eat(self.t)
                        name = self.t.val
                        self.eat(self.t)
                        params.append(Variable(name, type))
                        if self.t == Token('operator', ','):
                            self.eat(self.t)
                        else:
                            break
                    self.eat(Token('( block closer', ')'))
                    return [Step(['defmethod', Variable(varname, t1.val, static, final), params, self.parseBlock(), static, final], line)]
            
            t1 = self.parse1()
            if self.t.type == 'assignment operator': # assignment
                operator = self.t.val
                self.eat(self.t)
                val = self.parse7()
                self.eat(Token('operator', ';'))
                if len(operator) == 1:
                    return [Step(['set', t1, val], line)]
                else:
                    return [Step(['set', t1, Step(['eval', t1, operator[0], val], line)], line)]
            else: # method call
                self.eat(Token('operator', ';'))
                return [Step(['exec', t1], line)]

        raise SyntaxError(f"Could not parse Block, t={self.t}")

    def parse(self, win):
        try:
            if self.t.type == 'access modifier':
                self.eat(self.t)
            self.eat(Token('key word', 'class'))
            if self.t.type != 'type':
                raise ValueError(f"Parsing Error: Invalid Token: expected valid class name got '{self.t}'")
            self.className = self.t.val
            self.eat(self.t)
            
            steps = self.parseBlock()

            steps.append(Step(['eof'], self.t.line))

            self.eat(Token('end of file', 'EOF'))

            return Program(self.className, steps, win)
        except Exception as e:
            tbobject = sys.exc_info()[2]
            lines = f"First Parse failed with a{'n' if type(e).__name__[0] in 'aeiouAEIOU' else ''} {type(e).__name__}: {e} at line {self.t.line}"
            while tbobject is not None:
                lines += f"\n    At file '{os.path.basename(tbobject.tb_frame.f_code.co_filename)}' in method '{tbobject.tb_frame.f_code.co_name}' at line {tbobject.tb_lineno}"
                tbobject = tbobject.tb_next
            win.popupdialog = lines
            win.popuptype = "error"