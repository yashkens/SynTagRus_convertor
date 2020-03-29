#!/bin/bash

# the main convrsion pipeline
python3 ud2Convertor.py -i $1
# udapy-based punctuation fixer
./fixpunct.sh
# custom fixes for sentences
python3 postfix.py
