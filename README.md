# diceware

An improvement on the original `diceware` list, originally published by A G Reinhold. This list attempts to remove hard to memorize random letter combinations, words that may be unfamiliar even to native speakers, and words with uncommon spellings.

## Usage

Instructions on how to use diceware passphrases can be found [here](http://world.std.com/~reinhold/diceware.html).

## diff
For the curious, the full diff from the original list can be shown using:

```bash
diff wordlists/en_US/wordlist.txt <(wget -q http://world.std.com/~reinhold/diceware.wordlist.asc -O - | tail -n +3 | head -7776 | awk '{ print $NF }' | sort)
```

## Hacking

Set up the dev environment with `setup.sh`.

Run all the dev tasks with `cli.py`.

## License / Credits

In compliance with the `CC-BY-3.0` license, this work was made with modifications and is based on the work of A G Reinhold.

Other words came from Oren Tirosh’s [mnemonic encoding project](http://web.archive.org/web/20090918202746/http://tothink.com/mnemonic/wordlist.html).

This work itself is licensed under the MIT license.
