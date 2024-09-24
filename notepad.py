#!/usr/bin/env python3

import argparse
import code
import io
import sys

from pygments.lexers import guess_lexer_for_filename
from textual.app import App, on
from textual.containers import Horizontal
from textual.widgets import Footer, Header, TextArea

TEXTUAL_LANGUAGES = [
    'bash', 'css', 'go', 'html',
    'java', 'javascript', 'json', 'kotlin',
    'markdown', 'python', 'rust', 'regex',
    'sql', 'toml', 'yaml'
]

def execute_code_lines(code_lines):
    code_lines_merged = []
    i = 0
    while i < len(code_lines):
        j = i + 1
        while j < len(code_lines) and (
            code_lines[j].startswith(' ') or
            code_lines[j].startswith('\t') or
            code_lines[j].startswith('#') or
            code_lines[j] == ''
        ):
            j += 1
        while j > i + 1 and (
            code_lines[j - 1].startswith('#') or
            code_lines[j - 1].strip() == ''
        ):
            j -= 1
        code_lines_merged.append('\n'.join(code_lines[i:j]))
        i = j
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

    BINDINGS = [('ctrl+s', 'save', 'Save')]

    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        if filename:
            try:
                with open(filename, 'r') as f:
                    self.text = f.read()
            except:
                self.text = ''
        else:
            self.text = ''
        self.output = self.execute_code(self.text)
        try:
            lexer = guess_lexer_for_filename(self.filename, self.text)
            self.detected_language = lexer.name.lower()
            if self.detected_language not in TEXTUAL_LANGUAGES:
                self.detected_language = 'markdown'
        except:
            self.detected_language = 'markdown'

    def compose(self):
        yield Header()
        yield Footer()
        yield Horizontal(
            TextArea(id='main_text_area', show_line_numbers=True, language=self.detected_language, text=self.text, tab_behavior='indent'),
            TextArea(id='output_text_area', soft_wrap=False, read_only=True, text=self.output)
        )

    def execute_code(self, code):
        code_lines = code.split('\n')
        output_lines = execute_code_lines(code_lines)
        output_lines = [
            '' if error_output else output.replace('\n', ' ')
            for output, error_output in output_lines
        ]
        return '\n'.join(output_lines)

    @on(TextArea.Changed, '#main_text_area')
    def on_text_change(self, event: TextArea.Changed):
        output_text_area = self.query_one('#output_text_area')
        output_text_area.text = self.execute_code(event.control.text)
        output_text_area.scroll_to(event.control.scroll_x, event.control.scroll_y, animate=False)

    @on(TextArea.SelectionChanged, '#main_text_area')
    def on_cursor_change(self, event: TextArea.SelectionChanged):
        output_text_area = self.query_one('#output_text_area')
        output_text_area.scroll_to(event.control.scroll_x, event.control.scroll_y, animate=False)

    def action_save(self):
        if self.filename:
            with open(self.filename, 'w') as f:
                f.write(self.query_one('#main_text_area').text)

def main(filename):
    app = Notepad(filename)
    app.run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='?', type=str, default=None)
    args = parser.parse_args()
    main(args.filename)
