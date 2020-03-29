#!/usr/bin/env python3

""" Reordering and clean-up for compounds """

import re
import os

import lxml.etree as ET

from util import get_fnames, get_info, get_children_attrib

def main(ifiles, ofiles):
    for ifname, ofname in zip(ifiles, ofiles):
        tree = ET.parse(ifname)
        root = tree.getroot()
        for sentence in root[-1].findall('S'):
            list_of_compounds = []   
            for i, token in enumerate(sentence.findall('W')):
                if token.attrib.get('FEAT','EMPTY').split()[0] == 'COM':                    
                    link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(token, sentence)
                    children = get_children_attrib(sentence, token.attrib['ID'])
                    if head_token.text != 'FANTOM':
                        list_of_compounds.append((token, head_token, children))        
            for elem in list_of_compounds:
                wordf, head_word, children = elem
                if children != []:
                    for child in children:
                        child['DOM'] = head_word.attrib['ID'] 
            for elem in list_of_compounds:
                wordf, head_word, children = elem
                shift_position = wordf.attrib['ID']
                for elem in sentence.findall('W'):
                    if int(elem.attrib['ID']) == int(shift_position):
                        sentence.remove(elem)
                        break
                for item in sentence.findall('W'):
                    if int(item.attrib['ID']) > int(shift_position):
                        item.attrib['ID'] = str(int(item.attrib['ID']) - 1)
                    if item.attrib.get('DOM', 'EMPTY') != '_root' and int(item.attrib['DOM']) > int(shift_position) - 1:
                        item.attrib['DOM'] = str(int(item.attrib['DOM']) - 1)  
        tree.write(ofname, encoding = 'utf-8')
    return

def process_all(ifolder, ofolder):
	main(*get_fnames(ifolder, ofolder, '.xml', '.xml'))
	print('3: getCleanedCompounds.py completed')

if __name__ == "__main__":
    process_all(ifolder, ofolder)

