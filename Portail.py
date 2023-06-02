# Portail V0.2

import csv
import datetime
import json
import sys
from bson.objectid import ObjectId

VERSION = "0.3"
print("Portail v" + VERSION + "\n")

CSVToRead = 'Glomi.csv'
JSONToWrite = "Glomi.json"

Initial_id = ""
Initialpcid = ""
ValeurLvl = 0
ValeurGold = 0
ValeurDT = 0
Donnees = {}
OldJSON = {}
MagicItems = {}
StoryAwards = {}
Consumables = {}
Factions = {}
Logs = {}



def EntryLog(Ligne):
    if Ligne[7] == '':
        Ligne[7] = '0.0'
    if Ligne[8] == '':
        Ligne[8] = '0.0'
    
    
    LigneJSON = {
        "_id": str(ObjectId()),
        "type": TypeLog(Ligne[0]),
        "date": convertit_date(Ligne[3]),
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
        "dm": Ligne[12]
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
        sys.exit(1)# A REMETTRE

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

def FactionEntryLog(Ligne):
    FactionLog = {
          "name": Ligne[3],
          "rank": "0",
          "_id": str(ObjectId())
        }
    return FactionLog
    
def convertit_date(chaine_date):
    if chaine_date != '':
        dt = datetime.datetime.strptime(chaine_date, '%Y-%m-%d %H:%M:%S %Z')
        dt_utc = dt.astimezone(datetime.timezone.utc)
        return dt_utc.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    else:
        return None

def MagicItemRemove(Ligne):
    MagicItemLog = MagicItemEntryLog(Ligne)
    for i in range(len(Donnees["magicitems"])):
        if MagicItemLog["name"] == Donnees["magicitems"][i]["name"] and MagicItemLog["desc"] == Donnees["magicitems"][i]["desc"]:
            return i
    print("\nERREUR 03 : objet échangé non existant !\n" + MagicItemLog["name"] + "\n")
    sys.exit(1)

def NettoyageMagicItem(MagicItemsList):
    NewMagicItemsList = MagicItemsList.copy()#sinon on réfère la même chose
    compteur = len(MagicItemsList)#on vas faire simple avec un compteur
    for MagicItem in reversed(MagicItemsList):
        compteur -= 1#pour donner l'index précis correspondant dans la nouvelle list
        if MagicItem["name"] == "" and MagicItem["desc"] == "" :
            #NewMagicItemsList.pop(compteur)
            NewMagicItemsList[compteur]["inactive"] = True
    return NewMagicItemsList

#truc bête, mais pas le droit de modifier une variable globale depuis l'intérieur d'une fonction

with open(JSONToWrite, "r") as f:
    OldJSON = json.load(f)
    Initial_id = OldJSON["_id"]
    Initialpcid = OldJSON["userid"]


with open(CSVToRead, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for Row in reader:
        if reader.line_num == 2:#ligne info personnages
            Donnees = {
                "_id": Initial_id,
                "createdate": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                "name": Row[0],
                "pcClass": Row[2],
                "race": Row[1],
                "lvl": ValeurLvl, #a calculer
                "url": Row[6],
                "setting": "al",
                "userid": Initialpcid,
                "magicitems": [],
                "storyAwards": [],
                "consumables": [],
                "factions": [FactionEntryLog(Row)],
                "logs": [],
                "gold": ValeurGold,
                "dt": ValeurDT,
                "startinggold": 0#ça existait pas du tout
                }
            
        elif reader.line_num > 4:#les vrais logs commence
            if "PurchaseLogEntry" in Row[0]:#log d'achat
                Donnees["logs"].append(EntryLog(Row))
                Donnees["gold"] += float(Donnees["logs"][-1]["goldgain"])
                Donnees["dt"] += float(Donnees["logs"][-1]["dtgain"])
                
            elif "TradeLogEntry" in Row[0]:#log d'objet magic
                Donnees["logs"].append(EntryLog(Row))
                Donnees["gold"] += float(Donnees["logs"][-1]["goldgain"])
                Donnees["dt"] += float(Donnees["logs"][-1]["dtgain"])
                
            elif "CharacterLogEntry" in Row[0]:#log d'aventure
                Donnees["logs"].append(EntryLog(Row))
                Donnees["logs"][-1]["lvlgain"] += 1# la flemme d'ajouter un if dans la fonction
                ValeurLvl += 1 
                Donnees["gold"] += float(Donnees["logs"][-1]["goldgain"])
                Donnees["dt"] += float(Donnees["logs"][-1]["dtgain"])
            
            elif "DmLogEntry" in Row[0]:#log de dm reward
                Donnees["logs"].append(EntryLog(Row))
                Donnees["gold"] += float(Donnees["logs"][-1]["goldgain"])
                Donnees["dt"] += float(Donnees["logs"][-1]["dtgain"])
                
            elif Row[0] == "MAGIC ITEM":#log d'objet magic ajouté
                MagicItemLog = MagicItemEntryLog(Row)
                Donnees["logs"][-1]["magicitems"].append(MagicItemLog)
                Donnees["magicitems"].append(MagicItemLog)
            
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
        #fait dans une seconde boucle pour éviter les problèmes
        # de log d'échange daté avant l'ajout de l'objet
        if "TRADED MAGIC ITEM" in Row[0]:#log d'objet magique échangé (a enlever)
            IndexMagicItem = MagicItemRemove(Row)
            Donnees["magicitems"][IndexMagicItem]["inactive"] = True
            


Donnees["lvl"] = ValeurLvl 
Donnees["magicitems"] = NettoyageMagicItem(Donnees["magicitems"])
Donnees["logs"].reverse()
#print(Donnees["magicitems"])

with open(JSONToWrite, "w", encoding="utf-8", newline='\n') as f:
    json.dump(Donnees, f, ensure_ascii=False, indent=2)
    
    
print("Attention, les informations de faction sont perdus !\n")
print("Attention, si vous aviez supprimés des OMs,\nceux-ci sont présent sur Character Saga !\n")
print("Attention, les niveaux et DT peuvent être inexactes,\nne pas hésiter à les changer manuellement dans le json\nou directement sur Character Saga après import!\n")
print("Terminé !")
print("todo : faction à finir, rareté incorrect")