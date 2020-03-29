#!/usr/bin/env python3

""" Move prepositions to dependent position, assign them UD labels. """

import os
import re
from collections import Counter

import lxml.etree as ET

from util import get_fnames, get_info, get_children_attrib

garbage = ['PR', 'CONJ']
safe = ['S', 'ADV', 'A', 'NUM', 'NID', 'PART', 'INTJ']
ud_deprels = ['case','mark']

def munch(ifiles, ofiles):
    """
    Process all files in ifiles list.
    Output into ofiles list.
    """
    temp_info = []
    for ifname, ofname in zip(ifiles, ofiles):
        tree = ET.parse(ifname)
        root = tree.getroot()
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                if word.attrib.get('FEAT', 'EMPTY').split()[0] == 'PR':
                    link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(word, sent)
                    children = get_children_attrib(sent, word.attrib['ID'])
                    if children == [] and head_pos != 'CONJ': #CONJ is converted during syntax phase

                        # only 'за' is converted here
                        if word.attrib['LEMMA'] == 'за':
                            if head_token.attrib['DOM'] == '_root':
                                # small fix for one sentence
                                word.attrib['DOM'] = '3'
                            else:
                                word.attrib['DOM'] = head_token.attrib['DOM']

                        new_dep = relation(head_pos)
                        word.attrib['LINK'] = new_dep
                    elif len(children) >= 1:
                        if any(ch['LINK'] == 'предл' for ch in children):
                            new_head_found = True

                        elif any(ch['LINK'] == 'сочин' for ch in children):
                            list_of_coord_candidates = []
                            candidate_coord = [ch for ch in children if ch['LINK'] == 'сочин']
                            for cand in candidate_coord:
                                if cand['FEAT'] == 'PR':
                                    list_of_coord_candidates.append(cand)
                                elif cand['FEAT'] == 'CONJ':
                                    sub_children = get_children_attrib(sent, cand['ID'])
                                    check_pr = [ch for ch in sub_children if ch['FEAT'] == 'PR']
                                    list_of_coord_candidates += check_pr
                            new_head_found = all(any(elem['LINK'] == 'предл'
                                                     for elem in get_children_attrib(sent, item['ID']))
                                                 for item in list_of_coord_candidates)
                        else:
                            new_head_found = True

                        if new_head_found:
                            for child in children:
                                if child['FEAT'].split()[0] in safe + ['V'] and child.get('LINK', 'EMPTY') == 'предл':

                                    child['DOM'] = word.attrib['DOM']
                                    word.attrib['DOM'] = child['ID']

                                    if child['DOM'] == '_root':
                                        child.pop('LINK')
                                    else:
                                        child['LINK'] = word.attrib['LINK']
                                    word.attrib['LINK'] = relation(child['FEAT'].split()[0])

                                    for elem in children:
                                        if elem['ID'] != child['ID']:
                                            elem['DOM'] = child['ID']
                                    break
                            else:
                                if any(elem['LINK'] == 'сочин' for elem in children):
                                    continue
                                elif len(children) == 1 and children[0]['LINK'] in ['разъяснит', 'огранич']:
                                    continue
                                elif len(children) == 1 and children[0]['FEAT'] == 'CONJ МЕТА':
                                    child['DOM'] = word.attrib['DOM']
                                    word.attrib['DOM'] = child['ID']
                                    child['LINK'] = word.attrib['LINK']
                                    word.attrib['LINK'] = 'case'

                                elif  len(children) >= 1 and any(elem['LINK'] == 'предик' for elem in children):
                                    continue
                                elif word.text == 'кроме' and children[0]['LEMMA'] == 'как':
                                    sub_ch = get_children_attrib(sent, children[0]['ID'])
                                    children[0]['LINK'] = 'fixed'
                                    sub_ch[0]['DOM'] = children[0]['DOM']

                                elif children[0]['LEMMA'] == 'минус':
                                    sub_ch = get_children_attrib(sent, children[0]['ID'])
                                    sub_ch[0]['DOM'] = word.attrib['DOM']
                                    sub_ch[0]['LINK'] = word.attrib['LINK']
                                    word.attrib['DOM'] = sub_ch[0]['ID']
                                    word.attrib['LINK'] = 'case'
                                    children[0]['DOM'] = sub_ch[0]['ID']
                                    children[0]['FEAT'] = 'S ЕД МУЖ ИМ НЕОД'
                                    children[0]['LINK'] = 'nmod'

                                elif word.text == 'вроде' and children[0]['LEMMA'] == 'при':
                                    children[0]['LINK'] = 'об-аппоз'
                                elif word.text == 'Около' and children[0]['LEMMA'] == 'назад':
                                    sub_ch = get_children_attrib(sent, children[0]['ID'])
                                    sub_ch[0]['DOM'] = word.attrib['DOM']
                                    sub_ch[0]['LINK'] = word.attrib['LINK']
                                    word.attrib['DOM'] = sub_ch[0]['ID']
                                    word.attrib['LINK'] = 'case'
                                    children[0]['DOM'] = sub_ch[0]['ID']
                                    children[0]['FEAT'] = 'ADV'
                                    children[0]['LINK'] = 'advmod'
                                else:
                                    # these are for debug purposes and normaly silent; if they scream something went wrong 
                                    print(word.attrib.get('ID', 'EMPTY'), word.text, word.attrib.get('FEAT', 'EMPTY'))
                                    print(*[(ch.get('ID', 'EMPTY'),
                                             ch.get('LEMMA', 'EMPTY'),
                                             ch.get('FEAT', 'EMPTY'),
                                             ch.get('LINK', 'EMPTY'))
                                            for ch in children], sep=' ')
                                    print('+' * 20)
                                    print(*[(token.attrib.get('ID', 'EMPTY'),
                                             token.text, token.attrib.get('DOM', 'EMPTY'),
                                             token.attrib.get('FEAT', 'EMPTY'),
                                             token.attrib.get('LINK', 'EMPTY'),
                                             token.tail) for token in sent], sep='\n')
                                    print('*' * 20)
                        else:
                            continue

        tree.write(ofname, encoding="UTF-8")
            
def relation(elem): # define UD relation
    if elem == 'V':
        deprel = 'mark'
    if elem in safe:
        deprel = 'case'
    return deprel

def main(ifolder, ofolder):
	munch(*get_fnames(ifolder, ofolder, '.xml', '.xml'))
	print('4: prepositions.py completed')
    
if __name__ == "__main__":
    main(ifolder, ofolder)
