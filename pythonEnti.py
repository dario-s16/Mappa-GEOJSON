import json
import xml.etree.ElementTree as et

tree=et.parse('../xml/liste/listaEnti.xml')

root=tree.getroot()

idEnti = []

for node in root.findall('org'):
    datiEnte = {"idEnte": "", "orgName": "", "desc": "", "listPerson": ""}
    if '{http://www.w3.org/XML/1998/namespace}id' in node.attrib:
        datiEnte["idEnte"] = node.attrib['{http://www.w3.org/XML/1998/namespace}id']
        for nodo2 in node.findall('orgName'):
            datiEnte["orgName"] = nodo2.text
        for nodo2 in node.findall('desc'):
            descrizioneCorretta=" ".join(''.join(nodo2.itertext()).replace('\n', '').split())
            datiEnte["desc"] = descrizioneCorretta
        for nodo2 in node.findall('listPerson'):
            for nodo3 in nodo2.findall('person'):
                if 'sameAs' in nodo3.attrib:
                    datiEnte["listPerson"] = datiEnte["listPerson"]+nodo3.attrib['sameAs']+", "
        idEnti.append(datiEnte)

import os
Path = "../xml/doc/"

rows = []
rows.append(["idEnte", "Nome", "Descrizione", "Lista persone", "Documento prima attestazione", "Data documento prima attestazione", "Numero Occorrenze", "File occorrenza"])

files = os.listdir(Path)

for idEnte in idEnti:

    contatoreOccorrenze=0
    
    listaOccorrenze = []
    
    enteTemp = [idEnte["idEnte"], idEnte["orgName"], idEnte["desc"], idEnte["listPerson"]]
    
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
                
                if "#"+idEnte["idEnte"] in f.read():
                    #print("true\n")
                    datiFile = [doc["documento"], docDate]
                    listaOccorrenze.append(doc["documento"])
                    
                    if contatoreOccorrenze==0: #verifico se è la prima occorrenza dell'entità, in caso lo fosse è la prima attestazione perché i documenti analizzati vengono scorsi in ordine cronologico
                        enteTemp.append(doc["documento"])
                        enteTemp.append(doc["dataDocumento"])
                    
                    contatoreOccorrenze=contatoreOccorrenze+1
                #else:
                    #print("false\n")

    if contatoreOccorrenze == 0:
        enteTemp.append("none")
        enteTemp.append("none")
    
    enteTemp.append(listaOccorrenze)
    
    enteTemp.insert(6, contatoreOccorrenze)
    
    print(enteTemp)
    
    rows.append(enteTemp)

import pandas as pd

df = pd.DataFrame(rows)

df.to_csv('outputEnti.csv')

outputJson = {
    "enti":[]
}

for elemento in rows[1:]:
    enteJSONtemp={
        "idEnte":elemento[0], "orgName":elemento[1], "desc":elemento[2], "listPerson":elemento[3], "documentoPrimaAttestazione":elemento[4], "dataDocumentoPrimaAttestazione":elemento[5], "numeroOccorrenze":elemento[6], "fileOccorrenza":elemento[7]
    }
    outputJson["enti"].append(enteJSONtemp)

with open('outputEntiJson.json', 'w', encoding='utf-8') as f:
    json.dump(outputJson, f, ensure_ascii=False, indent=4)
