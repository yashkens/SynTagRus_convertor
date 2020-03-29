#!/usr/bin/env python3

#TODO: This script must be rewritten (non-optimal algorithm, does not cover all the cases).

""" Processes numerals:
1. fix lemmas 'назад', 'со стороны', 'внутри', 'изнутри' (part 1)
2. fix lemmas 'МИЛЛИАРД', 'МИЛЛИОН', 'ТРИЛЛИОН', 'ТЫСЯЧА': nummod:gov + change the head from"миллион" to its dependent (part 2)
3. fix lemmas 'больше', 'меньше', 'более', 'менее', 'столько', 'сколько', 'предостаточно', 'достаточно', 'мало', 'много', 'немало', 'немного' (part 3)
"""

import os

import lxml.etree as ET

from util import get_fnames, get_info, get_children_attrib

lemmas_adv = ['назад', 'со стороны', 'внутри', 'изнутри']
# collocations for lemmas
# 'миллионы лет' is not transformed
# МИЛЛИАРД
lemmas1 = ['ТОННА', 'НОМЕР', 'АТОМ', 'ДОЛЛАР-ЗНАК', 'ОТКАТ', 'СТОК', 'ДРУГ', 'КВТ/Ч', 'ТУЗЕМЕЦ', 'СТРОИТЕЛЬ', 'ТРАНЗИСТОР', 'ФРАГМЕНТ', 'СЕАНС', 'ДОМ', 'ПОЖАРНЫЙ', 'ПАЛОМНИК', 'ПЕРЕСЕЛЕНЕЦ', 'РЕБЕНОК', 'ТОННОКИЛОМЕТР', 'СЕМЬЯ', 'СТОРОННИК', 'ПАРТИЗАН','ДИССЕРТАЦИЯ', 'ШАГ', 'ЖИТЕЛЬ', 'МОЛОДЬ', 'КУБОМЕТР', 'ЧАСТЬ']
# МИЛЛИОН
lemmas2 = ['ДОЛЛАР', 'РУБЛЬ', 'МАРКА', 'ФУНТ', 'РЕЙХСМАРКА', 'ЕВРО', 'ДРАМ', 'ДИРХАМ', 'ЧЕЛОВЕК', 'ДУКАТ', 'ЭКЗЕМПЛЯР', 'ИСК', 'ЮАНЬ', 'ГОЛОВА', 'ТАН', 'НКО', 'ПАЧКА', 'АКТИВИСТ', 'ПРИВИВКА', 'КРАСНОАРМЕЕЦ', 'НАИМЕНОВАНИЕ', 'БОРЕЦ', 'КИЛОМЕТР', 'ПИСАТЕЛЬ', 'ГОЛОВА', 'ПАМЯТНИК', 'ЖЕРТВОВАТЕЛЬ', 'КРЕДИТ', 'ДЕТЕКТОР', 'ПОЗИЦИЯ', 'БАРРЕЛЬ', 'ДОЛЛАР-ЗНАК', 'ЕВРО-ЗНАК', 'ПОЛЬЗОВАТЕЛЬ', 'РАЗ', 'ДВОР', 'ПУД', 'МИЛЛИОНЕР', 'САЙТ', 'КОМПЬЮТЕР', 'МЕСТО', 'СПЕЦИАЛИСТ', 'ЧАС', 'СОЛНЫШКО', 'СОГРАЖДАНИН', 'СЛАВЯНИН', 'МЕТР', 'АМЕРИКАНЕЦ', 'НАРКОЗАВИСИМЫЙ', 'ТОЧКА', 'СЛУЧАЙ', 'КУБ', 'НЕДОДЕЛКА', 'ПРИЕЗЖИЙ', 'ПРИЕМНИК', 'ПАСТБИЩЕ', 'ИМПУЛЬС', 'ГОЛОС', 'РУБЛИК', 'ЗАЛОГ', 'АВАНС', 'ЗАКЛЮЧЕННЫЙ', 'КОММУНИСТ', 'МАРКСИСТ', 'ИЗБИРАТЕЛЬ', 'ПЕНСИОНЕР', 'ГРАЖДАНИН', 'ТУРИСТ', 'ПРЕДПРИЯТИЕ', 'НЕМЕЦ', 'ТОННА', 'ПОСЫЛКА', 'РАБОЧИЙ', 'РОССИЯНИН', 'ЗРИТЕЛЬ', 'СОГРАЖДАНИН', 'СТУДЕНТ', 'ЗАВОДИК', 'НАНОРОБОТ', 'АТОМ', 'МОЛЕКУЛА', 'КАДР', 'КРЕСТЬЯНИН', 'ДЕСЯТИНА', 'СОЛДАТ', 'БОЛЬНОЙ', 'ЖИЗНЬ', 'КИТАЕЦ', 'ПОТРЕБИТЕЛЬ', 'СЛОВО', 'ПЛЕННЫЙ', 'УБИТЫЙ', 'НОМЕР', 'ЦВЕТЫ', 'ЛИТР', 'УЧАЩИЙСЯ', 'ЛЕНИНГРАДЕЦ', 'МНЕНИЕ', 'СОМНЕНИЕ', 'БАЙТ']
# ТРИЛЛИОН
lemmas3 = ['РЕПЛИКАТОР', 'ПАССАЖИРОКИЛОМЕТР', 'ОВЦА', 'КОРОВА', 'ВЕРБЛЮД', 'МЯСНИК', 'ЯЗЫК', 'СИЛА', 'БОЕЦ', 'СОТРУДНИК', 'ТАБЛЕТКА', 'СРЕДСТВО', 'ЗВОНОК', 'ДЕНЬГИ', 'ЮНОША', 'ОТВЕРСТИЕ', 'НАСОС', 'АТМОСФЕРА', 'ГРАДУС', 'ШТУКА', 'РУКА']
# ТЫСЯЧА    
lemmas4 = ['НОМЕР', 'МИКРОПОСТАВЩИК', 'СОЕДИНЕНИЕ', 'ДОРОГА', 'ОБРАЗЕЦ', 'ГОД', 'ПОКОЛЕНИЕ', 'РАЗ', 'ПРОГРАММИСТ', 'БУТЫЛКА', 'ТЕЛЕМАРКЕР', 'ДОКУМЕНТ', 'ХОЗЯЙСТВО', 'МОТОРЧИК', 'ВАКАНСИЯ', 'ПРОБА', 'ЧЛЕН', 'ДЕТАЛЬ', 'АБОНЕНТ', 'ЛИНИЯ', 'ВЫПУСКНИК', 'АСПИРАНТ', 'ПОКОЛЕНИЕ', 'ОБИТАТЕЛЬ', 'КОЛОДНИК', 'МЕШОК', 'ЖЕНЩИНА', 'ВИД', 'ФЕРМЕР', 'ФУНКЦИЯ', 'МИНУТА', 'УБИЙСТВО', 'АБОНЕНТ', 'ДОЛЖНОСТЬ', 'ПРИЗЫВНИК', 'НАСЕЛЕНИЕ', 'СХЕМА', 'ЭКСПОНАТ', 'МАШИНА', 'ПРЕПАРАТ', 'ПОСЕТИТЕЛЬ', 'ПОЗИЦИЯ', 'ДРУГ', 'ВЕДЬМА', 'ПОСТРАДАВШИЙ', 'ЭКСПЕРИМЕНТ', 'НОГА', 'СТРАНИЦА', 'ОФИЦЕР', 'СНИМОК', 'РАБОТНИК', 'ЖИВОТНОЕ', 'БАНК', 'ПАССАЖИР', 'ПАЦИЕНТ', 'ДАТЧИК', 'БЮДЖЕТ', 'ДОМОХОЗЯЙСТВО', 'СУДЬБА', 'ГЕКТАР', 'ТАБЛЕТКА', 'БЛАНК', 'ПРОДУКТ', 'ССЫЛКА', 'ОРГАНИЗАЦИЯ', 'НПО', 'ЛЮДИ', 'ПРЕДПРИЯТИЕ', 'ШКОЛА', 'ТРАНСПОРТНИК', 'СПОРТСМЕН', 'СПОСОБ', 'ЛАБОРАТОРИЯ', 'МОЛЕКУЛА', 'СВИНЬЯ', 'РАБОТНИК', 'ЧИТАТЕЛЬ', 'ЗАКЛЮЧЕННЫЙ', 'АГРОНОМ', 'СТАНЦИЯ', 'ПОЛЕ', 'ОБЩЕСТВО', 'ТРУП', 'ГОЛОС', 'УБИТЫЙ', 'СОЛДАТ', 'ИНФАРКТ', 'БЕЖЕНЕЦ', 'ВОЕННОСЛУЖАЩИЙ', 'ЗАВЕДЕНИЕ', 'ЖИЗНЬ', 'ГЕКТАР', 'КУБ', 'КУБОМЕТР', 'РАБОЧИЙ', 'СТАНОК', 'РАЗРЯД', 'МОЛЕКУЛА', 'МЕТР']
lemmas = lemmas1 + lemmas2 + lemmas3 + lemmas4
lemmas = [elem.lower() for elem in lemmas]
go_away = ['сотня', 'десяток', 'четверть']
fix = ['миллиард', 'миллион', 'триллион', 'тысяча', 'биллион']
lemmas_compare = ['больше', 'меньше', 'более', 'менее', 'столько', 'сколько', 'предостаточно', 'достаточно', 'мало', 'много', 'немало', 'немного']
conjrels = ['сочин', 'соч-союзн', 'сент-соч', 'сравн-союзн', 'подч-союзн', 'инф-союзн']

def munch(ifiles, ofiles):
    # part 1
    count = 0
    for ifname, ofname in zip(ifiles, ofiles):
        tree = ET.parse(ifname)
        root = tree.getroot()
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):                                               
                if word.attrib.get('FEAT', 'EMPTY').split()[0] == 'PR' and word.attrib.get('LEMMA', 'EMPTY') in lemmas_adv:
                    count += 1
                    word.attrib['FEAT'] = 'ADV'
                    if 'LINK' in word.attrib and word.attrib['LINK'] not in conjrels: 
                        word.attrib['LINK'] = 'advmod'

        # part 2
        # (the code does not cover all cases on the first iteration,
        # therefore this part needs to be repeated twice)
        for r in range(2):
            for sent in root[-1].findall('S'):
                for candidate in sent.findall('W'):                                               
                    if candidate.attrib.get('LEMMA', 'EMPTY') in fix and 'МН' not in candidate.attrib['FEAT']:
                        link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(candidate, sent)
                        is_root = (candidate.attrib.get('DOM', 'EMPTY') == '_root')
                        ch = candidate.attrib['ID']
                        parent = candidate.attrib['DOM']
                        away = False
                        do_not_change = False
                        deprel = ''
                        if 'LINK' in candidate.attrib:
                            deprel = candidate.attrib['LINK']
                        if 'LINK' in candidate.attrib and candidate.attrib['LINK'] in conjrels:
                            do_not_change = True
                        for token in sent.findall('W'):
                            if token.attrib.get('ID','EMPTY') == parent and token.attrib.get('LEMMA','EMPTY') in go_away:
                                away = True
                        if away:
                            continue
                        children = get_children_attrib(sent, ch)
                        if len(children) == 0:
                            ch_parent = get_children_attrib(sent, parent)
                            check = 0
                            for elem in ch_parent:
                                if elem['FEAT'].split()[0] == 'NUM':
                                    check += 1
                            if check == 1:
                                for elem in ch_parent:
                                    if elem['FEAT'].split()[0] == 'NUM':
                                        elem['DOM'] = ch
                                        elem['LINK'] = 'compound'
                                        if not do_not_change:
                                            candidate.attrib['LINK'] = 'nummod:gov'
                        if len(children) == 1 and children[0]['FEAT'].split()[0] == 'NUM': #only one and it is NUM                    
                            children[0]['LINK'] = 'compound'
                            if not do_not_change:
                                candidate.attrib['LINK'] = 'nummod:gov'
                        if any(child['FEAT'].split()[0] == 'NUM' for child in children) and len(children) > 1: # NUM among others
                            if not do_not_change:
                                candidate.attrib['LINK'] = 'nummod:gov'
                            for elem in children:
                                if elem['FEAT'].split()[0] == 'NUM':
                                    elem['LINK'] = 'compound'
                        if len(children) == 1 and children[0]['FEAT'].split()[0] == 'A':
                            continue
                        if any(child['FEAT'].split()[0] == 'S' for child in children):
                            list_of_nouns = []
                            numgov = False
                            for elem in children:
                                genetive = False
                                if 'РОД' in elem['FEAT']:
                                    genetive = True
                                if elem['FEAT'].split()[0] == 'S' and elem['LEMMA'] in lemmas and genetive:
                                    list_of_nouns.append(elem)
                                if elem['FEAT'].split()[0] == 'NUM':
                                    elem['LINK'] = 'compound'
                                    numgov = True
                            if len(list_of_nouns) > 0:
                                trace = list_of_nouns[0]['ID']
                                for elem in children:
                                    if elem['ID'] == trace:
                                        if is_root:
                                            elem['DOM'] = '_root'
                                            candidate.attrib['LINK'] = elem['LINK']
                                            del elem['LINK']
                                        else:
                                            elem['DOM'] = parent
                                            if deprel != '':
                                                elem['LINK'] = deprel
                                            else:
                                                print(candidate.attrib, elem)
                                        candidate.attrib['DOM'] = elem['ID']
                                        if numgov:
                                            if not do_not_change:
                                                candidate.attrib['LINK'] = 'nummod:gov'
                                        for elem in children:
                                            if elem['ID'] != trace and elem['FEAT'].split()[0] != 'NUM':
                                                elem['DOM'] = trace

        # part 3
        for sent in root[-1].findall('S'):
            for word in sent.findall('W'):
                link, pos, feats, head_token, head_pos, head_feats, head_root = get_info(word, sent)
                if link not in ['предик'] + conjrels and word.attrib['DOM'] != '_root':
                    if 'NUM' in pos and word.attrib['LEMMA'] == 'один': # один
                        word.attrib['LINK'] = 'nummod'
                    if link != 'EMPTY' and 'NUM' in pos:
                        if 'ВИН' in feats or 'ИМ' in feats:
                            word.attrib['LINK'] = 'nummod:gov'
                        else:
                            word.attrib['LINK'] = 'nummod'
                    if word.attrib.get('LEMMA','EMPTY') in lemmas_compare:
                        children = get_children_attrib(sent, word.attrib['ID'])
                        for elem in children:
                            if 'FEAT' in elem and elem['FEAT'].startswith('S ') and 'РОД' in elem['FEAT']:
                                grandchildren = get_children_attrib(sent, elem['ID'])
                                if not any('PR' in grchild['FEAT'] for grchild in grandchildren):
                                    elem['DOM'] = word.attrib['DOM']
                                    word.attrib['DOM'] = elem['ID']
                                    word.attrib['LINK'] = 'nummod:gov'
        tree.write(ofname, encoding="UTF-8")
    return

def main(ifolder, ofolder):
	munch(*get_fnames(ifolder, ofolder, '.xml', '.xml'))
	print('6: numerals.py completed')
    
if __name__ == "__main__":
    main(ifolder, ofolder)
