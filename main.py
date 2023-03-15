import streamlit as st


import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os
import re


st.write("Generate a 'border' keyboard with keys around all four sides of the screen")

rows = st.number_input("Number of rows", min_value=1, max_value=100, value=5, step=1)
cols = st.number_input("Number of columns", min_value=1, max_value=100, value=5, step=1)


def safe_ascii(text):
    return re.sub(r'[\\/\×÷ç:"\'*?<>|␣—]+', "", text)

def remove_empty_lines(text):
    return os.linesep.join([s for s in text.splitlines() if s.replace(os.linesep,'').replace('\t', '').strip()])

def remove_double_newlines(text):
    double = os.linesep + os.linesep
    single = os.linesep
    text = text.replace(double, single)

    if (text.contains(double)):
        return remove_double_newlines(text)
    else:
        return text

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    reparsed = reparsed.toprettyxml(indent="\t").replace("&amp;&amp;","&")
    reparsed = remove_empty_lines(reparsed)
    #reparsed = remove_double_newlines(reparsed)
    return reparsed

def add_deadbutton(content_node, row, col):
    key = ET.SubElement(content_node,"DynamicKey")

    # Attributes
    key.set('BackgroundColor', "#010101")
    key.set('Row', str(row))
    key.set('Col', str(col))
    key.set('Width', str(width))
    key.set('Height', str(height))

def add_back_key(content_node, row, col):
    key = ET.SubElement(content_node,"DynamicKey")

    # Attributes
    key.set('Row', str(row))
    key.set('Col', str(col))
    
    # Elements
    label_elem = ET.SubElement(key, "Label")
    label_elem.text = "Back"
    
    action_elem = ET.SubElement(key, "Action")
    action_elem.text = "BackFromKeyboard"

def add_move_key(content_node, row, col, rows, cols):
    key = ET.SubElement(content_node,"DynamicKey")

    # Attributes
    key.set('Row', str(row))
    key.set('Col', str(col))
    
    x1 = 100.0/cols
    y1 = 100.0/rows

    # Elements
    label_elem = ET.SubElement(key, "Label")
    label_elem.text = "Move"
    
    action_elem = ET.SubElement(key, "MoveWindow")
    action_elem.text = f"{x1:.1f}%, {y1:.1f}%, {100-x1:.1f}%, {100-y1:.1f}%"


def add_textkey(content_node, row, col, text):
    key = ET.SubElement(content_node,"DynamicKey")

    # Attributes
    key.set('Row', str(row))
    key.set('Col', str(col))

    # Elements    
    label_elem = ET.SubElement(key, "Label")
    label_elem.text = text    
    

def add_linkkey(content_node, row, col, width, height, text, link):
    key = ET.SubElement(content_node,"DynamicKey")

    # Attributes
    key.set('Row', str(row))
    key.set('Col', str(col))
    key.set('Width', str(width))
    key.set('Height', str(height))

    # Elements
    keygroup_elem = ET.SubElement(key, "KeyGroup")
    keygroup_elem.text = 'GroupKeys'
    label_elem = ET.SubElement(key, "Label")
    label_elem.text = split_label(text)
    link_elem = ET.SubElement(key, "ChangeKeyboard")
    link_elem.text = link
    link_elem.set('BackReturnsHere', "True")

def split_label(text):
    L = len(text)
    if (L > 4):
        split_length = (int)((L+1)/2)
        t1 = text[0:split_length]
        t2 = text[split_length:]
        text = t1 + "\n" + t2
    return text

def save_file(xml_root, filename):
    text = prettify(xml_root)
    with open(filename, "w", encoding="utf-8") as f:
        for line in text.splitlines():
            if (line.strip()):
                f.write(line)
                f.write("\n")

def setup_keyboard(total_rows, total_cols, name=None,hidden=True):
    # Load basic content
    tree = ET.parse('skeleton.xml')
    root = tree.getroot()

    # Top level elements
    rows_element = ET.fromstring("<Rows>" + str(total_rows) + "</Rows>")
    cols_element = ET.fromstring("<Cols>" + str(total_cols) + "</Cols>")
    hidden_element = ET.fromstring("<HideFromKeyboardMenu>" + str(hidden) + "</HideFromKeyboardMenu>")

    root.insert(2, hidden_element)  # 2 means it being the third tag (in this moment)

    if name:
        name_element = ET.fromstring("<Name>" + str(name) + "</Name>")
        root.insert(0, name_element) # so hidden_element will be the forth tag

    # insert at top
    grid = tree.find('Grid')
    grid.insert(0, rows_element)
    grid.insert(1, cols_element)

    # Content node contains all the keys
    content = tree.find('Content')

    return tree, content


def keyboard():
    
    # Content node contains all the keys
    tree, content = setup_keyboard(rows, cols, f"Border_{rows}_{cols}", False)

    # Fixed keys in top left/bottom right
    add_move_key(content, 0, 0, rows, cols)
    add_back_key(content, rows-1, cols-1)

    # add text labels around edges
    i = 1
    for r in range(rows):
        for c in range(cols):
            if ( r == 0 or r == rows-1 or c == 0 or c == cols-1):   
                if (r==0 and c==0): # skip for existing button
                    continue
                if (r == rows-1 and c==cols-1):
                    continue

                add_textkey(content, r, c, str(i))
                i+=1


    xmlstr = prettify(tree.getroot())
    return xmlstr



text_contents=""

if (rows and cols):
    # Generate XML file    
    text_contents = keyboard()

st.download_button('Download XML', text_contents, f"Border_{rows}_{cols}.xml")

