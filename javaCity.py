import os, sys, pyperclip, json
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

from write import *
from scan import *
from parse import *
from method import MethodSet

DATADIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(__file__)

class JavaCity():

    def __init__(self):
        icon = pygame.image.load(os.path.join(DATADIR, "JavaCity.png"))
        pygame.display.set_icon(icon)

        f = open(os.path.join(DATADIR, "colorpallete.json"))
        self.COLORPALLETE = json.load(f)
        f.close()

        pygame.init()
        self.win = pygame.display.set_mode((1000, 500))
        # x breakdown: (0, 250)-code, (250,750)-heap, (750,1000)-stack
        pygame.display.set_caption("Java City")

        self.cursor_type = 'arrow'

        self.code_starting_point = [0, 0]
        self.code_bounding_box = pygame.Rect(0, 0, 250, 480)
        self.code = [""]
        self.highlight_row = None
        self.codeChanged = True
        self.cursor_pos = [0, 0]
        self.clicked_pos = None
        self.highlight_start = None
        self.highlight_end = None
        self.file_upload_rect = pygame.Rect(15, 482, 100, 16)
        self.file_upload = False
        self.file_download = False
        self.file_save_rect = pygame.Rect(135, 482, 100, 16)
        self.file_dialog_box = pygame.Surface((400, 120), pygame.SRCALPHA)
        self.file_path = ""
        self.file_path_start = 0
        self.file_path_cursor_pos = 0
        self.file_dialog_prompt_rect = pygame.Rect(320, 50, 360, 20)
        self.file_dialog_submit_rect = pygame.Rect(320, 85, 75, 18)
        self.file_dialog_cancel_rect = pygame.Rect(420, 85, 45, 18)

        self.continue_rect = pygame.Rect(400, 290, 90, 20)
        self.exit_rect = pygame.Rect(510, 290, 90, 20)

        self.heap_bounding_box = pygame.Rect(250, 0, 500, 480)
        self.heap_win = pygame.Surface((500, 480), pygame.SRCALPHA) # flexgrid layout
        self.heap_start = 0
        self.heap = {} # addresses stored as 0x00 hexidecimals, up to 256 objects can be stored simultaneously

        self.execute_rect = pygame.Rect(270, 482, 100, 16)
        self.step_rect = pygame.Rect(400, 482, 100, 16)

        self.stack_bounding_box = pygame.Rect(750, 0, 250, 500)
        self.stack_start = 0
        self.stack = {}

        self.popupdialog = None
        self.popuptype = "message"

        self.message = ""

        self.scanner = None
        self.parser = None
        self.program = None

        self.codemode = False
        self.codemode_button_rect = pygame.Rect(240, 240, 20, 20)
        self.overlay_layer = pygame.Surface((1000, 480), pygame.SRCALPHA)

        self.running = True
        self.tick = 0
        while self.running:
            self.update()

        pygame.quit()

    def update(self):
        self.tick += 1
        self.win.fill(pygame.Color(self.COLORPALLETE["base colors"]["code background"]))
        self.overlay_layer.fill((0, 0, 0, 0))

        if self.codeChanged:
            self.scanner = Scanner(self.code, self.COLORPALLETE)
            self.lexemes = self.scanner.read()

        if self.codemode:
            pygame.draw.rect(self.win, pygame.Color(self.COLORPALLETE["base colors"]["heap background"]), (990, 0, 10, 500))
        else:
            self.drawHeap()
            self.drawStack()
        self.drawCode()
        self.drawDialog()

        if self.popupdialog is not None:
            pygame.draw.rect(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["highlight"]), (200, 20, 600, 300), 0, 20)
            pygame.draw.rect(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["button panel"]), (200, 20, 600, 300), 1, 20)

            color = self.COLORPALLETE["base colors"]["button text"]
            if self.popuptype == "warning":
                color = self.COLORPALLETE["lexeme colors"]["warning"]
            if self.popuptype == "error":
                color = self.COLORPALLETE["lexeme colors"]["invalid"]

            linelen = 0
            line = 0
            for char in str(self.popupdialog):
                if char == '\n':
                    linelen = 0
                    line += 1
                    continue

                write(self.overlay_layer, char, (220 + linelen*6, 40 + line*14), color)

                linelen += 1
                if linelen >= 94:
                    linelen = 0
                    line += 1

            pygame.draw.rect(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["button background"]), self.continue_rect, 0, 6)
            write(self.overlay_layer, "continue", (421, 295), pygame.Color(self.COLORPALLETE["base colors"]["button text"]))
            pygame.draw.rect(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["button background"]), self.exit_rect, 0, 6)
            write(self.overlay_layer, "exit", (544, 295), pygame.Color(self.COLORPALLETE["base colors"]["button text"]))

        self.win.blit(self.overlay_layer, (0, 0))

        pygame.display.update()
        self.handleEvents()
        if self.tick >= 5000:
            self.tick -= 5000

    def drawCode(self):
        if self.codemode:
            self.code_bounding_box = pygame.Rect(0, 0, 990, 480)
            self.code_surface = pygame.Surface((990, 14*(len(self.code) + 10)), pygame.SRCALPHA)
            self.codemode_button_rect = pygame.Rect(980, 240, 20, 20)
            pygame.draw.circle(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["stack background"]), (990, 250), 10)
            pygame.draw.rect(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["highlight"]), (985, 249, 10, 2))
        else:
            self.code_bounding_box = pygame.Rect(0, 0, 250, 480)
            self.code_surface = pygame.Surface((250, 14*(len(self.code) + 10)), pygame.SRCALPHA)
            self.codemode_button_rect = pygame.Rect(240, 240, 20, 20)
            pygame.draw.circle(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["stack background"]), (250, 250), 10)
            pygame.draw.rect(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["highlight"]), (245, 249, 10, 2))
            pygame.draw.rect(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["highlight"]), (249, 245, 2, 10))

        self.code_surface.fill(pygame.Color(self.COLORPALLETE["base colors"]["code background"]))

        if type(self.highlight_row) == int:
            pygame.draw.rect(self.code_surface, pygame.Color(self.COLORPALLETE["base colors"]["highlight"]), (0, self.highlight_row*14 - 11, 250, 14))

        x, y = 0, 0
        for token in self.lexemes:
            for char in token.val:
                if char == '\n':
                    x = 0
                    y += 1
                else:
                    write(self.code_surface, char, (5 + 6*x, 5 + 14*y), token.color())
                    x += 1
        
        if self.highlight_start is not None and self.highlight_end is not None:
            if self.highlight_start[1] < self.highlight_end[1]:
                start = self.highlight_start
                end = self.highlight_end
            elif self.highlight_start[1] > self.highlight_end[1]:
                start = self.highlight_end
                end = self.highlight_start
            else:
                if self.highlight_start[0] <= self.highlight_end[0]:
                    start = self.highlight_start
                    end = self.highlight_end
                else:
                    start = self.highlight_end
                    end = self.highlight_start
            for r in range(start[1], end[1]+1):
                if r == start[1] and r == end[1]:
                    highlight = pygame.Surface(((end[0] - start[0])*6, 12), pygame.SRCALPHA)
                    highlight.fill((100, 100, 255, 100))
                    self.code_surface.blit(highlight, (5 + start[0]*6, 5 + r*14))
                elif r == start[1]:
                    highlight = pygame.Surface((self.code_surface.get_width() - (start[0]*6 + 5), 12), pygame.SRCALPHA)
                    highlight.fill((100, 100, 255, 100))
                    self.code_surface.blit(highlight, (5 + start[0]*6, 5 + r*14))
                elif r == end[1]:
                    highlight = pygame.Surface((end[0]*6 + 5, 12), pygame.SRCALPHA)
                    highlight.fill((100, 100, 255, 100))
                    self.code_surface.blit(highlight, (0, 5 + r*14))
                else:
                    highlight = pygame.Surface((self.code_surface.get_width(), 12), pygame.SRCALPHA)
                    highlight.fill((100, 100, 255, 100))
                    self.code_surface.blit(highlight, (0, 5 + r*14))

        if self.tick % 200 < 100 or self.file_upload or self.file_download: pygame.draw.line(self.code_surface, pygame.Color(self.COLORPALLETE["base colors"]["button text"]), (self.cursor_pos[0]*6 + 5, self.cursor_pos[1]*14 + 5), (self.cursor_pos[0]*6 + 5, self.cursor_pos[1]*14 + 16), 2)

        pygame.draw.rect(self.win, pygame.Color(self.COLORPALLETE["base colors"]["code background"]), self.code_bounding_box)
        self.win.blit(self.code_surface, self.code_starting_point)

        pygame.draw.rect(self.win, pygame.Color(self.COLORPALLETE["base colors"]["button panel"]), (0, 480, 990 if self.codemode else 750, 20))
        pygame.draw.rect(self.win, pygame.Color(self.COLORPALLETE["base colors"]["button background"]), self.file_upload_rect, 0, 4)
        write(self.win, "Upload File", (33, 485), pygame.Color(self.COLORPALLETE["base colors"]["button text"]))
        pygame.draw.rect(self.win, pygame.Color(self.COLORPALLETE["base colors"]["button background"]), self.file_save_rect, 0, 4)
        write(self.win, "Save File", (160, 485), pygame.Color(self.COLORPALLETE["base colors"]["button text"]))

        pygame.draw.rect(self.win, pygame.Color(self.COLORPALLETE["base colors"]["button text" if self.program is not None and self.program.executor.executing and not self.program.executor.finished else "button background"]), self.execute_rect, 0, 4)
        write(self.win, "Execute", (300, 485), pygame.Color(self.COLORPALLETE["base colors"]["button background" if self.program is not None and self.program.executor.executing and not self.program.executor.finished else "button text"]))
        pygame.draw.rect(self.win, pygame.Color(self.COLORPALLETE["base colors"]["button background"]), self.step_rect, 0, 4)
        write(self.win, "Step Once", (425, 485), pygame.Color(self.COLORPALLETE["base colors"]["button text"]))

        write(self.win, self.message, (670, 485), pygame.Color(self.COLORPALLETE["base colors"]["button background"]))

    def drawHeap(self):
        pygame.draw.rect(self.win, pygame.Color(self.COLORPALLETE["base colors"]["heap background"]), (250, 0, 750, 500))
        self.heap_win.fill(pygame.Color(self.COLORPALLETE["base colors"]["heap background"]))

        y_start = 10
        x_start = 10
        for address in self.heap:
            width, height = 0, 0
            lines = [address + " - " + self.heap[address].type]
            height += 14
            width = min(max(width, 40 + writtenlen(lines[-1])), 460)
            env = self.heap[address].env[Variable('this', 'Object')]
            for attr in env:
                if type(env[attr]) == MethodSet: continue
                lines.append(attr.name + " = " + str(env[attr]))
                height += 14
                width = min(max(width, 40 + writtenlen(lines[-1])), 460)

            if x_start + width + 30 > 500:
                x_start = 10
                y_start += height + 30

            pygame.draw.rect(self.heap_win, pygame.Color(self.COLORPALLETE["base colors"]["button panel"]), (x_start + 3, y_start + 3, width + 20, height + 20), 0, 8)
            pygame.draw.rect(self.heap_win, pygame.Color(self.COLORPALLETE["base colors"]["button background"]), (x_start, y_start, width + 20, height + 20), 0, 8)
            for i, line in enumerate(lines):
                write(self.heap_win, line, (x_start + 10, y_start + 10 + 14*i), pygame.Color(self.COLORPALLETE["base colors"]["button text"]))

            x_start += width + 30

        self.win.blit(self.heap_win, (250, self.heap_start))

    def get_next_address(self):
        chars = "0123456789ABCDEF"
        for i in range(256):
            addr = "0x" + chars[i//16] + chars[i%16]
            if addr not in self.heap.keys():
                return addr
        raise MemoryError("Ran out of Heap Space")

    def drawStack(self):
        pygame.draw.rect(self.win, pygame.Color(self.COLORPALLETE["base colors"]["stack background"]), self.stack_bounding_box)
        for i, var in enumerate(self.stack):
            write(self.win, str(var) + ": " + str(self.stack[var]), (755, 14*i + 3 + self.stack_start), pygame.Color(self.COLORPALLETE["base colors"]["button text"]))
            pygame.draw.line(self.win, pygame.Color(self.COLORPALLETE["base colors"]["highlight"]), (750, 14*i + 14 + self.stack_start), (1000, 14*i + 14 + self.stack_start))

    def drawDialog(self):
        if self.file_upload:
            self.file_dialog_box.fill((0, 0, 0, 0))
            pygame.draw.rect(self.file_dialog_box, pygame.Color(self.COLORPALLETE["base colors"]["highlight"]), (0, 0, 400, 120), 0, 4)
            write(self.file_dialog_box, "Enter File Path", (155, 20), pygame.Color(self.COLORPALLETE["base colors"]["button text"]))
            self.overlay_layer.blit(self.file_dialog_box, (300, 10))
            pygame.draw.rect(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["button background"]), self.file_dialog_prompt_rect, 0, 4)
            pygame.draw.rect(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["button text"]), self.file_dialog_prompt_rect, 1, 4)
            write(self.overlay_layer, self.file_path[self.file_path_start:59+self.file_path_start], (324, 54), pygame.Color(self.COLORPALLETE["base colors"]["button text"]))
            if self.tick % 200 < 100: pygame.draw.line(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["button text"]), ((self.file_path_cursor_pos-self.file_path_start)*6 + 324, 54), ((self.file_path_cursor_pos-self.file_path_start)*6 + 324, 65), 2)
            pygame.draw.rect(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["button background"]), self.file_dialog_submit_rect, 0, 4)
            pygame.draw.rect(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["button text"]), self.file_dialog_submit_rect, 1, 4)
            write(self.overlay_layer, "Upload File", (325, 89), pygame.Color(self.COLORPALLETE["base colors"]["button text"]))
            pygame.draw.rect(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["button background"]), self.file_dialog_cancel_rect, 0, 4)
            pygame.draw.rect(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["button text"]), self.file_dialog_cancel_rect, 1, 4)
            write(self.overlay_layer, "Cancel", (425, 89), pygame.Color(self.COLORPALLETE["base colors"]["button text"]))
        elif self.file_download:
            self.file_dialog_box.fill((0, 0, 0, 0))
            pygame.draw.rect(self.file_dialog_box, pygame.Color(self.COLORPALLETE["base colors"]["highlight"]), (0, 0, 400, 120), 0, 4)
            write(self.file_dialog_box, "Save as:", (180, 20), pygame.Color(self.COLORPALLETE["base colors"]["button text"]))
            self.overlay_layer.blit(self.file_dialog_box, (300, 10))
            pygame.draw.rect(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["button background"]), self.file_dialog_prompt_rect, 0, 4)
            pygame.draw.rect(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["button text"]), self.file_dialog_prompt_rect, 1, 4)
            write(self.overlay_layer, self.file_path[self.file_path_start:59+self.file_path_start], (324, 54), pygame.Color(self.COLORPALLETE["base colors"]["button text"]))
            if self.tick % 200 < 100: pygame.draw.line(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["button text"]), ((self.file_path_cursor_pos-self.file_path_start)*6 + 324, 54), ((self.file_path_cursor_pos-self.file_path_start)*6 + 324, 65), 2)
            pygame.draw.rect(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["button background"]), self.file_dialog_submit_rect, 0, 4)
            pygame.draw.rect(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["button text"]), self.file_dialog_submit_rect, 1, 4)
            write(self.overlay_layer, "Save File", (330, 89), pygame.Color(self.COLORPALLETE["base colors"]["button text"]))
            pygame.draw.rect(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["button background"]), self.file_dialog_cancel_rect, 0, 4)
            pygame.draw.rect(self.overlay_layer, pygame.Color(self.COLORPALLETE["base colors"]["button text"]), self.file_dialog_cancel_rect, 1, 4)
            write(self.overlay_layer, "Cancel", (425, 89), pygame.Color(self.COLORPALLETE["base colors"]["button text"]))

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEWHEEL:
                if self.code_bounding_box.collidepoint(pygame.mouse.get_pos()):
                    self.code_starting_point[1] += 2*event.y
                    if self.code_starting_point[1] > 0:
                        self.code_starting_point[1] = 0
                if not self.codemode and self.heap_bounding_box.collidepoint(pygame.mouse.get_pos()):
                    self.heap_start += 2*event.y
                    if self.heap_start > 0:
                        self.heap_start = 0
                if not self.codemode and self.stack_bounding_box.collidepoint(pygame.mouse.get_pos()):
                    self.stack_start += 2*event.y
                    if self.stack_start > 0:
                        self.stack_start = 0
            elif event.type == pygame.KEYDOWN:
                self.keydown(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mousebuttondown(event.pos, event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mousebuttonup(event.pos, event.button)
            elif event.type == pygame.MOUSEMOTION:
                if self.clicked_pos is not None:
                    self.cursor_pos = [max(0, (event.pos[0]-self.code_starting_point[0]-5)//6), max(0, (event.pos[1]-self.code_starting_point[1]-5)//14)]
                    self.highlight_end = self.cursor_pos

                if (self.code_bounding_box.collidepoint(event.pos) and not self.codemode_button_rect.collidepoint(event.pos)) or ((self.file_upload or self.file_download) and self.file_dialog_prompt_rect.collidepoint(event.pos)):
                    if self.cursor_type != 'text':
                        self.cursor_type = 'text'
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
                else:
                    if self.cursor_type != 'arrow':
                        self.cursor_type = 'arrow'
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            elif event.type == pygame.DROPFILE:
                f = open(event.file)
                self.code = [line.replace('\n', '') for line in f.readlines()]
                self.codeChanged = True
                f.close()
                self.cursor_pos = [0, 0]
                self.code_starting_point = [0, 0]

    def keydown(self, key):
        if key == pygame.K_RIGHT:
            if self.file_upload or self.file_download:
                self.file_path_cursor_pos += 1
                if self.file_path_cursor_pos >= len(self.file_path):
                    self.file_path_cursor_pos = len(self.file_path) - 1
            elif self.highlight_end is not None:
                self.cursor_pos = self.highlight_end
            else:
                self.cursor_pos[0] += 1
            if self.cursor_pos[1] > len(self.code) - 1:
                self.cursor_pos[1] = len(self.code) - 1
        elif key == pygame.K_LEFT:
            if self.file_upload or self.file_download:
                self.file_path_cursor_pos -= 1
                if self.file_path_cursor_pos < 0:
                    self.file_path_cursor_pos = 0
            elif self.highlight_start is not None:
                self.cursor_pos = self.highlight_start
            else:
                self.cursor_pos[0] -= 1
            if self.cursor_pos[0] < 0:
                self.cursor_pos[0] = 0
        elif key == pygame.K_UP:
            if not self.file_upload and not self.file_download:
                self.cursor_pos[1] -= 1
            if self.cursor_pos[1] < 0:
                self.cursor_pos[1] = 0
        elif key == pygame.K_DOWN:
            if not self.file_upload and not self.file_download:
                self.cursor_pos[1] += 1
            if self.cursor_pos[1] > len(self.code) - 1:
                self.cursor_pos[1] = len(self.code) - 1
        elif key == pygame.K_BACKSPACE:
            if self.file_upload or self.file_download:
                if self.file_path_cursor_pos > 0:
                    self.file_path = self.file_path[:self.file_path_cursor_pos-1] + self.file_path[self.file_path_cursor_pos:]
                    self.file_path_cursor_pos -= 1
            elif self.highlight_start is not None and self.highlight_end is not None:
                self.set_highlighted("")
            elif self.cursor_pos[0] == 0 and self.cursor_pos[1] > 0:
                start_pos = len(self.code[self.cursor_pos[1]-1])
                self.code[self.cursor_pos[1]-1] += self.code[self.cursor_pos[1]]
                self.code.pop(self.cursor_pos[1])
                self.cursor_pos[0] = start_pos
                self.cursor_pos[1] -= 1
            else:
                self.code[self.cursor_pos[1]] = self.code[self.cursor_pos[1]][:self.cursor_pos[0]-1] + self.code[self.cursor_pos[1]][self.cursor_pos[0]:]
                self.cursor_pos[0] -= 1
        elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
            if self.file_upload:
                try:
                    f = open(self.file_path)
                    self.code = [line.replace('\n', '') for line in f.readlines()]
                    self.codeChanged = True
                    f.close()
                    self.file_upload = False
                except Exception as e:
                    self.file_path = str(e)
                    self.file_path_cursor_pos = len(str(e))
            else:
                try:
                    f = open(self.file_path, "w")
                    for line in self.code: f.write(line + "\n")
                    f.close()
                    self.file_download = False
                except Exception as e:
                    self.file_path = str(e)
                    self.file_path_cursor_pos = len(str(e))
            if self.highlight_start is not None and self.highlight_end is not None:
                self.set_highlighted("\n")
            else:
                self.code.insert(self.cursor_pos[1] + 1, self.code[self.cursor_pos[1]][self.cursor_pos[0]:])
                self.code[self.cursor_pos[1]] = self.code[self.cursor_pos[1]][:self.cursor_pos[0]]
                self.cursor_pos[0] = 0
                self.cursor_pos[1] += 1
        elif key == pygame.K_TAB:
            if self.file_upload or self.file_download:
                self.file_path = self.file_path[:self.file_path_cursor_pos] + "    " + self.file_path[self.file_path_cursor_pos:]
                self.file_path_cursor_pos += 4
            elif pygame.key.get_pressed()[pygame.K_RSHIFT] or pygame.key.get_pressed()[pygame.K_LSHIFT]:
                if self.highlight_start is not None and self.highlight_end is not None:
                    if self.highlight_start[1] < self.highlight_end[1]:
                        start = self.highlight_start
                        end = self.highlight_end
                    else:
                        start = self.highlight_end
                        end = self.highlight_start
                    for r in range(start[1], end[1]+1):
                        if self.code[r][:4] == '    ':
                            self.code[r] = self.code[r][4:]
                else:
                    if self.code[self.cursor_pos[1]][:4] == '    ':
                        self.code[self.cursor_pos[1]] = self.code[self.cursor_pos[1]][4:]
            else:
                if self.highlight_start is not None and self.highlight_end is not None:
                    if self.highlight_start[1] < self.highlight_end[1]:
                        start = self.highlight_start
                        end = self.highlight_end
                    else:
                        start = self.highlight_end
                        end = self.highlight_start
                    for r in range(start[1], end[1]+1):
                        self.code[r] = '    ' + self.code[r]
                else:
                    self.code[self.cursor_pos[1]] = '    ' + self.code[self.cursor_pos[1]]
                    self.cursor_pos[0] += 4
        else:
            text = ''
            shift_held = pygame.key.get_pressed()[pygame.K_RSHIFT] or pygame.key.get_pressed()[pygame.K_LSHIFT]
            control_held = pygame.key.get_pressed()[pygame.K_RCTRL] or pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RMETA] or pygame.key.get_pressed()[pygame.K_LMETA]
            if control_held and key == pygame.K_c: return pyperclip.copy(self.get_highlighted())
            elif control_held and key == pygame.K_x: pyperclip.copy(self.get_highlighted());return self.set_highlighted("")
            elif control_held and key == pygame.K_v: text = pyperclip.paste() 
            elif key == pygame.K_SPACE: text = ' '
            elif key == pygame.K_EXCLAIM or key == pygame.K_1 and shift_held: text = '!'
            elif key == pygame.K_QUOTEDBL or key == pygame.K_QUOTE and shift_held: text = '"'
            elif key == pygame.K_QUOTE: text = '\''
            elif key == pygame.K_HASH or key == pygame.K_3 and shift_held: text = '#'
            elif key == pygame.K_DOLLAR or key == pygame.K_4 and shift_held: text = '$'
            elif key == pygame.K_AMPERSAND or key == pygame.K_7 and shift_held: text = '&'
            elif key == pygame.K_LEFTPAREN or key == pygame.K_9 and shift_held: text = '('
            elif key == pygame.K_RIGHTPAREN or key == pygame.K_0 and shift_held: text = ')'
            elif key == pygame.K_ASTERISK or key == pygame.K_8 and shift_held or key == pygame.K_KP_MULTIPLY: text = '*'
            elif key == pygame.K_PLUS or key == pygame.K_EQUALS and shift_held or key == pygame.K_KP_PLUS: text = '+'
            elif key == pygame.K_EQUALS or key == pygame.K_KP_EQUALS: text = '='
            elif key == pygame.K_LESS or key == pygame.K_COMMA and shift_held: text = '<'
            elif key == pygame.K_COMMA: text = ','
            elif key == pygame.K_UNDERSCORE or key == pygame.K_MINUS and shift_held: text = '_'
            elif key == pygame.K_MINUS or key == pygame.K_KP_MINUS: text = '-'
            elif key == pygame.K_GREATER or key == pygame.K_PERIOD and shift_held: text = '>'
            elif key == pygame.K_PERIOD or key == pygame.K_KP_PERIOD: text = '.'
            elif key == pygame.K_QUESTION or key == pygame.K_SLASH and shift_held: text = '?'
            elif key == pygame.K_SLASH or key == pygame.K_KP_DIVIDE: text = '/'
            elif key == pygame.K_COLON or key == pygame.K_SEMICOLON and shift_held: text = ':'
            elif key == pygame.K_SEMICOLON: text = ';'
            elif key == pygame.K_AT or key == pygame.K_2 and shift_held: text = '@'
            elif key == pygame.K_LEFTBRACKET and shift_held: text = '{'
            elif key == pygame.K_LEFTBRACKET: text = '['
            elif key == pygame.K_RIGHTBRACKET and shift_held: text = '}'
            elif key == pygame.K_RIGHTBRACKET: text = ']'
            elif key == pygame.K_BACKSLASH and shift_held: text = '|'
            elif key == pygame.K_BACKSLASH: text = '\\'
            elif key == pygame.K_CARET or key == pygame.K_6 and shift_held: text = '^'
            elif key == pygame.K_BACKQUOTE and shift_held: text = '~'
            elif key == pygame.K_BACKQUOTE: text = '`'
            elif key >= pygame.K_0 and key <= pygame.K_9: text = pygame.key.name(key)
            elif key >= pygame.K_a and key <= pygame.K_z: text = (pygame.key.name(key).upper() if shift_held else pygame.key.name(key))
            else: return

            if self.file_upload or self.file_download:
                self.file_path = self.file_path[:self.file_path_cursor_pos] + text.replace('\n', '') + self.file_path[self.file_path_cursor_pos:]
                self.file_path_cursor_pos += len(text)
            elif self.highlight_start is not None and self.highlight_end is not None:
                self.set_highlighted(text)
            else:
                if text.find('\n') != -1:
                    end = self.code[self.cursor_pos[1]][self.cursor_pos[0]:]
                    self.code[self.cursor_pos[1]] = self.code[self.cursor_pos[1]][:self.cursor_pos[0]] + text.split('\n')[0]
                    for i, line in enumerate(text.split('\n')[1:-1]):
                        self.code.insert(self.cursor_pos[1]+i+1, line)
                    self.code.insert(self.cursor_pos[1] + len(text.split('\n'))-1, text.split('\n')[-1] + end)
                else:
                    self.code[self.cursor_pos[1]] = self.code[self.cursor_pos[1]][:self.cursor_pos[0]] + text + self.code[self.cursor_pos[1]][self.cursor_pos[0]:]
                self.cursor_pos[0] += len(text)
                self.cursor_pos[1] += len(text.split('\n')) - 1
        
        if self.cursor_pos[1] < 0:
            self.cursor_pos[1] = 0
        if self.cursor_pos[1] > len(self.code) - 1:
            self.cursor_pos[1] = len(self.code) - 1
        if self.cursor_pos[0] > len(self.code[self.cursor_pos[1]]):
            self.cursor_pos[0] = len(self.code[self.cursor_pos[1]])
        if self.cursor_pos[0] < 0:
            self.cursor_pos[0] = 0
        self.codeChanged = True

    def get_highlighted(self):
        highlighted = ""
        if self.highlight_start is not None and self.highlight_end is not None:
            if self.highlight_start[1] < self.highlight_end[1]:
                start = self.highlight_start
                end = self.highlight_end
            elif self.highlight_start[1] > self.highlight_end[1]:
                start = self.highlight_end
                end = self.highlight_start
            else:
                if self.highlight_start[0] <= self.highlight_end[0]:
                    start = self.highlight_start
                    end = self.highlight_end
                else:
                    start = self.highlight_end
                    end = self.highlight_start
            for r in range(start[1], end[1]+1):
                if r == start[1] and r == end[1]:
                    highlighted += self.code[r][start[0]:end[0]+1]
                elif r == start[1]:
                    highlighted += self.code[r][start[0]:] + "\n"
                elif r == end[1]:
                    highlighted += self.code[r][:end[0]]
                else:
                    highlighted += self.code[r] + "\n"
        return highlighted

    def set_highlighted(self, text):
        if self.highlight_start is not None and self.highlight_end is not None:
            if self.highlight_start[1] < self.highlight_end[1]:
                start = self.highlight_start
                end = self.highlight_end
            elif self.highlight_start[1] > self.highlight_end[1]:
                start = self.highlight_end
                end = self.highlight_start
            else:
                if self.highlight_start[0] <= self.highlight_end[0]:
                    start = self.highlight_start
                    end = self.highlight_end
                else:
                    start = self.highlight_end
                    end = self.highlight_start
            for r in list(range(start[1], end[1]+1))[::-1]:
                if r == start[1] and r == end[1]:
                    self.code[r] = self.code[r][:start[0]] + self.code[r][end[0]:]
                elif r == start[1]:
                    self.code[r] = self.code[r][:start[0]]
                elif r == end[1]:
                    self.code[r] = self.code[r][end[0]:]
                    if len(self.code[r]) == 0: self.code.pop(r)
                else:
                    self.code.pop(r)
            self.cursor_pos = start
            text = text.split('\n')
            self.code[start[1]] = self.code[start[1]][:start[0]] + text[0] + self.code[start[1]][start[0]:]
            self.cursor_pos[0] += len(text[0])
            for line in text[1:][::-1]:
                self.code.insert(start[1]+1, line)
                self.cursor_pos[0] = len(line)
        self.highlight_start, self.highlight_end = None, None

    def mousebuttondown(self, pos, button):
        if button == 1:
            self.highlight_start, self.highlight_end = None, None
            if self.file_upload or self.file_download:
                if self.file_dialog_prompt_rect.collidepoint(pos):
                    self.file_path_cursor_pos = (pos[0] - 324) // 6 + self.file_path_start
                    if self.file_path_cursor_pos >= len(self.file_path):
                        self.file_path_cursor_pos = len(self.file_path)
                elif self.file_dialog_submit_rect.collidepoint(pos):
                    try:
                        if self.file_upload:
                            f = open(self.file_path)
                            self.code = [line.replace('\n', '') for line in f.readlines()]
                            self.codeChanged = True
                            f.close()
                            self.file_upload = False
                        else:
                            f = open(self.file_path, "w")
                            for line in self.code: f.write(line + "\n")
                            f.close()
                            self.file_download = False
                    except Exception as e:
                        self.file_path = str(e)
                        self.file_path_cursor_pos = len(str(e))
                elif self.file_dialog_cancel_rect.collidepoint(pos):
                    self.file_upload = False
                    self.file_download = False
            elif self.codemode_button_rect.collidepoint(pos) and (self.popupdialog is None or self.codemode):
                self.codemode = not self.codemode
            elif self.code_bounding_box.collidepoint(pos):
                self.clicked_pos = [max(0, (pos[0]-self.code_starting_point[0]-5)//6), max(0, (pos[1]-self.code_starting_point[1]-5)//14)]
                self.highlight_start = self.clicked_pos
            elif self.file_upload_rect.collidepoint(pos):
                self.file_upload = True
            elif self.file_save_rect.collidepoint(pos):
                self.file_download = True
            elif self.execute_rect.collidepoint(pos):
                self.popupdialog = None
                if self.program is None or self.program.executor.finished:
                    self.scanner = Scanner(self.code, self.COLORPALLETE)
                    self.parser = Parser(self.scanner)
                    self.program = self.parser.parse(self)
                    if self.program is not None: self.program.start(True)

                if self.program is not None and not self.program.executor.finished: self.program.step()
            elif self.step_rect.collidepoint(pos):
                self.popupdialog = None
                if self.program is None or self.program.executor.finished:
                    self.scanner = Scanner(self.code, self.COLORPALLETE)
                    self.parser = Parser(self.scanner)
                    self.program = self.parser.parse(self)
                    if self.program is not None: self.program.start(False)

                if self.program is not None: self.program.step()
            elif self.popupdialog is not None and self.continue_rect.collidepoint(pos):
                self.popupdialog = None
                if self.program is not None: self.program.executor.waiting = False
            elif self.popupdialog is not None and self.exit_rect.collidepoint(pos):
                self.popupdialog = None
                if self.program is not None: self.program.executor.finished = True
                self.message = "terminated"

    def mousebuttonup(self, pos, button):
        if button == 1:
            if self.clicked_pos is not None and not self.file_upload and not self.file_download:
                pos = [max(0, (pos[0]-self.code_starting_point[0]-5)//6), max(0, (pos[1]-self.code_starting_point[1]-5)//14)]
                if pos == self.clicked_pos:
                    self.cursor_pos = pos
                else:
                    if pos[1] < self.clicked_pos[1]:
                        self.highlight_start = pos
                        self.highlight_end = self.clicked_pos
                    elif pos[1] > self.clicked_pos[1]:
                        self.highlight_start = self.clicked_pos
                        self.highlight_end = pos
                    else:
                        if pos[0] < self.clicked_pos[0]:
                            self.highlight_start = pos
                            self.highlight_end = self.clicked_pos
                        else:
                            self.highlight_start = self.clicked_pos
                            self.highlight_end = pos
                    self.cursor_pos = self.highlight_end

        if self.cursor_pos[1] < 0:
            self.cursor_pos[1] = 0
        if self.cursor_pos[1] > len(self.code) - 1:
            self.cursor_pos[1] = len(self.code) - 1
        if self.cursor_pos[0] > len(self.code[self.cursor_pos[1]]):
            self.cursor_pos[0] = len(self.code[self.cursor_pos[1]])
        if self.cursor_pos[0] < 0:
            self.cursor_pos[0] = 0
        self.clicked_pos = None

if __name__ == "__main__":
    JavaCity()