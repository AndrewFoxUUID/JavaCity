import os, sys

from value import Value
from variable import Variable
from method import *
from environment import Environment
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
        this = program.scope[Variable('this', program.name)]
        try:
            for step in self.program.body:
                self.execute_step(step, this.env, False)
        except Exception as e:
            tbobject = sys.exc_info()[2]
            lines = f"Secondary Parsing failed with a{'n' if type(e).__name__[0] in 'aeiouAEIOU' else ''} {type(e).__name__}: {e} {'at line' if type(self.line) == int else 'in'} {self.line}"
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

        if isinstance(step, Step) and type(step.line) == int:
            self.line = step.line
            self.win.highlight_row = self.line
        self.win.update()

        if self.ret == True:
            return step
        elif isinstance(step, Variable):
            if step.name == self.program.name:
                return self.execute_step(scope[Variable('this', self.program.name)], scope, static)
            else:
                return self.execute_step(scope[step], scope, static)
        elif isinstance(step, Step):
            if step[0] == 'defmethod':
                try:
                    scope.define(step[1])
                    scope[step[1]] = MethodSet(step[1])
                except Exception:
                    pass
                return scope[step[1]].add(Method(step[1], step[2], step[3], step[4], step[5]))
            elif step[0] == 'def':
                if type(step[1]) == Variable:
                    self.win.stack[step[1].name] = 'null'
                return scope.define(step[1])
            elif step[0] == 'set':
                val = self.execute_step(step[2], scope, static)
                scope[step[1]] = val
                if type(step[1]) == Variable:
                    self.win.stack[step[1].name] = str(val)
                return val
            elif step[0] == 'eval':
                term1 = self.execute_step(step[1], scope, static)
                term2 = self.execute_step(step[3], scope, static)

                if step[2] == 'not':
                    return Value(not term2, 'boolean')
                elif step[2] == '*':
                    return term1 * term2
                elif step[2] == '/':
                    return term1 / term2
                elif step[2] == '%':
                    return term1 % term2
                elif step[2] == '+':
                    return term1 + term2
                elif step[2] == '-':
                    return term1 - term2
                elif step[2] == '<':
                    return term1 < term2
                elif step[2] == '>':
                    return term1 > term2
                elif step[2] == '<=':
                    return term1 <= term2
                elif step[2] == '>=':
                    return term1 >= term2
                elif step[2] == '==':
                    return term1 == term2
                elif step[2] == '!=':
                    return term1 != term2
                elif step[2] == 'and':
                    return term1 and term2
                elif step[2] == 'or':
                    return term1 or term2
                elif step[2] == '++':
                    term1 += Value(1, 'int')
                    return term1
                elif step[2] == '--':
                    term1 -= Value(1, 'int')
                    return term1
            elif step[0] == 'exec':
                if len(step) == 3:
                    params = [self.execute_step(param, scope, static) for param in step[2]]
                    s = step[1]
                    e = scope
                    if isinstance(s, Step):
                        olds = s
                        s = self.execute_step(s, e, static)
                        if olds[0] == 'dot':
                            e = self.execute_step(olds[1], e, static).env
                    if isinstance(s, MethodSet):
                        s = s[s.name, params]
                    if isinstance(s, Method):
                        return self.execute_method(s, params, e, s.static)
                    return self.execute_method(e[s, params], params, e, e[s, params].static)
                elif len(step) == 2:
                    return self.execute_step(step[1], scope, static)
            elif step[0] == 'new':
                addr = self.win.get_next_address()
                newobj = Object(step[1], Environment(scope, {}), addr)
                self.win.heap[addr] = newobj
                newobj.env.define(Variable('this', step[1]))
                newobj.env[Variable('this', step[1])] = Environment(newobj.env, {})
                scope = newobj.env[Variable('this', step[1])]

                if step[1] == self.program.name:
                    for s in self.program.body:
                        self.execute_step(s, scope, False)

                params = []
                for param in step[2]:
                    params.append(self.execute_step(param, scope, False))

                method = newobj.env[Variable(step[1], step[1]), params]
                self.execute_method(method, params, scope, False)

                return newobj
            elif step[0] == 'return':
                val = self.execute_step(step[1], scope, static)
                self.ret = True
                return val
            elif step[0] == 'print':
                val = self.execute_step(step[1], scope, static)
                self.win.popupdialog = str(val)
                self.win.popuptype = "message"
                self.waiting = True
                return
            elif step[0] == 'dot':
                parent = self.execute_step(step[1], scope, static)
                try:
                    child = parent.env[Variable('this')][step[2]]
                except UnboundLocalError:
                    child = parent.env[step[2]]
                return child
            elif step[0] == 'if':
                condition = self.execute_step(step[1], scope, static)
                if condition:
                    for s in step[2]:
                        val = self.execute_step(s, scope, static)
                        if self.ret == True:
                            return val
                elif len(step) == 4:
                    for s in step[3]:
                        val = self.execute_step(s, scope, static)
                        if self.ret == True:
                            return val
            elif step[0] == 'for':
                env = Environment(scope, {})
                env.define(step[1])
                env[step[1]] = self.execute_step(step[2], scope, static)
                while self.execute_step(step[3], env, static):
                    for s in step[5]:
                        val = self.execute_step(s, scope, static)
                        if self.ret == True:
                            return val
                    env[step[1]] = self.execute_step(step[4], env, static)
                return
            elif step[0] == 'while':
                env = Environment(scope, {})
                while self.execute_step(step[1], env, static):
                    for s in step[2]:
                        val = self.execute_step(s, env, static)
                        if self.ret == True:
                            return val
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
                if method.name.name == self.program.name:
                    raise GeneratorExit(f"Attempted to return out of constructor")
                self.ret = False
                return val

            if not self.executing: self.waiting = True

        return Value(None, 'Object')
