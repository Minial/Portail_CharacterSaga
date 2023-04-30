# -*- coding: utf-8 -*-

# Portail V0.1

import csv
import datetime
import json
import sys
from bson.objectid import ObjectId
import requests
from bs4 import BeautifulSoup

VERSION = "2.0a"

print("Portail v" + VERSION + "\n")

URLToRead = "https://www.adventurersleaguelog.com/users/35966/characters/103493/print"
#URLToRead = "https://www.adventurersleaguelog.com/users/35966/characters/96264/print"

ValeurLvl = 0
ValeurGold = 0
ValeurDT = 0
Donnees = {}
MagicItems = {}
StoryAwards = {}
Consumables = {}
Factions = {}
Logs = {}

def ExtractElementLabel(Soupe,ElementToExtract):
    LabelElement = Soupe.find('label', text=ElementToExtract)
    DivElement = LabelElement.find_previous_sibling('div')
    return DivElement.text

def ExtractElementP(Soupe):
    #DO NOT USE
    #breakpoint()
    return Soupe.find_all('p', class_="print-notes")[0].text
    # LabelElement = Soupe.find('p', text=ElementToExtract, class_="print-notes")
    # print(Soupe)
    # DivElement = LabelElement.find_previous_sibling('label')
    # return DivElement.text
    

def convertit_date(chaine_date):
    dt = datetime.datetime.strptime(chaine_date, '%Y-%m-%d %H:%M:%S %Z')
    dt_utc = dt.astimezone(datetime.timezone.utc)
    return dt_utc.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

def FactionEntryLog(Soupe):
    CharacterDivInternal = Soupe.find(class_="row print-character-box")
    FactionLog = {
          "name": ExtractElementLabel(CharacterDivInternal,"Faction"),
          "rank": "0",
          "_id": str(ObjectId())
        }
    return FactionLog


def TypeLog(typeLogOld):
    #récupère le type de log
    
    titreLog = typeLogOld.find_all('h4')
    #plein de truc utilise le h4, mais il n'y a pas de meilleures sélection
    for typeLogOld in titreLog:
    
        if "*** PURCHASE ENTRY ***" in typeLogOld :
            return "purchase"
        elif "*** TRADE ENTRY ***" in typeLogOld :
            return "trade"
        elif "*** DM ENTRY ***" in typeLogOld :
            return "dmreward"
    
    #faudrait vérifier en théorie, mais la flemme
    return "adventure"
        
    #print("\nERREUR 01 : type de log inconnu !\n" + typeLogOld + "\n")
    #sys.exit(1)# A REMETTRE



def EntryLog(EntryDiv):
    
    
    LigneJSON = {
        "_id": str(ObjectId()),
        "type": TypeLog(EntryDiv),
        "date": int(datetime.datetime.now().timestamp() * 1000),
        "code": ExtractElementP(EntryDiv),
        "dmrewardtype": None,
        "lvlgain": 0,
        "goldgain": "",
        "dtgain": "",
        "magicitems": [],
        "notes": "",
        "consumables": [],
        "storyawards": [],
        "pcid": Donnees["_id"],
        "tokenused": None,
        "itemout": None,
        "dm": ""
        }
    return LigneJSON
# Récupérer le contenu de la page
response = requests.get(URLToRead)
html_content = response.content

# Analyser le contenu HTML
soup = BeautifulSoup(html_content, 'html.parser')

#exemple
CharacterDiv = soup.find(class_="row print-character-box")
CharacterName = ExtractElementLabel(CharacterDiv,"Character Name")




CharacterDiv = soup.find(class_="row print-character-box")

Donnees = {
    "_id": "PRENDRESURFICHE_01",
    "createdate": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
    "name": ExtractElementLabel(CharacterDiv,"Character Name"),
    "pcClass": ExtractElementLabel(CharacterDiv,"Class and Levels"),
    "race": "???",
    "lvl": ValeurLvl, #a calculer
    "url": "",
    "setting": "al",
    "userid": "PRENDRESURFICHE_02",
    "magicItems": [],
    "storyAwards": [],
    "consumables": [],
    "factions": [FactionEntryLog(soup)],
    "logs": [],
    "gold": ValeurGold, #a calculer
    "dt": ValeurDT, #a calculer
    "startinggold": 0#ça existait pas du tout
    }

#Donnees["factions"][0] = FactionEntryLog(soup)

#récupérer toutes les entrées de log
EntryDivList = soup.find_all('div',class_="row print-log-entry-box")

for EntryDiv in EntryDivList:
    Entry = EntryLog(EntryDiv)



with open("96264.json", "w", encoding="utf-8", newline='\n') as f:
    json.dump(Donnees, f, ensure_ascii=False, indent=2)

print("Élément impossible à récupérer :\n\t- Race du personnage\n\t- Rang de faction du personnage")
print("\nTerminé !")