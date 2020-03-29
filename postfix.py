#!/usr/bin/env python3

""" Custom fixes for sentences.

A sentence must be added to 'patches' in the following structure:
'file_name.conllu': {'sentence_id':
                        {'token_id': {COLUMN_NAME: 'required_value'}
                        }
                    }
"""

import os

input_dir = 'syntagrus-final'
output_dir = 'syntagrus-ultimate'

ID, FORM, LEMMA, UPOS, XPOS, FEAT, HEAD, DEPREL, DEPS, MISC = list(range(10))

patches = {'ru_syntagrus-ud-train.conllu':
                {'2013Budushchee_Medvedeva.xml_33':
                    {'3': {DEPREL: 'conj', DEPS: '5:conj'},
                     '8': {DEPREL: 'root'}
                    },
                 '2009Reforma_obrazovaniya.xml_54':
                    {'9': {HEAD: '7', DEPS: '7:conj'}}
                },
           'ru_syntagrus-ud-test.conllu':
                {'2011Formula-1.xml_150':
                    {'1': {HEAD: '7', DEPS: '7:nsubj'},
                     '3': {HEAD: '7', DEPS: '7:nummod'},
                     '5': {DEPREL: 'conj', DEPS: '3:conj'},
                     '6': {HEAD: '7', DEPREL: 'amod', DEPS: '7:amod'},
                     '7': {HEAD: '0', DEPREL: 'root', DEPS: '0:root'}
                    }
                },
            'ru_syntagrus-ud-dev.conllu':
                {'uppsalaKorp_619.xml_158':
                    {'9.2': {ID: '9.1'},
                     '11': {DEPS: '9.1:obl'}
                    }
                }
           }

if __name__ == '__main__':
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for in_file_name in os.listdir(input_dir):
        in_path = os.path.join(input_dir, in_file_name)
        if not in_file_name.endswith('u'):
            in_file_name = in_file_name + 'u'
        out_path = os.path.join(output_dir, in_file_name)

        with open(in_path, 'r', encoding='utf-8') as in_file,\
             open(out_path, 'w', encoding='utf-8') as out_file:
            for line in in_file:
                if line.startswith('# sent_id'):
                    print(line.strip(), file=out_file)
                    sent_id = line.strip().split(' = ')[-1]
                elif line.startswith('#'):
                    print(line.strip(), file=out_file)
                    sent_tokens = []
                elif line == '\n':
                    for token in sent_tokens:
                        token_split = token.split('\t')
                        if in_file_name in patches and sent_id in patches[in_file_name]\
                           and token_split[ID] in patches[in_file_name][sent_id]:
                            for field in patches[in_file_name][sent_id][token_split[ID]]:
                                token_split[field] = patches[in_file_name][sent_id][token_split[ID]][field]
                            token = '\t'.join(token_split)
                        print(token, file=out_file)
                    print(file=out_file)
                else:
                    sent_tokens.append(line.strip())

