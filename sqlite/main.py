#!/usr/bin/env python3
# -*- coding: utf-8 -*-

if __name__ != "__main__":
    from sys import exit, stderr

    print('must be run as a script', file=stderr)
    exit(1)

# Standard Library
from os.path import expanduser
import sqlite3
from argparse import ArgumentParser, Namespace

# 3rd Party
from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory, ThreadedAutoSuggest
from prompt_toolkit.completion import ThreadedCompleter
from prompt_toolkit.history import ThreadedHistory, FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import style_from_pygments_cls
from pygments.lexers.sql import SqlLexer
from pygments.styles import get_style_by_name, STYLE_MAP
from tabulate import tabulate

# Relative
from completer import SQLiteCompleter

parser: ArgumentParser = ArgumentParser(
    prog='SQLiteREPL',
    description='A dead simple REPL for SQLite',
    epilog='bye!')

parser.add_argument(
    'database',
    help='path to database',
    nargs='?',
    default='~/.sqlite')

parser.add_argument(
    '-H',
    '--history',
    metavar='PATH',
    help='path to history file',
    nargs='?',
    default='~/.SqliteREPL_history')

parser.add_argument(
    '-m',
    '--multiline',
    help='enable multiline mode (useful for creating tables)',
    action='store_true',
    default=False)

parser.add_argument(
    '--no-history-search',
    dest='historysearch',
    help='disable history search',
    action='store_false',
    default=True)

parser.add_argument(
    '--no-complete-while-typing',
    dest='completewhiletyping',
    help='disable completion while typing',
    action='store_false',
    default=True)

parser.add_argument(
    '--no-infobar',
    dest='infobar',
    help='disable info bar at the bottom of the screen',
    action='store_false',
    default=True)

parser.add_argument(
    '--no-editor',
    dest='editor',
    help='disable opening in $EDITOR',
    action='store_false',
    default=True)

parser.add_argument(
    '-t',
    '--tablestyle',
    help='set table style to <STYLE> (hint: try "orgtbl", "pipe" or "simple"',
    metavar='STYLE',
    choices=[
        "plain",
        "simple",
        "grid",
        "fancy_grid",
        "pipe",
        "orgtbl",
        "jira",
        "presto",
        "psql",
        "rst",
        "mediawiki",
        "moinmoin",
        "youtrack",
        "html",
        "latex",
        "latex_raw",
        "latex_booktabs",
        "textile",
    ],
    default='simple')

parser.add_argument(
    '-s',
    '--style',
    metavar='STYLE',
    help='pygments style (see http://pygments.org/docs/styles/#builtin-styles)',
    nargs='?',
    choices=list(STYLE_MAP.keys()),
    default='monokai')

parser.add_argument(
    '-p',
    '--prompt',
    metavar='STRING',
    help='prompt string',
    nargs='?',
    default='SQLite >> ')

args: Namespace = parser.parse_args()

prompt_session: PromptSession = PromptSession(
    message=args.prompt,
    bottom_toolbar=((lambda: HTML("SQLite3 REPL | " + " | ".join([i for i in [
        f"<b><style bg=\"ansiblue\">{i}</style></b> {eval('args.' + i, globals(), locals())}" for i in dir(args) if
        i[0] != '_'] if not i.endswith("True") and not i.endswith("False") and not i.startswith(
        "prompt")]))) if args.infobar else None),
    history=ThreadedHistory(FileHistory(expanduser(args.history))),
    auto_suggest=ThreadedAutoSuggest(AutoSuggestFromHistory()),
    include_default_pygments_style=False,
    multiline=args.multiline,
    lexer=PygmentsLexer(SqlLexer),
    style=style_from_pygments_cls(get_style_by_name(args.style)),
    completer=ThreadedCompleter(SQLiteCompleter()),
    enable_history_search=args.historysearch,
    complete_while_typing=args.completewhiletyping,
    enable_open_in_editor=args.editor,
)

# used for fish-like history completion
while True:

    try:
        user_input: str = prompt_session.prompt().strip()
        low_case: str = user_input.lower()

        if low_case in ['.quit', 'quit', 'exit', '.exit', 'abort', 'abort']:
            break

        elif low_case == '.tables':
            user_input = 'select name from sqlite_master where type = "table";'

        try:
            with sqlite3.connect(expanduser(args.database)) as connection:
                print(tabulate(connection.execute(user_input), tablefmt=args.tablestyle))

        except (sqlite3.Error, sqlite3.IntegrityError) as e:
            print(f"An error occurred: {e.args[0]}")

    except (EOFError, KeyboardInterrupt) as e:
        break
