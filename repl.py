"""
This module contains a lexer and other utilities for syntax highlighting,
autocompletion and autosuggestion for the game's REPL
"""

import sys
from prompt_toolkit import prompt, AbortAction
from prompt_toolkit.history import FileHistory
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from pygments.style import Style
from pygments.lexer import words, RegexLexer
from pygments.token import Token
from pygments.token import Text, Comment, Operator, Keyword, Name, String, Number
from pygments.styles.default import DefaultStyle
from os import listdir
from os.path import isfile
from collections import OrderedDict
from parser import KEYWORDS, PARAMS, DOMAINS


def get_word_list(document, tokens):
    keywords = tokens.keys()
    index = document.find_start_of_previous_word()
    if index:
        keyword = document.text_before_cursor[index:]
        keyword = keyword.split()[0].strip()
        word_list = tokens.get(keyword, lambda: keywords)()
    else:
        word_list = keywords
    return list(map(str, word_list))

class MyLexer(RegexLexer):
    tokens = {
        'root': [
            (r'\s+', Text),
            (r'\d+[LlUu]*', Number.Integer),
            (words(KEYWORDS,suffix=r'\b'), Keyword),
            (words(PARAMS,suffix=r'\b'), Keyword.Reserved),
            (words(DOMAINS,suffix=r'\b'), Name.Builtin),
        ],
    }

class MyAutoSuggest(AutoSuggest):
    def __init__(self, tokens):
        self.tokens = tokens
    def get_suggestion(self, cli, buffer, document):
        word_list = get_word_list(document, self.tokens)
        text = document.text.rsplit('\n', 1)[-1]
        word_complete = text.endswith(' ')
        text = text.split()[-1]
        if word_list and word_complete:
            for word in word_list:
                if word.startswith(text) and word != text:
                    return Suggestion(word[len(text):])
            return Suggestion(word_list[0])

class MyCompleter(Completer):
    def __init__(self, tokens, meta_dict=dict()):
        self.tokens = tokens
        self.meta_dict = meta_dict
    def get_completions(self, document, complete_event):
        word_list = get_word_list(document, self.tokens)
        word_before_cursor = document.get_word_before_cursor().lower()
        def word_matches(word):
            word = word.lower()
            return word.startswith(word_before_cursor)
        for a in word_list:
            if word_matches(a):
                display_meta = self.meta_dict.get(a, '')
                yield Completion(a, -len(word_before_cursor), display_meta=display_meta)

class DynamicTokens(list):
    def __call__(self, *args, **kwargs):
        result = []
        for item in self:
            try:
                result += item(*args, **kwargs)
            except TypeError:
                result.append(item)
        return result

class DocumentStyle(Style):
    styles = {
        Token.Menu.Completions.Completion.Current: 'bg:#00aaaa #000000',
        Token.Menu.Completions.Completion: 'bg:#008888 #ffffff',
        Token.Menu.Completions.ProgressButton: 'bg:#003333',
        Token.Menu.Completions.ProgressBar: 'bg:#00aaaa',
    }
    styles.update(DefaultStyle.styles)

class REPL(object):
    def __init__(self, screen):
        self.screen = screen
        self.history = FileHistory(".history")
        self.tokens = {'topology': DynamicTokens(DOMAINS),
            'run': DynamicTokens(['', self.getfiles]),
            'load': DynamicTokens([self.getfiles]),
            'insert': DynamicTokens([self.getfiles]),
            'height': DynamicTokens([]),
            'width': DynamicTokens([]),
            'save': DynamicTokens([]),
            'clear': DynamicTokens([]),
            'quit': DynamicTokens([]),
            'exit': DynamicTokens([])
            }
        self.autosuggest_tokens = OrderedDict({'run': DynamicTokens(['', self.getfiles]),
            'topology': DynamicTokens(DOMAINS),
            'load': DynamicTokens([self.getfiles]),
            'insert': DynamicTokens([self.getfiles]),
            'height': DynamicTokens([self.screen.height]),
            'width': DynamicTokens([self.screen.width]),
            'save': DynamicTokens(['file_name']),
            'clear': DynamicTokens([]),
            'quit': DynamicTokens([]),
            'exit': DynamicTokens([])
            })
        self.meta_dict = {'run': 'run the game',
                     'topology': 'set the topology of the game',
                     'load': 'load an initial state',
                     'insert': 'insert object',
                     'height': 'set screen height',
                     'width': 'set screen width',
                     'save': 'save current state to file',
                     'clear': 'clear the screen'}
        self.completer = MyCompleter(self.tokens, meta_dict = self.meta_dict)
        self.autosuggest = MyAutoSuggest(self.autosuggest_tokens)

    def prompt(self):
        return prompt('> ', lexer = MyLexer, completer = self.completer,
                      style = DocumentStyle, history = self.history,
                      auto_suggest = self.autosuggest,
                      on_abort=AbortAction.RETRY)

    def getfiles(self):
        return ["'" + f + "'" for f in listdir('objects/') if isfile('objects/' + f)]
