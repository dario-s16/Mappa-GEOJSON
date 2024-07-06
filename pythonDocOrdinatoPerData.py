import json
import xml.etree.ElementTree as et
import os

Path = "../xml/doc/"

rows = []

files = os.listdir(Path)

for file in files:
    if file.endswith(".xml"):
       
        with open(Path + file, 'r', encoding="utf8") as f: 
        
            print(Path + file)
            
            treeDoc=et.parse(Path + file)

            rootDoc=treeDoc.getroot()
           
            docDate="none"
            tipoData="none"
            pbFol="none"
            
            for elem in treeDoc.findall(".//{http://www.tei-c.org/ns/1.0}pb"):
                if '{http://www.w3.org/XML/1998/namespace}id' in elem.attrib:
                    pbFol=elem.attrib['{http://www.w3.org/XML/1998/namespace}id']
           
            for nodoTemp in rootDoc.findall('{http://www.tei-c.org/ns/1.0}text'):
                for nodoTemp2 in nodoTemp.findall('{http://www.tei-c.org/ns/1.0}front'):
                    for nodoTemp3 in nodoTemp2.findall('{http://www.tei-c.org/ns/1.0}docDate'):
                        for nodoTemp4 in nodoTemp3.findall('{http://www.tei-c.org/ns/1.0}date'):
                        
                            if 'from' in nodoTemp4.attrib:
                                docDate=nodoTemp4.attrib['from']
                                tipoData="from"
                                
                            if 'when' in nodoTemp4.attrib:
                                docDate=nodoTemp4.attrib['when']
                                tipoData="when"
                                
                            if 'notBefore' in nodoTemp4.attrib:
                                docDate=nodoTemp4.attrib['notBefore']
                                tipoData="notBefore"
                        
            nomeDoc=file.removesuffix('.xml')
            
            datiFile = [nomeDoc, tipoData, docDate, pbFol]

    rows.append(datiFile)
    
print(rows)

rows.sort(key=lambda x: x[2])

rows.insert(0, ["Documento", "Tipo data", "Data documento", "Pb Fol"])

import pandas as pd

df = pd.DataFrame(rows)

df.to_csv('outputDocOrdinatoPerData.csv')

outputJson = {
    "documenti":[]
}

for elemento in rows[1:]:
    docJSONtemp={
        "documento":elemento[0], "tipoData":elemento[1], "dataDocumento":elemento[2], "pbFol":elemento[3]
    }
    outputJson["documenti"].append(docJSONtemp)

with open('outputDocJsonOrdinatoPerData.json', 'w', encoding='utf-8') as f:
    json.dump(outputJson, f, ensure_ascii=False, indent=4)
