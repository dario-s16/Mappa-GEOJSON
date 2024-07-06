import json
import xml.etree.ElementTree as et

tree=et.parse('../xml/liste/listaPopoli.xml')

root=tree.getroot()

idPopoli = []

for node in root.findall('org'):
    datiPopolo = {"idPopolo": "", "orgName": "", "desc": ""}
    if '{http://www.w3.org/XML/1998/namespace}id' in node.attrib:
        datiPopolo["idPopolo"] = node.attrib['{http://www.w3.org/XML/1998/namespace}id']
        for nodo2 in node.findall('orgName'):
            datiPopolo["orgName"] = nodo2.text
        for nodo2 in node.findall('desc'):
            descrizioneCorretta=" ".join(''.join(nodo2.itertext()).replace('\n', '').split())
            datiPopolo["desc"] = descrizioneCorretta
        idPopoli.append(datiPopolo)

import os
Path = "../xml/doc/"

rows = []
rows.append(["idPopolo", "Nome", "Descrizione", "Documento prima attestazione", "Data documento prima attestazione", "Numero Occorrenze", "File occorrenza"])

files = os.listdir(Path)

for idPopolo in idPopoli:

    contatoreOccorrenze=0
    
    listaOccorrenze = []
    
    popoloTemp = [idPopolo["idPopolo"], idPopolo["orgName"], idPopolo["desc"]]
    
    if os.path.isfile("outputDocJsonOrdinatoPerData.json") is True: #verifico che l'output json relativo ai documenti ordinati per data esista, perché necessario per l'analisi delle occorrenze e della prima attestazione
        
        fileJsonDocOrdinati = open('outputDocJsonOrdinatoPerData.json')
        outputDocJsonOrdinatoPerData = json.load(fileJsonDocOrdinati)
        
        for doc in outputDocJsonOrdinatoPerData["documenti"]:
        
            with open(Path + doc["documento"]+".xml", 'r', encoding="utf8") as f:
            
                treeDoc=et.parse(Path + doc["documento"]+".xml")
                rootDoc=treeDoc.getroot()
                
                docDate="none"
                
                for nodoTemp in rootDoc.findall('{http://www.tei-c.org/ns/1.0}text'):
                    for nodoTemp2 in nodoTemp.findall('{http://www.tei-c.org/ns/1.0}front'):
                        for nodoTemp3 in nodoTemp2.findall('{http://www.tei-c.org/ns/1.0}docDate'):
                            for nodoTemp4 in nodoTemp3.findall('{http://www.tei-c.org/ns/1.0}date'):
                                docDate=nodoTemp4.attrib
                
                if "#"+idPopolo["idPopolo"] in f.read():
                    #print("true\n")
                    datiFile = [doc["documento"], docDate]
                    listaOccorrenze.append(doc["documento"])
                    
                    if contatoreOccorrenze==0: #verifico se è la prima occorrenza dell'entità, in caso lo fosse è la prima attestazione perché i documenti analizzati vengono scorsi in ordine cronologico
                        popoloTemp.append(doc["documento"])
                        popoloTemp.append(doc["dataDocumento"])
                    
                    contatoreOccorrenze=contatoreOccorrenze+1
                #else:
                    #print("false\n")
    
    if contatoreOccorrenze == 0:
        popoloTemp.append("none")
        popoloTemp.append("none")
    
    popoloTemp.append(listaOccorrenze)
    
    popoloTemp.insert(5, contatoreOccorrenze)
    
    print(popoloTemp)
    
    rows.append(popoloTemp)

import pandas as pd

df = pd.DataFrame(rows)

df.to_csv('outputPopoli.csv')

outputJson = {
    "popoli":[]
}

for elemento in rows[1:]:
    popoloJSONtemp={
        "idPopolo":elemento[0], "orgName":elemento[1], "desc":elemento[2], "documentoPrimaAttestazione":elemento[3], "dataDocumentoPrimaAttestazione":elemento[4], "numeroOccorrenze":elemento[5], "fileOccorrenza":elemento[6]
    }
    outputJson["popoli"].append(popoloJSONtemp)

with open('outputPopoliJson.json', 'w', encoding='utf-8') as f:
    json.dump(outputJson, f, ensure_ascii=False, indent=4)
