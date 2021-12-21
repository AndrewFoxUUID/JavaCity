import os, sys

from environment import Environment
from object import Object
from variable import Variable
from execute import Executor

class Program(Object):

    def __init__(self, name, body, win):
        super().__init__(name, Environment(None, {}))
        self.body = body
        self.win = win

        self.env.define(Variable('this', name))
        self.env[Variable('this', name)] = self.env
        self.executor = Executor(self, win)

    def start(self, execute=False):
        try:
            this = self.env[Variable('this', self.type)]
            self.win.message = "executing"
            self.win.heap = {}
            self.win.stack = {}
            self.executor.executing = execute
            if this.contains(Variable("main", "void")):
                self.executor.execute_method(this[Variable("main", "void")][Variable("main", "void"), []], [], Environment(this, {}), True)
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
        s = self.type + "\n\n"
        for line in self.body:
            s += str(line) + "\n"
        return s