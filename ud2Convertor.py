#!/usr/bin/env python3

""" The main pipeline for conversion from original .tgt to .conll """

from argparse import ArgumentParser

from util import flatten_structure
import preparations
import changeCompounds
import getCleanedCompounds
import prepositions
import conjunctions
import numerals
import syntax
import morphology
import propernouns
import cleanup
import fixRegular
import checkReported
import ellipsis
import fixedDep
import punct
import toCONLL

def parse_arguments():
    parser = ArgumentParser(description='Main conversion pipeline')
    parser.add_argument('-i', '--input-directory', metavar='INPUT_DIR',
                        type=str, action='store',
                        default=None, dest='input_directory',
                        help='input directory', required=True)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_arguments()

    # transform original folder structure into flat structure
    flatten_structure(args.input_directory, 'Base')

    # fix some POS and erroneous sentences
    preparations.process_all('Base', 'Prepared')

    # delete sentences with irregular compounds (COM)
    # and 'glue' regular compounds in one token
    changeCompounds.main('Prepared', 'GetCompounds')

    # reorder and clean-up compounds
    getCleanedCompounds.process_all('GetCompounds', 'GotEm')

    # change prepositions (position and relation)
    prepositions.main('GotEm', 'Prepositions')

    # change the head of a root conjunction
    conjunctions.main('Prepositions', 'Conjunctions')

    # fix numerals
    numerals.main('Conjunctions', 'Numerals')

    # UD syntactic relations
    syntax.process_all('Numerals', 'Syntax')

    # UD morphology and features
    morphology.process_all('Syntax', 'Morphology')

    # 'predict' proper nouns
    propernouns.process_all('Morphology', 'Propernouns')

    # small fixes for 'fixed', 'det', 'name', 'discourse';
    # fixes for punctuation inside tokens
    cleanup.process_all('Propernouns', 'Cleaned')

    # find and re-annotate 'не' and 'быть'
    fixRegular.process_all('Cleaned', 'FixRegular')

    # check reported speech
    checkReported.process_all('FixRegular', 'Reported')

    # process ellipsis
    ellipsis.process_all('Reported', 'Ellipsis')

    # fix mwe, fix verb lemmas
    fixedDep.process_all('Ellipsis', 'Fixed')

    # extract punctuation
    punct.process_all('Fixed', 'PunctExtract')

    # convert data to .conll
    toCONLL.process_all('PunctExtract', 'syntagrus')

