#!/usr/bin/env python3

""" Fix mwe, fix verb lemmas. """

import os
import re
import sys
import csv

from util import import_xml_lib, get_fnames, get_info
from prop_tocheck import uncertain
from propn_lemmas_certain import certain
ET = import_xml_lib()

ifolder = 'Elided'
ofolder = 'Fixed'

csv_filename = 'mwe.csv'
fix_lemma = 'ImpToPerf.txt'
abbr = {'т.е', 'т.е.', 'т.д', 'т.д.', 'т.п.', 'т.п', 'т.к.', 'т.к', 'л.с.', 'л.c', 'o.s', 'р.х.', 'p.s', 'у.е.', 'ph.d', 'и.о.'}
glue = {'хотя', 'лишь', 'хоть'}

def munch(ifiles, ofiles):
    """
    Process all files in ifiles list.
    Output into ofiles list.
    """
    dict_of_fixed = get_fixed_rel()
    dict_of_lemmas = get_verb_lemmas()
    for ifname, ofname in zip(ifiles, ofiles):
        tree = ET.parse(ifname)
        root = tree.getroot()
        for k, sentence in enumerate(root[-1].findall('S')):
            for j, token in enumerate(sentence.findall('W')):
                    if (token.attrib['LEMMA'].lower(), token.attrib['FEAT']) in dict_of_fixed and token.text != 'FANTOM': # поменять сам токен
                        current_position = int(token.attrib['ID'])
                        shift_num = len(dict_of_fixed[token.attrib['LEMMA'].lower(), token.attrib['FEAT']][0]) - 1
                        shift_position = current_position - 1
                        for tok in sentence.findall('W'):
                            if '.' not in str(tok.attrib['ID']):
                                if int(tok.attrib['ID']) > current_position:
                                    tok.attrib['ID'] = str(int(tok.attrib['ID']) + shift_num)
                            else:
                                if float(tok.attrib['ID']) > float(current_position):
                                    tok.attrib['ID'] = str(round(float(tok.attrib['ID']) + float(shift_num), 1))

                            if '.' not in str(tok.attrib['DOM']):
                                if tok.attrib['DOM'] != '_root':
                                    if int(tok.attrib['DOM']) > current_position:
                                        tok.attrib['DOM'] = str(int(tok.attrib['DOM']) + shift_num)
                            else:
                                if float(tok.attrib['DOM']) > float(current_position):
                                    tok.attrib['DOM'] = str(round(float(tok.attrib['DOM']) + float(shift_num), 1))

                            first_position = ''
                            if tok.attrib['ENH'].startswith('E:E'):
                                first_position = 'E:E'
                                change_enh = tok.attrib['ENH'][3:].split(':')[0]
                            elif tok.attrib['ENH'].startswith('E'):
                                first_position = 'E'
                                change_enh = tok.attrib['ENH'][1:].split(':')[0]
                            else:
                                change_enh = tok.attrib['ENH'].split(':')[0]

                            if '.' not in str(change_enh):
                                #print(change_enh)
                                if int(change_enh) > current_position:
                                    change_enh = int(change_enh) + shift_num
                                    tok.attrib['ENH'] = first_position + str(change_enh) + ':' + tok.attrib['ENH'].split(':')[1]
                            else:
                                if float(change_enh) > float(current_position):
                                    change_enh = round(float(change_enh) + float(shift_num), 1)
                                    tok.attrib['ENH'] = first_position + str(change_enh) + ':' + tok.attrib['ENH'].split(':')[1]

                        if 'LINK' in token.attrib:
                            temp_rel = token.attrib['LINK'] # а если нет link
                        else:
                            temp_rel = '_root'
                        temp_dom = token.attrib['DOM']
                        temp_text = token.text.replace('.', '. ').split()[0]
                        temp_tail = token.tail

                        no_dot = (j == len(sentence.findall('W'))-1)
                        if not no_dot and temp_tail.startswith('.'):
                            temp_tail = temp_tail.lstrip('.')
                        sentence.remove(token)

                        starting_position = current_position

                        for i, elem in enumerate(dict_of_fixed[token.attrib['LEMMA'].lower(), token.attrib['FEAT']][0]):
                            tag = ET.fromstring('<W></W>')
                            tag.attrib['ID'] = str(current_position)
                            tag.attrib['LEMMA'] = elem[1]
                            tag.attrib['OLD'] = 'EMPTY'
                            tag.attrib['FEAT'] = elem[2]

                            head_position = dict_of_fixed[token.attrib['LEMMA'].lower(), token.attrib['FEAT']][1]
                            if i == head_position:
                                # this is the head token of the group
                                tag.attrib['DOM'] = str(temp_dom)
                                if elem[3] == '%':
                                    tag.attrib['LINK'] = temp_rel
                                else:
                                    tag.attrib['LINK'] = elem[3]
                            else:
                                tag.attrib['LINK'] = elem[3]
                                tag.attrib['DOM'] = str(starting_position + head_position)

                            # if DOM happened to become _root, remove LINK
                            if tag.attrib['DOM'] == '_root':
                                del tag.attrib['LINK']

                            if i == 0:
                                tag.text = temp_text
                            else:
                                tag.text = elem[0]

                            if i == len(dict_of_fixed[token.attrib['LEMMA'].lower(), token.attrib['FEAT']][0]) - 1:
                                tag.tail = temp_tail
                                if no_dot:
                                    tag.text = tag.text.rstrip('.')
                                    tag.attrib['LEMMA'] = tag.attrib['LEMMA'].strip('.')
                            else:
                                tag.tail = ' \n'

                            if 'LINK' not in tag.attrib and tag.attrib['DOM'] == '_root':
                                tag.attrib['ENH'] = '0:root'
                            else:
                                tag.attrib['ENH'] = str(tag.attrib['DOM']) + ':' + tag.attrib['LINK']

                            sentence.insert(shift_position, tag)
                            current_position += 1
                            shift_position += 1

            sorted_tokens = sorted(sentence.findall('W'), key=lambda x: float(x.attrib.get('ID', '100500')))
            while len(sentence.findall('W')) != 0:
                sentence.remove(sentence.findall('W')[-1])
            while len(sentence.findall('LF')) != 0:
                sentence.remove(sentence.findall('LF')[-1])
            for token in sorted_tokens:
                sentence.append(token)

        for sentence in root[-1].findall('S'):
            for i, token in enumerate(sentence.findall('W')):
                if i == 0:
                    token.text = token.text[0].upper() + token.text[1:]
                token.attrib['LEMMA'] = token.attrib['LEMMA'].replace('|', ',')
                if '|' in token.text:
                    token.text = token.text.replace('|', ',')
                if token.attrib['LEMMA'].endswith('-знак'):
                    token.attrib['LEMMA'] = token.text
                    token.attrib['FEAT'] = 'SYM'

        # small fixes from Olga 04.04.2018
        for sentence in root[-1].findall('S'):
            for i, token in enumerate(sentence.findall('W')):
                if token.attrib['LEMMA'] in glue:
                    if ifname.split('/')[-1] == '2011Petrushka.xml' and sentence.attrib['ID'] == '141':
                        sentence.findall('W')[39].attrib['DOM'] = '46'
                        sentence.findall('W')[40].attrib['DOM'] = '40'
                        sentence.findall('W')[40].attrib['LINK'] = 'fixed'
                        sentence.findall('W')[41].attrib['DOM'] = '46'
                        for h in range(39, 42):
                            sentence.findall('W')[h].attrib['ENH'] = sentence.findall('W')[h].attrib['DOM'] + ':' + sentence.findall('W')[h].attrib['LINK']
                    elif len(sentence.findall('W')) > i+1 and \
                       sentence.findall('W')[i+1].attrib['LEMMA'] == 'бы' and \
                       sentence.findall('W')[i+1].attrib['LINK'] != 'fixed':

                        sentence.findall('W')[i+1].attrib['LINK'] = 'fixed'
                        if token.attrib['DOM'] == sentence.findall('W')[i+1].attrib['ID']:
                            token.attrib['DOM'] = sentence.findall('W')[i+1].attrib['DOM']
                            token.attrib['ENH'] = ':'.join((token.attrib['DOM'], token.attrib['LINK']))

                        sentence.findall('W')[i+1].attrib['DOM'] = sentence.findall('W')[i].attrib['ID']
                        sentence.findall('W')[i+1].attrib['ENH'] = ':'.join((sentence.findall('W')[i+1].attrib['DOM'], sentence.findall('W')[i+1].attrib['LINK']))

                    elif len(sentence.findall('W')) > i+1 and \
                       sentence.findall('W')[i+1].attrib['LEMMA'] == 'бы' and \
                       sentence.findall('W')[i+1].attrib['DOM'] != sentence.findall('W')[i].attrib['ID']:
                        print(token.attrib['ID'])
                        print(*[(token.attrib['ID'], token.text, token.attrib['DOM'], token.attrib.get('LINK', 'EMPTY'), token.tail) for token in sentence], sep='\n')
                        print('*' * 20)
                elif token.attrib['LEMMA'] == 'второе' and ('ADJ' in token.attrib['FEAT'] or 'nmod' in token.attrib.get('LINK', 'EMPTY')):

                    token.attrib['LEMMA'] = 'второй'
                    token.attrib['FEAT'] = token.attrib['FEAT'].replace('Animacy=Inan|', '').replace('NOUN', 'ADJ')
                    if token.attrib.get('LINK', 'EMPTY') == 'nmod':
                        token.attrib['LINK'] = 'amod'
                        token.attrib['ENH'] = token.attrib['ENH'].replace('nmod', 'amod')

                elif token.attrib['LEMMA'] == 'вооружать' and 'ADJ' in token.attrib['FEAT']:
                    token.attrib['LEMMA'] = 'вооруженный'
                elif token.attrib['LEMMA'] == 'весь' and 'PRON' in token.attrib['FEAT']:
                    token.attrib['FEAT'] = ' '.join(['DET'] + token.attrib['FEAT'].split()[1:])
                elif token.attrib['LEMMA'] == 'главное' and 'ADV' in token.attrib['FEAT']:
                    token.attrib['FEAT'] = 'NOUN Animacy=Inan|Case=Nom|Gender=Neut|Number=Sing'
                elif token.attrib['LEMMA'] == 'дома' and 'NOUN' in token.attrib['FEAT']:
                    token.attrib['LEMMA'] = 'дом'
                elif token.attrib['LEMMA'] == 'звонок' and 'ADJ' in token.attrib['FEAT']:
                    token.attrib['FEAT'] = token.attrib['FEAT'].replace('Degree=Pos', 'Animacy=Inan|Case=Gen').replace('ADJ', 'NOUN').replace('|Variant=Short', '')
                elif token.attrib['LEMMA'] == 'многие' and 'ADJ' in token.attrib['FEAT']:
                    token.attrib['FEAT'] = 'NUM'
                    token.attrib['LEMMA'] = 'много'
                elif token.attrib['LEMMA'] == 'легкий' and 'NOUN' in token.attrib['FEAT']:
                    token.attrib['LEMMA'] = 'легкие'
                elif token.attrib['LEMMA'] == 'плюс' and 'SYM' in token.attrib['FEAT']:
                    token.attrib['LEMMA'] = '+'
                elif token.attrib['LEMMA'] == 'ли':
                    if token.attrib['LINK'] == 'conj':
                        token.attrib['LINK'] = 'advmod'
                    if token.attrib['LINK'] == 'discourse':
                        token.attrib['LINK'] = 'fixed'
                    token.attrib['ENH'] = token.attrib['ENH'].split(':')[0] + ':' + token.attrib['LINK']
                elif token.attrib['LEMMA'] == 'значит':
                    token.attrib['LINK'] = 'discourse'
                    token.attrib['ENH'] = token.attrib['ENH'].split(':')[0] + ':' + token.attrib['LINK']
                elif token.attrib['LEMMA'] == 'один' and 'ADJ' in token.attrib['FEAT']:
                    token.attrib['FEAT'] = ' '.join(['DET'] + token.attrib['FEAT'].split()[1:])

        for sentence in root[-1].findall('S'):
            for token in sentence.findall('W'):
                if token.attrib['LEMMA'].lower() in dict_of_lemmas and 'Aspect=Perf' in token.attrib['FEAT']:
                    token.attrib['LEMMA'] = dict_of_lemmas[token.attrib['LEMMA'].lower()]

        #this is test for debug purposes:
        #for sent in root[-1].findall('S'):

            #for wt in sent.findall('W'):
             #   link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(wt, sent)
             #   if wt.attrib.get('LINK') == 'acl:relcl' and head_token.attrib.get('LINK') == 'obl':
              #      print(wt.attrib['ID'], ifname, sent.attrib['ID'])

        # Change lemma capitalisation
        for sent in root[-1].findall('S'):

            for word in sent.findall('W'):
                link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(word, sent)
                if pos == 'PROPN' and word.attrib['ID'] == '1':

                    if word.attrib['LEMMA'] not in {'формула', 'чижик', 's', 'ps', 'fuck', 'да', 'ох'}:
                        if word.text.isupper():
                            word.attrib['LEMMA'] = word.attrib['LEMMA'].upper()
                        else:
                            word.attrib['LEMMA'] = word.attrib['LEMMA'].title()
                    elif word.attrib['LEMMA'] == 'чижик':
                        word.attrib['FEAT'] = word.attrib['FEAT'].replace('PROPN', 'NOUN')
                    elif word.attrib['LEMMA'] == 'ох':
                        word.attrib['FEAT'] = 'PART'
                    elif word.attrib['LEMMA'] in {'s', 'ps', 'fuck', 'да'}:
                        word.attrib['FEAT'] = word.attrib['FEAT'].replace('PROPN', 'X')
                    elif word.attrib['LEMMA'] == 'формула':
                        if sent[1].text == '1':
                            #sent[1].attrib['LINK'] = 'fixed' maybe later for all occurances
                            word.attrib['LEMMA'] = word.attrib['LEMMA'].title()
                        else:
                            word.attrib['FEAT'] = word.attrib['FEAT'].replace('PROPN', 'NOUN')
                elif pos == 'PROPN' and word.attrib['ID'] != '1':
                    if word.text.isupper():
                        word.attrib['LEMMA'] = word.attrib['LEMMA'].upper()
                    else:
                        word.attrib['LEMMA'] = word.attrib['LEMMA'].title()

                if word.text.istitle() and pos != 'PROPN' and word.attrib['ID'] != '1':
                    if word.text not in uncertain:
                        word.attrib['FEAT'] = 'PROPN' + (word.attrib['FEAT'] + '\t').split('\t', maxsplit=1)[1]
                        if word.text.isupper():
                            word.attrib['LEMMA'] = word.attrib['LEMMA'].upper()
                        else:
                            word.attrib['LEMMA'] = word.attrib['LEMMA'].title()
                    elif word.text in uncertain and word.attrib['LEMMA'].lower() in certain:
                        word.attrib['FEAT'] = 'PROPN' + (word.attrib['FEAT'] + '\t').split('\t', maxsplit=1)[1]
                        if word.text.isupper():
                            word.attrib['LEMMA'] = word.attrib['LEMMA'].upper()
                        else:
                            word.attrib['LEMMA'] = word.attrib['LEMMA'].title()
                    else:
                        pass # TODO: сделать ветку для неразобранных

        tree.write(ofname, encoding="utf-8")
    return

def get_fixed_rel():
    dict_of_fixed = {}
    with open(csv_filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        collecting_values = []
        for row in reader:
            if row[0][0].isalpha():
                key = (row[0], row[1])
                head_position = 0

            elif row[0].startswith('%'):
                if row[4] == '_':
                    feat = row[3]
                else:
                    feat = row[3] + ' ' + row[4]
                try:
                    value = (row[1], row[2].lower(), feat, row[5]) # word, lemma, feat, link
                except:
                    print(row)
                collecting_values.append(value)

                if row[5].startswith('%'):
                    head_position = len(collecting_values) - 1

            elif row[0].startswith('##'):
                dict_of_fixed[key] = (collecting_values, head_position)
                collecting_values = []

    return dict_of_fixed

def get_verb_lemmas():
    dict_of_lemmas = {}
    with open(fix_lemma, 'r', encoding='utf-8') as ffile:
        for line in ffile:
            line = line.strip().split('\t')
            dict_of_lemmas[line[0]] = line[1]
    return dict_of_lemmas

def process_all(ifolder, ofolder):
	munch(*get_fnames(ifolder, ofolder, '.xml', '.xml'))
	print('14: fixedDep.py completed')

if __name__ == "__main__":
    process_all(ifolder, ofolder)

