import pygame, re

class Token():

    def __init__(self, type, val, line=None, pallete=[]):
        self.type = type
        self.val = val
        self.line = line
        self.pallete = pallete

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return self.type == other.type and self.val == other.val

    def __str__(self):
        return self.type.upper() + "_" + str(self.val)

    def color(self):
        return pygame.Color(self.pallete[self.type])

lcaseLetters = 'abcdefghijklmnopqrstuvwxyz_'
ucaseLetters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
numbers = '1234567890'
operators = '=+-*/%!<>&|?:.;,'
whitespace = ' \t\r\n'
openers = '([{'
closers = ')]}'
stringOpeners = '"'
charOpeners = "'"
specialOperators = ['++', '--']
assignmentOperators = ['=', '+=', '-=', '*=', '/=', '%=']
accessKeyWords = ['public', 'private', 'protected']
keyWords = ['new', 'break', 'return', 'class', 'null', 'throw']
statementKeyWords = ['do', 'while', 'for', 'if', 'else']
varModifierKeyWords = ['static', 'final']
typeKeyWords = ['int', 'Integer', 'double', 'Double', 'boolean', 'Boolean', 'char', 'Character', 'String', 'void']
booleanKeyWords = ['true', 'false']

class Scanner():

    def __init__(self, code, pallete):
        self.code = '\n'.join(code)
        self.pos = 0
        self.eof = len(self.code) < 1
        self.line = 1
        self.pallete = pallete["lexeme colors"]

    def eat(self, char):
        if self.code[self.pos] == char:
            if char == '\n':
                self.line += 1
            self.pos += 1
            if self.pos >= len(self.code):
                self.eof = True
        else:
            raise ValueError("Scanning Error: Eat expected " + self.code[self.pos] + " but recieved " + char)

    def getToken(self):
        if self.eof:
            return Token('end of file', 'EOF', self.line, self.pallete)

        token = self.code[self.pos]
        char = self.code[self.pos]
        type = ''
        pattern = None

        if char == '/':
            pattern = '.*$'
            type = 'ambiguous'
        elif char in lcaseLetters + ucaseLetters:
            pattern = '[' + lcaseLetters + ucaseLetters + numbers + ']*$'
            type = 'variable'
        elif char in numbers:
            pattern = '[' + numbers + ']*\.?[' + numbers + ']*$'
            type = 'int'
        elif char in stringOpeners:
            pattern = '.*$'
            type = 'String'
        elif char in charOpeners:
            pattern = ".$"
            type = 'char'
        elif char in operators:
            if char == '=':
                pattern = '[=]$'
            elif char == '+':
                pattern = '[+=]$'
            elif char == '-':
                pattern = '[-=' + numbers + ']$'
            elif char == '*':
                pattern = '[=]$'
            elif char == '%':
                pattern = '[=]$'
            elif char == '!':
                pattern = '[=]$'
            elif char == '<':
                pattern = '[=]$'
            elif char == '>':
                pattern = '[=]$'
            elif char == '&':
                pattern = '&$'
            elif char == '|':
                pattern = '|$'
            type = 'operator'
        elif char in openers:
            type = char + ' block opener'
        elif char in closers:
            type = {')':'(',']':'[','}':'{'}[char] + ' block closer'
        elif char in whitespace:
            type = 'whitespace'
        else:
            c = char
            self.eat(char)
            return Token('invalid', c, self.line, self.pallete)

        self.eat(char)
        if self.eof: return Token(type if type != 'ambiguous' else 'operator', token, self.line, self.pallete)
        char = self.code[self.pos]

        if type == 'ambiguous':
            if char == '*':
                type = 'multiline comment'
            elif char == '/':
                type = 'singleline comment'
            else:
                type = 'operator'
                pattern = '[=]$'

        while pattern is not None and re.match(pattern, char):
            token += char

            if type == 'String' and token[-1] != '\\' and char == '"':
                self.eat(char)
                break
            if type == 'char':
                self.eat(char)
                if len(self.code) > self.pos and self.code[self.pos] == "'":
                    token += "'"
                    self.eat("'")
                    break
                else:
                    self.pos -= 1
                    type = 'invalid'
            elif type == 'operator':
                self.eat(char)
                break
            elif type == 'singleline comment' and char == '\n':
                self.eat(char)
                break
            elif type == 'multiline comment' and token[-2:] == '*/':
                self.eat(char)
                break

            self.eat(char)
            if self.eof: return Token(type, token, self.line, self.pallete)
            char = self.code[self.pos]

        if token in accessKeyWords:
            type = 'access modifier'
        elif token in keyWords:
            type = 'key word'
            if token == 'null':
                token = None
        elif token in statementKeyWords:
            type = 'statement opener'
        elif token in varModifierKeyWords:
            type = 'var modifier'
        elif token in typeKeyWords:
            type = 'type'
        elif token in specialOperators:
            type = 'special operator'
        elif token in assignmentOperators:
            type = 'assignment operator'
        elif token in booleanKeyWords:
            type = 'boolean'
        elif token[0] == '-' and len(token) > 1 and token[1] not in '-=':
            type = 'int'
        if type == 'int' and '.' in token:
            type = 'double'

        if type == 'variable' and len(typeKeyWords) == 10:
            type = 'type'
            typeKeyWords.append(token)

        return Token(type, token, self.line, self.pallete)

    def read(self):
        lexemes = []
        while not self.eof:
            lexemes.append(self.getToken())
        return lexemes