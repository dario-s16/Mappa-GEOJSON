import json
import xml.etree.ElementTree as et

tree=et.parse('../xml/liste/listaFamiglie.xml')

root=tree.getroot()

idFamiglie = []

for node in root.findall('org'):
    datiFamiglia = {"idFamiglia": "", "orgName": "", "desc": "", "person": ""}
    if '{http://www.w3.org/XML/1998/namespace}id' in node.attrib:
        datiFamiglia["idFamiglia"] = node.attrib['{http://www.w3.org/XML/1998/namespace}id']
        for nodo2 in node.findall('orgName'):
            datiFamiglia["orgName"] = nodo2.text
        for nodo2 in node.findall('desc'):
            descrizioneCorretta=" ".join(''.join(nodo2.itertext()).replace('\n', '').split())
            datiFamiglia["desc"] = descrizioneCorretta            
        for nodo2 in node.findall('person'):
            if 'sameAs' in nodo2.attrib:
                datiFamiglia["person"] = datiFamiglia["person"]+nodo2.attrib['sameAs']+", "
        for nodo2 in node.findall('listPerson'):
            for nodo3 in nodo2.findall('person'):
                if 'sameAs' in nodo3.attrib:
                    datiFamiglia["person"] = datiFamiglia["person"]+nodo3.attrib['sameAs']+", "
        idFamiglie.append(datiFamiglia)

import os
Path = "../xml/doc/"

rows = []
rows.append(["idFamiglia", "Nome", "Descrizione", "Lista persone", "Documento prima attestazione", "Data documento prima attestazione", "Numero Occorrenze", "File occorrenza"])

files = os.listdir(Path)

for idFamiglia in idFamiglie:

    contatoreOccorrenze=0
    
    listaOccorrenze = []
    
    famigliaTemp = [idFamiglia["idFamiglia"], idFamiglia["orgName"], idFamiglia["desc"], idFamiglia["person"]]

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
                
                if "#"+idFamiglia["idFamiglia"] in f.read():
                    #print("true\n")
                    datiFile = [doc["documento"], docDate]
                    listaOccorrenze.append(doc["documento"])
                    
                    if contatoreOccorrenze==0: #verifico se è la prima occorrenza dell'entità, in caso lo fosse è la prima attestazione perché i documenti analizzati vengono scorsi in ordine cronologico
                        famigliaTemp.append(doc["documento"])
                        famigliaTemp.append(doc["dataDocumento"])
                    
                    contatoreOccorrenze=contatoreOccorrenze+1
                #else:
                    #print("false\n")

    if contatoreOccorrenze == 0:
        famigliaTemp.append("none")
        famigliaTemp.append("none")
    
    famigliaTemp.append(listaOccorrenze)
    
    famigliaTemp.insert(6, contatoreOccorrenze)
    
    print(famigliaTemp)
    
    rows.append(famigliaTemp)

import pandas as pd

df = pd.DataFrame(rows)

df.to_csv('outputFamiglie.csv')

outputJson = {
    "famiglie":[]
}

for elemento in rows[1:]:
    famigliaJSONtemp={
        "idFamiglia":elemento[0], "orgName":elemento[1], "desc":elemento[2], "person":elemento[3], "documentoPrimaAttestazione":elemento[4], "dataDocumentoPrimaAttestazione":elemento[5], "numeroOccorrenze":elemento[6], "fileOccorrenza":elemento[7]
    }
    outputJson["famiglie"].append(famigliaJSONtemp)

with open('outputFamiglieJson.json', 'w', encoding='utf-8') as f:
    json.dump(outputJson, f, ensure_ascii=False, indent=4)
