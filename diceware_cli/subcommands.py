import copy
import os
import re
import sys
import traceback
from os import path
from diceware_cli.persistence import Base, WordList, db_session, engine, sqlite_file, word_states
from diceware_cli.util import colorize
from sqlalchemy import func, or_


base_dir = path.dirname(path.dirname(path.abspath(__file__)))


def load_db(args):
    _check_language(args.language)
    _init_db()
    _init_language(args.language)

    for f in args.files:
        _load_file_into_db(args.language, args.state, f, args.allow_updates)


def _init_db():
    full_path = path.join(base_dir, 'temp')
    if not os.path.isdir(full_path):
        if os.path.exists(full_path):
            raise Exception('Found a file at: {path}'.format(path=full_path))
        os.mkdir(full_path)
    Base.metadata.create_all(engine)


def _init_language(language):
    full_path = path.join(base_dir, 'wordlists', language)
    if not os.path.isdir(full_path):
        if os.path.exists(full_path):
            raise Exception('Found a file at: {path}'.format(path=full_path))
        os.mkdir(full_path)


def _load_file_into_db(language, state, f, allow_updates):
    assert(state in word_states)
    for line in f.readlines():
        word = line.strip()

        if _valid_regex.match(word) is not None:

            db_word = db_session.query(WordList).filter(WordList.language == language) \
                .filter(WordList.word == word).one_or_none()

            if db_word is not None:
                if allow_updates:
                    db_word.state = state
            else:
                db_session.add(WordList(word=word, state=state, language=language))

    db_session.commit()


def _check_language(language):
    if re.compile('^[a-z]{2}_[A-Z]{2}$').match(language) is None:
        raise Exception('The language you entered is not a valid language: ' + language)


def clean_project(args):
    os.remove(sqlite_file)


def finalize(args):
    print(colorize('Checking wordlists...', 'white', True))
    all_valid = True

    for d in os.listdir(path.join(base_dir, 'wordlists')):
        is_valid = _process_lang(d)
        all_valid = all_valid and is_valid

    if all_valid:
        print(colorize('Success: all files valid and enumerated', 'green', True))
        sys.exit(0)
    else:
        print(colorize('Failure: something bad happened', 'red', True))
        sys.exit(1)


# TODO this will have to change for other languages
_valid_regex = re.compile('^[a-z]{3,10}$')


def _regex_test(words):
    invalid_words = []
    for word in words:
        if _valid_regex.match(word) is None:
            invalid_words.append(word)
    if invalid_words:
        raise Exception('Invalid words found: ' + ', '.join(invalid_words))


def _check_for_rejected_words(words, rejected):
    invalid = []
    for word in words:
        if word in rejected:
            invalid.append(word)

    if invalid:
        raise Exception('Found invalid words: ' + ', '.join(invalid))


def _check_7776_wordlist(language, rejected):
    print('Checking 7776 wordlist for ' + language)
    try:
        with open(path.join(base_dir, 'wordlists', language, 'wordlist.txt'), 'r') as f:
            words = [line.rstrip('\n') for line in f.readlines()]

            _check_for_rejected_words(words, rejected)

            assert(len(words) == 7776)
            assert(len(set(words)) == 7776)

            _regex_test(words)

            words_copy = sorted(words)
            assert(words == words_copy)

            _write_numbered_file(words, language)

            print(colorize('Success for 7776 list for ' + language, 'green'))
            return True
    except:
        print(colorize('Failure for 7776 list for ' + language, 'red'))
        traceback.print_exc(file=sys.stdout)
        return False


def _check_8192_wordlist(language, rejected):
    print('Checking 8192 wordlist for ' + language)

    file_name = path.join(base_dir, 'wordlists', language, 'wordlist-8192.txt')
    if not os.path.isfile(file_name):
        print(colorize('8192 wordlist not found for ' + language, 'yellow'))
        return True

    try:
        with open(file_name, 'r') as f:
            words = [line.rstrip('\n') for line in f.readlines()]

            _check_for_rejected_words(words, rejected)

            assert(len(words) == 8192)
            assert(len(set(words)) == 8192)

            _regex_test(words)

            words_copy = sorted(copy.copy(words))
            assert(words == words_copy)

            print(colorize('Success for 8192 list for ' + language, 'green'))
            return True
    except:
        print(colorize('Failure for 8192 list for ' + language, 'red'))
        traceback.print_exc(file=sys.stdout)
        return False


def _get_rejected_words(language):
    file_name = path.join(base_dir, 'wordlists', language, 'rejected.txt')
    rejects = []

    if not os.path.isfile(file_name):
        print(colorize('No rejected words found for language ' + language, 'yellow'))
        return rejects

    with open(file_name, 'r') as f:
        rejects = [line.rstrip('\n') for line in f.readlines()]
        rejects_copy = sorted(rejects)
        # because I'm pedantic and want everything sorted
        assert(rejects == rejects_copy)
        assert(len(set(rejects)) == len(rejects))

    return rejects


def _process_lang(language):
    print(colorize('Checking language ' + language, 'white'))
    # TODO set locale based on 'language' var (for sorting)
    rejected = _get_rejected_words(language)
    result_7776 = _check_7776_wordlist(language, rejected)
    result_8192 = _check_8192_wordlist(language, rejected)
    return result_7776 and result_8192


def _write_numbered_file(words, language):
    print(colorize('Writing file for language ' + language, 'white'))

    with open(path.join(base_dir, 'wordlists', language, 'wordlist-numbered.txt'), 'w') as f:
        line_num = 0
        for word in words:
            f.write('{num}\t{word}\n'.format(num=_dice_num(line_num), word=word))
            line_num += 1
        print(colorize('Successfully wrote language ' + language, 'green'))


def _baseN(num, b, numerals='0123456789abcdef'):
    return ((num == 0) and numerals[0]) or (_baseN(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])


def _dice_num(num):
    ret = list()
    for char in str(_baseN(num, 6)).zfill(5):
        ret.append(chr(ord(char) + 1))
    return ''.join(ret)


def select_words(args):
    query = db_session.query(WordList).filter(WordList.language == args.language)

    if args.include_skipped:
        query = query.filter(or_(WordList.state == 'pending', WordList.state == 'skipped'))
    else:
        query = query.filter(WordList.state == 'pending')

    query = query.order_by(func.length(WordList.word))
    word = query.first()

    while word is not None:
        _cli_input_for_word(word)
        word = query.first()

    if args.include_skipped:
        print('DB has no more words in \'pending\' or \'skipped \' state')
    else:
        print('DB has no more words in \'pending\' state')


def _cli_input_for_word(word):
    while True:
        raw = input('Accept word? {word} > '.format(word=word.word)).strip()
        if raw == 'y':
            word.state = 'accepted'
            break
        elif raw == 'n':
            word.state = 'rejected'
            break
        elif raw == 's':
            word.state = 'skipped'
            break
        else:
            print('Invalid input. Options are: {y,n,s}')

    db_session.add(word)
    db_session.commit()


def dump_sqlite(args):
    languages = db_session.query(WordList.language).distinct().all()

    for l in languages:
        _dump_rejected(l[0])
        _dump_accepted(l[0])


def _dump_rejected(language):
    words = db_session.query(WordList).filter(WordList.language == language) \
        .filter(WordList.state == 'rejected').all()

    words = sorted(list(map(lambda w: w.word, words)))

    with open(path.join(base_dir, 'wordlists', language, 'rejected.txt'), 'w') as f:
        for word in words:
            f.write(word + '\n')


def _dump_accepted(language):
    words = db_session.query(WordList).filter(WordList.language == language) \
        .filter(WordList.state == 'accepted').all()

    words = sorted(list(map(lambda w: w.word, words)))

    with open(path.join(base_dir, 'wordlists', language, 'wordlist.txt'), 'w') as f:
        for word in words:
            f.write(word + '\n')


def db_state(args):
    engine.execute('vacuum')
    statuses = db_session.query(WordList.language, WordList.state, func.count(WordList.word)) \
        .group_by(WordList.language, WordList.state) \
        .order_by(WordList.language, WordList.state).all()

    # spacing: shitty, but good enough
    print(colorize('Language\tState\t\tCount', 'white', True))
    for status in statuses:
        print('{lang}\t\t{state} \t{count}'.format(lang=status[0], state=status[1], count=status[2]))
