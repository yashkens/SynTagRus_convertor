#!/usr/bin/env python3

""" Delete sentences with irregular compounds (COM) and 'glue' regular compounds in one token.
Delete 2 sentences with 'предик' to single head and transform FANTOM
"""

import os

import lxml.etree as ET

from util import get_fnames, get_info, get_children_attrib

garbage = ['PR', 'CONJ']

def munch(ifiles, ofiles):
    """
    Process all files in ifiles list.
    Output into ofiles list.
    """
    for ifname, ofname in zip(ifiles, ofiles):
        tree = ET.parse(ifname)
        root = tree.getroot()
        for sentence in root[-1].findall('S'):   
            remove_sentence = False
            for token in sentence.findall('W'):
                if token.attrib.get('FEAT','EMPTY').split()[0] == 'COM':
                    link, pos, feats, head_token, head_pos, head_feats, head_root, nodetype = get_info(token, sentence, get_nodetype=True)                    
                    if not nodetype and head_pos == 'COM':
                        print(ifname, sentence.attrib['ID'])
                    elif nodetype:
                        token.attrib['FEAT'] = head_token.attrib['FEAT']
                    elif not nodetype and head_pos in ['PR', 'NUM', 'CONJ']:
                        remove_sentence = True
                        continue
                    elif not nodetype and head_pos == 'V':
                        if token.text in ['не', 'полу']:
                            head_token.attrib['LEMMA'] = token.attrib['LEMMA'] + head_token.attrib['LEMMA']
                            head_token.text = token.text + head_token.text
                        else:
                            remove_sentence = True
                            continue
                    elif not nodetype and head_pos == 'A':
                        head_token.attrib['LEMMA'] = token.attrib['LEMMA'] + head_token.attrib['LEMMA']
                        head_token.text = token.text + head_token.text
                    elif not nodetype and head_pos == 'S':   
                        if head_token.attrib['LEMMA'] not in ['слово', 'фактор', 'циклон', 'янус', 'буква', 'орбита', 'мониторинг', 'спектроскопия']:
                            head_token.attrib['LEMMA'] = token.attrib['LEMMA'] + token.tail.strip() + head_token.attrib['LEMMA']
                            head_token.text = token.text + token.tail.strip() + head_token.text
                        else:
                            remove_sentence = True
                            continue                            
                    else:
                        print(ifname, sentence.attrib['ID'])
            if remove_sentence:
                sentence.clear()
                continue
        for sentence in root[-1].findall('S'):
            for token in sentence.findall('W'): 
                if 'NODETYPE' in token.attrib:
                    token.text = 'FANTOM'
                    del token.attrib['NODETYPE']
                    if 'LEMMA' not in token.attrib:
                        token.attrib['LEMMA'] = 'FANTOM'
                if 'LINK' in token.attrib and token.attrib['LINK'] == 'предик':
                    dom = int(token.attrib['DOM'])
                    number = int(token.attrib['ID'])
                    for item in sentence.findall('W'):
                        if 'LINK' in item.attrib and item.attrib['LINK'] == 'предик' and \
                            int(item.attrib['ID']) != number and int(item.attrib['DOM']) == dom:
                            remove_sentence = True
                # Это для отдельно болтающихся предлогох/союзов
                if token.attrib.get('FEAT', '') and  token.attrib.get('FEAT', '').split()[0] in garbage and token.attrib['DOM'] == '_root':
                    child_id = token.attrib['ID']
                    children = get_children_attrib(sentence, child_id)
                    if children == []:
                        remove_sentence = True
            if remove_sentence:
                sentence.clear()
                continue
        tree.write(ofname, encoding = 'utf-8')
    return

def main(ifolder, ofolder):
	munch(*get_fnames(ifolder, ofolder, '.xml', '.xml'))
	print('2: changeCompounds.py completed')

if __name__ == "__main__":
    main(ifolder, ofolder)

