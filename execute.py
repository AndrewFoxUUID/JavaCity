import os, sys

from value import Value
from variable import Variable
from method import *
from environment import *
from step import Step
from object import Object
from write import *

class Executor():

    def __init__(self, program, win):
        self.program = program
        self.ret = False
        self.line = 0
        self.finished = False
        self.waiting = False
        self.executing = False

        self.win = win
        this = program.env[Variable('this', program.type)]
        try:
            for step in self.program.body:
                self.execute_step(step, this, False)
        except Exception as e:
            tbobject = sys.exc_info()[2]
            lines = f"Secondary Parsing failed with a{'n' if type(e).__name__[0] in 'aeiouAEIOU' else ''} {type(e).__name__}: {e} 'at line' {self.line}"
            while tbobject is not None:
                lines += f"\n    At file '{os.path.basename(tbobject.tb_frame.f_code.co_filename)}' in method '{tbobject.tb_frame.f_code.co_name}' at line {tbobject.tb_lineno}"
                tbobject = tbobject.tb_next
            self.win.popupdialog = lines
            self.win.popuptype = "error"
            self.waiting = True

    def execute_step(self, step, scope, static):
        if self.finished: self.win.message="finished"; return

        while self.waiting:
            self.win.update()
        self.win.update()

        if isinstance(step, Step) and step.line is not None:
            self.line = step.line
            self.win.highlight_row = self.line
        self.win.update()

        if self.ret == True:
            return step
        elif isinstance(step, Variable):
            if step.name == self.program.type:
                return self.execute_step(scope[Variable('this', self.program.type)], scope, static)
            else:
                return self.execute_step(scope[step], scope, static)
        elif isinstance(step, Step):
            if step.action == 'defmethod':
                try:
                    scope.define(step.var0.name)
                    scope[step.var0.name] = MethodSet(step.var0.name)
                except Exception:
                    pass
                return scope[step.var0.name].add(step.var0)
            elif step.action == 'def':
                if type(step.var0) == Variable:
                    self.win.stack[step.var0.name] = 'null'
                return scope.define(step.var0)
            elif step.action == 'set':
                val = self.execute_step(step.arg, scope, static)
                scope[step.var0] = val
                if type(step.var0) == Variable:
                    self.win.stack[step.var0.name] = str(val)
                return val
            elif step.action == 'eval':
                term1 = self.execute_step(step.var0, scope, static)
                term2 = self.execute_step(step.var1, scope, static)

                if step.arg == 'not':
                    return Value(not term2, 'boolean')
                elif step.arg == '*':
                    return term1 * term2
                elif step.arg == '/':
                    return term1 / term2
                elif step.arg == '%':
                    return term1 % term2
                elif step.arg == '+':
                    return term1 + term2
                elif step.arg == '-':
                    return term1 - term2
                elif step.arg == '<':
                    return term1 < term2
                elif step.arg == '>':
                    return term1 > term2
                elif step.arg == '<=':
                    return term1 <= term2
                elif step.arg == '>=':
                    return term1 >= term2
                elif step.arg == '==':
                    return term1 == term2
                elif step.arg == '!=':
                    return term1 != term2
                elif step.arg == 'and':
                    return term1 and term2
                elif step.arg == 'or':
                    return term1 or term2
                elif step.arg == '++':
                    term1 += Value(1, 'int')
                    return term1
                elif step.arg == '--':
                    term1 -= Value(1, 'int')
                    return term1
            elif step.action == 'exec':
                if step.arg is not None:
                    params = [self.execute_step(param, scope, static) for param in step.arg]
                else:
                    params = []
                
                s = step.var0
                e = scope
                if isinstance(s, Step):
                    olds = s
                    s = self.execute_step(s, e, static)
                    if olds.action == 'dot':
                        e = self.execute_step(olds.var0, e, static).env
                        try:
                            e = e[Variable('this')]
                        except UnboundLocalError:
                            pass
                if isinstance(s, MethodSet):
                    s = s[s.name, params]
                if isinstance(s, Method):
                    return self.execute_method(s, params, e, s.static)
                return
            elif step.action == 'new':
                if Variable(step.var0) in javascope:
                    superclassenv = javascope[Variable(step.var0)].copyenv()
                elif step.var0 == self.program.type:
                    superclassenv = self.program.copyenv()
                else:
                    raise UnboundLocalError(f"Class not found: {step.var0}")

                addr = self.win.get_next_address()
                newobj = Object(step.var0, Environment(scope, superclassenv), addr)
                self.win.heap[addr] = newobj
                newobj.env.define(Variable('this', step.var0))
                newobj.env[Variable('this', step.var0)] = Environment(newobj.env, {})
                scope = newobj.env[Variable('this', step.var0)]

                params = []
                for param in step.arg:
                    params.append(self.execute_step(param, scope, False))

                method = newobj.env[Variable(step.var0, step.var0), params]
                self.execute_method(method, params, scope, False)

                return newobj
            elif step.action == 'return':
                val = self.execute_step(step.var0, scope, static)
                self.ret = True
                return val
            elif step.action == 'print':
                val = self.execute_step(step.var0, scope, static)
                self.win.popupdialog = str(val)
                self.win.popuptype = "message"
                self.waiting = True
                return
            elif step.action == 'dot':
                parent = self.execute_step(step.var0, scope, static)
                try:
                    child = parent.env[Variable('this')][step.arg]
                except UnboundLocalError:
                    child = parent.env[step.arg]
                return child
            elif step.action == 'if':
                condition = self.execute_step(step.var0, scope, static)
                if condition:
                    for s in step.arg:
                        val = self.execute_step(s, scope, static)
                        if self.ret == True:
                            return val
                elif step.var1 is not None:
                    for s in step.var1:
                        val = self.execute_step(s, scope, static)
                        if self.ret == True:
                            return val
            elif step.action == 'for':
                istartval, endcondition, iadvancer = step.arg
                env = Environment(scope, {})
                env.define(step.var0)
                env[step.var0] = self.execute_step(istartval, scope, static)
                while self.execute_step(endcondition, env, static):
                    for s in step.var1:
                        val = self.execute_step(s, scope, static)
                        if self.ret == True:
                            return val
                    env[step.var0] = self.execute_step(iadvancer, env, static)
                return
            elif step.action == 'while':
                env = Environment(scope, {})
                while self.execute_step(step.var0, env, static):
                    for s in step.arg:
                        val = self.execute_step(s, env, static)
                        if self.ret == True:
                            return val
            elif step.action == 'cast':
                if step.arg == 'int':
                    return int(self.execute_step(step.var0, scope, static))
                elif step.arg == 'Integer':
                    return self.execute_step(Step('new', 'Integer', [Value(int(self.execute_step(step.var0, scope, static)), 'int')]), scope, static)
                elif step.arg == 'double':
                    return float(self.execute_step(step.var0, scope, static))
                elif step.arg == 'Double':
                    return self.execute_step(Step('new', 'Double', [Value(float(self.execute_step(step.var0, scope, static)), 'double')]), scope, static)
                elif step.arg == 'boolean':
                    return bool(self.execute_step(step.var0, scope, static))
                elif step.arg == 'Boolean':
                    return self.execute_step(Step('new', 'Boolean', [Value(bool(self.execute_step(step.var0, scope, static)), 'boolean')]), scope, static)
                elif step.arg == 'char':
                    return str(self.execute_step(step.var0, scope, static))[0]
                elif step.arg == 'Character':
                    return self.execute_step(Step('new', 'Character', [Value(str(self.execute_step(step.var0, scope, static))[0], 'char')]), scope, static)
                elif step.arg == 'String':
                    return self.execute_step(Step('new', 'String', [Value(str(self.execute_step(step.var0, scope, static)), 'String')]), scope, static)
            elif step.action == 'length':
                return len(self.execute_step(step.var0, scope, static))
            elif step.action == 'substring':
                string = str(self.execute_step(step.var0, scope, static))[1:-1]
                start = int(self.execute_step(step.arg, scope, static))
                end = int(self.execute_step(step.var1, scope, static))
                return self.execute_step(Step('new', 'String', [Value(string[start:end], 'String')]), scope, static)
        return step

    def execute_method(self, method, params, upper, static):
        if self.finished: self.win.message="finished"; return

        if static == True and method.static == False:
            raise TypeError(f"Attempted to call non static method {method.name} in static method")

        scope = Environment(upper, {})
        for i, param in enumerate(params):
            scope.define(method.args[i])
            scope[method.args[i]] = self.execute_step(param, upper, static)

        for step in method.body:
            while self.waiting:
                self.win.update()
            self.win.update()

            val = self.execute_step(step, scope, method.static)
            if self.ret == True:
                if method.name.name == self.program.type:
                    raise GeneratorExit(f"Attempted to return out of constructor")
                self.ret = False
                return val

            if not self.executing: self.waiting = True

        return Value(None, 'Object')
