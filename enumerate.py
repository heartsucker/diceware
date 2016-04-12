#!/usr/bin/env python3

'''
Ensures wordlists are the correct size, and adds the dice lookup numbers.
'''

import copy, os, re, sys, traceback
from os import listdir, path

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))


def colorize(msg, color, bold=False):
    shell_colors = {
        'gray': '30',
        'red': '31',
        'green': '32',
        'yellow': '33',
        'blue': '34',
        'magenta': '35',
        'cyan': '36',
        'white': '37',
        'crimson': '38',
        'highlighted_red': '41',
        'highlighted_green': '42',
        'highlighted_brown': '43',
        'highlighted_blue': '44',
        'highlighted_magenta': '45',
        'highlighted_cyan': '46',
        'highlighted_gray': '47',
        'highlighted_crimson': '48'
    }
    attrs = [shell_colors[color]]
    if bold:
        attrs.append('1')
    return '\x1b[{}m{}\x1b[0m'.format(';'.join(attrs), msg)

valid_regex = re.compile('^[a-z0-9]{1,10}$')


def regex_test(words):
    for word in words:
        if valid_regex.match(word) is None:
            raise Exception(word + ' is invalid')


def check_7776_wordlist(language):
    print('Checking 7776 wordlist for ' + language)
    try:
        with open(path.join(script_dir, 'wordlists', language, 'wordlist.txt'), 'r') as f:
            words = [line.rstrip('\n') for line in f.readlines()]

            assert(len(words) == 7776)
            assert(len(set(words)) == 7776)

            regex_test(words)

            words_copy = copy.copy(words)
            words.sort()
            assert(words == words_copy)

            write_file(words, language)

            print(colorize('Success for 7776 list for ' + language, 'green'))
            return True
    except:
        print(colorize('Failure for 7776 list for ' + language, 'red'))
        traceback.print_exc(file=sys.stdout)
        return False


def check_8192_wordlist(language):
    print('Checking 8192 wordlist for ' + language)

    file_name = path.join(script_dir, 'wordlists', language, 'wordlist-8192.txt')
    if not os.path.isfile(file_name):
        print(colorize('8192 wordlist not found for ' + language, 'yellow'))
        return True

    try:
        with open(file_name, 'r') as f:
            words = [line.rstrip('\n') for line in f.readlines()]

            assert(len(words) == 8192)
            assert(len(set(words)) == 8192)

            regex_test(words)

            words_copy = copy.copy(words)
            words.sort()
            assert(words == words_copy)

            print(colorize('Success for 8192 list for ' + language, 'green'))
            return True
    except:
        print(colorize('Failure for 8192 list for ' + language, 'red'))
        traceback.print_exc(file=sys.stdout)
        return False


def process_lang(language):
    print(colorize('Checking language ' + language, 'white'))
    result_7776 = check_7776_wordlist(language)
    result_8192 = check_8192_wordlist(language)
    return result_7776 and result_8192


def write_file(words, language):
    print(colorize('Writing file for language ' + language, 'white'))

    with open(path.join(script_dir, 'wordlists', language, 'wordlist-numbered.txt'), 'w') as f:
        line_num = 0
        for word in words:
            f.write('{num}\t{word}\n'.format(num=dice_num(line_num), word=word))
            line_num += 1
        print(colorize('Successfully wrote language ' + language, 'green'))


def baseN(num, b, numerals='0123456789abcdef'):
    return ((num == 0) and numerals[0]) or (baseN(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])


def dice_num(num):
    ret = list()
    for char in str(baseN(num, 6)).zfill(5):
        ret.append(chr(ord(char) + 1))
    return ''.join(ret)

if (__name__ == '__main__'):
    print(colorize('Checking wordlists...', 'white', True))
    all_valid = True

    for dir in listdir(path.join(script_dir, 'wordlists')):
        is_valid = process_lang(dir)
        all_valid = all_valid and is_valid

    if all_valid:
        print(colorize('Success: all files valid and enumerated', 'green', True))
        sys.exit(0)
    else:
        print(colorize('Failure: something bad happened', 'red', True))
        sys.exit(1)
