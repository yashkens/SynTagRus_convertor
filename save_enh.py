#!/usr/bin/env python3

""" Preprocessing before udapi. 
At the time of the development udapi was not able 
to deal with enhances representation.

Divide inpit file into basic conllu file, 
enhanced parts (token ids and 9th column), 
and file with enhanced tokens only.  
"""

import os
import sys

in_folder = 'syntagrus'
out_folder = 'syntagrus-noenh'
save_folder = 'syntagrus-enh-saves'

(ID, FORM, LEMMA, UPOS, XPOS,
 FEATS, HEAD, DEPREL, DEPS, MISC) = list(range(10))

if __name__ == '__main__':
    if len(sys.argv) == 4:
        in_folder, out_folder, save_folder = sys.argv[1], sys.argv[2], sys.argv[3]

    for folder in [out_folder, save_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    for in_file_name in os.listdir(in_folder):
        in_path = os.path.join(in_folder, in_file_name)
        out_path = os.path.join(out_folder, in_file_name)
        deps_path = os.path.join(save_folder, in_file_name.replace('.conll', '-deps.csv'))
        enh_path = os.path.join(save_folder, in_file_name.replace('.conll', '-enh.csv'))

        with open(in_path, 'r', encoding='utf-8') as in_file,\
             open(out_path, 'w', encoding='utf-8') as out_file,\
             open(deps_path, 'w', encoding='utf-8') as deps_file,\
             open(enh_path, 'w', encoding='utf-8') as enh_file:
            for line in in_file:

                line = line.strip()

                if line.startswith('#') or line == '':
                    print(line, file=out_file)
                    print(line, file=deps_file)
                else:
                    split = line.split('\t')
                    if '.' in split[ID]:
                        # enhanced token: print to enh file as is
                        print(line, file=enh_file)
                    else:
                        # ordinary token: save deps, print to out
                        print(split[ID], split[DEPS], sep='\t', file=deps_file)
                        split[DEPS] = '_'
                        print(*split, sep='\t', file=out_file)

                if line.startswith('# sent_id') or line == '':
                    # new sentence: print id to enh file
                    print(line, file=enh_file)
                
