import json
import xml.etree.ElementTree as et
import os

Path = "../xml/doc/"

rows = []

files = os.listdir(Path)

all_name_elements="no"

for file in files:
    if file.endswith(".xml"):
       
        with open(Path + file, 'r', encoding="utf8") as f: 
        
            print(Path + file)
            
            treeDoc=et.parse(Path + file)

            rootDoc=treeDoc.getroot()
           
            pbFol="none"
            
            for elem in treeDoc.findall(".//{http://www.tei-c.org/ns/1.0}pb"):
                if '{http://www.w3.org/XML/1998/namespace}id' in elem.attrib:
                    pbFol=elem.attrib['{http://www.w3.org/XML/1998/namespace}id']
 
            datiFile = [file, pbFol]

    rows.append(datiFile)
    
print(rows)

rows.insert(0, ["Documento", "pb"])

import pandas as pd

df = pd.DataFrame(rows)

df.to_csv('outputDocFol.csv')
