"""A collection of utility functions used throughout the project"""

import os
import glob
import shutil

def flatten_structure(path, ofolder):
    """Transform original nested folder structure into flat structure"""
    if os.path.exists(ofolder):
        shutil.rmtree(ofolder)
    os.mkdir(ofolder)
    
    list_of_links = glob.glob(os.path.join(path, '**', '*.tgt'))
    
    for elem in list_of_links:
        file_name = os.path.split(elem)
        folder_name = os.path.split(file_name[0])
        target = os.path.join(ofolder, folder_name[1] + file_name[1])
        shutil.copy(elem, target)

def get_fnames(ifolder, ofolder, ext, postfix, plain=True):
    """Create two corresponding lists of input
    and output file paths.

    If plain is False, also recreate subfolder
    structure in ofolder mirroring the structure from ifolder. 
    """
    ifname_list, ofname_list = [], []
    if not os.path.exists(ofolder):
        os.makedirs(ofolder)

    for root, subdirs, fnames in os.walk(ifolder):
        for fname in fnames:
            if fname.endswith(ext):
                ifname_list.append(os.path.join(root, fname))
                ofname = fname.replace(ext, postfix)

                if plain: # just output everything to ofolder
                    ofname_list.append(os.path.join(ofolder, ofname))
                else: # recreate subfolder structure
                    osubfolder = root.replace(ifolder, ofolder)
                    if not os.path.exists(osubfolder):
	                    os.makedirs(osubfolder)
                    ofname_list.append(os.path.join(osubfolder, ofname))

    return ifname_list, ofname_list

def get_children_attrib(sentence, dom):
    """Collect list of 'attrib' property
    of child elements of the node with id 'dom'
    """
    children_attribs = []    
    for elem in sentence.findall('W'):
        if elem.attrib.get('DOM', '') == dom:
            children_attribs.append(elem.attrib)            
    return children_attribs

def get_children(sentence, dom, links=None):
    """Collect list of child elements
    of the node with id 'dom'

    If 'links' is specified, filter the children list
    to only contain nodes with specified relation(s)
    (can be either str if we need one relation
    or list of str in case of several possible relations)
    """
    children = []
    for elem in sentence.findall('W'):
        if elem.attrib.get('DOM', '') == dom:
            children.append(elem)

    # if link is specified, leave only children with that link
    if links is not None:
        if not isinstance(links, list):
            links = [links]
        children = [child for child in children
                    if child.attrib['LINK'] in links]

    return children

def get_info(word, sentence, get_nodetype=False):
    """Collect info about word element in xml tree structure"""
    link = word.attrib.get('LINK', 'EMPTY')
    feats = word.attrib.get('FEAT', 'EMPTY').split()
    pos = feats[0]
    try:
        head_token = sentence.findall('W')[int(word.attrib['DOM']) - 1]
        head_feats = head_token.attrib.get('FEAT', 'EMPTY').split()
        head_pos = head_feats[0]
        head_root = (head_token.attrib['DOM'] == '_root')
        if get_nodetype:
            nodetype = (head_token.attrib.get('NODETYPE', 'EMPTY') == 'FANTOM')
    except ValueError:
        head_token = head_feats = head_pos = head_root = None
    except IndexError:
        head_token = head_feats = head_pos = head_root = None
    if get_nodetype:
        return link, pos, feats, head_token, head_pos, head_feats, head_root, nodetype
    else:
        return link, pos, feats, head_token, head_pos, head_feats, head_root

