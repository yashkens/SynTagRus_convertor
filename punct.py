#!/usr/bin/env python3

""" Punctuation extraction. """

import os
import re
import sys
import csv

import xml.etree.ElementTree as ET

from util import get_fnames

ifolder = 'Fixed'
ofolder = 'PunctExtract'

def munch(ifiles, ofiles):
    """
    Process all files in ifiles list.
    Output into ofiles list.
    """
    for ifname, ofname in zip(ifiles, ofiles):
        tree = ET.parse(ifname)
        root = tree.getroot()
        for sentence in root[-1].findall('S'):
            if 'ID' not in sentence.attrib:
                continue 
            # add the first token punctuations
            suspect = sentence.text.strip('\n').lstrip('  ')
            if len(suspect.strip()) > 0:               
                shift_num = len(re.sub('\s', '', suspect))

                for tok in sentence.findall('W'):
                    if '.' not in str(tok.attrib['ID']):
                        tok.attrib['ID'] = str(int(tok.attrib['ID']) + shift_num)
                    if tok.attrib['DOM'] != '_root' and '.' not in str(tok.attrib['DOM']):
                        tok.attrib['DOM'] = str(int(tok.attrib['DOM']) + shift_num)
                    if '.' in str(tok.attrib['ID']):
                        tok.attrib['ID'] = str(round(float(tok.attrib['ID']) + float(shift_num), 1))
                    if tok.attrib['DOM'] != '_root' and '.' in str(tok.attrib['DOM']):
                        tok.attrib['DOM'] = str(round(float(tok.attrib['DOM']) + float(shift_num), 1))

                    first_position = ''
                    if not tok.attrib['ENH'].endswith('root'):
                        if tok.attrib['ENH'].startswith('E'):
                            first_position = 'E'
                            change_enh = tok.attrib['ENH'][1:].split(':')[0]
                        else:
                            change_enh = tok.attrib['ENH'].split(':')[0]
                        if '.' not in str(change_enh):
                            change_enh = int(change_enh) + shift_num
                            tok.attrib['ENH'] = first_position + str(change_enh) + ':' + tok.attrib['ENH'].split(':')[1]
                        else:
                            change_enh = round(float(change_enh) + float(shift_num), 1)
                            tok.attrib['ENH'] = first_position + str(change_enh) + ':' + tok.attrib['ENH'].split(':')[1]

                for i, (elem1, elem2) in enumerate(zip(suspect[:-1], suspect[1:])):
                    if re.match('\s', elem1) is None and elem1 != '\n':
                        tag = ET.fromstring('<W></W>')
                        tag.attrib['ID'] = str(i+1)
                        tag.attrib['DOM'] = str(1 + shift_num)
                        tag.attrib['LEMMA'] = tag.text = tag.attrib['OLD'] = elem1
                        tag.attrib['FEAT'] = 'PUNCT'
                        tag.attrib['LINK'] = tag.attrib['NEW'] = 'punct'
                        tag.attrib['ENH'] = str(tag.attrib['DOM']) + ':' + tag.attrib['LINK']
                        if re.match('\s', elem2) is None:
                            tag.tail = '\n'
                        else:
                            tag.tail = ' \n'
                        sentence.insert(i, tag)

                if re.match('\s', suspect[-1]) is None:
                    tag = ET.fromstring('<W></W>')
                    tag.tail = '\n'
                    tag.attrib['ID'] = str(shift_num)
                    tag.attrib['DOM'] = str(1 + shift_num)
                    tag.attrib['LEMMA'] = tag.text = tag.attrib['OLD'] = suspect[-1]
                    tag.attrib['FEAT'] = tag.attrib['NEW'] = 'PUNCT'
                    tag.attrib['LINK'] = 'punct'
                    tag.attrib['ENH'] = str(tag.attrib['DOM']) + ':' + tag.attrib['LINK']
                    tag.tail = '\n'
                    sentence.insert(shift_num-1, tag)

        for sentence in root[-1].findall('S'): # find the root
            if 'ID' in sentence.attrib:
                shifts = {'_root': '_root'}
                shift = 0
                
                for i, token in enumerate(sentence.findall('W')):
                    if token.attrib.get('DOM', 'NO').endswith('.0'):
                        for t in sentence.findall('W'):
                            print(t.text, t.attrib)
                        print()
                    if token.attrib.get('NEW', 'EMPTY') == 'punct':
                        continue
                    if '.' in token.attrib['ID']:
                        shifts[token.attrib['ID']] = str(round(float(token.attrib['ID']) + shift, 1))
                    else:
                        shifts[token.attrib['ID']] = str(int(token.attrib['ID']) + shift)
                    punct = token.tail

                    if punct.strip() != '':
                        to_prev, to_next = punct.split('\n')
                        prev_tok_id = int(float(token.attrib['ID']))
                        next_tok_id = prev_tok_id + 1

                        for j, (elem1, elem2) in enumerate(zip(to_prev[:-1], to_prev[1:])):
                            if re.match('\s', elem1) is None and elem1 != '\n':
                                shift += 1
                                tag = ET.fromstring('<W></W>')
                                tag.text = elem1
                                tag.attrib = {'ID': str(prev_tok_id + shift),
                                              'DOM': str(prev_tok_id),
                                              'LEMMA': elem1,
                                              'OLD': elem1,
                                              'FEAT': 'PUNCT',
                                              'LINK': 'punct',
                                              'ENH': str(prev_tok_id) + ':punct',
                                              'NEW': 'punct'}
                                if re.match('\s', elem2) is None:
                                    tag.tail = '\n'
                                else:
                                    tag.tail = ' \n'
                                sentence.insert(i + shift, tag)

                        if len(to_prev) > 0 and re.match('\s', to_prev[-1]) is None:
                            shift += 1
                            tag = ET.fromstring('<W></W>')
                            tag.attrib['ID'] = str(prev_tok_id + shift)
                            tag.attrib['DOM'] = str(prev_tok_id)
                            tag.attrib['LEMMA'] = tag.text = tag.attrib['OLD'] = to_prev[-1]
                            tag.attrib['FEAT'] = tag.attrib['NEW'] = 'PUNCT'
                            tag.attrib['LINK'] = 'punct'
                            tag.attrib['ENH'] = str(tag.attrib['DOM']) + ':' + tag.attrib['LINK']
                            tag.tail = '\n'
                            sentence.insert(i + shift, tag)

                        for k, (elem1, elem2) in enumerate(zip(to_next[:-1], to_next[1:])):
                            if re.match('\s', elem1) is None and elem1 != '\n':
                                shift += 1
                                tag = ET.fromstring('<W></W>')
                                tag.text = elem1
                                tag.attrib = {'ID': str(prev_tok_id + shift),
                                              'DOM': str(next_tok_id),
                                              'LEMMA': elem1,
                                              'OLD': elem1,
                                              'FEAT': 'PUNCT',
                                              'LINK': 'punct',
                                              'ENH': str(prev_tok_id) + ':punct',
                                              'NEW': 'punct'}
                                if re.match('\s', elem2) is None:
                                    tag.tail = '\n'
                                else:
                                    tag.tail = ' \n'
                                sentence.insert(i + shift, tag)

                        if len(to_next) > 0:
                            if re.match('\s', to_next[-1]) is None:
                                shift += 1
                                tag = ET.fromstring('<W></W>')
                                tag.attrib['ID'] = str(prev_tok_id + shift)
                                tag.attrib['DOM'] = str(next_tok_id)
                                tag.attrib['LEMMA'] = tag.text = tag.attrib['OLD'] = to_next[-1]
                                tag.attrib['FEAT'] = tag.attrib['NEW'] = 'PUNCT'
                                tag.attrib['LINK'] = 'punct'
                                tag.attrib['ENH'] = str(tag.attrib['DOM']) + ':' + tag.attrib['LINK']
                                tag.tail = '\n'
                                sentence.insert(i + shift, tag)
                            else:
                                token.tail = to_prev + '\n' + to_next.rstrip(' ')
                                sentence[i+shift].tail = ' ' + sentence[i+shift].tail
                        if token.tail.startswith(' '):
                            token.tail = ' \n'
                        else:
                            token.tail = '\n'

                for i, token in enumerate(sentence.findall('W')):
                    if '.' in token.attrib.get('DOM', '') and token.text != 'FANTOM':
                        print(ifname, sentence.attrib['ID'])
                        print(token.attrib['ID'], token.text, token.attrib, sep='\t')
                        for item in sentence.findall('W'):
                             print(item.attrib['ID'], item.text, item.attrib, sep='\t')
                        print()
                        print(*[(x, shifts[x]) for x in sorted(filter(lambda x: x != '_root', shifts), key=float)])
                        print()
                    try:
                        token.attrib['DOM'] = shifts[token.attrib['DOM']]
                    except KeyError as error:
                        token.attrib['DOM'] = {'13.4': '14', '10.2': '10'}[token.attrib['DOM']]
                    try:
                        enh_no = token.attrib['ENH'].split(':')[0]
                        if int(float(enh_no)) != 0:
                            token.attrib['ENH'] = token.attrib['ENH'].replace(enh_no, shifts[enh_no])
                    except KeyError as error:
                        print(error)
                        print(ifname, sentence.attrib['ID'])
                        for item in sentence.findall('W'):
                             print(item.attrib['ID'], item.text, item.attrib, sep='\t')
                        print()
                        print(*[(x, shifts[x]) for x in sorted(filter(lambda x: x != '_root', shifts), key=float)])
                        print()
                    if 'NEW' in token.attrib:
                        pass #del token.attrib['NEW']
                    else:
                        try:
                            token.attrib['ID'] = shifts[token.attrib['ID']]
                        except KeyError:
                            print(token.text, token.attrib)
                            print()
                last_token = sentence.findall('W')[-1]

                if 'LINK' not in last_token.attrib or last_token.attrib['LINK'] != 'punct':
                    if last_token.text != 'FANTOM':
                        last_id = int(float(last_token.attrib['ID']))
                        tag = ET.fromstring('<W></W>')
                        tag.tail = '\n'
                        tag.text = '.'
                        tag.attrib = {'ID': str(last_id + 1),
                                    'DOM': str(last_id),
                                    'LEMMA': '.',
                                    'OLD': '.',
                                    'FEAT': 'PUNCT',
                                    'LINK': 'punct',
                                    'ENH': str(last_id) + ':punct',
                                    'NEW': 'punct'}
                        sentence.append(tag)

                        if last_token.text.endswith('.'):
                            last_token.text = last_token.text.rstrip('.')
                            last_token.tail = '\n'
                    else:
                        second_to_last_token = sentence.findall('W')[-2]
                        if 'LINK' in second_to_last_token.attrib and last_token.attrib['LINK'] == 'punct':
                            last_token.attrib, last_token.text, last_token.tail, second_to_last_token.attrib, second_to_last_token.text, second_to_last_token.tail = \
                                second_to_last_token.attrib, second_to_last_token.text, second_to_last_token.tail, last_token.attrib, last_token.text, last_token.tail
                            last_token.attrib['ID'] = str(int(last_token.attrib['ID']) + 1)
                            second_to_last_token.attrib['ID'] = str(round(float(second_to_last_token.attrib['ID']) - 1.0, 1))

        tree.write(ofname, encoding="utf-8")
    return

def process_all(ifolder, ofolder):
	munch(*get_fnames(ifolder, ofolder, '.xml', '.xml'))
	print('15: punct.py completed')

if __name__ == "__main__":
    process_all(ifolder, ofolder)

