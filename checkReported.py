#!/usr/bin/env python3

""" check reported speech """

import os
import re
import sys
import csv

from util import import_xml_lib, get_fnames, get_children
ET = import_xml_lib()

ifolder = 'FixRegular'
ofolder = 'Reported'

fix_deprel = ['2005Stranitsy_voennoi_istorii.xml 169', '2009Stipendiat.xml 78', '2007Grechko.xml 217',
              '2013Nauka.xml 26', '2008Kobzon.xml 17', '2014Kulturnye_olimpiitsy.xml 83',
              '2010Khudozhestvennaya_gimnastika.xml 79', '2003Dvoe_v_dekabre.xml 123',
              '2013Martovskaya_revolyutsiya.xml 85', '2013Poslednii_dovod_issledovatelya.xml 175',
              'uppsalaKorp_726.xml 4', 'uppsalaGrekova_1.xml 234', '2008Nekommercheskie_organizatsii.xml 77',
              '2009Prognoz_inflyatsii.xml 113', '2015Gorbachov.xml 95', '2003Artist_mimansa.xml 206', 
              '2003Artist_mimansa.xml 221', '2003Somnambula_v_tumane.xml 273', 'uppsalaKorp_624.xml 6',
              '2003Ochishchenie_Olkhona.xml 61', 'uppsalaGrekova_2.xml 256', 'uppsalaBitov_1.xml 51', 
              'uppsalaGrekova_3.xml 42', 'uppsalaGrekova_3.xml 53', 'uppsalaGrekova_3.xml 162', 
              '2011Gde_zhe_Shliman.xml 50', '2005Voennaya_doktrina.xml 56', '2012Stalin_vozvrashchyalsya.xml 30',
              '2003Lyubit_drakona.xml 94', '2003A_on_myatezhnyi.xml 39', 'uppsalaKorp_722.xml 26',
              '2011Mariam_Petrosyan.xml 136', '2007Terpenie_lopnulo.xml 28', 'uppsalaGrekova_2.xml 122',
              'uppsalaGrekova_2.xml 190', '2013Kooperativ_Lavka.xml 88', '2014Vspolokhi-1.xml 252',
              'uppsalaGrekova_3.xml 33', '2015iz_predanii.xml 60', 'uppsalaNagibin_3.xml 40', '2013Doktor_Z.xml 130',
              '2014Na_dvukh_voinakh_2.xml 106']
ignore = ['2013Nauka.xml 133', 'uppsalaBitov_3.xml 156', '2005Tokarskaya.xml 8', '2003Internet-zavisimost.xml 10',
          '2014Vladimir_Vladimirovich.xml 221', '2003Dvoe_v_dekabre.xml 87', '2013Dvadtsat_let_spustya.xml 130',
          '2009Obrazovanie_-_novaya_model.xml 24', 'uppsalaNagibin_1.xml 262', 'newsYa_30.xml 23',
          '2003Krupnaya_kala.xml 31', '2003Chto_doktor_propisal.xml 67', '2013Algoritm.xml 55', '2009MGU.xml 98',
          '2009Informatsionnoe_obshchestvo.xml 56', '2006Lunnye_kamni.xml 27', '2008Molodezh.xml 6', '2011Formula-1.xml 198',
          '2011Formula-1.xml 199', '2011Formula-1.xml 390', '2003Zemlya_naiznanku.xml 62', '2003Chelovek_oshibka_prirody.xml 53',
          '2011Chto_takoe_ukhomor.xml 9', '2003Igrushki_bogov.xml 94', 'uppsalaKorp_705.xml 27', '2014Vysota.xml 73',
          '2011Nano.xml 27', '2003Armeniya.xml 33', 'uppsalaGrekova_2.xml 461', '2006Dobretsov.xml 143', '2006Dobretsov.xml 68',
          'uppsalaGrekova_3.xml 422', '2012Galileo_Galilei.xml 371', '2010Tsilindry_Faraona.xml 134', '2003Uidya_iz_skazki.xml 6', 
          '2010Spasenie_evro.xml 66', '2015iz_predanii.xml 107', 'uppsalaBitov_1.xml 111', 'uppsalaBitov_1.xml 144',
          '2003Bez_epokhi.xml 86', '2010Mozgi_naprokat.xml 137', '2003Bessonnitsa.xml 7', '2007Lesorub.xml 24',
          '2011Grisha_Perelman_devyatyi_genii.xml 179', '2011Chto_takoe_ukhomor.xml 15', 'newsYa_26.xml 40', '2009Voina_vozrastov.xml 6',
          '2012Poslednie_russkie.xml 113', '2007Podkormlennyi_natsizm.xml 164', '2014Vspolokhi-1.xml 255', '2009Letayushchaya_tarelka.xml 12',
          'uppsalaNagibin_1.xml 10', '2009Interviyu_Medvedeva.xml 78', '2010Mars_3.xml 122', '2011Mariam_Petrosyan.xml 159']
patches = {'uppsalaGrekova_3.xml 12': {'2': {'DOM': '_root'},
                                       '3': {'DOM': '2', 'LINK': 'parataxis'}},
           'uppsalaGrekova_3.xml 269': {'3': {'DOM': '_root'},
                                        '4': {'DOM': '3', 'LINK': 'parataxis'}},
           '2009Interviyu_Medvedeva.xml 78': {'1': {'DOM': '_root'},
                                              '12': {'DOM': '1', 'LINK': 'parataxis'}},
           '2012Poslednie_russkie.xml 235': {'5': {'DOM': '3', 'LINK': 'parataxis'}, #check 2003Prilet_ptits.xml 30 2009EGE.xml 23
                                             '8': {'DOM': '5', 'LINK': 'parataxis'}},
           '2011Mariam_Petrosyan.xml 159': {'8': {'LINK': 'parataxis'}, # and thiss
                                            '23': {'LINK': 'parataxis'},},
           'uppsalaBitov_1.xml 226': {'1': {'DOM': '_root'},
                                      '3': {'DOM': '1', 'LINK': 'parataxis'}},
           '2010Mars_3.xml 122': {'19': {'DOM': '17'}},
           '2014Granin.xml 61': {'1': {'DOM': '6', 'LINK': 'parataxis'},
                                 '2': {'DOM': '6'},
                                 '6': {'DOM': '_root'}
                                },
           '2003Bez_epokhi.xml 36': {'1': {'DOM': '_root'},
                                     '3': {'DOM': '1', 'LINK': 'parataxis'},
                                     '5': {'DOM': '3', 'LINK': 'parataxis'}},
           'uppsalaGrekova_1.xml 180': {'1': {'DOM': '_root'},
                                        '2': {'DOM': '1', 'LINK': 'parataxis'},
                                        '4': {'DOM': '1', 'LINK': 'conj'}
                                       },
           'uppsalaNagibin_1.xml 10': {'11': {'LINK': 'parataxis'},
                                       '19': {'LINK': 'parataxis'}
                                      },
           'uppsalaNagibin_1.xml 123': {'1': {'DOM': '_root'},
                                        '6': {'DOM': '1', 'LINK': 'parataxis'}
                                       },
           'uppsalaNagibin_1.xml 199': {'2': {'DOM': '_root'},
                                        '3': {'DOM': '2', 'LINK': 'parataxis'}
                                       },
           'uppsalaBitov_3.xml 472': {'3': {'DOM': '_root'},
                                      '4': {'DOM': '3', 'LINK': 'parataxis'},
                                     },
           'uppsalaKorp_606.xml 9': {'2': {'DOM': '5', 'LINK': 'parataxis'},
                                     '5': {'DOM': '_root'}
                                    },
           '2013Ukroshchenie_stroptivogo_naukograda.xml 116': {'1': {'DOM': '2'}},
           '2005Mamleev_svadba.xml 191': {'3': {'DOM': '4'},
                                          '4': {'DOM': '_root'},
                                          '6': {'DOM': '4', 'LINK': 'parataxis'}
                                         },
           '2014Vysota.xml 192': {'1': {'DOM': '_root'},
                                  '4': {'DOM': '1', 'LINK': 'parataxis'}
                                 },
           'uppsalaNagibin_2.xml 165': {'5': {'DOM': '_root'},
                                        '8': {'DOM': '5', 'LINK': 'parataxis'},
                                        '10': {'DOM': '5'}
                                       },
           '2012Otluchenie_tserkvi.xml 74': {'9': {'LINK': 'parataxis'},
                                             '17': {'LINK': 'parataxis'}
                                            },
           '2003Artist_mimansa.xml 273': {'1': {'DOM': '_root'},
                                          '4': {'DOM': '1', 'LINK': 'parataxis'},
                                          '16': {'DOM': '15'}
                                         },
           '2003Artist_mimansa.xml 244': {'2': {'DOM': '_root'},
                                          '4': {'DOM': '2'},
                                          '5': {'DOM': '2', 'LINK': 'parataxis'}
                                         }
          }

end_of_citation_re = re.compile('[,?!]')

whitespace_re = re.compile('\s')
terminal_punct_re = re.compile('[!?.,:]')
citation_punct_re = re.compile('["-]')

def patch_sentence(sentence, patch):
    for token in sentence.findall('W'):
        if token.attrib['ID'] in patch:
            for attr in patch[token.attrib['ID']]:
                token.attrib[attr] = patch[token.attrib['ID']][attr]
                if attr == 'DOM' and patch[token.attrib['ID']][attr] == '_root':
                    del token.attrib['LINK']

def munch(ifiles, ofiles):
    """
    Process all files in ifiles list.
    Output into ofiles list.
    """

    error_counter = 0

    for ifname, ofname in zip(ifiles, ofiles):

        tree = ET.parse(ifname)
        root = tree.getroot()
        for k, sentence in enumerate(root[-1].findall('S')):
            try:
                sentence_key = ' '.join((ifname.split('/')[-1], sentence.attrib['ID']))
            except KeyError:
                continue

            if sentence_key in patches:
                #print('\nPatching sentence:')
                #print_sentence(sentence)
                patch_sentence(sentence, patches[sentence_key])
                #print('\nPatched:')
                #print_sentence(sentence)
            elif sentence.text is not None and ('"' in sentence.text.strip() or '-' in sentence.text.strip()):
                symbol = sentence.text.strip().replace(' ', '')[0]
                for i, token in enumerate(sentence.findall('W')):
                    if (citation_punct_re.search(token.tail) is not None and
                        end_of_citation_re.search(token.tail) is not None and 
                        whitespace_re.sub('', token.tail) != '",' and
                        i + 1 != len(sentence.findall('W'))):

                        check_citation(sentence, symbol, i, token.attrib['ID'], ifname, start=True)
                        break
            else:
                for i, token in enumerate(sentence.findall('W')):
                    if ':"' in token.tail.strip().replace(' ', '').replace('\n', '') or ':-' in token.tail.strip().replace(' ', '').replace('\n', ''):
                        symbol = ''
                        check_citation(sentence, symbol, i, token.attrib['ID'], ifname, start=False)

            # let's see what we did
            error_counter += int(check_sentence(sentence, ifname, sentence_key))

        tree.write(ofname, encoding="UTF-8")

    print('Citation errors total:', error_counter)

switch = {'even': 'odd', 'odd': 'even'}

def print_sentence(sentence):
    print(sentence.text.lstrip())
    for token in sentence.findall('W'):
        print('{:20}{:>5}{:>5}{:>15}'.format(
                ''.join((token.text, token.tail.strip().replace('\n', ' ')
                                     if token.tail is not None else '')),
                token.attrib['ID'],
                token.attrib['DOM'].replace('_root', '0'),
                token.attrib.get('LINK', 'root')))

def check_sentence(sentence, file_name, sentence_key):

    if sentence_key in patches:
        return False

    have_some = False
    # first, check if the sentence starts with some suspicious
    # punctuation, maybe it's a candidate for citation-first
    if sentence.text is not None:
        starting_punct = whitespace_re.sub('', sentence.text)
        if starting_punct in {'-', '"', '-"'}:
            have_some = True

    if not have_some:
        # if not, check if there is anything suspicious later
        for token in sentence.findall('W'):
            if token.tail is not None:
                punct_after = whitespace_re.sub('', token.tail)
                if punct_after in {':"', ':-'}:
                    have_some = True
                    break

    if have_some:
        # okay, let's unravel it
        odd_index, even_index = [], []
        odd_ids, even_ids = [], []
        odd = [odd_index, odd_ids]
        even = [even_index, even_ids]
        part_counter = 0
        parts = {'odd': odd, 'even': even}
        current = 'odd'
        opening_quot_inside = False
        for i, token in enumerate(sentence.findall('W')):
            parts[current][0].append(i)
            parts[current][1].append(token.attrib['ID'])
            if token.tail is not None:
                punct_after = whitespace_re.sub('', token.tail)
                # check that there are both some of ["-] and [!?.,:]
                if punct_after == '"':
                    opening_quot_inside = True
                elif (citation_punct_re.search(punct_after) is not None and 
                      terminal_punct_re.search(punct_after) is not None and
                      not (opening_quot_inside and '"' in punct_after) and
                      punct_after != '",'):
                    # have to switch parts
                    current = switch[current]
                    part_counter += 1
                elif i == len(sentence.findall('W')) - 1:
                    part_counter += 1

        if part_counter > 1:
            # check if we encountered a problematic case
            we_did = False

            for (part_index, part_ids) in [odd, even]:
                for token_index in part_index:
                    token = sentence.findall('W')[token_index]
                    try:
                        if not (token.attrib['DOM'] == '_root' or
                                token.attrib['DOM'] in part_ids or
                                token.attrib.get('LINK', 'root') == 'parataxis' or
                                '.' in token.attrib['ID']):

                            sentence_key = ' '.join((file_name.split('/')[-1], sentence.attrib['ID']))

                            if sentence_key in ignore:
                                break
                            elif sentence_key in fix_deprel:
                                token.attrib['LINK'] = 'parataxis'
                            else:
                                we_did, bad_id = True, token.attrib['ID']
                            break
                    except ValueError:
                        pass
                if we_did:
                    break

            if we_did:
                print_sentence(sentence)
                print('Offender:', bad_id)
                print(file_name.split('/')[-1], sentence.attrib['ID'])
                print(part_counter)
                print(odd[1])
                print(even[1])

            return we_did
    return False

def check_citation(sentence, symbol, i, token_id, file_name, start):
    sentence_element = sentence
    sentence = sentence.findall('W')
    if start:
        for tok in sentence[:i+1]:
            root_token = [token for token in sentence if token.attrib['DOM'] == '_root' and '.' not in token.attrib['ID']]
            if tok.attrib['DOM'] == '_root':
                if all(ch.attrib.get('LINK', 'EMPTY') != 'parataxis' for ch in get_children(sentence_element, tok.attrib['ID'])):
                    for j, new_tok in enumerate(sentence[i+1:]):
                        if ',-' in new_tok.tail.strip().replace(' ', '').replace('\n', '') or ',"' in new_tok.tail.strip().replace(' ', '').replace('\n', ''):

                            for t in sentence[i+1:i+j+2]:
                                if float(t.attrib['DOM']) < float(sentence[i+1].attrib['ID']) or float(t.attrib['DOM']) > float(sentence[i+j+2].attrib['ID']) and \
                                   t.text != 'FANTOM':
                                    t.attrib['LINK'] = 'parataxis'
                                    t.attrib['DOM'] = root_token[0].attrib['ID']

                            for t in sentence[i+j+2:]:
                                if float(t.attrib['DOM']) < float(sentence[i+j+2].attrib['ID']) and t.text != 'FANTOM' and t.attrib['LINK'] in ['orphan', 'conj']:
                                    head_token = [token.attrib for token in sentence if token.attrib['ID'] == t.attrib['DOM']]
                                    if head_token[0].get('LINK', 'EMPTY') != 'conj':
                                        t.attrib['LINK'] = 'conj'
                                        t.attrib['DOM'] = root_token[0].attrib['ID']
                            break
                    else:
                        local_list = []
                        for t in sentence[i+1:]:
                            if float(t.attrib['DOM']) <= float(token_id):
                                local_list.append(t)

                        if len(local_list) > 0:
                            local_list[0].attrib['LINK'] = 'parataxis'
                            local_list[0].attrib['DOM'] = root_token[0].attrib['ID']
                break
        else:
            for j, t in enumerate(sentence[i+1:]):
                if (citation_punct_re.search(t.tail) is not None and
                    end_of_citation_re.search(t.tail) is not None and 
                    whitespace_re.sub('', t.tail) != '",'):

                    if any(token.attrib['DOM'] == '_root' for token in sentence[i+j+2:]):
                        break
            else:
                if not any(',-' in t.tail.strip().replace(' ', '').replace('\n', '') or ',"' in t.tail.strip().replace(' ', '').replace('\n', '') \
                   for t in sentence[i+1:]):
                    candidates = [t for t in sentence[:i+1] if t.attrib['DOM'] == root_token[0].attrib['ID']]

                    if len(candidates) == 1:
                        candidates[0].attrib['DOM'] = '_root'
                        del candidates[0].attrib['LINK']
                        root_token[0].attrib['DOM'] = candidates[0].attrib['ID']
                        root_token[0].attrib['LINK'] = 'parataxis'
                    else:
                        #exceptions
                        if sentence[0].text == 'Николай':
                            print('\nException:')
                            print(' '.join((file_name.split('/')[-1], sentence_element.attrib['ID'])))
                            print_sentence(sentence_element)
                            sentence[0].attrib['LINK'] = 'vocative'
                            sentence[1].attrib['LINK'] = 'flat:name'
                            print('\nCorrected to:')
                            print_sentence(sentence_element)

                        elif sentence[0].text == 'Быстро':
                            print('\nException:')
                            print(' '.join((file_name.split('/')[-1], sentence_element.attrib['ID'])))
                            print_sentence(sentence_element)
                            sentence[3].attrib['DOM'] = '_root'
                            del sentence[3].attrib['LINK']
                            sentence[4].attrib['DOM'] = '3'
                            sentence[4].attrib['LINK'] = 'parataxis'
                            print('\nCorrected to:')
                            print_sentence(sentence_element)
                else:
                    #print(i, token_id, sentence[0].text, sentence[1].text)
                    #print('+' * 20)
                    #print(*[(token.attrib['ID'], token.text, token.attrib['DOM'], token.attrib.get('LINK', 'EMPTY'), token.tail) for token in sentence], sep='\n')
                    #print('*' * 20)
                    pass
    else:
        if any(token.attrib['DOM'] == '_root' for token in sentence[:i+1]):
            candidates = [t for t in sentence[i+1:] if t.text != 'FANTOM' and '.' not in t.attrib['DOM'] and int(t.attrib['DOM']) <= i+1]
            if len(candidates) == 1 and candidates[0].attrib['LINK'] != 'parataxis':
                candidates[0].attrib['LINK'] = 'parataxis'
            elif len(candidates) == 1 and candidates[0].attrib['LINK'] == 'parataxis':
                pass
            elif len(candidates) > 1:
                for j, t in enumerate(sentence[i+1:]):
                    if ',"' in t.tail.strip().replace(' ', '').replace('\n', '') or \
                       '!"' in t.tail.strip().replace(' ', '').replace('\n', '') or \
                       '?"' in t.tail.strip().replace(' ', '').replace('\n', ''):
                        candidate = [t for t in sentence[i+1:i+j+2] if t.text != 'FANTOM' and '.' not in t.attrib['DOM'] and int(t.attrib['DOM']) <= i+1]
                        if len(candidate) == 1:
                            candidate[0].attrib['LINK'] = 'parataxis'
                        elif len(candidate) == 2:
                            if any(can.text == 'то' and can.attrib['LINK'] == 'mark' for can in candidate):
                                try:
                                    sentence[23].attrib['DOM'] = '28'
                                except IndexError:
                                    pass
                            elif any(can.text == 'Париже' and can.attrib['LINK'] == 'conj' for can in candidate):
                                print('\nException:')
                                print(' '.join((file_name.split('/')[-1], sentence_element.attrib['ID'])))
                                print_sentence(sentence_element)
                                sentence[9].attrib['LINK'] = 'parataxis'
                                sentence[7].attrib['DOM'] = '10'
                                sentence[7].attrib['LINK'] = 'discourse'
                                print('\nCorrected to:')
                                print_sentence(sentence_element)
                            elif any(can.text == 'смотришь' and can.attrib['LINK'] == 'conj' for can in candidate):
                                print('\nException:')
                                print(' '.join((file_name.split('/')[-1], sentence_element.attrib['ID'])))
                                print_sentence(sentence_element)
                                sentence[12].attrib['LINK'] = 'parataxis'
                                sentence[25].attrib['DOM'] = '13'
                                print('\nCorrected to:')
                                print_sentence(sentence_element)

                        else:
                            if any(can.text == 'Aravot' for can in candidate):
                                for el in candidate:
                                    if el.attrib['LINK'] == 'flat:foreign':
                                        el.attrib['DOM'] = '5'
        else:
            for j, t in enumerate(sentence[i+1:]):
                if ',"' in t.tail.strip().replace(' ', '').replace('\n', '') or \
                   '!"' in t.tail.strip().replace(' ', '').replace('\n', '') or \
                   '?"' in t.tail.strip().replace(' ', '').replace('\n', '') or \
                   '".' in t.tail.strip().replace(' ', '').replace('\n', ''):
                    if any(token.attrib['DOM'] == '_root' for token in sentence[i+1:i+j+2]):
                        root_token = [token for token in sentence if token.attrib['DOM'] == '_root' and '.' not in token.attrib['ID']]
                        children = get_children(sentence_element, root_token[0].attrib['ID'])
                        if any(ch.attrib['LINK'] in {'parataxis', 'cc'} for ch in children):
                            cand = [c for c in children if c.attrib['LINK'] in {'parataxis', 'cc'}]
                            if len(cand) == 1:
                                root_token[0].attrib['DOM'] = cand[0].attrib['ID']
                                root_token[0].attrib['LINK'] = 'parataxis'
                                cand[0].attrib['DOM'] = '_root'
                                cand[0].attrib.pop('LINK')
                        else:
                            pass
                    else:
                        pass

def process_all(ifolder, ofolder):
	munch(*get_fnames(ifolder, ofolder, '.xml', '.xml'))
	print('12: checkReported.py completed')

if __name__ == "__main__":
    process_all(ifolder, ofolder)

