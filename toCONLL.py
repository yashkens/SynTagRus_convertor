#!/usr/bin/env python3

""" convert data to .conll """

import os
import re

from util import import_xml_lib
ET = import_xml_lib()

ifolder = 'PunctExtract'
ofolder = 'syntagrus'


def munch(ifolder, ifiles, ofname):
    """
    Process all files in ifiles list.
    Output into ofiles list.
    """
    with open(ofname, 'w', encoding='utf-8') as ofile:
        num = 0
        for ifname in ifiles:
            ipath = os.path.join(ifolder, ifname)

            # skip non-existing files from the list
            if not os.path.exists(ipath):
                continue

            tree = ET.parse(ipath)
            root = tree.getroot()

            for sentence in root[-1].findall('S'):
                if 'ID' in sentence.attrib:
                    sentence[-2].tail = '\n'
                    num += 1
                    ofile.write('# sent_id = ' + os.path.basename(ifname) + '_' + sentence.attrib['ID'] + '\n')
                    text_line = '# text = '
                    for e in sentence.findall('W'):
                        if e.text == 'FANTOM':
                            text_line += e.tail.replace('\n', '')
                        else:
                            text_line += e.text + e.tail.replace('\n', '')
                    text_line = text_line.strip()
                    ofile.write(text_line)
                    ofile.write('\n')

                    last_num = len(sentence.findall('W')) - 1
                    for i, token in enumerate(sentence.findall('W')):
                        if token.text == 'FANTOM':
                            attributes = [token.attrib['ID']] + ['_'] * 7 + [token.attrib['ENH'], '_']
                        else:
                            attributes = [token.attrib['ID'], token.text, token.attrib['LEMMA']]
                            (pos, feats) = (token.attrib['FEAT'].split(' ') + ['_'])[:2]
                            if feats == '':
                                feats = '_'
                            attributes.extend([pos, '_', feats])
                            attributes.extend([token.attrib['DOM'].replace('_root', '0'), token.attrib.get('LINK', 'root')])
                            attributes.append(token.attrib['ENH'])
                            lookahead = 0
                            while i + lookahead < last_num:
                                if sentence.findall('W')[i + lookahead + 1].text == 'FANTOM':
                                    lookahead += 1
                                else:
                                    break
                            if lookahead == 0:
                                if not re.match('^[  ]', token.tail) and i != last_num:
                                    attributes.append('SpaceAfter=No')
                                else:
                                    attributes.append('_')
                            else:
                                last_fantom = sentence.findall('W')[i + lookahead]
                                if not re.match('^[  ]', last_fantom.tail) and not re.match('^[  ]', token.tail) and i != last_num:
                                    attributes.append('SpaceAfter=No')
                                else:
                                    attributes.append('_')
                        ofile.write('\t'.join(attributes) + '\n')
                    ofile.write('\n')

def process_all(ifolder, ofolder):
    # development set and testing set are created using lists: dev_list.txt and test_list.txt
    dev_list = open('dev_list.txt', 'r', encoding='utf-8').read().split('\n')[:-1]
    test_list = open('test_list.txt', 'r', encoding='utf-8').read().split('\n')[:-1]
    all_list = os.listdir(ifolder)
    train_list = list(set(all_list) - set(dev_list) - set(test_list))
    train_list.sort()
    if not os.path.exists(ofolder):
        os.makedirs(ofolder)
    munch(ifolder, dev_list, os.path.join(ofolder, 'ru_syntagrus-ud-dev.conll'))
    munch(ifolder, test_list, os.path.join(ofolder, 'ru_syntagrus-ud-test.conll'))
    munch(ifolder, train_list, os.path.join(ofolder, 'ru_syntagrus-ud-train.conll'))
    print('15: toCONLL.py completed')

if __name__ == "__main__":
    process_all(ifolder, ofolder)

