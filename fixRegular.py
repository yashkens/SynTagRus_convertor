#!/usr/bin/env python3

""" find and re-annotate 'не' and 'быть' """

import re
import os

from util import import_xml_lib, get_fnames, get_info, get_children
ET = import_xml_lib()

ifolder = 'Cleaned'
ofolder = 'MoreFixes'

suspicious = {'кто':'некого', 'что':'нечего', 'куда':'некуда', 'зачем':'незачем', 'откуда':'неоткуда', 'где':'негде'}
useless = {'вводн', 'cc', 'mark', 'огранич', 'соч-союзн', 'сент-соч', 'аналит', 'подч-союзн', 'сравнит', 'сравн-союзн', 'разъяснит', 'пасс-анал ', 'инф-союзн', 'сочин', 'присвяз', 'несобст-агент'}
priority = {'1-компл': 1, '2-компл': 2, '1-несобст-компл': 3, '2-несобст-компл': 4, 'неакт-компл': 5, 'nummod': 6, 'nummod:gov': 7, 'обст': 8, 'предик':9}
forbidden_head = {'как', 'будто', 'словно', 'точно', 'вроде', 'хотя'}

def munch(ifiles, ofiles):
    """
    Process all files in ifiles list.
    Output into ofiles list.
    """
    for ifname, ofname in zip(ifiles, ofiles):
        tree = ET.parse(ifname)
        root = tree.getroot()
        for sentence in root[-1].findall('S'):
            for token in sentence.findall('W'): # step 0: detect and re-annotate 'не'
                if token.attrib['LEMMA'] == 'не' and 'VERB' in token.attrib['FEAT']:
                    link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(token, sentence)
                    children  = get_children(sentence, token.attrib['ID'])
                    if token.text != 'FANTOM' and all(ch.text != 'FANTOM' for ch in children):
                        for elem in children:
                            if 'VerbForm=Inf' in elem.attrib['FEAT']:
                                gr_children = get_children(sentence, elem.attrib['ID'])
                                break
                        for item in gr_children:
                            if item.attrib['LEMMA'] in suspicious:
                                gr_gr_children = get_children(sentence, item.attrib['ID'])
                                if all(gr_gr.attrib['FEAT'].split()[0] != 'ADP' for gr_gr in gr_gr_children):
                                    token.attrib['LEMMA'] = suspicious[item.attrib['LEMMA']]
                                    token.text = token.text + item.text
                                    token.attrib['FEAT'] = item.attrib['FEAT']
                                    item.attrib['DEL'] = 'YES'
                                break
                    elif token.text != 'FANTOM' and any(ch.text == 'FANTOM' for ch in children):
                        for elem in children:
                            if 'VerbForm=Inf' in elem.attrib['FEAT']:
                                gr_children = get_children(sentence, elem.attrib['ID'])
                                break
                        for item in gr_children:
                            if item.attrib['LEMMA'] in suspicious:
                                gr_gr_children = get_children(sentence, item.attrib['ID'])
                                if all(gr_gr.attrib['FEAT'].split()[0] != 'ADP' for gr_gr in gr_gr_children):
                                    token.attrib['LEMMA'] = suspicious[item.attrib['LEMMA']]
                                    token.attrib['FEAT'] = item.attrib['FEAT']
                                    item.attrib['DEL'] = 'YES'
                                break
                    elif token.text == 'FANTOM' and children == []:
                        if sentence.attrib['ID'] == '217':
                            for elem in sentence.findall('W'):
                                if elem.attrib['ID'] == '11':
                                    elem.attrib['DEL'] = 'YES'
                                if elem.attrib['ID'] == '12':
                                    elem.attrib['LEMMA'] = 'нечего'
                        if sentence.attrib['ID'] == '94':
                            for elem in sentence.findall('W'):
                                if elem.attrib['ID'] == '11':
                                    elem.attrib['DEL'] = 'YES'
                        if sentence.attrib['ID'] == '169':
                            for elem in sentence.findall('W'):
                                if elem.attrib['ID'] == '6':
                                    elem.attrib['DOM'] = '14'
                                if elem.attrib['ID'] == '9':
                                    elem.attrib['DEL'] = 'YES'
                                if elem.attrib['ID'] == '10':
                                    elem.attrib['LEMMA'] = 'некого'
                                if elem.attrib['ID'] == '11':
                                    elem.attrib['DOM'] = '13'
                                if elem.attrib['ID'] == '12':
                                    elem.attrib['DEL'] = 'YES'
                                if elem.attrib['ID'] == '13':
                                    elem.attrib['LEMMA'] = 'негде'
                                    elem.attrib['DOM'] = '10'

                    elif token.text == 'FANTOM' and any(ch.text == 'FANTOM' for ch in children):
                        for elem in sentence.findall('W'):
                            if elem.attrib['ID'] == '11':
                                elem.attrib['DEL'] = 'YES'
                            if elem.attrib['ID'] == '2':
                                elem.attrib['LEMMA'] = suspicious[elem.attrib['LEMMA']]
                                elem.attrib['DOM'] = '_root'
                                del elem.attrib['LINK']
                            if elem.attrib['DOM'] == '1':
                                elem.attrib['DOM'] == '2'

                    elif token.text == 'FANTOM' and all(ch.text != 'FANTOM' for ch in children):
                        if all('VerbForm=Inf' not in ch.attrib['FEAT'] for ch in children):
                            if sentence.attrib['ID'] == '440':
                                for elem in sentence.findall('W'):
                                    if elem.attrib['ID'] == '16':
                                        elem.attrib['DOM'] = '18'
                                    if elem.attrib['ID'] == '17':
                                        elem.attrib['DEL'] = 'YES'
                                    if elem.attrib['ID'] == '18':
                                        elem.attrib['LEMMA'] = suspicious[elem.attrib['LEMMA']]
                        for elem in children:
                            if 'VerbForm=Inf' in elem.attrib['FEAT']:
                                gr_children = get_children(sentence, elem.attrib['ID'])
                                if head_token is None:
                                    for item in gr_children:
                                        if item.attrib['LEMMA'] in suspicious:
                                            gr_gr_children = get_children(sentence, item.attrib['ID'])
                                            if all(gr_gr.attrib['FEAT'].split()[0] != 'ADP' for gr_gr in gr_gr_children):
                                                item.attrib['LEMMA'] = suspicious[item.attrib['LEMMA']]
                                                item.attrib['DOM'] = '_root'
                                                del item.attrib['LINK']
                                                token.attrib['DEL'] = 'YES'
                                                for renum in sentence.findall('W'):
                                                    if renum.attrib['DOM'] == token.attrib['ID']:
                                                        renum.attrib['DOM'] = item.attrib['ID']
                                            break
                                    else:
                                        for broken in children:
                                            if broken.attrib['LEMMA'] in suspicious:
                                                broken.attrib['LEMMA'] = suspicious[broken.attrib['LEMMA']]
                                                broken.attrib['DOM'] = '_root'
                                                del broken.attrib['LINK']
                                                token.attrib['DEL'] = 'YES'
                                                for renum in sentence.findall('W'):
                                                    if renum.attrib['DOM'] == token.attrib['ID']:
                                                        renum.attrib['DOM'] = broken.attrib['ID']

                                else:
                                    for item in gr_children:
                                        if item.attrib['LEMMA'] in suspicious:
                                            gr_gr_children = get_children(sentence, item.attrib['ID'])
                                            if all(gr_gr.attrib['FEAT'].split()[0] != 'ADP' for gr_gr in gr_gr_children):
                                                token.attrib['LEMMA'] = suspicious[item.attrib['LEMMA']]
                                                token.attrib['FEAT'] = item.attrib['FEAT']
                                                token.text = item.text
                                                item.attrib['DEL'] = "YES"
                                                for renum in sentence.findall('W'):
                                                    if renum.attrib['DOM'] == item.attrib['ID']:
                                                        renum.attrib['DOM'] = token.attrib['ID']
                    else:
                        pass
        for sentence in root[-1].findall('S'): # step 2: collect token numbers old:new
            numbering = {}
            token_number = 0
            for token in sentence.findall('W'):
                if 'DEL' not in token.attrib:
                    token_number += 1
                numbering[token.attrib['ID']] = str(token_number)

            for word in sentence.findall('W'):  # step 3: assign new numbers
                word.attrib['ID'] = numbering[word.attrib['ID']]
                if word.attrib['DOM'] != '_root':
                    word.attrib['DOM'] = numbering[word.attrib['DOM']]
            for elem in sentence.findall('W'): # step 4: remove tokens
                if 'DEL' in elem.attrib:
                    sentence.remove(elem)

        for sentence in root[-1].findall('S'):
            for token in sentence.findall('W'): # Mood=Cnd fix
                if token.attrib['LEMMA'] in {'бы', 'б', 'чтобы', 'чтоб'}:
                    link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(token, sentence)
                    try:
                        if head_token.attrib['LEMMA'] not in forbidden_head:
                            if pos in {'SCONJ', 'PART'}:
                                token.attrib['FEAT'] = token.attrib['FEAT'] + ' Mood=Cnd'
                            else:
                                token.attrib['FEAT'] = token.attrib['FEAT'].replace(' Foreign=Yes', '')
                    except:
                        print('Something went wrong')
                        print(*[(elem.text, elem.tail.rstrip('\n'), elem.attrib) for elem in sentence], sep='\n')
                        print()

        tree.write(ofname, encoding="UTF-8")
    return

def process_all(ifolder, ofolder):
	munch(*get_fnames(ifolder, ofolder, '.xml', '.xml'))
	print('11: fixRegular.py completed')

if __name__ == "__main__":
    process_all(ifolder, ofolder)

