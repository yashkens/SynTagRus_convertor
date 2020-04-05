#!/usr/bin/env python3

""" 'predict' proper nouns """

import re
import os
from collections import defaultdict

from util import import_xml_lib, get_fnames, get_info
ET = import_xml_lib()

ifolder = 'Morphology'
ofolder = 'Propernouns'

def main(ifname_list, ofname_list):
    #collect all PROPN
    proper_detected = defaultdict(int)
    for ifname, ofname in zip(ifname_list, ofname_list):
        tree = ET.parse(ifname)
        root = tree.getroot()
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                feats = word.attrib.get('FEAT', 'EMPTY').split()
                if 'PROPN' in feats:
                    proper_detected[word.attrib['LEMMA']] += 1

    not_proper_detected = defaultdict(int)
    for ifname, ofname in zip(ifname_list, ofname_list):
        tree = ET.parse(ifname)
        root = tree.getroot()
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                if word.attrib['LEMMA'] in proper_detected:
                    feats = word.attrib.get('FEAT', 'EMPTY').split()
                    if 'PROPN' not in feats:
                        not_proper_detected[word.attrib['LEMMA']] += 1

    for ifname, ofname in zip(ifname_list, ofname_list):
        tree = ET.parse(ifname)
        root = tree.getroot()

        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                feats = word.attrib.get('FEAT', 'EMPTY').split()
                if (word.text is not None and
                    word.text.istitle() and 
                    ('NOUN' in feats or 'ADJ' in feats) and
                     word.attrib['LEMMA'] in proper_detected and
                     proper_detected[word.attrib['LEMMA']] > not_proper_detected[word.attrib['LEMMA']]):

                    feats[0] = 'PROPN'
                    word.attrib['FEAT'] = ' '.join(feats)

        for sent in root[-1].findall('S'):
            nidChain = []
            listOfChains = []
            for word in sent.findall('W'):
                feats = word.attrib.get('FEAT', 'EMPTY').split()
                if 'NID' in feats:
                    nidChain.append(word)
                elif nidChain != []:
                    listOfChains.append(nidChain)
                    nidChain = []
            if nidChain != []:
                listOfChains.append(nidChain)
                nidChain = []

            for nidChain in listOfChains:
                if len(nidChain) == 1:
                    assign(nidChain)
                else:
                    ids = [elem.attrib['ID'] for elem in nidChain]
                    condidates = [elem for elem in nidChain if elem.attrib['DOM'] not in ids]
                    if len(condidates) == 1:
                        domNumber = condidates[0].attrib['DOM']
                        nidChain = revertLink(domNumber, nidChain)
                        assign(nidChain)
                    else:
                        for item in condidates:
                            revisedNidChaine = [item]
                            going = False
                            currentHeadID = item.attrib['ID']
                            while not going:
                                for elem in nidChain:
                                    if elem.attrib['DOM'] == currentHeadID:
                                        revisedNidChaine.append(elem)
                                        currentHeadID = elem.attrib['ID']
                                        break
                                else:
                                    going = True
                            if len(revisedNidChaine) > 1:
                                nidChain = revertLink(item.attrib['DOM'], revisedNidChaine)
                                assign(nidChain)
                            else:
                                assign(revisedNidChaine)

        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(word, sent)
                if word.attrib.get('LEMMA', 'EMPTY') in ['все', 'это', 'то'] and pos in ['PROPN', 'NOUN']:
                    feats_temp = word.attrib['FEAT'].split(' ')
                    word.attrib['FEAT'] = 'PRON ' + feats_temp[1]

        tree.write(ofname, encoding="UTF-8")

def revertLink(domNumber, nidChain):
    nidChain[0].attrib['DOM'] = domNumber
    for i, elem in enumerate(nidChain[1:]):
        elem.attrib['DOM'] = nidChain[i].attrib['ID']
    return nidChain

def assign(newChain):
    for elem in newChain:
        if re.match(r'\b[^А-ЯЁа-яё]+\b', elem.attrib['LEMMA']):
            if 'LINK' in elem.attrib:
                if elem.attrib['LINK'] not in ['nsubj', 'nsubj:pass']:
                    elem.attrib['LINK'] = 'flat:foreign'
        if elem.text.isalnum() and not elem.text.islower():
            elem.attrib['FEAT'] = 'PROPN Foreign=Yes'
        else:
            elem.attrib['FEAT'] = 'X Foreign=Yes'
    return

def collect_foreign(sent): # find and collect children
    foreignTok = []
    for child in sent.findall('W'):
        if child.attrib.get('FEAT', '').split()[0] == 'NID':
            foreignTok.append([child.attrib, child.text])
    return foreignTok

def process_all(ifolder, ofolder):
	main(*get_fnames(ifolder, ofolder, '.xml', '.xml'))
	print('9: propernouns.py completed')

if __name__ == "__main__":
    process_all(ifolder, ofolder)

