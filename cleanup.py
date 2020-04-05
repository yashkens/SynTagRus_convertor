#!/usr/bin/env python3

""" small fixes for 'fixed', 'det', 'name', 'discourse'.
Fixes for punctuation inside tokens
"""

import os
import re

from util import import_xml_lib, get_fnames, get_children
ET = import_xml_lib()

ifolder = 'Propernouns'
ofolder = 'Final'
tmpfname = 'tmp.xml'

def main(ifname_list, ofname_list):
    logfile = open('cleanup.log', 'w', encoding='utf-8')
    for ifname, ofname in zip(ifname_list, ofname_list):
        logfile.write('{}\nProcessing {}\n{}\n'.format('=' * 75, ifname, '=' * 75))
        tree = ET.parse(ifname)
        root = tree.getroot()
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                logfile.write('Fixed {}, sentence {}, token {}:\n\t{} {}\n'.format(ifname, sent.attrib['ID'], word.attrib['ID'], str(word.attrib), str(word.text)))
                link = word.attrib.get('LINK', 'EMPTY')
                feats = word.attrib.get('FEAT', 'EMPTY')
                lemma = word.attrib.get('LEMMA', 'EMPTY')

                # fix spaces inside link and lemma
                if ' ' in link:
                    word.attrib['LINK'] = link.split()[0]

                # fix empty feat
                if 'FEAT' in word.attrib and word.attrib['FEAT'] == '':
                    word.attrib['FEAT'] = '_'

                # fix flat:name relation
                if 'flat:name' in link:
                    head_token = sent.findall('W')[int(word.attrib['DOM']) - 1]
                    chain = collect_chain(sent, head_token, 'flat:name')
                    flatten(sent, head_token, chain, 'flat:name')

                # fix flat:foreign relation
                if 'flat:foreign' in link:
                    head_token = sent.findall('W')[int(word.attrib['DOM']) - 1]
                    chain = collect_chain(sent, head_token, 'flat:foreign')
                    flatten(sent, head_token, chain, 'flat:foreign')

                # fix flat relation
                if link == 'flat':
                    head_token = sent.findall('W')[int(word.attrib['DOM']) - 1]
                    chain = collect_chain(sent, head_token, 'flat')
                    flatten(sent, head_token, chain, 'flat')

                # fix fixed relation
                # before: head sometimes goes after and bears the relation
                #         with meaningful label
                # after:  head must be the first and bear the relation
                #         with meaningful label, all the rest hang on it
                if link == 'fixed':
                    # first, find head
                    head_token = sent.findall('W')[int(word.attrib['DOM']) - 1]
                    candidate_list, link_to_use = get_fixed_info(sent, head_token)
                    flatten(sent, head_token, candidate_list, link_to_use)

                # det relation
                if 'DET' in feats and word.attrib['DOM'] != '_root' and word.attrib['LINK'] not in {'nsubj', 'csubj', 'nsubj:pass', 'csubj:pass'}:
                    word.attrib['LINK'] = 'det'

                logfile.write('\t{} {}\n'.format(str(word.attrib), str(word.text)))

            # change temporary links back
            for word in sent.findall('W'):
                if 'LINK' in word.attrib:
                    word.attrib['LINK'] = word.attrib['LINK'].replace('_already', '')

        tree.write(tmpfname, encoding="utf-8")

        # fix for punctuation inside token
        with open(tmpfname, 'r', encoding='utf-8') as ifile, open(ofname, 'w', encoding='utf-8') as ofile:
            for line in ifile:
                line = re.sub(r'^(<W.*">)(\W*)(\w{5,})(\W*)(</W>)', r'\2\1\3\5\4', line)
                ofile.write(line)

    logfile.close()

def flatten(sent, head_token, candidate_list, link_to_use):
    link_to_use = link_to_use + '_already'

    # new_head
    new_head = candidate_list[0]
    new_head.attrib['DOM'] = head_token.attrib['DOM']
    if 'LINK' in head_token.attrib:
        new_head.attrib['LINK'] = head_token.attrib['LINK']
    elif 'LINK' in new_head.attrib:
        del new_head.attrib['LINK']

    # repossess all children
    new_children_ids = set()
    for item in candidate_list:
        new_children_ids |= set(int(child.attrib['ID']) - 1 for child in get_children(sent, item.attrib['ID']))
    new_children_ids -= set(int(item.attrib['ID']) - 1 for item in candidate_list)
    for new_child_id in new_children_ids:
        sent.findall('W')[new_child_id].attrib['DOM'] = new_head.attrib['ID']

    # repossess all words that are included in this fixed expression
    for item in candidate_list[1:]:
        item.attrib['DOM'] = new_head.attrib['ID']
        item.attrib['LINK'] = link_to_use

def collect_chain(sent, head_token, link):
    stack = get_children(sent, head_token.attrib['ID'], links=link)
    chain = []
    while stack != []:
        candidate = stack.pop()
        chain.append(candidate)
        stack.extend(get_children(sent, candidate.attrib['ID'], links=link))
    return sorted(chain + [head_token], key=lambda x: int(x.attrib['ID']))

def get_fixed_info(sent, head_token):
    children = get_children(sent, head_token.attrib['ID'])
    candidate_list = sorted(children + [head_token], key=lambda x: int(x.attrib['ID']))
    lemma_list = tuple(item.attrib['LEMMA'] for item in candidate_list)

    friend_start, friend_end = None, None
    onetwo_start, onetwo_end = None, None
    etc_start, etc_end = None, None

    for i, item in enumerate(lemma_list):
        # друг PR друг
        if item == 'друг':
            if friend_start is None:
                friend_start = i
            else:
                friend_end = friend_end or i + 1
        # один PR другой
        elif item == 'один':
            onetwo_start = onetwo_start or i
        elif item == 'другой' and onetwo_start is not None:
            onetwo_end = i + 1
        
    # и так далее
    if 'и так далее' in ' '.join(lemma_list):
        etc_start = lemma_list.index('и')
        etc_end = etc_start + 3

    for trim_start, trim_end in [(friend_start, friend_end),
                                 (onetwo_start, onetwo_end),
                                 (etc_start, etc_end),
                                ]:
        if trim_end is not None:
            candidate_list = candidate_list[trim_start:trim_end]
            lemma_list = tuple(lemma_list[trim_start:trim_end])
            break
    else:
        children = get_children(sent, head_token.attrib['ID'], links='fixed')
        candidate_list = sorted(children + [head_token], key=lambda x: int(x.attrib['ID']))
        lemma_list = tuple(item.attrib['LEMMA'] for item in candidate_list)

    if ' '.join(lemma_list) == 'точка зрение':
        link = 'compound' # the only compound
    elif any(len(lemma) == 2 and lemma.endswith('.') for lemma in lemma_list):
        link = 'flat:name' # initials
    else:
        link = 'fixed'

    return candidate_list, link

def process_all(ifolder, ofolder):
	main(*get_fnames(ifolder, ofolder, '.xml', '.xml'))
	print('10: cleanup.py completed')

if __name__ == "__main__":
    process_all(ifolder, ofolder)
      
