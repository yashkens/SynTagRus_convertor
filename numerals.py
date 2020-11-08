#!/usr/bin/env python3

# 'количест' and 'аппрокс-колич'; simple 'колич-вспом' will go to syntax

""" Processes numerals:
1. fix lemmas 'назад', 'со стороны', 'внутри', 'изнутри' (part 1)
2. fix lemmas 'МИЛЛИАРД', 'МИЛЛИОН', 'ТРИЛЛИОН', 'ТЫСЯЧА': nummod:gov + change the head from"миллион" to its dependent (part 2)
3. fix lemmas 'больше', 'меньше', 'более', 'менее', 'столько', 'сколько', 'предостаточно', 'достаточно', 'мало', 'много', 'немало', 'немного' (part 3)
"""

import sys
import os
from collections import  defaultdict

from util import import_xml_lib, get_fnames, get_info, get_children_attrib
ET = import_xml_lib()

ifolder = 'Conjunctions'
ofolder = 'Numerals'

lemmas_adv = ['назад', 'со стороны', 'внутри', 'изнутри']

#q_num = ['сотня', 'десяток', 'четверть', 'дюжина'] - these are nouns and syntactic heads
big_num = ['миллиард', 'миллион', 'триллион', 'биллион']
big_num_fem = ['тысяча']

conjrels = ['сочин', 'соч-союзн', 'сент-соч', 'сравн-союзн', 'подч-союзн', 'инф-союзн']
lemmas_to_check = ['больше', 'меньше', 'более', 'менее', 'столько', 'сколько', 'несколько', 'предостаточно', 'достаточно', 'мало', 'много', 'немало', 'немного']

for_debug_rels =defaultdict(int)

def munch(ifiles, ofiles):
    # part 1
    count = 0
    for ifname, ofname in zip(ifiles, ofiles):
        tree = ET.parse(ifname)
        root = tree.getroot()
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):                                               
                if word.attrib.get('FEAT', 'EMPTY').split()[0] == 'PR' and word.attrib.get('LEMMA', 'EMPTY') in lemmas_adv:
                    word.attrib['FEAT'] = 'ADV'
                    if 'LINK' in word.attrib and word.attrib['LINK'] not in conjrels: 
                        word.attrib['LINK'] = 'advmod'

        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                if word.attrib.get('LINK', 'EMPTY') in ['количест', 'аппрокс-колич']:
                    link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(word, sent)
                    feats_str = ''.join(feats)

                    if 'NUM' in pos and word.attrib['LEMMA'] == 'один':
                        word.attrib['LINK'] = 'nummod'
                    elif word.attrib['LEMMA'].endswith('1'):
                        word.attrib['LINK'] = 'nummod'
                    elif feats_str == 'NUM':
                        word.attrib['LINK'] = 'nummod'
                    elif 'ИМ' in feats_str:
                        word.attrib['LINK'] = 'nummod:gov'
                    elif 'ВИНОД' in feats_str:
                        word.attrib['LINK'] = 'nummod:gov'
                    elif 'ОД' not in feats_str and 'НЕОД' not in feats_str and 'ВИН' in feats_str:
                        head_feats_str = ''.join(head_feats)
                        if 'ОД' in head_feats_str:
                            word.attrib['LINK'] = 'nummod:gov'
                        else:
                            word.attrib['LINK'] = 'nummod'
                    else:
                        word.attrib['LINK'] = 'nummod'


        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                if word.attrib.get('LEMMA', 'EMPTY') in big_num + big_num_fem:
                    link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(word, sent)
                    if link == 'колич-вспом': # we need to deal with it later
                        if head_token.attrib['FEAT'].split(' ')[0] == 'A': # will be converted in syntax.py
                            pass
                        else:
                            #fix sentences
                            if ifname.endswith('newsYa_16.xml') and sent.attrib['ID'] == '31':
                                sent[44].attrib['DOM'] = '47'
                                sent[44].attrib['LINK'] = 'колич-вспом'
                            elif ifname.endswith('2014Na_dvukh_voinakh_2.xml') and sent.attrib['ID'] == '232':
                                sent[8].attrib['DOM'] = '12'
                                sent[9].attrib['DOM'] = '12'
                            elif ifname.endswith('2014Na_dvukh_voinakh_1.xml') and sent.attrib['ID'] == '397':
                                sent[2].attrib['DOM'] = '5'
                            elif ifname.endswith('2003Opasnaya_blizost.xml') and sent.attrib['ID'] == '5':
                                sent[18].attrib['DOM'] = '14'
                                sent[18].attrib['LINK'] = 'компл-аппоз'
                                sent[17].attrib['DOM'] = '19'
                                sent[17].attrib['LINK'] = 'nummod'
                                sent[16].attrib['LINK'] = 'колич-вспом'
                                sent[14].attrib['DOM'] = '18'
                                sent[14].attrib['LINK'] = 'колич-вспом'
                            elif ifname.endswith('2003Bolshie_peremeny.xml') and sent.attrib['ID'] == '6':
                                sent[11].attrib['DOM'] = '5'
                                sent[11].attrib['LINK'] = 'обст'
                                sent[9].attrib['DOM'] = '12'
                                sent[9].attrib['LINK'] = 'nummod'
                                sent[8].attrib['LINK'] = 'колич-вспом'
                                sent[6].attrib['DOM'] = '10'
                                sent[6].attrib['LINK'] = 'колич-вспом'
                                sent[5].attrib['DOM'] = '12'
                            elif ifname.endswith('2003Bolshie_peremeny.xml') and sent.attrib['ID'] == '45':
                                sent[14].attrib['DOM'] = '20'
                                sent[15].attrib['DOM'] = '19'
                                sent[15].attrib['LINK'] = 'колич-вспом'
                                sent[17].attrib['LINK'] = 'колич-вспом'
                                sent[18].attrib['DOM'] = '20'
                                sent[18].attrib['LINK'] = 'nummod:gov'
                                sent[19].attrib['LINK'] = 'обст'
                                sent[19].attrib['DOM'] = '26'
                                sent[21].attrib['DOM'] = '24'
                                sent[21].attrib['LINK'] = 'колич-вспом'
                                sent[22].attrib['DOM'] = '24'
                            elif ifname.endswith('2003Tyurma_dlya_svekrovei.xml') and sent.attrib['ID'] == '18':
                                sent[12].attrib['DOM'] = '18'
                                sent[13].attrib['DOM'] = '17'
                                sent[13].attrib['LINK'] = 'колич-вспом'
                                sent[15].attrib['LINK'] = 'колич-вспом'
                                sent[16].attrib['DOM'] = '18'
                                sent[16].attrib['LINK'] = 'nummod'
                                sent[17].attrib['DOM'] = '9'
                                sent[17].attrib['LINK'] = '3-компл'
                            elif ifname.endswith('2014Vladimir_Vladimirovich.xml') and sent.attrib['ID'] == '96':
                                sent[15].attrib['DOM'] = '19'
                                sent[15].attrib['LINK'] = 'колич-вспом'
                                sent[17].attrib['LINK'] = 'колич-вспом'
                                sent[18].attrib['DOM'] = '20'
                                sent[18].attrib['LINK'] = 'nummod'
                                sent[19].attrib['DOM'] = '15'
                                sent[19].attrib['LINK'] = '1-компл'
                            else:
                                print('Unaccounted entry:', ifname, sent.attrib['ID'], file=sys.stderr)
                    else:
                        feats_str = ''.join(feats)
                        children = get_children_attrib(sent, word.attrib['ID'])

                        if link == 'предик' and any(child['LINK'] == 'квазиагент' for child in children):
                            continue

                        if 'РОД' in feats_str:
                            new_link = 'nummod'
                        elif word.attrib.get('LEMMA', 'EMPTY') in big_num and ('ИМ' in feats_str or 'ВИН' in feats_str):
                            new_link = 'nummod:gov'
                        elif word.attrib.get('LEMMA', 'EMPTY') in big_num_fem and ('ИМ' in feats_str or 'ВИНОД' in feats_str):
                            new_link = 'nummod:gov'
                        else:
                            if all(child['LINK'] != 'квазиагент' for child in children):
                                # Not interested in this condition
                                pass
                            else:
                                for child in children:
                                    if child['LINK'] == 'квазиагент':
                                        if 'РОД' in child['FEAT'] or '$' in child['LEMMA']:
                                            new_link = 'nummod:gov'
                                        else:
                                            new_link = 'nummod'

                        for child_token in children:
                            if child_token['LINK'] == 'квазиагент':
                                child_token['LINK'] = link
                                child_token['DOM'] = word.attrib['DOM']

                                word.attrib['LINK'] = new_link
                                word.attrib['DOM'] = child_token['ID']
                                for ch in children:
                                    if ch['ID'] != child_token['ID'] and ch['LINK'] not in ['nummod', 'nummod:gov']:
                                        ch['DOM'] = child_token['ID']

        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                if word.attrib.get('LEMMA', '') in ['сколько', 'несколько'] and word.attrib.get('LINK', 'EMPTY')  in ['присвяз', 'соч-союзн']:
                    word.attrib['FEAT'] = 'NUM'
                if word.attrib.get('LEMMA', 'EMPTY') in lemmas_to_check and word.attrib.get('LINK', 'EMPTY') not in ['огранич', 'присвяз', 'соч-союзн', 'nummod', 'nummod:gov']:
                    children = get_children_attrib(sent, word.attrib['ID'])
                    if len(children) != 0:
                        if word.attrib.get('LINK', '') == 'предик' and word.attrib.get('LEMMA', '') != 'сколько':
                            pass # do nothing
                        elif word.attrib['DOM'] == '_root' or word.attrib['LINK']in ['вспом']:

                            if word.attrib['DOM'] == '_root' and any(ch['LINK'] == '1-компл' for ch in children) and 'СРАВ' not in word.attrib.get('FEAT', ''):
                                if (ifname + '_' + sent.attrib['ID']).split('/')[1] in ['uppsalaBitov_3.xml_454', '2007Pylesos.xml_77',
                                                                                        '2009Nebesnye_formatsii.xml_8', '2012Chto_delat_posle_24_dekabrya.xml_9',
                                                                                        '2003Nelzya_sebya_delit.xml_49', '2006Dobretsov.xml_57', 
                                                                                        '2011Mariam_Petrosyan.xml_296', '2003Lyubit_drakona.xml_122',
                                                                                        'uppsalaKorp_220.xml_112', '2005Sluzhit_by_rad.xml_82',
                                                                                        '2009Final_Ligi_Chempionov.xml_30', '2003Zhores.xml_336',
                                                                                        '2003Opasnaya_blizost.xml_74']:

                                    for ch in children:
                                        if ch['LINK'] == '1-компл':
                                            ch['DOM'] = word.attrib['DOM']
                                            for child in children:
                                                if child['ID'] != ch['ID'] and child['LINK'] not in {'огранич', 'колич-огран'}:
                                                    child['DOM'] = ch['ID']
                                            word.attrib['DOM'] = ch['ID']
                                            del ch['LINK']
                                            word.attrib['LINK'] = 'nummod:gov'
                                    word.attrib['FEAT'] = 'NUM'
                            else:
                                pass
                        elif word.attrib.get('LINK', '') == 'предик' and word.attrib.get('LEMMA', '') in ['сколько', 'несколько']:
                            if len(children) == 1 and ('S' in children[0]['FEAT'] or 'A ' in children[0]['FEAT']):
                                children[0]['LINK'] = 'предик'
                                children[0]['DOM'] = word.attrib['DOM']
                                word.attrib['DOM'] = children[0]['ID']
                                word.attrib['LINK'] = 'nummod:gov'
                                word.attrib['FEAT'] = 'NUM'

                            else:
                                for child in children:
                                    if 'S ' in child['FEAT']:
                                        child['LINK'] = 'предик'
                                        child['DOM'] = word.attrib['DOM']
                                        word.attrib['DOM'] = child['ID']
                                        word.attrib['LINK'] = 'nummod:gov'
                                        word.attrib['FEAT'] = 'NUM'
                                        if len(children) == 3:
                                            for ch in children:
                                                if ch['LINK'] == 'соч-союзн':
                                                    ch['DOM'] = child['ID']

                        elif all(ch['LINK'] in ['огранич', 'колич-огран', 'вспом', 'case'] for ch in children):
                            pass # don't need to do anything
                        
                        elif word.attrib.get('LINK', '') == 'обст':
                            if word.attrib.get('LEMMA', '') == 'немного':
                                pass # do nothing
                            elif word.attrib['LEMMA'] in ['больше', 'столько', 'мало', 'много']:
                                if len(children) == 1:
                                    if word.attrib['LEMMA'] in ['мало', 'много']:
                                        malo = True
                                    else:
                                        malo = False
                                    if children[0]['FEAT'].strip().split(' ')[0] in ['S']: #TODO проверить - может быть тут еще надо поменять связь
                                        children[0]['DOM'] = word.attrib['DOM']
                                        word.attrib['DOM'] = children[0]['ID']
                                        if malo and children[0]['LINK'] != 'предик': 
                                            word.attrib['LINK'] = 'nummod:gov'
                                            word.attrib['FEAT'] = 'NUM'
                                    elif children[0]['FEAT'].strip().split(' ')[0] not in ['CONJ', 'A', 'ADV', 'V']:
                                        print('Unaccounted entry (FEAT):', file=sys.stderr)
                                else:
                                    for ch in children:
                                        if ch['LINK'] == 'сравнит':
                                            if ch['FEAT'].strip().split(' ')[0] in ['S']:
                                                ch['DOM'] = word.attrib['DOM']
                                                word.attrib['DOM'] = ch['ID']
                                            break
                            elif word.attrib['LEMMA'] == 'меньше':
                                pass
                            elif word.attrib['LEMMA'] in ['сколько', 'несколько']:
                                for ch in children:
                                    if ch['LINK'] == '1-компл':
                                        ch['LINK'] = word.attrib['LINK']
                                        ch['DOM'] = word.attrib['DOM']
                                        word.attrib['DOM'] = ch['ID']
                                        word.attrib['LINK'] = 'nummod:gov'
                                        word.attrib['FEAT'] = 'NUM'
                                        break
                                else:
                                    print('Unaccounted entry (FEAT):', file=sys.stderr)
            
                            elif word.attrib['LEMMA'] in ['более', 'менее']:
                                for ch in children:
                                    if ch['FEAT'].strip().split(' ')[0] in ['S'] and ch['LINK'] != 'атриб':
                                        ch['DOM'] = word.attrib['DOM']
                                        word.attrib['DOM'] = ch['ID']
                                        for chld in children:
                                            if chld['ID'] != ch['ID'] and chld['LINK'] not in ['огранич']:
                                                chld['DOM'] = ch['ID']

                        elif word.attrib.get('LINK', '').endswith('компл'):# перевесить на существительное. Сколько -> NUM?
                            if (len(children) == 1 
                                and children[0]['FEAT'].strip().split(' ')[0] in ['S', 'A'] 
                                and children[0]['LINK'] not in ['атриб', 'предик']):
                                children[0]['DOM'] = word.attrib['DOM']
                                word.attrib['DOM'] = children[0]['ID']
                                if word.attrib['LEMMA'] in ['сколько', 'несколько']:
                                    word.attrib['LINK'] = 'nummod:gov'
                                    word.attrib['FEAT'] = 'NUM'
                            elif (len(children) == 1 
                                and children[0]['FEAT'].strip().split(' ')[0] in ['CONJ', 'V']):
                                pass

                            elif len(children) == 1:
                                if ifname.endswith('2003Vyzhivshii_kamikadze.xml') and sent.attrib['ID'] == '257':
                                    children[0]['DOM'] = word.attrib['DOM']
                                    word.attrib['DOM'] = children[0]['ID']
                                if ifname.endswith('2003Artist_mimansa.xml') and sent.attrib['ID'] == '330':
                                    word.attrib['FEAT'] = 'NUM'
                            elif (len(children) > 1):
                                candidate_1 = None
                                candidate_2 = None
                                found_predic = False
                                for chld in children:
                                    if chld['LINK'] == 'предик':
                                        found_predic = True
                                        break
                                    if chld['LINK'] == '1-компл':
                                        candidate_1 = chld
                                        break
                                    if chld['LINK'] == 'сравнит':
                                        candidate_2 = chld

                                if not found_predic:
                                    if candidate_1 is not None:
                                        candidate_1['DOM'] = word.attrib['DOM']
                                        word.attrib['DOM'] = candidate_1['ID']
                                    elif candidate_2 is not None:
                                        candidate_2['DOM'] = word.attrib['DOM']
                                        word.attrib['DOM'] = candidate_2['ID']

                                    if word.attrib['LEMMA'] in ['сколько', 'несколько']:
                                        word.attrib['LINK'] = 'nummod:gov'
                                        word.attrib['FEAT'] = 'NUM'
                            else:
                                print('Unaccounted entry (FEAT):', file=sys.stderr)

                        elif word.attrib.get('LINK', '') == 'вводн': # there is no 'сколько', 'несколько' here
                            for chld in children:
                                if chld['FEAT'].strip().split(' ')[0] == 'S':
                                    chld['DOM'] = word.attrib['DOM']
                                    word.attrib['DOM'] = chld['ID']

                        elif word.attrib.get('LINK', '') == 'подч-союзн':
                            word.attrib['FEAT'] = 'NUM'
                            if any(ch['LINK'] == 'предик' for ch in children):
                                pass
                            else:
                                for ch in children:
                                    if ch['LINK'] == '1-компл':
                                        ch['DOM'] = word.attrib['DOM']
                                        for child in children:
                                            if child['ID'] != ch['ID'] and child['LINK'] not in {'огранич', 'колич-огран'}:
                                                child['DOM'] = ch['ID']
                                        word.attrib['DOM'] = ch['ID']
                                        ch['LINK'] = word.attrib['LINK']
                                        word.attrib['LINK'] = 'nummod:gov'


                        elif word.attrib.get('LINK', '') in [
                            'соотнос', 'кратн', 'электив', 'аппоз',
                            'эксплет', 'атриб', 'релят', 'квазиагент',
                            'колич-копред', 'разъяснит', 'сент-соч', 
                            'сравнит', 'изъясн', 'компл-аппоз']:
                            pass


                        elif word.attrib.get('LINK', '') == 'уточн':
                            for ch in children:
                                if ch['LINK'] == 'сравнит':
                                    ch['DOM'] = word.attrib['DOM']
                                    for child in children:
                                        if child['ID'] != ch['ID'] and child['LINK'] not in {'огранич', 'колич-огран'}:
                                            child['DOM'] = ch['ID']
                                    word.attrib['DOM'] = ch['ID']

                        elif word.attrib.get('LINK', '') in ['длительн']:
                            if any(ch['LINK'] == '1-компл' for ch in children):
                                for ch in children:
                                    if ch['LINK'] == '1-компл':
                                        ch['DOM'] = word.attrib['DOM']
                                        for child in children:
                                            if child['ID'] != ch['ID'] and child['LINK'] not in {'огранич', 'колич-огран'}:
                                                child['DOM'] = ch['ID']
                                        word.attrib['DOM'] = ch['ID']
                                        ch['LINK'] = word.attrib['LINK']
                                        word.attrib['LINK'] = 'nummod:gov'
                                word.attrib['FEAT'] = 'NUM'
                            else:
                                for ch in children:
                                    if ch['LINK'] == 'сравнит':
                                        ch['DOM'] = word.attrib['DOM']
                                        for child in children:
                                            if child['ID'] != ch['ID'] and child['LINK'] not in {'огранич', 'колич-огран'}:
                                                child['DOM'] = ch['ID']
                                        word.attrib['DOM'] = ch['ID']

                        elif word.attrib.get('LINK', '') in ['примыкат', 'колич-огран']:
                            if any(ch['LINK'] == 'сравнит' for ch in children) and not any(ch['LINK'] == '1-компл' for ch in children):
                                pass
                            else:
                                if word.attrib.get('LINK', '') == 'примыкат' and word.attrib.get('LEMMA', '') == 'более':
                                    pass # one exception

                                for ch in children:
                                    if ch['LINK'] == '1-компл':
                                        ch['DOM'] = word.attrib['DOM']
                                        for child in children:
                                            if child['ID'] != ch['ID'] and child['LINK'] not in {'огранич', 'колич-огран'}:
                                                child['DOM'] = ch['ID']
                                        word.attrib['DOM'] = ch['ID']
                                        ch['LINK'] = word.attrib['LINK']
                                        word.attrib['LINK'] = 'nummod:gov'
                                word.attrib['FEAT'] = 'NUM'

                        elif word.attrib.get('LINK', '') == 'сравн-союзн':
                            if any(ch['LINK'] == 'предик' for ch in children) or any(ch['LINK'] == 'разъяснит' for ch in children):
                                pass
                            else:

                                for ch in children:
                                    if ch['LINK'] == '1-компл':
                                        ch['DOM'] = word.attrib['DOM']
                                        for child in children:
                                            if child['ID'] != ch['ID'] and child['LINK'] not in {'огранич', 'колич-огран'}:
                                                child['DOM'] = ch['ID']
                                        word.attrib['DOM'] = ch['ID']
                                        ch['LINK'] = word.attrib['LINK']
                                        word.attrib['LINK'] = 'nummod:gov'
                                word.attrib['FEAT'] = 'NUM'

                        elif word.attrib.get('LINK', '') == 'сочин':
                            if any(ch['LINK'] == '1-компл' for ch in children) and 'СРАВ' not in word.attrib.get('FEAT', ''):
                                for ch in children:
                                    if ch['LINK'] == '1-компл':
                                        ch['DOM'] = word.attrib['DOM']
                                        for child in children:
                                            if child['ID'] != ch['ID'] and child['LINK'] not in {'огранич', 'колич-огран'}:
                                                child['DOM'] = ch['ID']
                                        word.attrib['DOM'] = ch['ID']
                                        ch['LINK'] = word.attrib['LINK']
                                        word.attrib['LINK'] = 'nummod:gov'
                                word.attrib['FEAT'] = 'NUM'

                            else:
                                pass

                        else:
                            #for_debug_rels[word.attrib['LINK']] += 1
                            print('Error in numerals.py: missing condition')
                            print(word.attrib.get('ID', ''), word.attrib.get('LINK', ''), word.attrib.get('LEMMA', ''), word.attrib.get('FEAT', ''), file=sys.stderr)
                            print(children, file=sys.stderr)
                            print(ifname + '_' + sent.attrib['ID'], file=sys.stderr)
                            print(*[(token.attrib.get('ID', 'EMPTY'), token.text, token.attrib.get('DOM', 'EMPTY'), token.attrib.get('FEAT', 'EMPTY'), token.attrib.get('LINK', 'EMPTY'), token.tail) for token in sent], file=sys.stderr, sep='\n')
                            print('***', file=sys.stderr)
                            #count += 1


        #for sent in root[-1].findall('S'):
        #    for word in sent.findall('W'):
        #        if word.attrib.get('LINK', 'EMPTY') in ['nummod', 'nummod:gov']:
        #            print(word.attrib.get('ID', ''), word.attrib.get('LINK', ''), word.attrib.get('FEAT', ''), file=sys.stderr)
        #            print(*[(token.attrib.get('ID', 'EMPTY'), token.text, token.attrib.get('DOM', 'EMPTY'), token.attrib.get('FEAT', 'EMPTY'), token.attrib.get('LINK', 'EMPTY'), token.tail) for token in sent], file=sys.stderr, sep='\n')
        #            print('***', file=sys.stderr)
        #            continue

        tree.write(ofname, encoding="UTF-8")
    #print(count)
    #for elem in for_debug_rels:
    #    print(elem, for_debug_rels[elem])
    return

def main(ifolder, ofolder):
	munch(*get_fnames(ifolder, ofolder, '.xml', '.xml'))
	print('6: numerals.py completed')
    
if __name__ == "__main__":
    main(ifolder, ofolder)
