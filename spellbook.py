import pickle, os
from spell import *

class Spellbook:
    def __init__(self, name):
        self.name = name
        self.spells = list()

    def addSpell(self, spell):
        self.spells.append(spell)
        self.spells.sort(key=lambda k: k.name)

    def removeSpell(self, spell):
        try:
            self.spells.remove(spell)
        except:
            pass

def spellbookFinder(spellbooks, spellbookName):
    savedSpellbook = None
    text = []
    for spellbook in spellbooks.keys():
        if spellbook.lower().replace("'", "").replace(" ", "") == spellbookName.lower().replace("'", "").replace(" ", ""):
            return True, spellbook
        elif spellbookName.lower().replace("'", "").replace(" ", "") in spellbook.lower().replace("'", "").replace(" ", ""):
            if not savedSpellbook:
                savedSpellbook = spellbook
            else:
                text.append(spellbook)
    if not savedSpellbook:
        return False, "Spellbook not found"
    elif text == []:
        return True, savedSpellbook
    else:
        text.append(savedSpellbook)
        return False, "? ".join(sorted(text)) + "?"

def spellbookParser(spells, spellbooks, command):
    try:
        if command[0] == "list":
            if len(command) > 1:
                sbfound, sbresult = spellbookFinder(spellbooks, command[1])
                if sbfound:
                    spellList = spellbooks[sbresult].spells
                    return ", ".join([spell.name for spell in spellList]) if len(spellList) > 0 else "Spellbook is empty"
                else:
                    return sbresult
            text = ", ".join(spellbooks.keys())
            return text if text else "No spellbooks found"
        elif command[0] == "new":
            if command[1].isalpha():
                if command[1] not in spellbooks.keys():
                    spellbooks[command[1]] = Spellbook(command[1])
                    return "Created spellbook " + command[1]
                else:
                    return "Spellbook already exists"
            else:
                return "Please use letters exclusively for the spellbook name"
        elif command[0] == "delete":
            try:
                del spellbooks[command[1]]
                return "Deleted spellbook " + command[1]
            except:
                return "Spellbook doesn't exist"
        elif command[0] == "save":
            sbfound, sbresult = spellbookFinder(spellbooks, command[1])
            if sbfound:
                pickle.dump(spellbooks[sbresult], open("spellbooks/" + sbresult + '.pickle', 'wb'))
                return "Sucessfully saved " + sbresult
            else:
                return sbresult
        elif command[0] in ["fullsave", "saveall"]:
            for spellbook in spellbooks.keys():
                pickle.dump(spellbooks[spellbook], open("spellbooks/" + spellbook + '.pickle', 'wb'))
            return "Saved all spellbooks"
        elif command[0] == "load":
            try:
                spellbooks[command[1]] = pickle.load(open("spellbooks/" + command[1] + '.pickle', 'rb'))
                return "Sucessfully loaded " + command[1]
            except:
                return "Spellbook not found"
        elif command[0] in ["fullload", "loadall"]:
            for file in [file for file in os.listdir("spellbooks/") if os.path.isfile("spellbooks/" + file) and file[-7:] == ".pickle"]:
                spellbooks[file[:-7]] = pickle.load(open("spellbooks/" + file, 'rb'))
            return "Loaded all spellbooks"
        elif command[1] == "add":
            sbfound, sbresult = spellbookFinder(spellbooks, command[0])
            if sbfound:
                found, result = spellFinder(spells, "".join(command[2:]))
                if found:
                    spellbooks[sbresult].addSpell(result)
                    return "Added " + result.name + " to " + sbresult
                else:
                    return result
            else:
                return sbresult
        elif command[1] == "remove":
            sbfound, sbresult = spellbookFinder(spellbooks, command[0])
            if sbfound:
                found, result = spellFinder(spellbooks[sbresult].spells, "".join(command[2:]))
                if found:
                    spellbooks[sbresult].removeSpell(result)
                    return "Removed " + result.name + " from " + sbresult
                else:
                    return result
            else:
                return sbresult
        elif command[1] == "multiadd":
            sbfound, sbresult = spellbookFinder(spellbooks, command[0])
            if sbfound:
                reply = ""
                for spell in "".join(command[2:]).split("|"):
                    found, result = spellFinder(spells, spell.lower().replace(" ", "").replace("'", ""))
                    if found:
                        spellbooks[sbresult].addSpell(result)
                        reply += "Added " + result.name + " to " + sbresult + "\n"
                    else:
                        reply += result + "\n"
                return reply
            else:
                return sbresult
        elif command[1] == "multiremove":
            sbfound, sbresult = spellbookFinder(spellbooks, command[0])
            if sbfound:
                reply = ""
                for spell in "".join(command[2:]).split("|"):
                    found, result = spellFinder(spells, spell.lower().replace(" ", "").replace("'", ""))
                    if found:
                        spellbooks[sbresult].removeSpell(result)
                        reply += "Removed " + result.name + " from " + sbresult + "\n"
                    else:
                        reply += result + "\n"
                return reply
            else:
                return sbresult
        elif command[1] == "list":
            sbfound, sbresult = spellbookFinder(spellbooks, command[0])
            if sbfound:
                spellList = spellbooks[sbresult].spells
                return ", ".join([spell.name for spell in spellList]) if len(spellList) > 0 else "Spellbook is empty"
            else:
                return sbresult
        elif command[1] == "search":
            sbfound, sbresult = spellbookFinder(spellbooks, command[0])
            if sbfound:
                if len(command) > 2:
                    spellList = spellbooks[sbresult].spells
                    returnList = spellSearch(spellList, command[2:])
                    if len(returnList) == 0:
                        return "No valid spells found"
                    elif len(returnList) == 1:
                        found, result = spellFinder(spells, returnList[0])
                        return Spell.spellText(result)
                    else:
                        return ", ".join(returnList)
                else:
                    return "No filter supplied"
            else:
                return sbresult
        elif command[1] == "bulkadd":
            sbfound, sbresult = spellbookFinder(spellbooks, command[0])
            if sbfound:
                if len(command) > 2:
                    returnList = spellSearch(spells, command[2:])
                    count = 0
                    for spell in returnList:
                        found, result = spellFinder(spells, spell)
                        if found:
                            spellbooks[sbresult].addSpell(result)
                            count = count + 1
                    return "Added " + str(count) + " spell(s) to " + sbresult
                else:
                    return "No filter supplied"
            else:
                return sbresult
        elif command[1] == "bulkremove":
            sbfound, sbresult = spellbookFinder(spellbooks, command[0])
            if sbfound:
                if len(command) > 2:
                    returnList = spellSearch(spellbooks[sbresult].spells, command[2:])
                    count = 0
                    for spell in returnList:
                        found, result = spellFinder(spellbooks[sbresult].spells, spell)
                        if found:
                            spellbooks[sbresult].removeSpell(result)
                            count = count + 1
                    return "Removed " + str(count) + " spell(s) from " + sbresult
                else:
                    return "No filter supplied"
            else:
                return sbresult
        else:
            return "Invalid spellbook command"
    except Exception as e:
        print(e)
        return "Spellbook command exception"