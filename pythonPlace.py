import json
import requests
import xml.etree.ElementTree as et

#Funzione che calcola le coordinate di un luogo, sulla base degli elementi placeName (toponimo moderno) e 
#district (comune o "nei pressi di").
#La funzione effettua la ricerca delle coordinate con diverse combinazioni di dati, finché non ottiene una risposta 
#o conferma l'impossibilità dell'ottenimento.
def ottieniCoordinatePlaceName(placeName, district):
    formati = [
        placeName + "," + district + ",Italia",
        placeName + "," + district,
        placeName + ",Italia",
        placeName
    ]

    for formato in formati:
        try:
            url="https://nominatim.openstreetmap.org/search?q=" +formato+ "&format=json"
            #headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
            headers={'User-Agent': 'Mozilla/5.0'}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Solleva un'eccezione in caso di errore HTTP
            response = response.json()
            if len(response) > 0:
                return float(response[0]["lon"]), float(response[0]["lat"])
        except requests.exceptions.RequestException as e: # Gestione dell'eccezione per errori nelle richieste HTTP
            print("Errore nella richiesta HTTP: " + str(e))

    # Se nessuna risposta ha restituito risultati, restituisco dei risultati standard
    return 11, 40

#Funzione che svolge lo stesso compito della funzione ottieniCoordinatePlaceName, ma usata nel caso un luogo non fosse fornito del placeName (toponimo moderno).
def ottieniCoordinateDistrict(district):
    formati = [
        district + ",Italia",
        district
    ]
    
    for formato in formati:
        try:
            url="https://nominatim.openstreetmap.org/search?q=" +formato+ "&format=json&polygon_geojson"
            headers={'User-Agent': 'Mozilla/5.0'}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Solleva un'eccezione in caso di errore HTTP
            response = response.json()
            if len(response) > 0:
                return response[0]["geojson"]["coordinates"][0]
        except requests.exceptions.RequestException as e: # Gestione dell'eccezione per errori nelle richieste HTTP
            print("Errore nella richiesta HTTP: " + str(e))
    
    # Se nessuna risposta ha restituito risultati restituisco dei risultati standard
    return 11, 40
    
def ottieniTipoPoligonoDistrict(district):
    formati = [
        district + ",Italia",
        district
    ]
    
    for formato in formati:
        try:
            url="https://nominatim.openstreetmap.org/search?q=" +formato+ "&format=json&polygon_geojson"
            headers={'User-Agent': 'Mozilla/5.0'}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Solleva un'eccezione in caso di errore HTTP
            response = response.json()
            if len(response) > 0:
                return response[0]["geojson"]["type"]
        except requests.exceptions.RequestException as e: # Gestione dell'eccezione per errori nelle richieste HTTP
            print("Errore nella richiesta HTTP: " + str(e))
    
    # Se nessuna risposta ha restituito risultati restituisco un risultato standard
    return "Polygon"

tree=et.parse('../xml/liste/listaPlace.xml')

root=tree.getroot()

idLuoghi = []

for node in root.findall('place'):
    datiPlace = {"idLuogo": "", "settlement": "", "placeName": "", "district": "", "note": ""}
    if '{http://www.w3.org/XML/1998/namespace}id' in node.attrib:
        datiPlace["idLuogo"] = node.attrib['{http://www.w3.org/XML/1998/namespace}id']
        for nodo2 in node.findall('settlement'):
            datiPlace["settlement"] = nodo2.text
        for nodo3 in node.findall('placeName'):
            datiPlace["placeName"] = nodo3.text
        for nodo4 in node.findall('district'):
            datiPlace["district"] = nodo4.text
        for nodo4 in node.findall('note'):
            noteCorretta=" ".join(''.join(nodo4.itertext()).replace('\n', '').split())
            datiPlace["note"] = noteCorretta
        idLuoghi.append(datiPlace)

import os
Path = "../xml/doc/"

rows = []
rows.append(["idLuogo", "Settlement", "PlaceName (Nome moderno)", "District", "Note", "Longitudine", "Latitudine", "Documento prima attestazione", "Data documento prima attestazione", "Numero Occorrenze", "File occorrenza"])

files = os.listdir(Path)

for idLuogo in idLuoghi:

    contatoreOccorrenze=0

    listaOccorrenze = []
    
    longitudineLuogo=None #longitudine standard per inizializzare la variabile, che resterà inalterata in caso fosse impossibile calcolare la longitudine del luogo
    latitudineLuogo=None #latitudine standard per inizializzare la variabile, che resterà inalterata in caso fosse impossibile calcolare la latitudine del luogo
    
    #print(idLuogo)
    #print("placeName="+idLuogo["placeName"]+".")
    
    if idLuogo["placeName"] != "":
        longitudineLuogo, latitudineLuogo = ottieniCoordinatePlaceName(idLuogo["placeName"], idLuogo["district"])
    
    luogoTemp = [idLuogo["idLuogo"], idLuogo["settlement"], idLuogo["placeName"], idLuogo["district"], idLuogo["note"], longitudineLuogo, latitudineLuogo]
    
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
                
                if "#"+idLuogo["idLuogo"] in f.read():
                    #print("true\n")
                    datiFile = [doc["documento"], docDate]
                    listaOccorrenze.append(doc["documento"])
                    
                    if contatoreOccorrenze==0: #verifico se è la prima occorrenza dell'entità, in caso lo fosse è la prima attestazione perché i documenti analizzati vengono scorsi in ordine cronologico
                        luogoTemp.append(doc["documento"])
                        luogoTemp.append(doc["dataDocumento"])
                    
                    contatoreOccorrenze=contatoreOccorrenze+1
                #else:
                    #print("false\n")
    
    if contatoreOccorrenze == 0:
        luogoTemp.append("none")
        luogoTemp.append("none")

    luogoTemp.append(listaOccorrenze)
    
    luogoTemp.insert(9, contatoreOccorrenze)
    
    print(luogoTemp)
    
    rows.append(luogoTemp)

GeoJson = {
    "type": "FeatureCollection",
    "features": []
}

GeoJsonSoloPoint = {
    "type": "FeatureCollection",
    "features": []
}

GeoJsonSoloDistrict = {
    "type": "FeatureCollection",
    "features": []
}

listaIdLuoghi = []
listaPlaceName = []
listaDistrict = []

#blocco di codice/ciclo che scorre tutti gli elementi della lista rows per riempire i dizionari GeoJson e GeoJsonSoloPoint, che vengono usati per l'output dei file GeoJSON generale e relativo ai point (placeName)
for luogo in rows[1:]:
    #print(luogo)
    #print("\n")
    listaIdLuoghi.append(luogo[0])
    if luogo[2] != "":
        listaPlaceName.append(luogo[2])
    if luogo[3] != "":
        listaDistrict.append(luogo[3])
    GeoJsonTemp={
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [luogo[5], luogo[6]]
        },
        "properties": {
            "idLuogo": luogo[0],
            "settlement": luogo[1],
            "placeName": luogo[2],
            "district": luogo[3],
            "note": luogo[4],
            "longitudine": luogo[5],
            "latitudine": luogo[6],
            "documentoPrimaAttestazione": luogo[7],
            "dataDocumentoPrimaAttestazione": luogo[8],
            "numeroOccorrenze": luogo[9],
            "fileOccorrenza": luogo[10]
        }
    }
    GeoJson["features"].append(GeoJsonTemp)
    #blocco in cui prodoco l'output con solo gli elementi che hanno il placeName (nome moderno)
    if luogo[2] != "":
        GeoJsonSoloPointTemp={
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [luogo[5], luogo[6]]
            },
            "properties": {
                "idLuogo": luogo[0],
                "settlement": luogo[1],
                "placeName": luogo[2],
                "district": luogo[3],
                "note": luogo[4],
                "longitudine": luogo[5],
                "latitudine": luogo[6],
                "documentoPrimaAttestazione": luogo[7],
                "dataDocumentoPrimaAttestazione": luogo[8],
                "numeroOccorrenze": luogo[9],
                "fileOccorrenza": luogo[10]
            }
        }
        GeoJsonSoloPoint["features"].append(GeoJsonSoloPointTemp)
    
listaDistrict = list(dict.fromkeys(listaDistrict)) #elimino i doppioni dalla lista listaDistrict

#blocco di codice/ciclo che scorre tutti gli elementi della lista listaDistrict e riempie il dizionario GeoJsonSoloDistrict, che viene usato per l'output del file GeoJSON relativo ai district
for district in listaDistrict:

    contatoreOccorrenzeDistrict=0
    listaOccorrenzeDistrict = []
    
    #ciclo che scorre tutti i luoghi per ogni district, e calcola le occorrenze totali del district analizzato nell'iterazione corrente
    for luogo in rows[1:]:
        if luogo[3]==district:
            contatoreOccorrenzeDistrict=contatoreOccorrenzeDistrict+1
            listaOccorrenzeDistrict.append(luogo[0])
   
    tipoPoligono=ottieniTipoPoligonoDistrict(district)
    
    if tipoPoligono!= "Polygon" and "MultiPolygon":
        tipoPoligono="Polygon"
  
    GeoJsonSoloDistrictTemp={
        "type": "Feature",
        "geometry": {
            "type": tipoPoligono,
            "coordinates": [ottieniCoordinateDistrict(district)]
        },
        "properties": {
            "district": district,
            "coordinate": ottieniCoordinateDistrict(district),
            "documentoPrimaAttestazione": None,
            "dataDocumentoPrimaAttestazione": None,
            "numeroLuoghiDistrict": contatoreOccorrenzeDistrict,
            "luogoOccorrenza": [listaOccorrenzeDistrict]
        }
    }
    GeoJsonSoloDistrict["features"].append(GeoJsonSoloDistrictTemp)

#with open('outputPlaceGeoJson.json', 'w', encoding='utf-8') as f:
    #json.dump(GeoJson, f, ensure_ascii=False, indent=4)
    
with open('outputPlaceGeoJsonSoloPoint.json', 'w', encoding='utf-8') as f:
    json.dump(GeoJsonSoloPoint, f, ensure_ascii=False, indent=4)

with open('outputPlaceGeoJsonSoloDistrict.json', 'w', encoding='utf-8') as f:
    json.dump(GeoJsonSoloDistrict, f, ensure_ascii=False, indent=4)

import geopandas

fileDaSemplificare = geopandas.read_file('outputPlaceGeoJsonSoloDistrict.json')

fileDaSemplificare['geometry'] = fileDaSemplificare['geometry'].simplify(0.001)

fileDaSemplificare.to_file("outputPlaceGeoJsonSoloDistrict.json") #produce in output il file semplificato che sovrascrive quello precedentemente creato

import pandas as pd

df = pd.DataFrame(rows)

df.to_csv('outputPlace.csv')

outputJson = {
    "luoghi":[]
}

for elemento in rows[1:]:
    luogoJSONtemp={
        "idLuogo":elemento[0], "settlement":elemento[1], "placeName":elemento[2], "district":elemento[3], "note":elemento[4], "longitudine":elemento[5], "latitudine":elemento[6], "documentoPrimaAttestazione":elemento[7], "dataDocumentoPrimaAttestazione":elemento[8], "numeroOccorrenze":elemento[9], "fileOccorrenza":elemento[10]
    }
    outputJson["luoghi"].append(luogoJSONtemp)

with open('outputPlaceJson.json', 'w', encoding='utf-8') as f:
    json.dump(outputJson, f, ensure_ascii=False, indent=4)