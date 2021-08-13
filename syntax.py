#!/usr/bin/env python3

""" UD syntactic relations """

import re
import os
import sys
from collections import Counter, namedtuple

from util import import_xml_lib, get_fnames, get_info, get_children_attrib, get_children
ET = import_xml_lib()

PosDep = namedtuple('PosDep', ['replace_dict', 'default'])

ifolder = 'Numerals'
ofolder = 'Syntax'
logfile = 'relations_log.txt'

conj_set = {'а', 'ан', 'да', 'зато', 'и', 'или', 'иль', 'иначе',
            'либо', 'ни', 'но', 'однако', 'притом', 'причем',
            'причём', 'сколько', 'столько', 'также', 'тоже', 'только',
            'и/или', 'а также', 'а то и', 'не то', 'так же как',
            'так и', 'в противном случае', 'х'}

for_discourse = {'ох', 'де', 'ишь', 'нет', 'то', 'ка',  
                 'ну', 'ну и', 'там', 'а', 'ладно', 'ничего'}

for_advmod = {'чуть-чуть', 'чуть ли не', 'чуть не', 'что ни на есть', 'ли', 'аж',
              'тем более', 'нет-нет да и', 'точно', 'только', 'только-только', 'же',
              'не то чтобы', 'не то что', 'как будто', 'как бы', 'хотя бы', 'все',
              'в том числе', 'все же', 'разве', 'всего', 'едва', 'едва не', 'да', 'хотя',
              'единственно', 'еле', 'еле-еле', 'невесть', 'неужели', 'ни', 'уж', 'зато',
              'попало', 'попросту', 'просто', 'просто-напросто', 'просто-таки', 'ведь',
              'прямо', 'прямо-таки', 'все-таки', 'так', 'таки', 'было', 'себе', 'черт-те',
              'будто', 'вон', 'вот', 'эвон', 'тоже', 'лишь', 'и', 'именно', 'даже',
              'пускай', 'пусть', 'пущай', 'наиболее'}
# "откуда-то", "лично", "очень", "неизбежно", "так",
# "как", "всего", "в первую очередь", "насколько", "полностью", "наиболее", 'не', "уже", "еще"

for_aux = {'бы'}

nesobst_compl = ['1-несобст-компл', '2-несобст-компл', '3-несобст-компл', '4-несобст-компл']
nmod_sampl = ['аддит', 'адр-присв']
obl_sampl = ['обст-тавт','суб-обст', 'об-обст']
compl = ['1-компл', '2-компл', '3-компл', '4-компл', '5-компл']

is_clause = {'nsubj', 'nsubj:pass', 'cop', 'aux', 'aux:pass'} #What about csubj?

simple_rels = {#'аппрокс-порядк':'amod', # relation disappeared
               'электив':'nmod',
               'релят':'acl:relcl',
               'дистанц':'obl',
               'кратно-длительн':'obl',
               'нум-аппоз':'nummod:entity',
               'количест':'nummod',
               'аппрокс-колич':'nummod',
               'колич-вспом':'compound',
               'композ':'compound',
               'сент-предик':'expl',
               'разъяснит':'parataxis',
               'изъясн':'parataxis',
               'вспом':'fixed',
               'предл':'fixed', # заплатка
               'пролепт':'appos', # вторая волна
               'об-аппоз':'appos',
               'оп-аппоз':'appos', # опечатка
               'ном-аппоз':'appos',
              }

ogranic = {('S','ADV'):'obl',
        ('A','ADV'):'obl',
        ('NUM','ADV'):'obl',
        ('NID','ADV'):'obl',
        ('PRON','ADV'):'obl',
        ('PR','ADV'):'obl',
        ('PR','S'):'obl',
        ('A','S'):'obl',
        ('PART','S'):'obl',
        ('V','S'):'obl',
        ('ADV','S'):'obl',
        ('S','A'):'obl',
        ('A','A'):'obl',
        ('A','NID'):'obl',
        ('V','A'):'obl',
        ('NUM','A'):'obl',
        ('ADV','A'):'obl',
        ('V','V'):'obl',
        ('ADV','V'):'obl',
        ('S','S'):'nmod',
        ('S','NUM'):'nmod',
        ('V','NUM'):'nummod',
        ('A','NUM'):'advmod',
        ('NUM','S'):'nmod',
        ('NID','S'):'nmod',
        ('S','NID'):'nmod',
        ('S','V'):'advcl',
        ('V','ADV'):'advmod',
        ('ADV','ADV'):'advmod',
        ('PART','ADV'):'advmod',
        ('NUM','ADV'):'advmod',
        ('A','CONJ'):'mark',
        ('V','CONJ'):'mark',
        ('S','CONJ'):'mark',
        ('ADV','CONJ'):'mark',
        ('CONJ','ADV'):'advmod',
        }

agent = {('V','S'):'obl',
        ('V','NUM'):'obl',
        ('V','NID'):'obl',
        ('V','PART'):'obl',
        ('V','A'):'obl',
        ('V','V'):'obl',
        ('S','A'):'obl',
        #('S','S'):'nmod:agent',
        ('S','S'):'nmod',
        ('S','NUM'):'nmod', #nummod?
        ('A','S'):'obl'
        }

sub_copr = {('V','S'):'obl',
        ('V','A'):'obl',
        ('V','NUM'):'obl',
        ('A','NUM'):'obl',
        ('V','V'):'advcl',
        ('V','ADV'):'advmod',
        ('S','A'):'obl',
        ('S','S'):'nmod',
        ('S','V'):'acl',
        ('A','S'):'obl',
        ('A','A'):'obl',
        ('ADV','A'):'obl',
        }
			  
vvodn = {'simple':'parataxis',
		'conditional':'vocative'
		}

compl_appos = {'V':'appos',
               'NUM':'nummod',
               'ADV':'advmod',
               'A':'obl',
              }
utochn = {('S','S'):'nmod',
        ('S', 'NUM'):'nmod',
        ('NID','NUM'):'nmod',
        ('NUM','S'):'nmod',
        ('A','S'):'nmod',
        ('S','A'):'nmod',
        ('A','A'):'nmod',
        ('ADV','S'):'obl',
        ('ADV','A'):'obl',
        ('ADV', 'NUM'): 'obl',
        ('S','ADV'):'advmod',
        ('ADV','ADV'):'advmod',
        ('NUM','ADV'):'advmod',
        ('A','ADV'):'advmod',
        ('A','V'):'acl',
         }
kratn = {'V':'xcomp',
         'NUM':'nummod',
         'ADV':'advmod',
         'A':'amod'
        }
kolich_ogran = {('S','S'):'nmod',
                ('A','PART'):'advmod',
                ('NUM','PART'):'advmod',
                ('ADV','PART'):'advmod',
                ('ADV','ADV'):'advmod',
                ('A','ADV'):'advmod',
                ('NUM','ADV'):'advmod',
                ('PART','ADV'):'advmod',
                ('V','ADV'):'advmod',
                ('S','ADV'):'advmod',
                ('S','A'):'obl',
                ('A','S'):'obl',
                ('NUM','S'):'obl',
                ('ADV','S'):'obl',
                ('V','S'):'obl',
               }
kolich_kopred = {('V','ADV'):'advmod',
                ('V','S'):'obl',
                ('V','NUM'):'obl',
                ('ADV','ADV'):'advmod',
                ('A','ADV'):'advcl',
                ('A','S'):'advcl',
                }
dliteln = {('V','ADV'):'advmod',
           ('A','ADV'):'advmod',
           ('S', 'ADV'): 'advmod',
           ('V','S'):'obl',
           ('V','NUM'):'obl',
           ('S','S'):'nmod',
           ('S','NUM'):'obl',
           ('ADV','S'):'obl',
           ('A','S'):'obl',
           ('V','A'):'obl',
          }
prisvyaz = {('S','S'):'nmod',
           ('V','S'):'obl',
           ('V','A'):'obl',
           ('V','V'):'xcomp',
           ('V','ADV'):'advmod',
           ('V','PART'):'obl',
           ('V','NID'):'obl',
           ('V','NUM'):'xcomp',
           ('S','ADV'):'advmod',
           ('S','A'):'obl',
           }
kvaziagent = {('S','S'):'nmod',
              ('S','NID'):'nmod',
              ('S','NUM'):'nmod',
              ('S','A'):'nmod',
              ('S','PART'):'nmod',
              ('NUM','S'):'nmod',
              ('NID','A'):'nmod',
              ('S','V'):'nmod',
              ('V','S'):'obl',
              ('A','S'):'obl',
              ('S','CONJ'):'nmod',
              ('S','ADV'):'advmod',
             }

atrib = {('S','S'):'nmod',
         ('S','NUM'):'nmod',
         ('NUM','NUM'):'nmod',
         ('A','S'):'nmod',
         ('NID','S'):'nmod',
         ('S','NID'):'nmod',
         ('NID','NID'):'nmod',
         ('NUM','S'):'nmod',
         ('S','PR'):'nmod',
         ('S','PART'):'nmod',
         ('S','ADV'):'advmod',
         ('A','ADV'):'advmod',
         ('ADV','ADV'):'advmod',
         ('NID','ADV'):'advmod',
         ('NUM','ADV'):'advmod',
         ('ADV','S'):'obl',
         ('ADV','NUM'):'obl',
         ('ADV','A'):'obl',
         ('S','A'):'obl',
         ('A','A'):'obl',
         ('NUM','A'):'obl',
         ('V','S'):'obl',
         ('A','NUM'):'obl',
         ('S','V'):'acl',
         ('A','V'):'acl',
         ('V','V'):'nmod', # one case, NP ellipsis
        }

raspred = {('S','S'):'nmod',
            ('NUM','S'):'nmod',
            ('V','S'):'obl',
            ('V','NUM'):'obl',
            ('S','A'):'obl',
            ('ADV','S'):'obl',
            ('S','ADV'):'obl',
            ('A','A'):'obl',
          }

nesobst_compl_dict = {('S','S'):'nmod',
                        ('S','NID'):'nmod',
                        ('V','S'):'obl',
                        ('V','NUM'):'obl',
                        ('V','A'):'obl',
                        ('A','S'):'obl',
                        ('ADV','S'):'obl',
                        ('V','ADV'):'advmod',
                        ('A','ADV'):'advmod',
                        ('V','V'):'xcomp',
                     }

pos_dependent_rels = {'компл-аппоз':PosDep(compl_appos, 'nmod')}

def collector(sent, filename): # file for unidentified sentences
    with open(logfile, 'a', encoding='utf-8') as file:
        file.write(filename + ': ' + sent.attrib['ID'] + '\n')
        for word in sent:
            file.write(str(word.attrib)+ str(word.text))
            file.write('\n')
        file.write('\n')

        file.close()

# start of block of functions for recursive transformation of conj/cc chains

conjrels = ['сочин', 'соч-союзн', 'сент-соч']

def get_tree_r(sent, start_token, rels):
    """
    Get chain recursively starting with start_token.
    """
    children = get_children(sent, start_token.attrib['ID'], links=rels)
    if children == []:
        return (start_token, [])
    tails = [get_tree_r(sent, child, rels) for child in children]
    return (start_token, tails)

def detect_trees(sent, rels):
    """
    Return a list of all trees.
    """
    starts = []
    for token in sent.findall('W'):
        if token.attrib.get('LINK', '') in conjrels:
            head_token = sent.findall('W')[int(token.attrib['DOM']) - 1]
            if head_token.attrib.get('LINK', '') not in conjrels and \
               head_token not in starts:
                starts.append(head_token)
    return [get_tree_r(sent, start, conjrels) for start in starts]

def get_chains_r(tree):
    """
    Get chains from tree.
    """
    if tree[1] == []:
        return [[tree[0]]]
    tails = []
    for branch in tree[1]:
        tails.extend(get_chains_r(branch))
    return [[tree[0]] + tail for tail in tails]

# ends here ^-^

def main(ifname_list, ofname_list):
    logfile = open('deprel.log', 'w', encoding='utf-8')
    for ifname, ofname in zip(ifname_list, ofname_list):
        logfile.write('{}\nProcessing {}\n{}\n'.format('=' * 75, ifname, '=' * 75))
        tree = ET.parse(ifname)
        root = tree.getroot()

        # first we crack the shell
        # капризные связи
        # new attribute for old relation 'OLD'
        #for sent in root[-1].findall('S'):
            #for word in sent.findall('W'):
            #    if word.attrib.get('LEMMA', '') in ['это', 'Это'] and word.attrib.get('LINK', '') == 'предик':
            #        print(word.attrib.get('ID', ''), word.attrib.get('LINK', ''), word.attrib.get('FEAT', ''), file=sys.stderr)
            #        print(*[(token.attrib.get('ID', 'EMPTY'), token.text, token.attrib.get('DOM', 'EMPTY'), token.attrib.get('FEAT', 'EMPTY'), token.attrib.get('LINK', 'EMPTY'), token.tail) for token in sent], file=sys.stderr, sep='\n')
            #        print('***', file=sys.stderr)
        #continue

        # first we crack the shell
        # капризные связи
        # new attribute for old relation 'OLD'
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                if 'LINK' in word.attrib:
                    word.attrib['OLD'] = word.attrib['LINK']
                else:
                    word.attrib['OLD'] = 'UNKNOWN'

        # this is for neg deprel
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(word, sent)
                if word.attrib.get('LEMMA', 'EMPTY') == 'не' and word.attrib.get('LINK', 'EMPTY') not in conjrels + ['подч-союзн', 'инф-союзн', 'сравн-союзн'] and word.attrib.get('DOM', 'EMPTY') != '_root':
                    word.attrib['LINK'] = 'advmod'
                try:
                    if link == 'предик': # посмотри на токен и на его вершину. Если хотя бы в одном найдется 'страд' -> nsubjpass, иначе -> nsubj
                        if 'СТРАД' in pos or 'СТРАД' in head_token.attrib.get('FEAT', 'EMPTY'):
                            if pos == 'V' and 'ПРИЧ' not in feats and 'ДЕЕПР' not in feats:
                                word.attrib['LINK'] = 'csubj:pass'                               
                            else:
                                word.attrib['LINK'] = 'nsubj:pass'
                        else:
                            if pos == 'V' and 'ПРИЧ' not in feats and 'ДЕЕПР' not in feats:
                                word.attrib['LINK'] = 'csubj'
                            else:
                                word.attrib['LINK'] = 'nsubj'
                except AttributeError:
                    print('AttributeError')
                    print(word.attrib, sent.attrib['ID'])
                    sys.exit(1)

        # подч-союзн + инф-союзн
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(word, sent)
                if link in {'подч-союзн', 'инф-союзн'}:
                    children = get_children_attrib(sent, head_token.attrib['ID'])
                    if head_token.attrib['DOM'] == '_root':
                        word.attrib['LINK'] = 'advcl'
                    else:
                        if head_token.attrib['LEMMA'] == 'если':
                            for chi in children:
                                if chi['LEMMA'] == 'то' and chi['LINK'] == 'соотнос':
                                    chi['DOM'] = head_token.attrib['DOM']
                                    chi['LINK'] = 'then-mark'                         

                        word.attrib['DOM'] = head_token.attrib['DOM']
                        head_token.attrib['DOM'] = word.attrib['ID']
                        
                        if head_token.attrib['LINK'] in conjrels:
                            word.attrib['LINK'] = head_token.attrib['LINK']
                        else:
                            new_children = get_children_attrib(sent, word.attrib['ID'])
                            if link == 'инф-союзн':
                                word.attrib['LINK'] = 'advcl'
                            else:
                                if head_token.attrib['LINK'] == 'эксплет':
                                    if sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'S', 'NID', 'NUM'}:
                                        if word.attrib['FEAT'].split()[0] not in {'V'}:
                                            if all(ch['FEAT'].split()[0] not in {'V'} for ch in new_children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in new_children):
                                                if word.attrib['FEAT'].split()[0] == 'S' and sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] == 'S':
                                                    word.attrib['LINK'] = 'nmod'
                                                elif word.attrib['FEAT'].split()[0] == 'S':
                                                    word.attrib['LINK'] = 'obl'
                                                elif word.attrib['FEAT'].split()[0] == 'A':
                                                    word.attrib['LINK'] = 'amod'
                                                elif word.attrib['FEAT'].split()[0] == 'ADV':
                                                    word.attrib['LINK'] = 'acl'
                                            else:                                            
                                                word.attrib['LINK'] = 'acl'
                                        else:                                            
                                            word.attrib['LINK'] = 'acl'   
                                    elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'A'}:
                                        if sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['DOM'] != "_root":
                                            word.attrib['DOM'] = sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['DOM']
                                            if word.attrib['FEAT'].split()[0] not in {'V'}:
                                                if all(ch['FEAT'].split()[0] not in {'V'} for ch in new_children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in new_children):
                                                    if word.attrib['FEAT'].split()[0] == 'S' and sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] == 'S':
                                                        word.attrib['LINK'] = 'nmod'
                                                    elif word.attrib['FEAT'].split()[0] in {'S', 'ADV'}:
                                                        word.attrib['LINK'] = 'obl'
                                                    elif word.attrib['FEAT'].split()[0] == 'A':
                                                        word.attrib['LINK'] = 'amod'
                                                else:
                                                    word.attrib['LINK'] = 'acl'
                                            else:
                                                word.attrib['LINK'] = 'acl'
                                        else:
                                            word.attrib['LINK'] = 'obl'
                                    else:
                                        word.attrib['LINK'] = 'advcl'
                                elif head_token.attrib['LINK'] in {'изъясн', 'примыкат', 'cc', 'вводн', 'разъяснит'}:
                                    word.attrib['LINK'] = 'parataxis'
                                elif head_token.attrib['LINK'] == 'уточн':
                                    word.attrib['LINK'] = 'advcl'
                                elif head_token.attrib['LINK'] == 'огранич':
                                    if any(ch['LEMMA'] in ['если', 'пока'] for ch in new_children):
                                        word.attrib['LINK'] = 'advcl'
                                    elif any(ch['LEMMA'] == 'поскольку' for ch in new_children):
                                        word.attrib['LINK'] = 'parataxis'
                                    else:
                                        word.attrib['LINK'] = 'amod'
                                elif head_token.attrib['LINK'] in {'атриб'}:
                                    if word.attrib['FEAT'].split()[0] not in {'V'}:
                                        if all(ch['FEAT'].split()[0] not in {'V'} for ch in new_children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in new_children):
                                            if word.attrib['FEAT'].split()[0] == 'S' and sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] == 'S':
                                                word.attrib['LINK'] = 'nmod'
                                            elif word.attrib['FEAT'].split()[0] == 'A':
                                                word.attrib['LINK'] = 'amod'
                                            else:
                                                word.attrib['LINK'] = 'obl'
                                        else:
                                            word.attrib['LINK'] = 'acl'
                                    else:
                                        word.attrib['LINK'] = 'acl'
                                elif head_token.attrib['LINK'] in {'оп-опред', 'квазиагент'}:
                                    word.attrib['LINK'] = 'acl'
                                elif head_token.attrib['LINK'] == 'релят':
                                    if sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'S', 'NID', 'NUM'}:
                                        word.attrib['LINK'] = 'acl:relcl'
                                    elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'ADV'}:
                                        word.attrib['LINK'] = 'advcl'
                                elif head_token.attrib['LINK'] in {'обст', 'вспом', 'сравнит', 'сравн-союзн', 'соотнос'}:
                                    if word.attrib['FEAT'].split()[0] not in {'V'}:
                                        if all(ch['FEAT'].split()[0] not in {'V'} for ch in new_children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in new_children):
                                            if sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'S', 'NUM', 'NID'}:
                                                if word.attrib['FEAT'].split()[0] == 'S':
                                                    word.attrib['LINK'] = 'nmod'
                                                elif word.attrib['FEAT'].split()[0] == 'A':
                                                    if 'СРАВ' in word.attrib['FEAT']:
                                                        word.attrib['LINK'] = 'amod'
                                                    else:
                                                        word.attrib['LINK'] = 'acl'
                                                else:
                                                    word.attrib['LINK'] = 'obl'
                                            elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] == 'V':
                                                if word.attrib['FEAT'].split()[0] == 'ADV':
                                                    word.attrib['LINK'] = 'advmod'
                                                elif word.attrib['FEAT'].split()[0] in {'A', 'S', 'NUM', 'NID'}:
                                                    word.attrib['LINK'] = 'obl'
                                                elif word.attrib['FEAT'].split()[0] == 'CONJ' and word.attrib['LEMMA'] == 'и':
                                                    for item in sent.findall('W'):
                                                        if item.attrib['ID'] == '1':
                                                            item.attrib['DOM'] = '3'
                                                            item.attrib['LINK'] = 'mark'
                                                        elif item.attrib['ID'] == '2':
                                                            item.attrib['DOM'] = '3'
                                                            item.attrib['FEAT'] = 'PART'
                                                            item.attrib['LINK'] = 'discourse'
                                                        elif item.attrib['ID'] == '3':
                                                            item.attrib['DOM'] = '14'
                                                            item.attrib['LINK'] = 'advmod'
                                                        elif int(item.attrib['ID']) > 3:
                                                            break
                                                    continue
                                                elif word.attrib['FEAT'].split()[0] == 'PART':
                                                    word.attrib['LINK'] = 'discourse'
                                            elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'A', 'ADV', 'PART'}:
                                                if word.attrib['FEAT'].split()[0] == 'ADV':
                                                    word.attrib['LINK'] = 'advmod'
                                                else:
                                                    word.attrib['LINK'] = 'obl'
                                        else:
                                            word.attrib['LINK'] = 'advcl'
                                    else:
                                        word.attrib['LINK'] = 'advcl'
                                elif head_token.attrib['LINK'] == 'пролепт':
                                    word.attrib['LINK'] = 'appos'
                                elif head_token.attrib['LINK'] in {'1-компл', '2-компл', '3-компл'}:
                                    if sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in { 'V', 'A'}: 
                                        word.attrib['LINK'] = 'ccomp'
                                    elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'ADV'}:
                                        word.attrib['LINK'] = 'advcl'
                                    elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'S', 'NID', 'NUM'}:
                                        if word.attrib['FEAT'].split()[0] not in {'V', 'ADV'}:
                                            if all(ch['FEAT'].split()[0] not in {'V', 'ADV'} for ch in new_children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in new_children):
                                                word.attrib['LINK'] = 'nmod'
                                            else:
                                                word.attrib['LINK'] = 'acl'
                                        else:
                                            word.attrib['LINK'] = 'acl'
                                    else:
                                        word.attrib['LINK'] = 'obj'
                                elif head_token.attrib['LINK'] in {'4-компл'}:
                                    word.attrib['LINK'] = 'advcl'
                                elif head_token.attrib['LINK'] in {'nsubj','nsubj:pass'}:
                                    word.attrib['LINK'] = 'ccomp'
                                else: # these are exceptions
                                    if word.attrib['LEMMA'] in {'позорить', 'приезжать', 'грубый', 'показывать'}:
                                        word.attrib['LINK'] = 'сочин'
                                    elif word.attrib['LEMMA'] == 'выражаться':
                                        word.attrib['LINK'] = 'parataxis'
                                    else:
                                        word.attrib['LINK'] = 'mark'
                                        # print('Something went wrong 2')
                        head_token.attrib['LINK'] = 'mark'
                        for elem in children:
                            if elem['ID'] != word.attrib['ID'] and elem['LINK'] != 'вспом':
                                if elem['LINK'] == 'then-mark':
                                    elem['LINK'] = 'mark'
                                else:
                                    elem['DOM'] = word.attrib['ID']

        # сравн-союзн
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(word, sent)
                if link == 'сравн-союзн' and head_pos == 'CONJ':
                    if word.attrib['DOM'] == '_root' or head_token.attrib['DOM'] == '_root':
                        print('Ooopsey!')
                    children = get_children_attrib(sent, head_token.attrib['ID'])
                    word.attrib['DOM'] = head_token.attrib['DOM']
                    head_token.attrib['DOM'] = word.attrib['ID']
                    if head_token.attrib['LINK'] not in {'mark', 'cc'}:
                        word.attrib['LINK'] = head_token.attrib['LINK']
                    if word.attrib['LINK'] in conjrels:
                        continue
                    elif word.attrib['LINK'] in {"вводн", "аппоз", "разъяснит"}:
                        word.attrib['LINK'] = 'parataxis' 
                    elif word.attrib['LINK'] == "сравнит":
                        if sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'S', 'NID', 'NUM', 'PART'}: # PART is an exception here
                            if word.attrib['FEAT'].split()[0] not in {'V', 'ADV'}:
                                if all(ch['FEAT'].split()[0] not in {'V', 'ADV'} for ch in new_children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in new_children):
                                    if sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'S', 'NUM', 'NID'}:
                                        if word.attrib['FEAT'].split()[0] in {'S', 'NID'}:
                                            word.attrib['LINK'] = 'nmod'
                                        elif word.attrib['FEAT'].split()[0] == 'A':
                                            word.attrib['LINK'] = 'amod'
                                else:
                                    word.attrib['LINK'] = 'acl'
                            else:
                                word.attrib['LINK'] = 'acl'
                        elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'V', 'ADV'}:
                            if word.attrib['FEAT'].split()[0] not in {'V'}:
                                if all(ch['FEAT'].split()[0] not in {'V'} for ch in new_children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in new_children):
                                    if word.attrib['FEAT'].split()[0] in {'S', 'NID', 'A'}:
                                        word.attrib['LINK'] = 'obl'
                                    else:
                                        word.attrib['LINK'] = 'advmod'
                                else:
                                    word.attrib['LINK'] = 'advcl'
                            else:
                                word.attrib['LINK'] = 'advcl'
                    elif word.attrib['LINK'] == "примыкат":
                        if sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'S'}:
                            if word.attrib['FEAT'].split()[0] not in {'V'}:
                                if all(ch['FEAT'].split()[0] not in {'V'} for ch in new_children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in new_children):
                                    word.attrib['LINK'] = 'nmod'
                            else:
                                word.attrib['LINK'] = 'acl'
                        elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'V'}:
                            new_children = get_children_attrib(sent, word.attrib['ID'])
                            if any(ch['LEMMA'] in {'теперь', 'например'} for ch in new_children):
                                word.attrib['LINK'] = 'parataxis'
                            else:
                                if word.attrib['FEAT'].split()[0] not in {'V'}:
                                    if all(ch['FEAT'].split()[0] not in {'V'} for ch in new_children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in new_children):
                                        if word.attrib['FEAT'].split()[0] == 'S':
                                            word.attrib['LINK'] = 'obl'
                                        elif word.attrib['FEAT'].split()[0] == 'ADV':
                                            word.attrib['LINK'] = 'advmod'
                                    else:
                                        word.attrib['LINK'] = 'advcl'
                                else:
                                    word.attrib['LINK'] = 'advcl'
                        elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'ADV'}:
                            word.attrib['LINK'] = 'advcl'
                        elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'CONJ', 'A'}:
                            word.attrib['LINK'] = 'parataxis'
                    elif word.attrib['LINK'] == 'огранич':
                        if sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'S'}:
                            if word.attrib['FEAT'].split()[0] not in {'V'}:
                                if all(ch['FEAT'].split()[0] not in {'V'} for ch in new_children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in new_children):
                                    word.attrib['LINK'] = 'nmod'
                                else:
                                    word.attrib['LINK'] = 'acl'
                            else:
                                word.attrib['LINK'] = 'acl'
                        elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'V'}: #this is an exception
                            if head_token.attrib['LEMMA'] == 'тем' and word.attrib['LEMMA'] == 'более':
                                word.attrib['LINK'] = 'fixed'
                                head_token.attrib['DOM'] = word.attrib['DOM']
                                word.attrib['DOM'] = head_token.attrib['ID']
                                head_token.attrib['LINK'] = 'advmod'
                                head_token.attrib['FEAT'] = 'PRON Animacy=Inan|Case=Ins|Gender=Neut|Number=Sing'
                                continue
                    elif word.attrib['LINK'] in {'обст', 'сравн-союзн', 'nsubj', 'nsubj:pass', 'присвяз', 'колич-огран', 'об-копр', 'суб-копр', '4-компл', '3-компл'}:
                        if word.attrib['FEAT'].split()[0] not in {'V'}:
                            if all(ch['FEAT'].split()[0] not in {'V'} for ch in new_children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in new_children):
                                if sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'V', 'A'}:
                                    if word.attrib['FEAT'].split()[0] in {'S', 'NID', 'A', 'NUM'}:
                                        word.attrib['LINK'] = 'obl'
                                    elif word.attrib['FEAT'].split()[0] == 'ADV':
                                        word.attrib['LINK'] = 'advmod'
                                else:
                                    word.attrib['LINK'] = 'nmod' # two sentences are here
                            else:
                                word.attrib['LINK'] = 'advcl'
                        else:
                            word.attrib['LINK'] = 'advcl'
                    elif word.attrib['LINK'] == 'соотнос':
                        if sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'S', 'CONJ'}:
                            if word.attrib['FEAT'].split()[0] not in {'V'}:
                                if all(ch['FEAT'].split()[0] not in {'V'} for ch in new_children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in new_children):
                                    word.attrib['LINK'] = 'obl'
                                else:
                                    word.attrib['LINK'] = 'advcl'
                            else:
                                word.attrib['LINK'] = 'advcl'
                            word.attrib['DOM'] = sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['DOM']
                        elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'A', 'ADV', 'V'}:
                            if word.attrib['FEAT'].split()[0] not in {'V'}:
                                if all(ch['FEAT'].split()[0] not in {'V'} for ch in new_children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in new_children):
                                    word.attrib['LINK'] = 'obl'
                                else:
                                    word.attrib['LINK'] = 'advcl'
                            else:
                                word.attrib['LINK'] = 'advcl'
                    elif word.attrib['LINK'] == 'эксплет':
                        if sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'ADV'}:
                            if word.attrib['FEAT'].split()[0] not in {'V'}:
                                if all(ch['FEAT'].split()[0] not in {'V'} for ch in new_children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in new_children):
                                    word.attrib['LINK'] = 'advmod'
                                else:
                                    word.attrib['LINK'] = 'advcl'
                            else:
                                word.attrib['LINK'] = 'advcl'
                        elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'A'}:
                            if sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['DOM'] != "_root":
                                word.attrib['DOM'] = sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['DOM']
                                if word.attrib['FEAT'].split()[0] not in {'V'}:
                                    if all(ch['FEAT'].split()[0] not in {'V'} for ch in new_children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in new_children):
                                        word.attrib['LINK'] = 'nmod'
                                    else:
                                        word.attrib['LINK'] = 'acl'
                                else:
                                    word.attrib['LINK'] = 'acl'
                            else:
                                word.attrib['LINK'] = 'advcl'
                        elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'S'}:
                                word.attrib['LINK'] = 'acl'
                    elif word.attrib['LINK'] == 'релят':
                        word.attrib['LINK'] = 'acl:relcl'
                    elif word.attrib['LINK'] == 'атриб':
                        if sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'S'}:
                            word.attrib['LINK'] = 'acl'
                        elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'A'}:
                            word.attrib['LINK'] = 'advcl'
                    elif word.attrib['LINK'] in {'acl', 'ccomp', 'advcl'}:
                        continue
                    elif word.attrib['LINK'] in {'2-компл'}:
                        if sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'V', 'A'}:
                            if word.attrib['FEAT'].split()[0] not in {'V'}:
                                if all(ch['FEAT'].split()[0] not in {'V'} for ch in new_children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in new_children):
                                    if sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'V', 'A'}:
                                        if word.attrib['FEAT'].split()[0] in {'S', 'NID', 'A', 'NUM'}:
                                            word.attrib['LINK'] = 'obl'
                                else:
                                    word.attrib['LINK'] = 'advcl'
                            else:
                                word.attrib['LINK'] = 'advcl'
                        elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'S'}:
                            if word.attrib['FEAT'].split()[0] not in {'V'}:
                                if all(ch['FEAT'].split()[0] not in {'V'} for ch in new_children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in new_children):
                                    word.attrib['LINK'] = 'nmod'
                            else:
                                word.attrib['LINK'] = 'acl'
                    elif word.attrib['LINK'] in {'1-компл'}:
                        if sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'ADV'}:
                            word.attrib['LINK'] = 'advcl'
                        elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'V'}:
                            if head_token.attrib['LEMMA'].lower() == 'будто':
                                word.attrib['LINK'] = 'ccomp'
                            elif head_token.attrib['LEMMA'].lower() == 'как':
                                if word.attrib['FEAT'].split()[0] not in {'V'}:
                                    if all(ch['FEAT'].split()[0] not in {'V'} for ch in new_children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in new_children):
                                        if sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'V', 'A'}:
                                            if word.attrib['FEAT'].split()[0] in {'S', 'NID', 'A', 'NUM'}:
                                                word.attrib['LINK'] = 'obl'
                                            else:
                                                word.attrib['LINK'] = 'obj'
                                        else:
                                            word.attrib['LINK'] = 'obj'
                                    else:
                                        word.attrib['LINK'] = 'advcl'
                                else:
                                    word.attrib['LINK'] = 'advcl'
                            else:
                                word.attrib['LINK'] = 'parataxis'
                        elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'S'}:
                            if word.attrib['FEAT'].split()[0] not in {'V'}:
                                if all(ch['FEAT'].split()[0] not in {'V'} for ch in new_children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in new_children):
                                    word.attrib['LINK'] = 'ccomp'
                                else:
                                    word.attrib['LINK'] = 'acl'
                            else:
                                word.attrib['LINK'] = 'acl'
                        else:
                            print('Actually, something went wrong.\n Setting 1-компл to default obj')
                            word.attrib['LINK'] = 'obj'
                    else:
                        print('Something went wrong 3')
                        print(word.attrib['ID'], word.text)
                        print(*[(token.attrib.get('ID', 'EMPTY'), token.text, token.attrib.get('DOM', 'EMPTY'), token.attrib.get('FEAT', 'EMPTY'), token.attrib.get('LINK', 'EMPTY'), token.tail) for token in sent], sep='\n')
                    head_token.attrib['LINK'] = 'mark'
                    for elem in children:
                        if elem['ID'] != word.attrib['ID'] and elem['LINK'] != 'вспом':
                            elem['DOM'] = word.attrib['ID']
                elif link == 'сравн-союзн' and head_pos != 'CONJ':
                    if head_token.attrib['LEMMA'] == 'как':

                        children = get_children_attrib(sent, head_token.attrib['ID'])
                        word.attrib['DOM'] = head_token.attrib['DOM']
                        head_token.attrib['DOM'] = word.attrib['ID']
                        if head_token.attrib['LINK'] not in {'mark', 'cc'}:
                            word.attrib['LINK'] = head_token.attrib['LINK']
                        if word.attrib['LINK'] in conjrels:
                            continue
                        if sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'V'}:
                            word.attrib['LINK'] = 'advcl'
                        elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'S'}:
                            word.attrib['LINK'] = 'acl'
                        elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'A'}:
                            word.attrib['LINK'] = 'nmod'
                            word.attrib['DOM'] = sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['DOM']
                        elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'ADV'}: #exception
                            word.attrib['DOM'] = '26'
                            word.attrib['LINK'] = 'acl'

                        head_token.attrib['LINK'] = 'mark'
                        head_token.attrib['FEAT'] = 'CONJ'
                        for elem in children:
                            if elem['ID'] != word.attrib['ID']:
                                elem['DOM'] = word.attrib['ID']

                    elif head_token.attrib['LEMMA'] == 'кроме':

                        children = get_children_attrib(sent, head_token.attrib['ID'])
                        word.attrib['DOM'] = head_token.attrib['DOM']
                        head_token.attrib['DOM'] = word.attrib['ID']
                        head_token.attrib['LINK'] = 'advmod'
                        if word.attrib['FEAT'].split()[0] in {'V'}:
                            word.attrib['LINK'] = 'advcl'
                        elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'S'}:
                            word.attrib['LINK'] = 'nmod'
                        elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'A', 'ADV'}:
                            word.attrib['LINK'] = 'obl'

                    elif word.attrib['LEMMA'] == 'быть':
                        if sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'V'}:
                            word.attrib['LINK'] = 'advcl'
                        else:
                            word.attrib['LINK'] = 'acl'
                    elif head_pos == 'PART':
                        word.attrib['DOM'] = head_token.attrib['DOM']
                        head_token.attrib['DOM'] = word.attrib['ID']
                        word.attrib['LINK'] = 'advcl'
                        head_token.attrib['LINK'] = 'mark'
                    elif word.attrib['LEMMA'] == 'миллион':
                        word.attrib['LINK'] = 'nmod'
                    elif word.attrib['LEMMA'] == 'ощупь':
                        word.attrib['LINK'] = 'nmod'
                        for item in sent.findall('W'):
                            if item.attrib['ID'] == '7':
                                item.attrib['DOM'] = '10'                
                    elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'S', 'NID'}:
                        if word.attrib['FEAT'].split()[0] in {'S'}  and word.attrib['LEMMA'] == 'мысль':
                            for item in sent.findall('W'):
                                if item.attrib['ID'] == '9':
                                    item.attrib['DOM'] = '11'
                                    item.attrib['LINK'] = 'mark'
                                elif item.attrib['ID'] == '11':
                                    item.attrib['DOM'] = '7'
                                    item.attrib['LINK'] = 'obl'
                        elif word.attrib['FEAT'].split()[0] in {'A'} and word.attrib['LEMMA'] == 'старший':
                            for item in sent.findall('W'):
                                if item.attrib['ID'] == '10':
                                    item.attrib['DOM'] = '12'
                                    item.attrib['FEAT'] = 'CONJ'
                                    item.attrib['LINK'] = 'mark'
                                elif item.attrib['ID'] == '12':
                                    item.attrib['DOM'] = '9'
                                    item.attrib['LINK'] = 'соч-союзн'
                    elif sent.findall('W')[int(word.attrib['DOM']) - 1].attrib['FEAT'].split(' ')[0] in {'ADV'}:
                        if word.attrib['FEAT'].split()[0] in {'S', 'A'}:
                            word.attrib['LINK'] = 'obl'
                        elif word.attrib['FEAT'].split()[0] in {'ADV'}:
                            word.attrib['LINK'] = 'advmod'
                    else:
                        print('Something went wrong 4')
                        print(word.attrib['ID'], word.text)
                        print(*[(token.attrib.get('ID', 'EMPTY'), token.text, token.attrib.get('DOM', 'EMPTY'), token.attrib.get('FEAT', 'EMPTY'), token.attrib.get('LINK', 'EMPTY'), token.tail) for token in sent], sep='\n')

        # сравнит
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(word, sent)
                if link == 'сравнит' and pos == 'CONJ':
                    children = get_children_attrib(sent, word.attrib['ID'])
                    if len(children) == 1:
                        if head_token.attrib['DOM'] == '_root':
                            word.attrib['LINK'] = 'advmod'
                            word.attrib['FEAT'] = 'ADV'
                        else:
                            if children[0]['LINK'] in {'advcl'}:
                                children[0]['DOM'] = sent.findall('W')[int(head_token.attrib['DOM']) - 1].attrib['ID']
                                word.attrib['DOM'] = children[0]['ID']
                                if word.attrib['LEMMA'] not in conj_set:
                                    word.attrib['LINK'] = 'mark'
                                else:
                                    word.attrib['LINK'] = 'cc'
                            else:
                                children[0]['DOM'] = word.attrib['DOM']
                                children[0]['LINK'] = 'obl'
                                word.attrib['DOM'] = children[0]['ID']
                                if word.attrib['LEMMA'] not in conj_set:
                                    word.attrib['LINK'] = 'mark'
                                else:
                                    word.attrib['LINK'] = 'cc'
                    else:
                        if word.attrib['LEMMA'] == 'как':
                            word.attrib['DOM'] = '11'
                            word.attrib['LINK'] = 'mark'
                            for item in sent.findall('W'):
                                if item.attrib['ID'] == '11':
                                    item.attrib['DOM'] = '5'
                                if item.attrib['DOM'] == '9':
                                    item.attrib['DOM'] = '11'
                        elif word.attrib['LEMMA'] == 'чем' and head_token.attrib['LEMMA'] == 'более':
                            word.attrib['DOM'] = '13'
                            word.attrib['LINK'] = 'mark'
                            for item in sent.findall('W'):
                                if item.attrib['ID'] == '8':
                                    item.attrib['DOM'] = '15'
                                if item.attrib['DOM'] == '13':
                                    item.attrib['DOM'] = '8'
                        else:
                            word.attrib['LINK'] = 'mark'
                elif link == 'сравнит' and pos != 'CONJ':
                    children = get_children_attrib(sent, word.attrib['ID'])
                    if word.attrib['FEAT'].split()[0] not in {'V'}:
                        if all(ch['FEAT'].split()[0] not in {'V'} for ch in children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in children):
                            if head_token.attrib['FEAT'].split()[0] in {'S', 'NUM', 'NID', 'PART'}:
                                if word.attrib['FEAT'].split()[0] in {'S', 'NUM', 'NID'}:
                                    word.attrib['LINK'] = 'nmod'
                                elif word.attrib['FEAT'].split()[0] in {'A'}:
                                    word.attrib['LINK'] = 'amod'
                                elif word.attrib['FEAT'].split()[0] in {'ADV'}:
                                    word.attrib['LINK'] = 'obl'
                            elif head_token.attrib['FEAT'].split()[0] in {'A', 'V', 'ADV'}:
                                if word.attrib['FEAT'].split()[0] in {'ADV'}:
                                    word.attrib['LINK'] = 'advmod'
                                else:
                                    word.attrib['LINK'] = 'obl'
                        else:
                            if head_token.attrib['FEAT'].split()[0] in {'S', 'NUM', 'NID'}:
                                word.attrib['LINK'] = 'acl'
                            elif head_token.attrib['FEAT'].split()[0] in {'V', 'A', 'ADV'}:
                                word.attrib['LINK'] = 'advcl'
                    else:
                        if head_token.attrib['FEAT'].split()[0] in {'S', 'NUM', 'NID'}:
                            word.attrib['LINK'] = 'acl'
                        elif head_token.attrib['FEAT'].split()[0] in {'V', 'A', 'ADV'}:
                            word.attrib['LINK'] = 'advcl'

        # сочин, соч-союзн, сент-соч
        for sent in root[-1].findall('S'):
            conjtrees = detect_trees(sent, conjrels)
            for conjtree in conjtrees:
                chains = get_chains_r(conjtree)
                for chain in chains:
                    if chain[0].attrib['FEAT'].split(' ')[0] == 'CONJ':
                        start, start_index = chain[1], 1
                        if chain[0].attrib['LINK'] in {'вводн', 'примыкат', 'разъяснит'}:
                            start.attrib['LINK'] = 'parataxis'
                        # irregularity in the source markup
                        elif chain[0].attrib['LINK'] in {'cc'} and chain[1].text == 'значит':
                            start.attrib['LINK'] = 'parataxis'
                        # irregularity in the source markup
                        elif chain[0].attrib['LINK'] in {'обст'} and chain[0].attrib['ID'] == '1':
                            start.attrib['LINK'] = 'advcl'
                        # irregularity in the source markup
                        elif chain[0].attrib['LINK'] in {'nsubj'} and chain[0].attrib['ID'] == '1':
                            start.attrib['LINK'] = 'csubj'
                        else:
                            start.attrib['LINK'] = chain[0].attrib['LINK']
                        chain[0].attrib['DOM'], start.attrib['DOM'] = start.attrib['ID'], chain[0].attrib['DOM']
                        chain[0].attrib['LINK'] = 'cc' 
                    else:
                        start, start_index = chain[0], 0

                    for i, el in enumerate(chain[start_index+1:]):
                        pos = el.attrib['FEAT'].split(' ')[0]
                        if pos == 'CONJ':
                            el.attrib['LINK'] = 'cc'

                            for el_chain in chain[i+2:]:
                                if el_chain.attrib['FEAT'].split()[0] != 'CONJ':
                                    el.attrib['DOM'] = el_chain.attrib['ID']
                                    break
                            else:
                                el.attrib['DOM'] = start.attrib['ID']
                        else:
                            if el.attrib['LINK'] not in {'parataxis', 'advcl', 'csubj'}:
                                el.attrib['LINK'] = 'conj'
                            el.attrib['DOM'] = start.attrib['ID']

        # соотнос
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(word, sent)
                if link == 'соотнос' and ('CONJ' in pos or 'PART' in pos) and 'CONJ' in head_pos:

                    word.attrib['DOM'] = sent.findall('W')[int(head_token.attrib['DOM']) - 1].attrib['DOM']
                    if word.attrib['LEMMA'] not in conj_set:
                         word.attrib['LINK'] = 'mark'
                    else:
                         word.attrib['LINK'] = 'cc'


                elif link == 'соотнос' and 'CONJ' in pos and 'CONJ' not in head_pos:
                    if sent.findall('W')[int(head_token.attrib['DOM']) - 1].attrib['DOM'] != '_root':
                        word.attrib['DOM'] = sent.findall('W')[int(head_token.attrib['DOM']) - 1].attrib['DOM']
                    else:
                        word.attrib['DOM'] = sent.findall('W')[int(head_token.attrib['DOM']) - 1].attrib['ID']
                    if word.attrib['LEMMA'] not in conj_set:
                         word.attrib['LINK'] = 'mark'
                    else:
                         word.attrib['LINK'] = 'cc'

        # аналит
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(word, sent)
                if link == 'аналит':

                    if word.attrib.get('FEAT', 'EMPTY') in {'V НЕСОВ СТРАД ИНФ', 'V НЕСОВ ИНФ'}:
    
                        word.attrib['DOM'] = head_token.attrib['DOM']
                        head_token.attrib['DOM'] = word.attrib['ID']
                        if word.attrib['DOM'] == '_root':
                            word.attrib.pop('LINK')
                        else:
                            word.attrib['LINK'] = head_token.attrib['LINK']
                        if 'СТРАД' in word.attrib.get('FEAT', 'EMPTY'):
                            word.attrib['LINK'] = 'aux:pass'

                            if any(ch['LINK'] in {'nsubj', 'csubj'} for ch in get_children_attrib(sent, head_token.attrib['ID'])):
                                subj_to_rename = [ch for ch in get_children_attrib(sent, head_token.attrib['ID']) if ch['LINK'] in {'nsubj', 'csubj'}]
                                subj_to_rename[0]['LINK'] += ':pass'

                        else:
                            word.attrib['LINK'] = 'aux'
                        for elem in sent.findall('W'):
                            if elem.attrib['DOM'] == head_token.attrib['ID']:
                                elem.attrib['DOM'] = word.attrib['ID']

                    elif pos == 'PART' and word.attrib.get('LEMMA', 'EMPTY') == 'бы':
                        word.attrib['LINK'] = 'aux'
                    elif pos == 'PART' and word.attrib.get('LEMMA', 'EMPTY') == 'было':
                        word.attrib['LINK'] = 'advmod'
                    else:
                        word.attrib['DOM'] = head_token.attrib['DOM']
                        head_token.attrib['DOM'] = word.attrib['ID']
                        if word.attrib['DOM'] == '_root':
                            word.attrib.pop('LINK')
                        if word.attrib['LEMMA'].lower() == 'один':
                            word.attrib['LINK'] = 'cop'
                        else:
                            word.attrib['LINK'] = 'aux'

        # пасс-анал
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(word, sent)
                if link == 'пасс-анал':
                    word.attrib['DOM'] = head_token.attrib['DOM']
                    head_token.attrib['DOM'] = word.attrib['ID']
                    if word.attrib['DOM'] == '_root':
                        word.attrib.pop('LINK')
                    else:
                        word.attrib['LINK'] = head_token.attrib.get('LINK', 'EMPTY')
                    head_token.attrib['LINK'] = 'aux:pass'
                    for elem in sent.findall('W'):
                        if elem.attrib['DOM'] == head_token.attrib['ID']:
                            elem.attrib['DOM'] = word.attrib['ID']

                    if any(ch['LINK'] in {'nsubj', 'csubj'} for ch in get_children_attrib(sent, word.attrib['ID'])):
                        subj_to_rename = [ch for ch in get_children_attrib(sent, word.attrib['ID']) if ch['LINK'] in {'nsubj', 'csubj'}]
                        subj_to_rename[0]['LINK'] += ':pass'

                    elif any(ch.get('LINK', 'EMPTY') in {'nsubj', 'csubj'} for ch in get_children_attrib(sent, word.attrib['DOM'])):
                        subj_to_rename = [ch for ch in get_children_attrib(sent, word.attrib['DOM']) if ch['LINK'] in {'nsubj', 'csubj'}]
                        subj_to_rename[0]['LINK'] += ':pass'

        # присвяз
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(word, sent)
                if link == 'присвяз':
                    if head_token.attrib.get('LEMMA', 'EMPTY') == 'быть':
                        word.attrib['DOM'] = head_token.attrib['DOM']
                        head_token.attrib['DOM'] = word.attrib['ID']
                        if word.attrib['DOM'] == '_root':
                            word.attrib.pop('LINK')
                        else:
                            word.attrib['LINK'] = head_token.attrib['LINK']
                        head_token.attrib['LINK'] = 'cop'
                        for elem in sent.findall('W'):
                            if elem.attrib['DOM'] == head_token.attrib['ID']:
                                elem.attrib['DOM'] = word.attrib['ID']

        # пролепт
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(word, sent)
                if link == 'пролепт' and head_token.attrib['LEMMA'] == 'вот':
                    word.attrib['LINK'] = head_token.attrib['LINK']
                    word.attrib['DOM'] = head_token.attrib['DOM']
                    head_token.attrib['LINK'] = 'cop'
                    head_token.attrib['FEAT'] = 'PART'
                if link == 'пролепт' and head_token.attrib['LEMMA'] == 'это':
                    word.attrib['LINK'] = head_token.attrib['LINK']
                    word.attrib['DOM'] = head_token.attrib['DOM']
                    head_token.attrib['LINK'] = 'expl'
                    head_token.attrib['FEAT'] = 'PRON'

        # n-компл These are exceptions because no '-союзн' was found in original annotation
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(word, sent)                
                if link in compl and pos == 'CONJ':
                    children = get_children_attrib(sent, word.attrib['ID'])
                    if head_token.attrib['FEAT'].split()[0] == 'S':
                        word.attrib['LINK'] = 'nmod'
                        for ch in children:
                            if ch['LEMMA'] == 'или':
                                ch['LINK'] = 'fixed'
                    elif head_token.attrib['FEAT'].split()[0] == 'ADV':
                        word.attrib['LINK'] = 'discourse'
                        children[0]['LINK'] = 'discourse'
                    else:
                        if head_token.attrib['LEMMA'] == 'почитать':
                            word.attrib['LINK'] = 'obj'
                            word.attrib['FEAT'] = 'PRON'
                        elif head_token.attrib['LEMMA'] == 'спрашивать':
                            word.attrib['LINK'] = 'mark'
                        else:
                            children[0]['DOM'] = word.attrib['DOM']
                            word.attrib['DOM'] = children[0]['ID']
                            children[0]['LINK'] = 'advcl'
                            if word.attrib['LEMMA'] not in conj_set:
                                 word.attrib['LINK'] = 'mark'
                            else:
                                 word.attrib['LINK'] = 'cc'
        # эксплет
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(word, sent)
                children = get_children_attrib(sent, word.attrib['ID'])
                if link == 'эксплет':
                    if word.attrib['FEAT'].split()[0] not in {'V'}:
                        if all(ch['FEAT'].split()[0] not in {'V'} for ch in children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in children):
                            if head_token.attrib['FEAT'].split()[0] in {'S'}:
                                if word.attrib['FEAT'].split()[0] in {'S', 'A'}:
                                    word.attrib['LINK'] = 'nmod'
                                elif word.attrib['FEAT'].split()[0] in {'ADV'}:
                                    word.attrib['LINK'] = 'obl'
                            elif head_token.attrib['FEAT'].split()[0] in {'ADV', 'A'}:
                                word.attrib['LINK'] = 'obl'
                            else: # one exception
                                word.attrib['LINK'] = 'advmod'
                                word.attrib['DOM'] = head_token.attrib['DOM']
                        else:
                            if head_token.attrib['FEAT'].split()[0] in {'S'}:
                                if word.attrib['FEAT'].split()[0] in {'S', 'A', 'ADV'}:
                                    word.attrib['LINK'] = 'acl'
                            elif head_token.attrib['FEAT'].split()[0] in {'A'}:
                                if word.attrib['FEAT'].split()[0] in {'A', 'S'}:
                                    word.attrib['LINK'] = 'acl'
                            elif head_token.attrib['FEAT'].split()[0] in {'ADV'}:
                                if word.attrib['LEMMA'] == 'человек':
                                    word.attrib['DOM'] = head_token.attrib['DOM']
                                    word.attrib['LINK'] = 'acl'
                                else:
                                    word.attrib['LINK'] = 'advcl'
                    else:
                        if head_pos in {'S'}:
                            word.attrib['LINK'] = 'acl'
                        elif head_pos in {'ADV'}:
                            word.attrib['LINK'] = 'advcl'
                        elif head_pos in {'A'}:
                            if sent.findall('W')[int(head_token.attrib['DOM']) - 1].attrib['FEAT'].split()[0] == 'S':
                                word.attrib['DOM'] = sent.findall('W')[int(head_token.attrib['DOM']) - 1].attrib['ID']
                                word.attrib['LINK'] = 'acl'
                            else:
                                if word.attrib['LEMMA'] == 'идти':
                                    for item in sent.findall('W'):
                                        if item.attrib['ID'] == '13':
                                            item.attrib['DOM'] = '10'
                                            item.attrib['LINK'] = 'acl'
                                            break
                                    word.attrib['LINK'] = 'acl'
                                else:
                                    word.attrib['LINK'] = 'acl'
                    if pos == 'CONJ':
                        if head_token.attrib['LEMMA'] == 'потому':
                            word.attrib['LINK'] = 'mark'
                            word.attrib['DOM'] = head_token.attrib['DOM']
                        else:
                            if head_token.attrib['LEMMA'] == 'то':
                                for item in sent.findall('W'):
                                    if item.attrib['ID'] == '24':
                                        item.attrib['DOM'] = '27'
                                        item.attrib['LINK'] = 'mark'
                                    if item.attrib['ID'] == '27':
                                        item.attrib['DOM'] = '23'
                                        item.attrib['LINK'] = 'acl'
                                        break

        # обст
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(word, sent)
                if link == 'обст' and pos == 'CONJ':
                    children = get_children_attrib(sent, word.attrib['ID'])
                    if len(children) == 0:
                        word.attrib['LINK'] = 'mark'
                    elif len(children) == 1:
                        word.attrib['LINK'] = 'mark'
                        children[0]['DOM'] = word.attrib['DOM']
                    else:
                        print('Something went wrong 1')

        # вспом
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(word, sent)
                if link == 'вспом':
                    if word.attrib['LEMMA'] == 'себя':
                            if 'ТВОР' in feats:
                                word.attrib['LINK'] = 'fixed'
                            else:
                                word.attrib['LINK'] = 'obl'
                    elif pos == 'NUM' and head_token.text.istitle():
                        word.attrib['LINK'] = 'flat:name'
                    elif head_token.text.istitle() and int(word.attrib['DOM']) > int(word.attrib['ID']):
                        word.attrib['DOM'] = head_token.attrib['DOM']
                        head_token.attrib['DOM'] = word.attrib['ID']
                        if word.attrib['DOM'] == '_root':
                            word.attrib.pop('LINK')
                        else:
                            word.attrib['LINK'] = head_token.attrib['LINK']
                        head_token.attrib['LINK'] = 'flat:name'
                    elif head_token.text.istitle() and int(word.attrib['DOM']) < int(word.attrib['ID']):
                        word.attrib['LINK'] = 'flat:name'
                    else:
                        if word.attrib['LEMMA'] == 'так' and head_token.attrib['LEMMA'] not in {'далее', 'называть', 'чтобы'}:
                            word.attrib['LINK'] = 'discourse'
                        else:
                            word.attrib['LINK'] = 'fixed'

        # then we crack the nuts inside
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                logfile.write('Fixed {}, sentence {}, token {}:\n\t{} {}\n'.format(ifname, sent.attrib['ID'], word.attrib['ID'], str(word.attrib), str(word.text)))
                link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(word, sent)

                if link in simple_rels: # все однозначные замены
                    word.attrib['LINK'] = simple_rels[link]

                if link == 'агент':
                    word.attrib['LINK'] = agent[(head_pos, pos)]

                if link == 'суб-копр':
                    word.attrib['LINK'] = sub_copr[(head_pos, pos)]

                if link == 'огранич':
                    if pos == 'PART':
                        if head_token.attrib.get('LINK', '') == 'cc':
                            word.attrib['LINK'] = 'fixed'
                        elif word.attrib['LEMMA'].lower() in for_discourse:
                            word.attrib['LINK'] = 'discourse'
                        elif word.attrib['LEMMA'].lower() in for_advmod:
                            word.attrib['LINK'] = 'advmod'
                            if head_token.attrib.get('LEMMA', '').lower() == 'это' and head_token.attrib.get('LINK', '') == 'expl':
                                word.attrib['DOM'] = head_token.attrib['DOM']
                                #print(word.attrib.get('ID', ''), word.attrib.get('LINK', ''), word.attrib.get('FEAT', ''), file=sys.stderr)
                                #print(*[(token.attrib.get('ID', 'EMPTY'), token.text, token.attrib.get('DOM', 'EMPTY'), token.attrib.get('FEAT', 'EMPTY'), token.attrib.get('LINK', 'EMPTY'), token.tail) for token in sent], file=sys.stderr, sep='\n')
                                #print('***', file=sys.stderr)

                        elif word.attrib['LEMMA'].lower() in for_aux:
                            if head_token.attrib['LEMMA'].lower() in for_advmod:
                                word.attrib['LINK'] = 'fixed'
                            else:
                                word.attrib['LINK'] = 'aux'
                                if head_token.attrib['DOM'] != '_root':
                                    word.attrib['DOM'] = head_token.attrib['DOM']

                        elif word.attrib['LEMMA'].lower() == 'это':

                            if head_pos == 'V':
                                word.attrib['LINK'] = 'expl'
                            else:
                                word.attrib['LINK'] = 'discourse'
                        elif word.attrib['LEMMA'].lower() == 'словно':
                            word.attrib['LINK'] = 'mark'
                        elif word.attrib['LEMMA'].lower() in {'плюс', 'минус'}:
                            word.attrib['LINK'] = 'obl'
                        elif word.attrib['LEMMA'].lower() == 'кое':
                            word.attrib['LINK'] = 'dep'
                        else:
                            word.attrib['LINK'] = 'advmod'
                        continue
                    if pos == 'INTJ':
                        word.attrib['LINK'] = 'discourse'
                        continue
                    if pos == 'CONJ' and word.attrib['LEMMA'].lower() == 'и':
                        word.attrib['LINK'] = 'discourse'
                        word.attrib['FEAT'] = 'PART'
                        continue
                    if head_pos == 'CONJ':
                        word.attrib['DOM'] = head_token.attrib['DOM']

                    if pos == 'NUM':
                        # exception 
                        if head_pos == 'V' and head_token.attrib.get('LINK', '') == 'conj':
                            word.attrib['LINK'] = 'parataxis'
                        # exception
                        elif head_pos == 'A' and word.attrib['LEMMA'].lower() == 'один':
                            word.attrib['LINK'] = 'advmod'
                        else:
                            word.attrib['LINK'] = 'advmod'
                    # else:
                    #     word.attrib['LINK'] = 'advmod'

                    # print('Not in any ifs!')
                    # print(word.attrib['LINK'], word.attrib['LEMMA'], word.attrib['ID'])
                    word.attrib['LINK'] = ogranic[(head_pos, pos)]

                if link == 'оп-опред':
                    if head_pos == 'S':
                        children = get_children_attrib(sent, word.attrib['ID'])
                        if word.attrib['FEAT'].split()[0] not in {'V'}:
                            if all(ch['FEAT'].split()[0] not in {'V'} for ch in children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in children):
                                word.attrib['LINK'] = 'amod'
                            else:
                                word.attrib['LINK'] = 'acl'
                        else:
                            word.attrib['LINK'] = 'acl'
                    else:
                        word.attrib['LINK'] = 'acl'

                if link == 'опред':
                    children = get_children_attrib(sent, word.attrib['ID'])

                    if len(children) != 0:
                        if word.attrib['FEAT'].split()[0] not in {'V'}:
                            if all(ch['FEAT'].split()[0] not in {'V'} for ch in children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in children) and any(ch['LINK'] in {'parataxis', 'вводн'} for ch in children):
                                word.attrib['LINK'] = 'amod'
                            elif all(ch['FEAT'].split()[0] not in {'V'} for ch in children) and all(ch.get('LINK', 'EMPTY') not in is_clause for ch in children):
                                if head_pos in {'S', 'A', 'NUM', 'NID', 'ADV', 'V', 'CONJ'} and pos == 'A':
                                    word.attrib['LINK'] = 'amod'
                                elif head_pos in {'S'} and pos in ['S', 'NUM']:
                                    word.attrib['LINK'] = 'nmod'

                            else:
                                word.attrib['LINK'] = 'acl'
                        else:
                            word.attrib['LINK'] = 'acl'
                    else:
                        if pos == 'NUM':
                            if word.text in ['27,81', '4,5', '81,85', '12,5', '1,6', '10,2', '13,6']:
                                word.attrib['LINK'] = 'nummod'
                                continue
                            else:
                                word.attrib['FEAT'] = 'A'

                        word.attrib['LINK'] = 'amod'

                if link == 'вводн': # вводное
                    if 'ЗВ' in feats:
                        word.attrib['LINK'] = vvodn['conditional']
                    else:
                        word.attrib['LINK'] = vvodn['simple']

                if link == 'уточн':

                    word.attrib['LINK'] = utochn[(head_pos, pos)]

                if link == 'кратн':
                    if head_token.attrib['LEMMA'] == word.attrib['LEMMA']:
                        word.attrib['LINK'] = 'flat'
                    elif head_pos == 'V' and pos == 'V':
                        word.attrib['LINK'] = 'conj'
                    elif head_pos == 'ADV' and pos == 'ADV':
                        word.attrib['LINK'] = 'conj'
                    elif head_pos == 'A' and pos == 'A':
                        word.attrib['LINK'] = 'conj'
                    elif head_pos == 'PART' and pos == 'PART':
                        word.attrib['LINK'] = 'fixed'
                    elif head_pos == 'CONJ' and pos == 'CONJ':
                        word.attrib['LINK'] = 'fixed'
                    elif head_pos == 'S' and pos == 'S':
                        if head_token.attrib['LEMMA'] == 'хуан' and word.attrib['LEMMA'] == 'мануэль':
                            word.attrib['LINK'] = 'flat:name'
                        else:
                            word.attrib['LINK'] = 'nmod'
                    elif head_pos == 'NID' and pos == 'NID':
                        word.attrib['LINK'] = 'nmod'
                    elif head_pos == 'NUM' and pos == 'A':
                        word.attrib['LINK'] = 'nmod'
                    elif head_pos == 'NUM' and pos == 'S':
                        word.attrib['LINK'] = 'nmod'
                    elif head_pos == 'S' and pos == 'A':
                        word.attrib['LINK'] = 'nmod'
                    elif head_pos == 'A' and pos == 'S':
                        word.attrib['LINK'] = 'nmod'
                    elif head_pos == 'ADV' and pos == 'S':
                        word.attrib['LINK'] = 'nmod'
                    elif head_pos == 'NUM' and pos == 'NUM':
                        word.attrib['LINK'] = 'nmod'
                    elif head_pos == 'S' and pos == 'NUM':
                        word.attrib['LINK'] = 'nmod'
                    elif head_pos == 'A' and pos == 'NUM':
                        word.attrib['LINK'] = 'amod'

                if link == 'колич-огран':
                    word.attrib['LINK'] = kolich_ogran[(head_pos, pos)]

                if link == 'колич-копред':
                    word.attrib['LINK'] = kolich_kopred[(head_pos, pos)]

                if link == 'длительн':
                    #print(word.attrib.get('ID', ''), word.attrib.get('LINK', ''), word.attrib.get('FEAT', ''), file=sys.stderr)
                    #print(*[(token.attrib.get('ID', 'EMPTY'), token.text, token.attrib.get('DOM', 'EMPTY'), token.attrib.get('FEAT', 'EMPTY'), token.attrib.get('LINK', 'EMPTY'), token.tail) for token in sent], file=sys.stderr, sep='\n')
                    #print('***', file=sys.stderr)
                    word.attrib['LINK'] = dliteln[(head_pos, pos)]



                if link == 'присвяз':
                    if head_pos == 'S' and pos == 'S' and head_token.attrib['LEMMA'] == 'это':
                        children = get_children_attrib(sent, head_token.attrib['ID'])
                        word.attrib['DOM'] = head_token.attrib['DOM']
                        head_token.attrib['LINK'] = 'expl'
                        head_token.attrib['DOM'] = word.attrib['ID']
                        if word.attrib['DOM'] == '_root':
                            word.attrib.pop('LINK')
                        for ch in children:
                            if ch['ID'] != word.attrib['ID']:
                                ch['DOM'] = word.attrib['ID']
                    else:
                        word.attrib['LINK'] = prisvyaz[(head_pos, pos)]

                # все замены, зависящие от части речи
                if link in pos_dependent_rels:
                    description = pos_dependent_rels[link]
                    word.attrib['LINK'] = description.replace_dict.get(pos, description.default)

                if link == 'несобст-агент':
                    if head_pos in {'V'} and pos in {'S'}:
                        if 'ДАТ' in word.attrib['FEAT']:
                            word.attrib['LINK'] = 'iobj'
                        else:
                            word.attrib['LINK'] = 'obl'
                    else:
                        word.attrib['LINK'] = 'nmod'

                if link == 'квазиагент':
                    try:
                        word.attrib['LINK'] = kvaziagent[(head_pos, pos)]
                    # unexpected (head_pos, pos) pair
                    except KeyError:
                        print(word.attrib['ID'])
                        print(*[(token.attrib.get('ID', 'EMPTY'), token.text, token.attrib.get('DOM', 'EMPTY'), token.attrib.get('LINK', 'EMPTY'), token.tail) for token in sent], sep='\n')
                        print('*' * 20)

                if link == 'атриб':
                    if head_pos in {'NUM'} and pos in {'S'}:
                        if head_token.attrib['LEMMA'].isdigit():
                            word.attrib['LINK'] = 'flat'
                        else:
                            word.attrib['LINK'] = atrib[(head_pos, pos)]  
                    elif head_pos in {'S'} and pos in {'V'}:
                        if 'ПРИЧ' in word.attrib['FEAT'] or 'ДЕЕПР' in word.attrib['FEAT']:
                            word.attrib['LINK'] = atrib[(head_pos, pos)]
                        else:
                            word.attrib['LINK'] = 'nmod'
                    elif head_pos in {'A'} and pos in {'V'}:
                        if 'ПРИЧ' in word.attrib['FEAT'] or 'ДЕЕПР' in word.attrib['FEAT']:
                            word.attrib['LINK'] = atrib[(head_pos, pos)]
                        else:
                            word.attrib['LINK'] = 'advcl'
                    elif pos == 'NUM':
                        #print(word.attrib.get('ID', ''), word.attrib.get('LINK', ''), word.attrib.get('FEAT', ''), file=sys.stderr)
                        #print(*[(token.attrib.get('ID', 'EMPTY'), token.text, token.attrib.get('DOM', 'EMPTY'), token.attrib.get('FEAT', 'EMPTY'), token.attrib.get('LINK', 'EMPTY'), token.tail) for token in sent], file=sys.stderr, sep='\n')
                        #print('***', file=sys.stderr)
                        word.attrib['LINK'] = atrib[(head_pos, pos)]
                    else:
                        try:
                            word.attrib['LINK'] = atrib[(head_pos, pos)]
                        # unexpected (head_pos, pos) pair
                        except KeyError:
                            print(word.attrib.get('ID', 'EMPTY'), word.text, word.attrib.get('FEAT', 'EMPTY'))
                            print(*[(ch.get('ID', 'EMPTY'), ch.get('LEMMA', 'EMPTY'), ch.get('FEAT', 'EMPTY'), ch.get('LINK', 'EMPTY')) for ch in children], sep=' ')
                            print('+' * 20)
                            print(*[(token.attrib.get('ID', 'EMPTY'), token.text, token.attrib.get('DOM', 'EMPTY'), token.attrib.get('FEAT', 'EMPTY'), token.attrib.get('LINK', 'EMPTY'), token.tail) for token in sent], sep='\n')
                            print('*' * 20)

                if link == 'распред':
                    word.attrib['LINK'] = raspred[(head_pos, pos)]

                if link in nmod_sampl:
                    word.attrib['LINK'] = 'nmod'

                if link in obl_sampl:
                    word.attrib['LINK'] = 'obl'

                if link in {'дат-субъект', 'дат-сент', 'неакт-компл'}:
                    children = get_children_attrib(sent, word.attrib['ID'])
                    if 'ДАТ' in feats and all(ch['FEAT'].split()[0] != 'PR' for ch in children) and \
                        head_token.attrib.get('LINK', 'EMPTY') not in {'nsubj', 'nsubj:pass'}:
                        word.attrib['LINK'] = 'iobj'
                    else:
                        if head_pos in {'NUM','S', 'A'} and pos == 'S':
                            word.attrib['LINK'] = 'nmod'
                        elif head_pos in {'S'} and pos == 'A':
                            word.attrib['LINK'] = 'nmod' 
                        elif head_pos in {'V', 'ADV'} and pos == 'S':
                            word.attrib['LINK'] = 'obl'
                        elif head_pos == 'NUM' and pos == 'A':
                            word.attrib['LINK'] = 'iobj'
                            word.attrib['DOM'] = '10'

                if link == 'примыкат':
                    if word.attrib.get('FEAT', 'EMPTY') == head_token.attrib['FEAT']:
                        word.attrib['LINK'] = 'appos'
                    else:
                        word.attrib['LINK'] = 'parataxis'

                if link == 'аппоз':
                    if word.text.istitle() and head_token.text.istitle() and \
                       head_token.attrib['ID'] != '1' and \
                       'ОД' in head_feats and 'ОД' in feats:
                        word.attrib['LINK'] = 'flat:name'
                    else:
                        word.attrib['LINK'] = 'appos'

                if link in nesobst_compl:
                    if pos == 'V' and head_pos == 'V' and 'ПРИЧ' not in head_feats:
                        children = get_children_attrib(sent, word.attrib['ID'])
                        if any(child['LINK'] in {'nsubj:pass', 'nsubj', 'предик'} for child in children):
                            word.attrib['LINK'] = 'ccomp'
                        else:
                            word.attrib['LINK'] = 'xcomp'
                    else:
                        word.attrib['LINK'] = nesobst_compl_dict[(head_pos, pos)]

                if link in compl:
                    children = get_children_attrib(sent, word.attrib['ID'])
                    if pos == 'V':
                        if head_pos in {'V', 'A', 'ADV'}:
                            if any(child['LINK'] in {'csubj:pass', 'csubj', 'nsubj:pass', 'nsubj', 'предик'} for child in children):
                                word.attrib['LINK'] = 'ccomp'
                            else:
                                word.attrib['LINK'] = 'xcomp'
                        elif head_pos == 'S':
                            if 'ИНФ' in feats:
                                word.attrib['LINK'] = 'obl'
                            else:
                                for_slice = [int(word.attrib['ID']) - 1, int(head_token.attrib['ID']) - 1]
                                for_slice.sort()
                                if any('"' in elem.tail.strip() or '-' in elem.tail.strip() or ':' in elem.tail.strip() \
                                    for elem in sent.findall('W')[for_slice[0]:for_slice[1]]):
                                    word.attrib['LINK'] = 'appos'
                                elif any(child['FEAT'].split()[0] == 'PR' for child in children):
                                    word.attrib['LINK'] = 'obl'
                                else:
                                    word.attrib['LINK'] = 'acl'
                    elif pos == 'S':
                        if link == '2-компл' and 'РОД' in feats and all(child['FEAT'].split()[0] != 'PR' for child in children) \
                            and head_token.attrib.get('LINK', 'EMPTY') not in {'nsubj', 'nsubj:pass'}:
                            word.attrib['LINK'] = 'iobj'
                        elif 'ДАТ' in feats and all(child['FEAT'].split()[0] != 'PR' for child in children) \
                            and head_token.attrib.get('LINK', 'EMPTY') not in {'nsubj', 'nsubj:pass'}:
                            word.attrib['LINK'] = 'iobj'
                        elif link != '2-компл' and 'ВИН' in feats and all(child['FEAT'].split()[0] != 'PR' for child in children) \
                            and head_token.attrib.get('LINK', 'EMPTY') not in {'nsubj', 'nsubj:pass'}:
                            word.attrib['LINK'] = 'obj'                        
                        else:
                            if head_pos in {'S', 'NUM', 'NID'} and pos == 'S':
                                word.attrib['LINK'] = 'nmod'
                            elif head_pos in {'V', 'A', 'ADV','PART', 'INTJ'} and pos == 'S':
                                word.attrib['LINK'] = 'obl'
                    elif pos == 'A':
                        if 'ВИН' in feats and all(child['FEAT'].split()[0] != 'PR' for child in children) \
                            and head_token.attrib.get('LINK', 'EMPTY') not in {'nsubj', 'nsubj:pass'}:
                            word.attrib['LINK'] = 'obj'
                        elif 'ДАТ' in feats and all(child['FEAT'].split()[0] != 'PR' for child in children) \
                            and head_token.attrib.get('LINK', 'EMPTY') not in {'nsubj', 'nsubj:pass'}:
                            word.attrib['LINK'] = 'iobj'
                        else:
                            if head_pos in {'S', 'V', 'ADV'} and pos == 'A':
                                word.attrib['LINK'] = 'obl'
                            elif head_pos == 'A' and pos == 'A':
                                if head_token.attrib['LEMMA'] == 'должен':
                                    word.attrib['LINK'] = 'xcomp'
                                else:
                                    word.attrib['LINK'] = 'obl'
                    elif pos == 'ADV':
                        word.attrib['LINK'] = 'advmod'
                    elif pos == 'NID':
                        if head_pos == 'V':
                            if link == '1-компл' and all(child['FEAT'].split()[0] != 'PR' for child in children) \
                            and head_token.attrib.get('LINK', 'EMPTY') not in {'nsubj', 'nsubj:pass'}:
                                word.attrib['LINK'] = 'obj'
                            else:
                                word.attrib['LINK'] = 'obl'
                        elif head_pos == 'S':
                            word.attrib['LINK'] = 'nmod'
                        elif head_pos in {'ADV', 'A'}:
                            word.attrib['LINK'] = 'obl'
                    elif pos in {'PART', 'INTJ'}:
                        if head_pos == 'V':
                            if link == '1-компл' and all(child['FEAT'].split()[0] != 'PR' for child in children) \
                            and head_token.attrib.get('LINK', 'EMPTY') not in {'nsubj', 'nsubj:pass'}:
                                word.attrib['LINK'] = 'obj'
                            else:
                                word.attrib['LINK'] = 'obl'
                        else:
                            word.attrib['LINK'] = 'nmod'
#----- check
                    elif 'NUM' in pos:
                        if link in ['1-компл', '3-компл', '4-компл'] and head_pos == 'V':
                            word.attrib['LINK'] = 'obl'
                        if link in ['1-компл', '2-компл', '3-компл'] and head_pos == 'S':
                            word.attrib['LINK'] = 'nmod'
                        if link == '2-компл' and head_pos == 'V':
                            if 'ДАТ' in feats and all(child['FEAT'].split()[0] != 'PR' for child in children) \
                               and head_token.attrib.get('LINK', 'EMPTY') not in {'nsubj', 'nsubj:pass'}:
                                word.attrib['LINK'] = 'iobj'
                            else:
                                word.attrib['LINK'] = 'obl'
                        if link in ['1-компл'] and head_pos == 'ADV':
                            word.attrib['LINK'] = 'obl'
                        if link in ['1-компл'] and head_pos == 'A':
                            word.attrib['LINK'] = 'obl'
                        
#----- maybe merge
                if link == 'обст':
                    children = get_children_attrib(sent, word.attrib['ID'])
                    if pos == 'ADV':
                        word.attrib['LINK'] = 'advmod'
                    elif pos in {'INTJ', 'PR', 'NID', 'A', 'NUM'}:
                        word.attrib['LINK'] = 'obl'
                    elif pos == 'PART':
                        if word.attrib['LEMMA'] in ['нет', 'эдь']:
                            word.attrib['LINK'] = 'obl'
                        else:
                            word.attrib['LINK'] = 'advmod'
                    elif pos == 'S':
                        if head_pos in {'V', 'A', 'ADV', 'NUM', 'PART', 'PR'}:
                            if any(child['LINK'] in {'nsubj:pass', 'nsubj', 'предик'} for child in children):
                                word.attrib['LINK'] = 'advcl'                            
                            else:
                                word.attrib['LINK'] = 'obl'
                        elif head_pos in {'S'}:
                            word.attrib['LINK'] = 'nmod'
                    elif pos == 'V':
                        if 'ДЕЕПР' in feats:
                            if head_pos == 'S':
                                word.attrib['LINK'] = 'acl'
                            else:
                                word.attrib['LINK'] = 'advcl'
                        elif 'ИНФ' in feats:
                            if head_pos == 'V':
                                word.attrib['LINK'] = 'xcomp'
                            else:
                                word.attrib['LINK'] = 'advcl'
                        else:
                            word.attrib['LINK'] = 'advcl'

                if link == 'об-копр':
                    if head_pos == 'V' and pos in {'A', 'S', 'NUM'}:
                        word.attrib['LINK'] = 'obl'
                    elif head_pos == 'V' and pos == 'V':
                        word.attrib['LINK'] = 'xcomp'
                    elif head_pos == 'S' and pos == 'A':
                        word.attrib['LINK'] = 'obl'

                if link == 'соотнос':
                    if {head_pos, pos} == {'S', 'A'} or {head_pos, pos} == {'S'}\
                       or {head_pos, pos} == {'A'} or {head_pos, pos} == {'NID'}: # от ... до, с ... по
                        word.attrib['LINK'] = 'nmod'
                    elif head_pos == 'NUM' and pos == 'S':
                        word.attrib['LINK'] = 'obl'
                    elif head_pos == 'V' and pos == 'ADV':
                        word.attrib['LINK'] = 'obl'
                    elif head_pos == 'ADV' and pos == 'ADV':
                        if head_token.attrib['LEMMA'].lower() == 'сколько' and word.attrib['LEMMA'].lower() == 'столько':
                            # rename for convenience
                            stolko_token, skolko_token = word, head_token
                            # fix stolko
                            stolko_token.attrib['DOM'] = skolko_token.attrib['DOM']
                            stolko_token.attrib['LINK'] = 'mark'
                            for stolko_child in get_children_attrib(sent, stolko_token.attrib['ID']):
                                stolko_child['DOM'] = stolko_token.attrib['DOM']
                            # fix skolko
                            for candidate_token in sent.findall('W')[int(skolko_token.attrib['ID']):]:
                                if candidate_token.attrib['DOM'] == skolko_token.attrib['DOM']:
                                    skolko_token.attrib['DOM'] = candidate_token.attrib['ID']
                                    skolko_token.attrib['LINK'] = 'mark'
                                    break
                        #elif head_token.attrib['LEMMA'] == 'столько' and head_token.attrib['LINK'] == 'nummod:gov':
                        #    word.attrib['DOM'] = '10'
                        #    word.attrib['LINK'] = 'amod'
                        elif head_token.attrib['LEMMA'].lower()  == 'сверху' and word.attrib['LEMMA'].lower()  == 'донизу':
                            word.attrib['DOM'] = head_token.attrib['ID']
                            word.attrib['LINK'] = 'fixed'
                        #elif head_token.attrib['LEMMA'] == 'столько' and word.attrib['LEMMA'] == 'сколько':
                            #word.attrib['DOM'] = '20'
                            #word.attrib['LINK'] = 'mark'
                            #rost_token = sent.findall('W')[19]
                            #rost_token.attrib['DOM'] = '13'
                            #rost_token.attrib['LINK'] = 'conj'
                    elif head_token.attrib['LEMMA'].lower()  == 'сколько' and word.attrib['LEMMA'].lower()  == 'только':
                        word.attrib['DOM'] = '12'
                        word.attrib['LINK'] = 'mark'
                        head_token.attrib['DOM'] = '14'
                        head_token.attrib['LINK'] = 'mark'
                        army_token = sent.findall('W')[13]
                        army_token.attrib['DOM'] = '12'
                        army_token.attrib['LINK'] = 'conj'
                    elif word.attrib['LEMMA'].lower()  in {'тогда', 'так'}:
                        word.attrib['LINK'] = 'mark'
                        min_dom, min_cand = 1000, None
                        for candidate_token in sent.findall('W')[int(word.attrib['ID']):]:
                            if candidate_token.attrib['DOM'] == '_root':
                                word.attrib['DOM'] = candidate_token.attrib['ID']
                                break
                            if int(candidate_token.attrib['DOM']) < min_dom:
                                min_dom = int(candidate_token.attrib['DOM'])
                                min_cand = candidate_token
                        else:
                            word.attrib['DOM'] = min_cand.attrib['ID']
                    elif head_token.attrib['LEMMA'].lower()  == 'просыпаться' and word.attrib['LEMMA'].lower()  == 'происки' or\
                         head_token.attrib['LEMMA'].lower()  == 'полезный' and word.attrib['LEMMA'].lower()  == 'терять':
                        word.attrib['LINK'] = 'nmod'
                    elif pos == 'V':
                        word.attrib['LINK'] = 'advcl'
                    else:
                        word.attrib['LINK'] = 'obl'
                logfile.write('\t{} {}\n'.format(str(word.attrib), str(word.text)))

            for word in sent.findall('W'):
                # check if appos goes in wrong direction
                if word.attrib.get('LINK') == 'appos' and int(word.attrib['DOM']) > int(word.attrib['ID']):
                    head = sent.findall('W')[int(word.attrib['DOM']) - 1]
                    word.attrib['DOM'], head.attrib['DOM'] = head.attrib['DOM'], word.attrib['ID']
                    if 'LINK' in head.attrib:
                        word.attrib['LINK'] = head.attrib['LINK']
                    head.attrib['LINK'] = 'appos'

        # check if everything is converted
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(word, sent)
                if link not in {'nsubj', 'nsubj:pass', 'csubj', 'csubj:pass', 'cop', 'aux', 'aux:pass', 'iobj', 'obj', 'obl', 'nmod', 'advmod', 'nummod', 'amod', 'nummod:gov', 'nummod:entity', 'nmod:agent', 'acl', 'acl:relcl', 'advcl', 'parataxis', 'discourse', 'case', 'cc', 'mark', 'ccomp', 'xcomp', 'conj', 'fixed', 'flat:name', 'flat', 'appos', 'compound', 'expl', 'dep', 'vocative', 'EMPTY'}:
                    print('Cannot convert this')
                    print(link, word.attrib['ID'])
                    for item in sent.findall('W'):
                        print(item.text, item.attrib)
                    print('---------------')
                
        tree.write(ofname, encoding="UTF-8")
    logfile.close()

def process_all(ifolder, ofolder):
	main(*get_fnames(ifolder, ofolder, '.xml', '.xml'))
	print('7: syntax.py completed')

if __name__ == "__main__":
    process_all(ifolder, ofolder)
