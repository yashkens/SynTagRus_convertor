#!/usr/bin/env python3

""" UD morphology and features """

import os
import re
from collections import namedtuple
from collections import defaultdict
import json

import lxml.etree as ET

from util import get_fnames, get_children

whitespace_re = re.compile('\s+')
opening_cite_re = re.compile('(:["-]|,-)')

with open('PROPN_exc.json') as data_file:    
    load_exceptions = json.load(data_file)

Feature = namedtuple('Feature', ['ud_id', 'regex', 'convert', 'default'])
Pos = namedtuple('Pos', ['ud_id', 'feats'])

ifolder = 'Syntax'
ofolder = 'Morphology'

# nominal
gender = Feature('Gender', re.compile(r'\b((МУЖ)|(ЖЕН)|(СРЕД))\b'), {'МУЖ':'Masc', 'ЖЕН':'Fem', 'СРЕД':'Neut'}, None)
anim = Feature('Animacy', re.compile(r'\b((ОД)|(НЕОД))\b'), {'ОД':'Anim', 'НЕОД':'Inan'}, None)
number = Feature('Number', re.compile(r'\b((ЕД)|(МН))\b'), {'ЕД':'Sing', 'МН':'Plur'}, None)
case = Feature('Case', re.compile(r'\b((ИМ)|(РОД)|(ДАТ)|(ВИН)|(ТВОР)|(ПР)|(ПАРТ)|(МЕСТН)|(ЗВ)|(НЕСКЛ))\b'), 
		{'ИМ':'Nom', 'РОД':'Gen', 'ДАТ':'Dat', 'ВИН':'Acc', 'ТВОР':'Ins', 
		 'ПР':'Loc', 'ПАРТ':'Par', 'МЕСТН':'Loc', 'ЗВ':'Voc'}, None)
degree = Feature('Degree', re.compile(r'\b((СРАВ)|(ПРЕВ))\b'), {'СРАВ':'Cmp', 'ПРЕВ':'Sup'}, 'Pos')
variant = Feature('Variant', re.compile(r'\b(КР)\b'), {'КР':'Short'}, None)

# verb
vform = Feature('VerbForm', re.compile(r'\b((ИНФ)|(ДЕЕПР)|(ПРИЧ)|(ФИН))\b'), {'ИНФ':'Inf', 'ДЕЕПР':'Conv', 'ПРИЧ':'Part', 'ФИН':'Fin'}, None) # also Fin for ИЗЪЯВ and ПОВ
mood = Feature('Mood', re.compile(r'\b((ИЗЪЯВ)|(ПОВ))\b'), {'ИЗЪЯВ':'Ind', 'ПОВ':'Imp'}, None)
tense = Feature('Tense', re.compile(r'\b((ПРОШ)|(НАСТ)|(БУДУЩ))\b'), {'ПРОШ':'Past', 'НАСТ':'Pres', 'БУДУЩ':'Fut'}, None) # needs pre-fix
aspect = Feature('Aspect', re.compile(r'\b((НЕСОВ)|(СОВ))\b'), {'НЕСОВ':'Imp', 'СОВ':'Perf'}, None)
voice = Feature('Voice', re.compile(r'\b(СТРАД)\b'), {'СТРАД':'Pass'}, 'Act')
person = Feature('Person', re.compile(r'\b([123]-Л)\b'), {'1-Л':'1', '2-Л':'2', '3-Л':'3'}, None)

S_feats = (anim, case, gender, number)
ADJ_feats = (anim, case, degree, gender, number, variant)
DET_feats = (case, gender, number)
ADV_feats = (degree,)
NUM_feats = (anim, case, gender)
V_feats = (anim, aspect, case, gender, mood, number, person, tense, variant, vform, voice)
VI_feats = (aspect, mood, number, tense, vform, voice)
SPRO_feats = (gender, number, person)

det_set = {'такой', 'какой', 'всякий',
           'некоторый', 'никакой', 'некий', 'сей', 'чей', 
           'какой-либо', 'какой-нибудь','кое-какой',
           'весь', 'этот', 'тот', 'каждый',
           'мой', 'твой', 'ваш', 'наш', 'свой',
           'любой', 'каждый', 'какой-то', 'некоторый'}

conj_set = {'а', 'ан', 'да', 'зато', 'и', 'или', 'иль', 'иначе',
            'либо', 'ни', 'но', 'однако', 'притом', 'причем',
            'причём', 'сколько', 'столько', 'также', 'тоже', 'только',
            'и/или', 'а также', 'а то и', 'не то', 'так же как',
            'так и', 'в противном случае', 'х'}

sconj_set = {'благо', 'будто', 'ведь', 'где', 'дабы', 'едва',
            'ежели', 'ежель', 'если', 'ибо', 'кабы', 'как',
            'когда', 'коли', 'коль', 'куда', 'лишь', 'насколько',
            'настолько', 'нежели', 'откуда', 'пока', 'покамест',
            'покуда', 'поскольку', 'постольку', 'пускай', 'пусть',
            'раз', 'разве', 'ровно', 'сколь', 'словно', 'так',
            'тем', 'то', 'точно', 'хоть', 'хотя', 'чем', 'что',
            'чтоб', 'чтобы', 'чуть', 'а не то', 'а то',
            'в случае если', 'в то время как', 'до того как',
            'как будто', 'как если бы', 'как только', 'коль скоро',
            'оттого что', 'потому как', 'потому что', 'по мере того как',
            'прежде чем', 'при условии что', 'разве что', 'с тех пор как',
            'так как', 'т.к.', 'так что', 'то есть', 'тогда как'} 

spro_dict = {
    'я':'1-Л ЕД',
    'мы':'1-Л МН',
    'ты':'2-Л ЕД',
    'вы':'2-Л МН',
    'он':'3-Л ЕД МУЖ',
    'она':'3-Л ЕД ЖЕН', 
    'оно':'3-Л ЕД СРЕД', 
    'они':'3-Л МН'
    }

pron_set = {'себя', 'кто', 'что', 'никто', 'ничто', 'некто', 'нечто', 'который',
            'кто-то', 'кто-либо', 'кто-нибудь', 'кое-кто', 'кот-в-пальто',
            'что-то', 'что-либо', 'что-нибудь'}

pos_dict = {'A':Pos('ADJ', ADJ_feats),
            'ADV':Pos('ADV', ADV_feats),
            'NUM':Pos('NUM', NUM_feats),
            'V':Pos('VERB', V_feats),
            'AUX':Pos('AUX', V_feats),
            'Vi':Pos('VERB', VI_feats),
            'AUXi':Pos('AUX', VI_feats),
            'S':Pos('NOUN', S_feats),
            'Sp':Pos('PROPN', S_feats)}

aux_links = ('aux', 'aux:pass', 'cop')

sym_set = {'%', '$', '№', '°', '€', '+', '=', '№№'}

compr_dict = {'более', 'менее', 'больше', 'меньше'}

def conv_tense(feats):
    if 'НЕСОВ' in feats:
        return feats.replace('НЕПРОШ', 'НАСТ')
    if 'СОВ' in feats:
        return feats.replace('НЕПРОШ', 'БУДУЩ')
    return feats

def conv_feat(line, feat):
    match = feat.regex.search(line)
    return feat.convert[match.group(0)] if match is not None else feat.default

def format_feats(feats_converted, pos):
    return pos + ' ' + '|'.join(['='.join(feat) 
                                    for feat in feats_converted 
                                        if feat[1] is not None])

def fix_token(fname, i, j, token, lemma, pos, prev_punct, logfile):
    """
    Fix token's feats and log it.
    """
    word = safe_text(token.text)
    feats = token.attrib.get('FEAT', ' ')

    logfile.write('Fixed {}, sentence {}, token {}:\n\t{} {}\n'.format(fname, i, j, str(token.attrib), word))

    # ugly patches for verbs
    if pos == 'V':
        # tense
        feats = conv_tense(feats)
        # ИЗЪЯВ or ПОВ -> + ФИН
        if mood.regex.search(feats) is not None:
            feats = feats + ' ФИН'
        if ' ИНФ' in feats or ' ИМП' in feats:
            pos = 'Vi'
        # check for aux
        if lemma == 'быть' and token.attrib.get('LINK', '') in aux_links:
            pos = pos.replace('V', 'AUX')

    if pos == 'S':
        # personal pron
        if lemma in spro_dict:
            feats_converted = [(case.ud_id, conv_feat(feats, case))] + \
                              [(feat.ud_id, conv_feat(spro_dict[lemma], feat)) 
                                    for feat in SPRO_feats]
            token.attrib['FEAT'] = format_feats(feats_converted, 'PRON')
            pos = 'PRON'
        # other pron
        elif lemma in pron_set:
            feats_converted = [(case.ud_id, conv_feat(feats, case))]
            token.attrib['FEAT'] = format_feats(feats_converted, 'PRON')
            pos = 'PRON'
        # proper nouns
        elif (j > 1 and token.text is not None and
              opening_cite_re.match(prev_punct) is None and
              not prev_punct.endswith('"') and
              (token.text.istitle() or
              (token.text.isupper() and lemma in load_exceptions))):
            pos = 'Sp'
            feats_converted = [(feat.ud_id, conv_feat(feats, feat)) 
                                for feat in S_feats]
            token.attrib['FEAT'] = format_feats(feats_converted, 'PROPN')
        # regular nouns
        else:
            feats_converted = [(feat.ud_id, conv_feat(feats, feat)) 
                                for feat in S_feats]
            token.attrib['FEAT'] = format_feats(feats_converted, 'NOUN')
    elif word in sym_set:
        token.attrib['FEAT'] = 'SYM'
    elif pos == 'DET':
        if lemma in ['его', 'ее', 'их']:
            token.attrib['FEAT'] = 'DET'
        else:
            feats_converted = [(feat.ud_id, conv_feat(feats, feat)) 
                                    for feat in DET_feats]
            token.attrib['FEAT'] = format_feats(feats_converted, 'DET')
    elif pos in pos_dict:
        # S, A, ADV, NUM, V, Vi, AUX, AUXi
        feats_converted = [(feat.ud_id, conv_feat(feats, feat)) 
                                for feat in pos_dict[pos].feats]
        token.attrib['FEAT'] = format_feats(feats_converted, pos_dict[pos].ud_id)
    elif pos == 'PR':
        token.attrib['FEAT'] = 'ADP'
    elif pos == 'CONJ' and lemma in sconj_set:
        token.attrib['FEAT'] = 'SCONJ'
    elif pos == 'CONJ' and lemma in conj_set:
        token.attrib['FEAT'] = 'CCONJ'    
    elif 'FEAT' in token.attrib:
        token.attrib['FEAT'] = pos

    # fix for 'бы':
    if token.attrib['LEMMA'] == 'бы' and token.attrib['LINK']== 'aux':
        token.attrib['FEAT'] = 'AUX'

    if word in compr_dict:
        if 'Degree=' in token.attrib['FEAT']:
            feats_full_temp = token.attrib['FEAT'].split()
            pos_temp = feats_full_temp[0]
            feats_temp = feats_full_temp[1].split('|')
            for i, elem in enumerate(feats_temp):
                if 'Degree=' in elem:
                    feats_temp[i] = 'Degree=Cmp'
            feats_temp.sort()                    
            token.attrib['FEAT'] = pos_temp + ' ' + '|'.join(feats_temp)
    if 'Voice=' in token.attrib['FEAT'] and (token.attrib['LEMMA'].endswith('ся') or token.attrib['LEMMA'].endswith('сь')):
        token.attrib['FEAT'] = re.sub(r'Voice=\w+', 'Voice=Mid', token.attrib['FEAT'])

    logfile.write('\t{} {}\n'.format(str(token.attrib), word))

    return

def munch(ifiles, ofiles):
    """
    Process all files in ifiles list.
    Output into ofiles list.
    """
    #this is for being precise 

    collect_prop_nouns = defaultdict(int)

    logfile = open('convfeat.log', 'w', encoding='utf-8')
    for ifname, ofname in zip(ifiles, ofiles):
        logfile.write('{}\nProcessing {}\n{}\n'.format('=' * 75, ifname, '=' * 75))
        tree = ET.parse(ifname)
        root = tree.getroot()        
        for sentence in root[-1].findall('S'):
            prev_punct = whitespace_re.sub('', safe_text(sentence.text))
            for j, token in enumerate(sentence.findall('W')):
                word = safe_text(token.text)
                if 'NODETYPE' not in token.attrib and 'FEAT' in token.attrib:
                    lemma = token.attrib.get('LEMMA', '').lower()
                    pos = token.attrib.get('FEAT', ' ').split(' ')[0]

                    if (word in {'его', 'ее', 'их'} and
                        token.attrib['DOM'] != '_root' and
                        token.attrib['OLD'] in {'атриб', 'квазиагент'}):
                        token.attrib['LEMMA'] = lemma = word
                        pos = 'DET'

                    elif lemma in det_set:  #fix it; only if the head is noun
                        pos = 'DET'

                    if lemma == 'сколько':
                        pos = 'NUM'

                    if word in compr_dict and lemma in ['много', 'мало']:
                        pos = 'NUM'

                    # fix token
                    fix_token(ifname, int(sentence.attrib['ID']), j + 1, token, lemma, pos, prev_punct, logfile)

                prev_punct = whitespace_re.sub('', safe_text(token.tail))

        tree.write(ofname, encoding = 'utf-8')
    logfile.close()
    return

def safe_text(text):
    if text is not None:
        return text.strip().lower().replace('ё', 'е')
    return ''

def process_all(ifolder, ofolder):
	munch(*get_fnames(ifolder, ofolder, '.xml', '.xml'))
	print('8: morphology.py completed')

if __name__ == "__main__":
    process_all(ifolder, ofolder)

