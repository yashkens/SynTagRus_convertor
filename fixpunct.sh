#!/bin/bash

initial_dir=syntagrus
save_dir=syntagrus-enh-saves
noenh_dir=syntagrus-noenh
fixed_dir=syntagrus-noenh-fixed-punct
final_dir=syntagrus-final

echo 'Saving enhanced parts'
python3 ./save_enh.py ${initial_dir} ${noenh_dir} ${save_dir}
echo 'Fixing punctuation'
mkdir ${fixed_dir}
for filename in ru_syntagrus-ud-test.conll ru_syntagrus-ud-dev.conll ru_syntagrus-ud-train.conll
do
    echo 'Fixing '${filename}
    cat ${noenh_dir}/${filename} | udapy read.Conllu ud.FixPunct write.Conllu >${fixed_dir}/${filename}
done
echo 'Loading enhanced parts back'
python3 ./load_enh.py ${fixed_dir} ${final_dir} ${save_dir}
rm -rf ${save_dir} ${noenh_dir} ${fixed_dir}
