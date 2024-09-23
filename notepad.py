#!/usr/bin/env python3

import code
import io
import sys

from textual.app import App, on
from textual.containers import Horizontal
from textual.widgets import Footer, Header, TextArea

def execute_code_lines(code_lines):
    code_lines_merged = []
    i = 0
    while i < len(code_lines):
        line = code_lines[i]
        i += 1
        while i < len(code_lines) and (code_lines[i].startswith(' ') or code_lines[i].startswith('\t')):
            line += '\n' + code_lines[i]
            i += 1
        code_lines_merged.append(line)
    code_lines = code_lines_merged

    interpreter = code.InteractiveInterpreter()
    buffer = ''
    ret = []
    for line in code_lines:
        buffer += line + '\n'
        stdout = io.StringIO()
        stderr = io.StringIO()
        sys.stdout = stdout
        sys.stderr = stderr
        more = interpreter.runsource(buffer)
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        ret.extend([('', '')] * line.count('\n'))
        if more:
            ret.append(('', ''))
            continue
        output = stdout.getvalue().strip()
        error_output = stderr.getvalue().strip()
        ret.append((output, error_output))
        buffer = ''
    return ret

class Notepad(App):
    CSS_PATH = 'notepad.tcss'

    def compose(self):
        yield Header()
        yield Footer()
        yield Horizontal(
            TextArea(id='main_text_area', show_line_numbers=True, language='python'),
            TextArea(id='output_text_area', soft_wrap=False, read_only=True)
        )

    @on(TextArea.Changed, '#main_text_area')
    def execute_code(self, event: TextArea.Changed):
        output_text_area = self.query_one('#output_text_area')
        code_lines = event.control.text.split('\n')
        output_lines = execute_code_lines(code_lines)
        output_lines = [
            '' if error_output else output.replace('\n', ' ')
            for output, error_output in output_lines
        ]
        output_text_area.text = '\n'.join(output_lines)
        output_text_area.scroll_to(event.control.scroll_x, event.control.scroll_y, animate=False)

    @on(TextArea.SelectionChanged, '#main_text_area')
    def on_cursor_change(self, event: TextArea.SelectionChanged):
        output_text_area = self.query_one('#output_text_area')
        output_text_area.scroll_to(event.control.scroll_x, event.control.scroll_y, animate=False)

if __name__ == '__main__':
    Notepad().run()
