# SynTagRus_convertor

This is a pipeline that converts SynTagRus from its original format into Universal Dependencies.

To fetch the required libraries, run:

``$ pip3 install -r requirements.txt``

To run the pipeline:

``$ ./convert_all.sh input_dir``

where input_dir is the path to original SynTagRus directory

Development set and testing set are created using the following lists:
dev_list.txt
test_list.txt

Multiword expressions are split according to mwe.csv

Verb lemmas are fixed using ImpToPerf.txt

Lists for proper noun detection are taken from the following files:
prop_tocheck.py
propn_lemmas_certain.py

If you make use this tool, please cite the following paper: TBD
