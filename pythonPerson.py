import json
import xml.etree.ElementTree as et

tree=et.parse('../xml/liste/listaPerson.xml')
root=tree.getroot()

idPersone = []

for node in root.findall('person'):
    datiPersona = {"idPersona": "", "sex": "", "nome": "", "cognome": "", "occupation": "", "note": ""}
    if '{http://www.w3.org/XML/1998/namespace}id' in node.attrib:
        datiPersona["idPersona"] = node.attrib['{http://www.w3.org/XML/1998/namespace}id']
        for nodo2 in node.findall('sex'):
            datiPersona["sex"] = nodo2.text
        for nodo3 in node.findall('persName'):
            for nodo4 in nodo3.findall('forename'):
                datiPersona["nome"] = nodo4.text
            for nodo5 in nodo3.findall('surname'):
                datiPersona["cognome"] = nodo5.text
        for nodo2 in node.findall('occupation'):
            datiPersona["occupation"] = nodo2.text
        for nodo2 in node.findall('note'):
            noteCorretta=" ".join(''.join(nodo2.itertext()).replace('\n', '').split())
            datiPersona["note"] = noteCorretta
        idPersone.append(datiPersona)

import os
Path = "../xml/doc/"

rows = []
rows.append(["idPersona", "Nome", "Cognome", "Sex", "Mestiere", "Note", "Documento prima attestazione", "Data documento prima attestazione", "Numero Occorrenze", "File occorrenza"])

files = os.listdir(Path)

for idPersona in idPersone:
    contatoreOccorrenze=0
    listaOccorrenze = []
    personaTemp = [idPersona["idPersona"], idPersona["nome"], idPersona["cognome"], idPersona["sex"], idPersona["occupation"], idPersona["note"]] #accedo all'id all'interno del dizionario che contiene idPersona e sex
    
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
                
                if "#"+idPersona["idPersona"] in f.read():
                    #print("true\n")
                    datiFile = [doc["documento"], docDate]
                    listaOccorrenze.append(doc["documento"])
                    
                    if contatoreOccorrenze==0: #verifico se è la prima occorrenza dell'entità, in caso lo fosse è la prima attestazione perché i documenti analizzati vengono scorsi in ordine cronologico
                        personaTemp.append(doc["documento"])
                        personaTemp.append(doc["dataDocumento"])
                    
                    contatoreOccorrenze=contatoreOccorrenze+1
                #else:
                    #print("false\n")
    
    if contatoreOccorrenze == 0:
        personaTemp.append("none")
        personaTemp.append("none")
    
    personaTemp.append(listaOccorrenze)
    personaTemp.insert(8, contatoreOccorrenze)
    print(personaTemp)
    
    rows.append(personaTemp)

import pandas as pd

df = pd.DataFrame(rows)
df.to_csv('outputPersone.csv')

outputJson = {
    "persone":[]
}

for elemento in rows[1:]:
    personaJSONtemp={
        "idPersona":elemento[0], "nome":elemento[1], "cognome":elemento[2], "sex":elemento[3], "occupation":elemento[4], "note":elemento[5], "documentoPrimaAttestazione":elemento[6], "dataDocumentoPrimaAttestazione":elemento[7], "numeroOccorrenze":elemento[8], "fileOccorrenza":elemento[9]
    }
    outputJson["persone"].append(personaJSONtemp)

with open('outputPersoneJson.json', 'w', encoding='utf-8') as f:
    json.dump(outputJson, f, ensure_ascii=False, indent=4)