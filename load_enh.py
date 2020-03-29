#!/usr/bin/env python3

""" Postprocessing after udapi. 
At the time of the development udapi was not able 
to deal with enhances representation.

Insert enhanced tokens and 9th column into the udapi output.
"""

import os
import sys

in_folder = 'syntagrus-noenh-fixed-punct'
out_folder = 'syntagrus-final'
save_folder = 'syntagrus-enh-saves'

(ID, FORM, LEMMA, UPOS, XPOS,
 FEATS, HEAD, DEPREL, DEPS, MISC) = list(range(10))

if __name__ == '__main__':
    if len(sys.argv) == 4:
        in_folder, out_folder, save_folder = sys.argv[1], sys.argv[2], sys.argv[3]

    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    for in_file_name in os.listdir(in_folder):
        in_path = os.path.join(in_folder, in_file_name)
        out_path = os.path.join(out_folder, in_file_name)
        deps_path = os.path.join(save_folder, in_file_name.replace('.conll', '-deps.csv'))
        enh_path = os.path.join(save_folder, in_file_name.replace('.conll', '-enh.csv'))

        enh_dict = {}
        with open(enh_path, 'r', encoding='utf-8') as enh_file:
            for line in enh_file:
                line = line.strip()
                if line.startswith('#'):
                    current_id = line
                    enh_dict[current_id] = {}
                elif line != '':
                    split = line.split('\t')
                    enh_dict[current_id][split[ID]] = line

        with open(in_path, 'r', encoding='utf-8') as in_file,\
             open(out_path, 'w', encoding='utf-8') as out_file,\
             open(deps_path, 'r', encoding='utf-8') as deps_file:

            current_sent = {}

            for in_line, deps_line in zip(in_file, deps_file):
                in_line, deps_line = in_line.strip(), deps_line.strip()

                assert (in_line.startswith('#') or
                        in_line == deps_line == '' or
                        in_line.split('\t', maxsplit=1)[0] == deps_line.split('\t', maxsplit=1)[0])

                if in_line.startswith('# sent_id'):
                    current_id = in_line

                if in_line.startswith('#'):
                    print(in_line, file=out_file)
                elif in_line == '':
                    current_sent.update(enh_dict[current_id])
                    for token_id in sorted(current_sent, key=lambda x: float(x)):
                        print(current_sent[token_id], file=out_file)
                    print(in_line, file=out_file)
                    current_sent = {}
                else:
                    in_split = in_line.split('\t')
                    if in_split[UPOS] == 'PUNCT':
                        in_split[DEPS] = ':'.join((in_split[HEAD], in_split[DEPREL]))
                    else:
                        deps_split = deps_line.split('\t')
                        in_split[DEPS] = deps_split[1]
                    current_sent[in_split[ID]] = '\t'.join(in_split)
