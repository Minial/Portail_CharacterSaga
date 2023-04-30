# Portail V0.1

import csv
import datetime
import json
import sys
from bson.objectid import ObjectId

VERSION = "0.2"

CSVToRead = 'bourin1.csv'

ValeurLvl = 0
ValeurGold = 0
ValeurDT = 0
Donnees = {}
MagicItems = {}
StoryAwards = {}
Consumables = {}
Factions = {}
Logs = {}



def EntryLog(Ligne):
    
    LigneJSON = {
        "_id": str(ObjectId()),
        "type": TypeLog(Ligne[0]),
        "date": int(datetime.datetime.now().timestamp() * 1000),
        "code": Ligne[1],
        "dmrewardtype": None,
        "lvlgain": 0,
        "goldgain": Ligne[7],
        "dtgain": Ligne[8],
        "magicitems": [],
        "notes": Ligne[14],
        "consumables": [],
        "storyawards": [],
        "pcid": Donnees["_id"],
        "tokenused": None,
        "itemout": None,
        "dm": ""
        }
    return LigneJSON

def TypeLog(typeLogOld):
    #récupère le type de log depuis le premier élément de la ligne
    if "PurchaseLogEntry" in typeLogOld :
        return "purchase"
    elif "TradeLogEntry" in typeLogOld :
        return "trade"
    elif "DmLogEntry" in typeLogOld :
        return "dmreward"
    elif "CharacterLogEntry" in typeLogOld :
        return "adventure"
    else:
        print("\nERREUR 01 : type de log inconnu !\n" + typeLogOld + "\n")
        #sys.exit(1)# A REMETTRE

def MagicItemEntryLog(Ligne):
#pour ajouter la log de l'objet dans la log
    LigneJSON = {
        "name": Ligne[1],
        "desc": Ligne[6],
        "rarity": Ligne[2],
        "idx": 0,
        "_id": str(ObjectId()),
        }
    return LigneJSON

    
def convertit_date(chaine_date):
    dt = datetime.datetime.strptime(chaine_date, '%Y-%m-%d %H:%M:%S %Z')
    dt_utc = dt.astimezone(datetime.timezone.utc)
    return dt_utc.strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def MagicItemRemove(Ligne):
    MagicItemLog = MagicItemEntryLog(Ligne)
    for i in range(len(Donnees["magicItems"])):
        if MagicItemLog["name"] == Donnees["magicItems"][i]["name"] and MagicItemLog["desc"] == Donnees["magicItems"][i]["desc"]:
            return i
    print("\nERREUR 03 : objet échangé non existant !\n" + MagicItemLog["name"] + "\n")
    sys.exit(1)


print("Portail v" + VERSION + "\n")

with open(CSVToRead, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for Row in reader:
        #print("Ligne", reader.line_num, ":", Row)
        #print(Row[0]+"")
        if reader.line_num == 2:#ligne info personnages
            Donnees = {
                "_id": "PRENDRESURFICHE_01",
                "createdate": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                "name": Row[0],
                "pcClass": Row[2],
                "race": Row[1],
                "lvl": ValeurLvl, #a calculer
                "url": Row[6],
                "setting": "al",
                "userid": "PRENDRESURFICHE_02",
                "magicItems": [],
                "storyAwards": [],
                "consumables": [],
                #"factions": [Row[3]],
                "logs": [],
                "gold": ValeurGold,
                "dt": ValeurDT,
                "startinggold": 0#ça existait pas du tout
                }
            
        elif reader.line_num > 4:#les vrais logs commence
            if "PurchaseLogEntry" in Row[0]:#log d'achat
                Donnees["logs"].append(EntryLog(Row))
                
            elif "TradeLogEntry" in Row[0]:#log d'objet magic
                Donnees["logs"].append(EntryLog(Row))
                
            elif "CharacterLogEntry" in Row[0]:#log d'aventure
                Donnees["logs"].append(EntryLog(Row))
                Donnees["logs"][-1]["lvlgain"] = 1# la flemme d'ajouter un if dans la fonction
                ValeurLvl += 1
            
            elif "DmLogEntry" in Row[0]:#log de dm reward
                Donnees["logs"].append(EntryLog(Row))
                
            elif Row[0] == "MAGIC ITEM":#log d'objet magic ajouté
                MagicItemLog = MagicItemEntryLog(Row)
                Donnees["logs"][-1]["magicitems"].append(MagicItemLog)
                Donnees["magicItems"].append(MagicItemLog)
            
            elif Row[0] == "TRADED MAGIC ITEM":#log d'objet magic ajouté
                #fait dans une seconde boucle pour éviter les problèmes
                # de log d'échange daté avant l'ajout de l'objet
                pass
            
            else:
                print("\nERREUR 02 : type de log inconnu !\n" + Row[0] + "\n")
                sys.exit(1)
            
with open(CSVToRead, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for Row in reader:
        if "TRADED MAGIC ITEM" in Row[0]:#log d'objet magique échangé (a enlever)
            IndexMagicItem = MagicItemRemove(Row)
            #print(Donnees["magicItems"][IndexMagicItem])
            Donnees["magicItems"].pop(IndexMagicItem)
            #print(Donnees["magicItems"][IndexMagicItem])
            #print("top")
            
            
Donnees["lvl"] = ValeurLvl
#print(Donnees["magicItems"])

with open("96264.json", "w", encoding="utf-8", newline='\n') as f:
    json.dump(Donnees, f, ensure_ascii=False, indent=2)

print("Attention, les niveaux peuvent être inexactes,\nne pas hésiter à les changer manuellement dans le json\nou directement sur Character Saga après import.\n")
print("Terminé !")
print("todo : faction, dmreward, erreur bourin1")