#!/usr/bin/env python3

""" Small fixes.

1. delete sentences from targets_for_deletion list
2. replaces 'ё' -> 'е'
3. replaces PART -> ADV for lemmas 'уже', 'еще', 'почти', 'также', 'чуть'
"""

import os

import lxml.etree as ET

from util import get_fnames

targets_for_deletion = {'Problema_vybora.tgt': 5, 'Vyzhivshii_kamikadze.tgt': 255, 'Ukroshchenie_stroptivogo_naukograda.tgt': 47, 'Korp_622.tgt': 13, 'Korp_624.tgt': 51, 'Pravilo_75.tgt': 48, 'V_perevode_s_nebesnogo.tgt': 41}

def safe_str(text):
    if text is not None:
        return text.strip().lower().replace('ё', 'е')
    return ''

def fix_token(fname, i, j, token, word, lemma, newfeat, logfile):
    """
    Fix token's feats and log it.
    """
    logfile.write('Fixed {}, sentence {}, token {}:\n\t{} {}\n'.format(fname, i, j, str(token.attrib), word))
    token.attrib['FEAT'] = newfeat
    token.attrib['LEMMA'] = lemma
    logfile.write('\t{} {}\n'.format(str(token.attrib), word))

def munch(ifiles, ofiles):
    """
    Process all files in ifiles list.
    Output into ofiles list.
    """
    logfile = open('special.log', 'w', encoding='utf-8')
    for ifname, ofname in zip(ifiles, ofiles):
        logfile.write('{}\nProcessing {}\n{}\n'.format('=' * 75, ifname, '=' * 75))
        tree = ET.parse(ifname)
        root = tree.getroot()
        
        for elem in targets_for_deletion.keys():
            if os.path.split(ifname)[1].endswith(elem):
                sent_id = targets_for_deletion.get(elem, '')
                for sentence in root[-1].findall('S'):
                    if sentence.attrib.get('ID', '') == str(sent_id):
                        sentence.clear()
        
        for i, sentence in enumerate(root[-1].findall('S')):
            for j, token in enumerate(sentence.findall('W')):
                if 'NODETYPE' in token.attrib:
                    pass
                elif 'FEAT' in token.attrib:
                    word = safe_str(token.text)
                    lemma = token.attrib.get('LEMMA', '')
                    pos = token.attrib.get('FEAT', ' ').split(' ')[0]

                    if pos == 'PART' and lemma in ['уже', 'еще', 'почти', 'также', 'чуть']:
                        fix_token(ifname, i, j, token, word, lemma, 'ADV', logfile)
        tree.write(ofname, encoding = 'utf-8')
    logfile.close()

def process_all(ifolder, ofolder):
	munch(*get_fnames(ifolder, ofolder, '.tgt', '.xml'))
	print('1: preparations.py completed')

if __name__ == "__main__":
    process_all(ifolder, ofolder)

