#!/usr/bin/env python3

""" Change the head of a root conjunction """

import os

from util import import_xml_lib, get_fnames, get_children_attrib
ET = import_xml_lib()

CONJ_root_rel_list = ["соч-союзн", "подч-союзн", "сравн-союзн", "инф-союзн"]
logfile = 'garbagecollector.txt'
ifolder = 'Prepositions'
ofolder = 'Conjunctions'

conj_set = {'а', 'ан', 'да', 'зато', 'и', 'или', 'иль', 'иначе',
            'либо', 'ни', 'но', 'однако', 'притом', 'причем',
            'причём', 'сколько', 'столько', 'также', 'тоже', 'только',
            'и/или', 'а также', 'а то и', 'не то', 'так же как',
            'так и', 'в противном случае', 'х'}

def munch(ifiles, ofiles):
    count_garbage = 0
    for ifname, ofname in zip(ifiles, ofiles):
        tree = ET.parse(ifname)
        root = tree.getroot()
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                if word.attrib.get('FEAT', 'EMPTY').split()[0] == 'CONJ' and word.attrib['DOM'] == '_root': # is this root conjunction?
                    child_PR = word.attrib.get('ID', '')
                    chain = [word.attrib]
                    current = word.attrib
                    while True:
                        children = get_children_attrib(sent, current['ID'])
                        if not all(child['FEAT'] == 'CONJ' for child in children):
                            count_garbage = assign(sent, chain, children, count_garbage, ifname)
                            break
                        if len(children) == 1 and children[0]['FEAT'] == 'CONJ':
                            current = children[0]
                            chain.append(current)
        for sent in root[-1].findall('S'): # this part is for two exceptions which can be found in garbagecollector.txt
            for word in sent.findall('W'):
                if word.attrib.get('FEAT', 'EMPTY').split()[0] == 'CONJ' and word.attrib['DOM'] == '_root':
                    child_PR = word.attrib.get('ID', '')
                    chain = [word.attrib]
                    current = word.attrib
                    while True:
                        children = get_children_attrib(sent, current['ID'])
                        if not all(child['FEAT'] == 'CONJ' for child in children):
                            count_garbage = assign_fix(sent, chain, children, count_garbage, ifname)
                            break
                        if len(children) == 1 and children[0]['FEAT'] == 'CONJ':
                            current = children[0]
                            chain.append(current)
                            
        tree.write(ofname, encoding="UTF-8")
    return 
    
def garbagecollector(sent, ifname, count, place): # file for unidentified sentences
    with open(logfile, 'a', encoding='utf-8') as file:
        file.write(place + '   ' + count + '. ' + ifname + ': ' + sent.attrib['ID'] + '\n')
        for word in sent:
            file.write(str(word.attrib)+ str(word.text))
            file.write('\n')
        file.write('\n')
        file.close()
    return

def assign(sent, chain, children, count_garbage, ifname):
    if len(children) == 1:
        children[0]['DOM'] = '_root'
        children[0].pop('LINK')
        for elem in chain:
            elem['DOM'] = children[0]['ID']
            if elem['FEAT'].split()[0] == 'CONJ':
                if elem['LEMMA'] in conj_set:
                    elem['LINK'] = 'cc'
                else:
                    elem['LINK'] = 'mark'
    elif len(children) > 1:
        sanity_check = 0
        for elem in children:
            if elem['LINK'] in CONJ_root_rel_list:
                sanity_check += 1
        if sanity_check == 1:
            for token in children:
                if token['LINK'] in CONJ_root_rel_list and token['FEAT'].split()[0] != 'CONJ':
                    head = token['ID']
                    token['DOM'] = '_root'
                    token.pop('LINK')
                    for elem in chain:
                        if elem['FEAT'].split()[0] == 'CONJ':
                            if elem['LEMMA'] in conj_set:
                                elem['LINK'] = 'cc'
                            else:
                                elem['LINK'] = 'mark'
                            elem['DOM'] = head
                        else:
                            elem['DOM'] = head
                    for token in children:
                        if token['ID'] != head:
                            token['DOM'] = head
                            if token['FEAT'].split()[0] == 'CONJ':
                                if token['LEMMA'] in conj_set:
                                    token['LINK'] = 'cc'
                                else:
                                    token['LINK'] = 'mark'
        else:
            count_garbage += 1
            garbagecollector(sent, ifname, str(count_garbage), place = 'assign_inclosed')
    else:
        count_garbage += 1
        garbagecollector(sent, ifname, str(count_garbage), place = 'assign_main')
    return count_garbage
    
def assign_fix(sent, chain, children, count_garbage, ifname):
    if len(children) == 1:
        children[0]['DOM'] = '_root'
        children[0].pop('LINK')
        for elem in chain:
            elem['DOM'] = children[0]['ID']
            if elem['FEAT'].split()[0] == 'CONJ':
                if elem['LEMMA'] in conj_set:
                    elem['LINK'] = 'cc'
                else:
                    elem['LINK'] = 'mark'
    elif len(children) > 1:
        for token in children:
            if token['FEAT'].split()[0] != 'CONJ' and token['LINK'] == 'предик':
                head = token['ID']
                token['DOM'] = '_root'
                token.pop('LINK')
                for elem in chain:
                    if elem['FEAT'].split()[0] == 'CONJ':
                        if elem['LEMMA'] in conj_set:
                            elem['LINK'] = 'cc'
                        else:
                            elem['LINK'] = 'mark'
                        elem['DOM'] = head
                    else:
                        elem['DOM'] = head
                for token in children:
                    if token['ID'] != head:
                        token['DOM'] = head
                        if token['FEAT'].split()[0] == 'CONJ':
                            if token['LEMMA'] in conj_set:
                                token['LINK'] = 'cc'
                            else:
                                token['LINK'] = 'mark'
    else:
        count_garbage += 1
        garbagecollector(sent, ifname, str(count_garbage), place = 'assign_main')
    return count_garbage

def main(ifolder, ofolder):
	munch(*get_fnames(ifolder, ofolder, '.xml', '.xml'))
	print('5: conjunctions.py completed')
    
if __name__ == "__main__":
    main(ifolder, ofolder)
        
