#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import argparse
import os
from diceware_cli import subcommands
from diceware_cli.persistence import word_states
from os import path
from sys import argv

diceware_dir = path.dirname(path.abspath(__file__))
os.chdir(diceware_dir)


def get_args(cli_args):
    parser = argparse.ArgumentParser(prog=path.basename(__file__),
                                     allow_abbrev=False,
                                     )

    subparsers = parser.add_subparsers()
    subparsers.required = True
    subparsers.dest = 'command'

    load_db_subparser = subparsers.add_parser('load-db',
                                              help='Load words into the database',
                                              allow_abbrev=False,
                                              )
    load_db_subparser.add_argument('-l',
                                   '--language',
                                   help='The language of the wordlist',
                                   type=str,
                                   required=True,
                                   )
    load_db_subparser.add_argument('-f',
                                   '--file',
                                   help='A file to load into the db. Use \'-\' for stdin.'
                                        'Repeat this argument for multiple files.',
                                   action='append',
                                   dest='files',
                                   type=argparse.FileType('r'),
                                   required=True,
                                   )
    load_db_subparser.add_argument('-s',
                                   '--state',
                                   help='The initial state for the loaded words',
                                   type=str,
                                   default='pending',
                                   choices=word_states,
                                   )
    load_db_subparser.add_argument('--allow-updates',
                                   help='Allow words in the DB to have their state updated.'
                                        'Default behavior is insert only.',
                                   dest='allow_updates',
                                   action='store_true',
                                   )
    load_db_subparser.set_defaults(func=subcommands.load_db)

    clean_subparser = subparsers.add_parser('clean',
                                            help='Clean the project',
                                            allow_abbrev=False,
                                            )
    clean_subparser.set_defaults(func=subcommands.clean_project)

    finalize_subparser = subparsers.add_parser('finalize',
                                               help='Run checks and generate enumerated wordlists',
                                               allow_abbrev=False,
                                               )
    finalize_subparser.set_defaults(func=subcommands.finalize)

    select_words_subparser = subparsers.add_parser('select-words',
                                                   help='Iterate through the DB and select or reject words',
                                                   allow_abbrev=False,
                                                   )
    select_words_subparser.add_argument('-l',
                                        '--language',
                                        help='The language of the wordlist',
                                        type=str,
                                        required=True,
                                        )
    select_words_subparser.add_argument('--include-skipped',
                                        help='Re-evaluated words that were previously skipped',
                                        dest='include_skipped',
                                        action='store_true',
                                        )
    select_words_subparser.set_defaults(func=subcommands.select_words)

    dump_db_subparser = subparsers.add_parser('dump-db',
                                              help='Dump the contents of the sqlite db to disk',
                                              allow_abbrev=False,
                                              )
    dump_db_subparser.set_defaults(func=subcommands.dump_sqlite)

    db_state_subparser = subparsers.add_parser('db-state',
                                               help='Get the state of the db',
                                               allow_abbrev=False,
                                               )
    db_state_subparser.set_defaults(func=subcommands.db_state)

    return parser.parse_args(cli_args)

if __name__ == '__main__':
    try:
        args = get_args(argv[1:])
        args.func(args)
    except KeyboardInterrupt:
        print('')  # for a pretty newline
        exit(1)
