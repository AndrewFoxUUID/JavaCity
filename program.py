import os, sys

from environment import Environment
from object import Object
from variable import Variable
from execute import Executor

class Program():

    def __init__(self, name, body, win):
        self.name = name
        self.body = body
        self.win = win

        self.scope = Environment(None, {})
        self.scope.define(Variable('this', self.name))
        self.scope[Variable('this', self.name)] = Object(name, Environment(self.scope, {}))
        self.executor = Executor(self, win)

    def start(self, execute=False):
        try:
            this = self.scope[Variable('this', self.name)]
            self.win.message = "executing"
            self.win.heap = {}
            self.win.stack = {}
            self.executor.executing = execute
            if this.env.contains(Variable("main", "void")):
                self.executor.execute_method(this.env[Variable("main", "void")][Variable("main", "void"), []], [], Environment(this, {}), True)
            self.executor.finished = True
            self.win.message = "finished"
        except Exception as e:
            tbobject = sys.exc_info()[2]
            lines = f"Execution failed with a{'n' if type(e).__name__[0] in 'aeiouAEIOU' else ''} {type(e).__name__}: {e} {'at line' if type(self.executor.line) == int else 'in'} {self.executor.line}"
            while tbobject is not None:
                lines += f"\n    At file '{os.path.basename(tbobject.tb_frame.f_code.co_filename)}' in method '{tbobject.tb_frame.f_code.co_name}' at line {tbobject.tb_lineno}"
                tbobject = tbobject.tb_next
            self.win.popupdialog = lines
            self.win.popuptype = "error"
            self.executor.waiting = True

    def step(self):
        self.executor.waiting = False

    def __str__(self):
        s = self.name + "\n\n"
        for line in self.body:
            s += str(line) + "\n"
        return s