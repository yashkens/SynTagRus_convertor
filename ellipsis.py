#!/usr/bin/env python3

""" process ellipsis """

import os
import re
import sys

import lxml.etree as ET

from util import get_fnames, get_children

ifolder = 'FixRegular'
ofolder = 'Ellipsis'

if len(sys.argv) > 1:
    ifolder = sys.argv[1]
    ofolder = sys.argv[2]

priority = {'предик': 0, '1-компл': 1, '2-компл': 2, '3-компл': 3, '4-компл': 4, '1-несобст-компл': 5, 'неакт-компл':6, 'nummod': 7, 'nummod:gov': 8, 'обст': 9, 'суб-копр': 10,}

promotion = {'nsubj': 1, 'nsubj:pass': 2, 'obj': 3, 'iobj': 4, 'obl': 5, 'advmod': 6, 'csubj': 7, 'csubj': 8, 'xcomp': 9, 'ccomp': 10, 'aux': 11}

promotion_nominal = {'amod': 1, 'nummod': 2, 'det': 3, 'compound': 4, 'nmod': 5, 'appos': 6, 'acl': 7, 'case': 8}

priority_nominal = {'квазиагент': 1, 'атриб': 2, 'композ': 3, '1-компл': 4, '2-компл': 5, 'nummod:gov': 6, 'огранич': 7,}


def munch(ifiles, ofiles):
    """
    Process all files in ifiles list.
    Output into ofiles list.
    """
    for ifname, ofname in zip(ifiles, ofiles):
        tree = ET.parse(ifname)
        root = tree.getroot()
        for sentence in root[-1].findall('S'): # step 1: collect token numbers old:new
            numbering = {}
            fantom_number = 0
            token_number = 0
            for token in sentence.findall('W'):
                if token.text != 'FANTOM':
                    token_number += 1
                    fantom_number = 0
                    numbering[token.attrib['ID']] = str(token_number)
                else:
                    fantom_number += 1
                    numbering[token.attrib['ID']] = str(token_number) + '.' + str(fantom_number)

            for word in sentence.findall('W'):  # step 2: assign new numbers
                word.attrib['ID'] = numbering[word.attrib['ID']]
                if word.attrib['DOM'] != '_root':
                    word.attrib['DOM'] = numbering[word.attrib['DOM']]

            for elem in sentence.findall('W'):  # step 3: add new atribute for enhanced representation
                if elem.attrib['DOM'] == '_root':
                    elem.attrib['ENH'] = '0:root'
                else:
                    elem.attrib['ENH'] = elem.attrib['DOM'] + ':' + elem.attrib['LINK']

            for token in sentence.findall('W'): # step 7: fix head ellipsys
                if token.text == 'FANTOM' and token.attrib['DOM'] == '_root':
                    candidate_children = get_children(sentence, token.attrib['ID'])
                    children = []
                    fantom_children = []
                    for child in candidate_children:
                        # real children to the left,
                        # fantom children to the right
                        if child.text == 'FANTOM':
                            fantom_children.append(child)
                        else:
                            children.append(child)
                    guy_to_promote = None # haven't found him yet

                    token.attrib['LINK'] = 'none'

                    if len(children) == 1:
                        guy_to_promote = children[0]
                        new_children = get_children(sentence, children[0].attrib['ID'])
                        children[0].attrib['DOM'] = '_root'
                        children[0].attrib['ENH'] = '0:root'
                        del children[0].attrib['LINK']
                        token.attrib['DOM'] = children[0].attrib['ID']

                        if len(new_children) == 1:
                            if new_children[0].text != 'FANTOM' and new_children[0].attrib['LINK'] != 'parataxis':
                                new_children[0].attrib['LINK'] = 'orphan'
                        elif len(new_children) == 2 and any(n_ch.attrib['LINK'] == 'fixed' for n_ch in new_children):
                            for ch in new_children:
                                if ch.attrib['LINK'] != 'fixed':
                                    if ch.text != 'FANTOM' and ch.attrib['LINK'] != 'parataxis':
                                        ch.attrib['LINK'] = 'orphan'
                                    break
                        else:
                            for ch in new_children:
                                if ch.attrib['LINK'] != 'iobj':
                                    if ch.text != 'FANTOM' and ch.attrib['LINK'] != 'parataxis':
                                        ch.attrib['LINK'] = 'orphan'
                                    break

                    elif len(children) >= 2:
                        if token.attrib['FEAT'].split()[0] in {'PROPN', 'NOUN', 'PRON', 'SYM'}:
                            if any(child.attrib['LINK'] == 'nsubj' for child in children):
                                for item in children:
                                    if item.attrib['LINK'] == 'nsubj': #**
                                        guy_to_promote = item
                                        item.attrib['DOM'] = '_root'
                                        item.attrib['ENH'] = '0:root'
                                        del item.attrib['LINK']
                                        token.attrib['DOM'] = item.attrib['ID']
                                        for elem in children:
                                            if elem.attrib['ID'] != item.attrib['ID']:
                                                 elem.attrib['DOM'] = item.attrib['ID']
                                                 if elem.text != 'FANTOM' and elem.attrib['LINK'] != 'parataxis':
                                                     elem.attrib['LINK'] = 'orphan'
                                        break

                            elif any(child.attrib['LINK'] in promotion_nominal for child in children): # UD relations priority
                                children.sort(key = lambda x: promotion_nominal.get(x.attrib['LINK'], 100))
                                if children[0].attrib['LINK'] != children[1].attrib['LINK']: #**
                                    guy_to_promote = children[0]
                                    children[0].attrib['DOM'] = '_root'
                                    children[0].attrib['ENH'] = '0:root'
                                    del children[0].attrib['LINK']
                                    token.attrib['DOM'] = children[0].attrib['ID']
                                    for elem in children:
                                        if elem.attrib['ID'] != children[0].attrib['ID']:
                                            elem.attrib['DOM'] = children[0].attrib['ID']
                                else:
                                    if any(child.attrib['OLD'] in priority for child in children): # original relations priority
                                        children.sort(key = lambda x: priority.get(x.attrib['OLD'], 100))
                                        if children[0].attrib['OLD'] != children[1].attrib['OLD']: #**
                                            guy_to_promote = children[0]
                                            children[0].attrib['DOM'] = '_root'
                                            children[0].attrib['ENH'] = '0:root'
                                            del children[0].attrib['LINK']
                                            token.attrib['DOM'] = children[0].attrib['ID']
                                            for elem in children:
                                                if elem.attrib['ID'] != children[0].attrib['ID']:
                                                    elem.attrib['DOM'] = children[0].attrib['ID']

                        elif any(child.attrib['LINK'] in promotion for child in children): # UD relations priority
                            children.sort(key = lambda x: promotion.get(x.attrib['LINK'], 100))
                            if children[0].attrib['LINK'] != children[1].attrib['LINK']:
                                guy_to_promote = children[0]
                                children[0].attrib['DOM'] = '_root'
                                children[0].attrib['ENH'] = '0:root'
                                del children[0].attrib['LINK']
                                token.attrib['DOM'] = children[0].attrib['ID']
                                for elem in children:
                                    if elem.attrib['ID'] != children[0].attrib['ID']:
                                         elem.attrib['DOM'] = children[0].attrib['ID']
                                         if elem.text != 'FANTOM' and elem.attrib['LINK'] != 'parataxis':
                                             elem.attrib['LINK'] = 'orphan'
                            else:
                                if any(child.attrib['OLD'] in priority for child in children): # original relations priority
                                    children.sort(key = lambda x: priority.get(x.attrib['OLD'], 100))
                                    #if children[0].attrib['OLD'] != children[1].attrib['OLD']:
                                    # we can't distinguish them in any further way,
                                    # so we just pick the first one regardless
                                    guy_to_promote = children[0]
                                    children[0].attrib['DOM'] = '_root'
                                    children[0].attrib['ENH'] = '0:root'
                                    del children[0].attrib['LINK']
                                    token.attrib['DOM'] = children[0].attrib['ID']
                                    for elem in children:
                                        if elem.attrib['ID'] != children[0].attrib['ID']:
                                            elem.attrib['DOM'] = children[0].attrib['ID']
                                            if elem.text != 'FANTOM' and elem.attrib['LINK'] != 'parataxis':
                                                elem.attrib['LINK'] = 'orphan'

                        else: # parataxis: 2 examples
                            for elem in children:
                                if elem.attrib['LINK'] == 'parataxis':
                                    guy_to_promote = 'parataxis'
                                    elem.attrib['DOM'] = '_root'
                                    elem.attrib['ENH'] = '0:root'
                                    del elem.attrib['LINK']
                                    token.attrib['DOM'] = elem.attrib['ID']
                                    for it in children:
                                        if it.attrib['ID'] !=elem.attrib['ID']:
                                            it.attrib['DOM'] = elem.attrib['ID']
                                            if it.text != 'FANTOM' and it.attrib['LINK'] != 'parataxis':
                                                it.attrib['LINK'] = 'orphan'

                    # rehang fantom children onto guy_to_promote
                    for fantom_child in fantom_children:
                        fantom_child.attrib['DOM'] = guy_to_promote.attrib['ID']
                    break

            for token in sentence.findall('W'):
                # step 4: detect orphan deprel
                if token.text != 'FANTOM':
                    children = get_children(sentence, token.attrib['ID'])
                    if all(child.text != 'FANTOM' for child in children):
                        continue

                    # populate with initial fantoms
                    fantom_list = [child for child in children if child.text == 'FANTOM']
                    fantom_queue = [fantom for fantom in fantom_list]

                    while fantom_queue != []:
                        current_fantom = fantom_queue.pop(0)
                        grand_children = get_children(sentence, current_fantom.attrib['ID'])
                        for ch in grand_children:
                            if ch.text == 'FANTOM':
                                fantom_queue.append(ch)
                                fantom_list.append(ch)

                    # fix unexpected orphans in fantoms
                    for fantom in fantom_list:
                        if fantom.attrib['LINK'] == 'orphan':
                            fantom.attrib['LINK'] = fantom.attrib['ENH'].split(':', maxsplit=1)[1]

                    for initial_fantom in fantom_list[::-1]:

                        children_list = [child for child in get_children(sentence, initial_fantom.attrib['ID']) if child.text != 'FANTOM']
                        nominal_successful = False
                        fantom_feat = initial_fantom.attrib['FEAT'].split()[0]

                        if fantom_feat in {'PROPN', 'NOUN', 'PRON', 'SYM', 'ADJ'}:
                            if any(child.attrib['LINK'] == 'nsubj' for child in children_list):
                                for item in children_list:
                                    if item.attrib['LINK'] == 'nsubj':
                                        item.attrib['LINK'] = initial_fantom.attrib['LINK']
                                        item.attrib['DOM'] = initial_fantom.attrib['DOM']
                                        for elem in children_list:
                                            if elem.attrib['ID'] != item.attrib['ID']:
                                                elem.attrib['DOM'] = item.attrib['ID']
                                                elem.attrib['LINK'] = 'orphan'
                                        break
                                nominal_successful = True
                            else:
                                
                                if len(children_list) == 1:
                                    if children_list[0].attrib['LINK'] != 'acl': 
                                        children_list[0].attrib['LINK'] = initial_fantom.attrib['LINK']
                                    children_list[0].attrib['DOM'] = initial_fantom.attrib['DOM']
                                    nominal_successful = True
                                else:
                                    promotion_sorted, priority_sorted, evolution_list = None, None, None
                                    if any(child.attrib['LINK'] in promotion_nominal for child in children_list): # UD relations priority
                                        promotion_sorted = sorted(children_list, key = lambda x: promotion_nominal.get(x.attrib['LINK'], 100))

                                    if any(child.attrib['OLD'] in priority_nominal for child in children_list): # original relations priority
                                        priority_sorted = sorted(children_list, key = lambda x: priority_nominal.get(x.attrib['OLD'], 100))
                                    if promotion_sorted is None:
                                        evolution_list = priority_sorted
                                    elif promotion_sorted[0].attrib['LINK'] == promotion_sorted[1].attrib['LINK']:
                                        if promotion_sorted[0].attrib['LINK'] == 'amod':
                                            evolution_list = promotion_sorted
                                        elif priority_sorted is None:
                                            evolution_list = promotion_sorted
                                        elif priority_sorted[0].attrib['OLD'] != priority_sorted[1].attrib['OLD']:
                                            evolution_list = priority_sorted
                                        else:
                                            evolution_list = promotion_sorted
                                    else:
                                        evolution_list = promotion_sorted

                                    if evolution_list is not None:
                                        children_list = evolution_list

                                        children_list[0].attrib['LINK'] = initial_fantom.attrib['LINK']
                                        children_list[0].attrib['DOM'] = initial_fantom.attrib['DOM']
                                        for elem in children_list:
                                            if elem.attrib['ID'] != children_list[0].attrib['ID']:
                                                 elem.attrib['DOM'] = children_list[0].attrib['ID']
                                        nominal_successful = True
                        if not nominal_successful:
                            if len(children_list) == 1:
                                children_list[0].attrib['LINK'] = initial_fantom.attrib['LINK']
                                children_list[0].attrib['DOM'] = initial_fantom.attrib['DOM']
                            else:
                                promotion_sorted, priority_sorted, evolution_list = None, None, None

                                if any(child.attrib['LINK'] in promotion for child in children_list): # UD relations priority
                                    promotion_sorted = sorted(children_list, key = lambda x: promotion.get(x.attrib['LINK'], 100))

                                if any(child.attrib['OLD'] in priority for child in children_list): # original relations priority
                                    priority_sorted = sorted(children_list, key = lambda x: priority.get(x.attrib['OLD'], 100))

                                if promotion_sorted is None:
                                    evolution_list = priority_sorted
                                elif promotion_sorted[0].attrib['LINK'] == promotion_sorted[1].attrib['LINK']:
                                    if priority_sorted is None:
                                        evolution_list = promotion_sorted
                                    elif priority_sorted[0].attrib['OLD'] != priority_sorted[1].attrib['OLD']:
                                        evolution_list = priority_sorted
                                    else:
                                        evolution_list = promotion_sorted
                                else:
                                    evolution_list = promotion_sorted
                                   
                                if evolution_list is not None:
                                    children_list = evolution_list
                                    children_list[0].attrib['LINK'] = initial_fantom.attrib['LINK']
                                    children_list[0].attrib['DOM'] = initial_fantom.attrib['DOM']
                                    for elem in children_list:
                                        if elem.attrib['ID'] != children_list[0].attrib['ID']:
                                            elem.attrib['DOM'] = children_list[0].attrib['ID']
                                            if elem.attrib['LINK'] not in {'cc', 'mark', 'parataxis', 'conj'}:
                                                elem.attrib['LINK'] = 'orphan'
                                else:
                                    if any(child.attrib['LINK'] == 'discourse' and child.attrib['LEMMA'] == 'нет' for child in children_list):
                                        for elem in children_list:
                                            if elem.attrib['LINK']  == 'discourse' and elem.attrib['LEMMA'] == 'нет':
                                                elem.attrib['LINK'] = initial_fantom.attrib['LINK']
                                                elem.attrib['DOM'] = initial_fantom.attrib['DOM']
                                                for item in children_list:
                                                    if item.attrib['ID'] != elem.attrib['ID']:
                                                        item.attrib['DOM'] = elem.attrib['ID']
                                                        if item.attrib['LINK'] not in {'cc', 'mark', 'parataxis', 'conj'}:
                                                            item.attrib['LINK'] = 'orphan'
                                    elif any(child.attrib['LINK'] == 'advcl' for child in children_list):
                                        for elem in children_list:
                                            if elem.attrib['LINK']  == 'advcl':
                                                elem.attrib['LINK'] = initial_fantom.attrib['LINK']
                                                elem.attrib['DOM'] = initial_fantom.attrib['DOM']
                                                for item in children_list:
                                                    if item.attrib['ID'] != elem.attrib['ID']:
                                                        item.attrib['DOM'] = elem.attrib['ID']
                                                        if item.attrib['LINK'] not in {'cc', 'mark', 'parataxis', 'conj'}:
                                                            item.attrib['LINK'] = 'orphan'
                                    elif any(child.attrib['LINK'] == 'discourse' for child in children_list):
                                        for elem in children_list:
                                            if elem.attrib['LINK']  == 'discourse':
                                                elem.attrib['LINK'] = initial_fantom.attrib['LINK']
                                                elem.attrib['DOM'] = initial_fantom.attrib['DOM']
                                                for item in children_list:
                                                    if item.attrib['ID'] != elem.attrib['ID']:
                                                        item.attrib['DOM'] = elem.attrib['ID']
                                                        if item.attrib['LINK'] not in {'cc', 'mark', 'parataxis', 'conj'}:
                                                            item.attrib['LINK'] = 'orphan'

            for token in sentence.findall('W'):
                # step 5: delete 'cop' fantom tokens (preparations)
                # well, looks like not only 'cop', but all fantoms
                # that are leaves and have another fantom as a head
                change_number = {}
                if token.text == 'FANTOM':
                    children = get_enh_children(sentence, token.attrib['ID'])
                    if children == []:
                        token.attrib['DEL'] = 'YES'
                        current_fantom = round(float(token.attrib['ID']), 1)
                        start_token = round(float(token.attrib['ID'].split('.')[0]), 1)
                        end_token = start_token + 1
                        for elem in sentence.findall('W'):
                            if start_token < round(float(elem.attrib['ID']), 1) < end_token:
                                if round(float(elem.attrib['ID']), 1) > current_fantom:
                                    change_number[elem.attrib['ID']] = str(round(float(elem.attrib['ID']) - 0.1, 1))
                        if change_number != {}:
                            for fantom in sentence.findall('W'):
                                if fantom.attrib['ID'] in change_number:
                                    fantom.attrib['ID'] = change_number[fantom.attrib['ID']]
                                if fantom.attrib['DOM'] != '_root' and fantom.attrib['DOM'] in change_number:
                                    fantom.attrib['DOM'] = change_number[fantom.attrib['DOM']]
                                enh_no = fantom.attrib['ENH'].split(':')[0]
                                if enh_no in change_number:
                                    fantom.attrib['ENH'] = fantom.attrib['ENH'].replace(enh_no, change_number[enh_no])

            for token in sentence.findall('W'): # step 6: delete 'cop' fantom tokens (deletion)
                if token.text == 'FANTOM' and token.attrib.get('DEL', 'EMPTY') == 'YES':# and token.attrib.get('LINK', 'EMPTY') == 'cop':
                    sentence.remove(token)

            for token in sentence.findall('W'): # fix orphan + CCONJ 29.11.17
                if token.attrib.get('FEAT', 'EMPTY').split()[0] in {'CCONJ', 'SCONJ'} and token.attrib.get('LINK', 'EMPTY') == 'orphan':
                    if token.attrib['ENH'].split(':')[1] == 'orphan':
                        if token.attrib['LEMMA'] == 'чтобы':
                            token.attrib['LINK'] = 'mark'
                        else:
                            token.attrib['LINK'] = 'cc'
                    else:
                        token.attrib['LINK'] = token.attrib['ENH'].split(':')[1]

            # Something went wrong
            for token in sentence.findall('W'):
                if token.text != 'FANTOM' and '.' in token.get('DOM', ''):
                    print('-' * 20)
                    print(ifname)
                    print('-' * 20)
                    print(token.attrib['DOM'])
                    print(*[ch.attrib['LINK'] for ch in get_children(sentence, token.attrib['DOM'])])
                    print(*[ch.attrib['OLD'] for ch in get_children(sentence, token.attrib['DOM'])])
                    print('-' * 20)
                    for item in sentence.findall('W'):
                        print(item.text, item.attrib['LEMMA'], item.attrib['FEAT'].split()[0], item.attrib['ID'], item.attrib['DOM'], item.attrib.get('LINK', ''), item.attrib['ENH'])
                    print('=' * 20)

        tree.write(ofname, encoding="UTF-8")
    return

def get_enh_children(sent, dad_id):
    """
    Collect all direct enhanced children.
    """
    children = []
    for token in sent:
        if token.attrib.get('ENH', '').split(':', maxsplit=1)[0] == dad_id:
            children.append(token)
    return children

def process_all(ifolder, ofolder):
	munch(*get_fnames(ifolder, ofolder, '.xml', '.xml'))
	print('13: ellipsys.py completed')

if __name__ == "__main__":
    process_all(ifolder, ofolder)

