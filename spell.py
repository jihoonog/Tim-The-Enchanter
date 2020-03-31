from parsers import *


schools = {"A":"Abjuration", "C":"Conjuration", "D":"Divination", "E":"Enchantment", "V":"Evocation", "I":"Illusion", "N":"Necromancy", "T":"Transmutation"}


class Spell:
    def __init__(self, spell):
        self.name = spell["name"]
        self.id = spell["name"].lower().replace(" ", "").replace("'", "")
        self.level = str(spell["level"])
        self.school = spell["school"]
        self.time = str(spell["time"][0]["number"]) + " " + spell["time"][0]["unit"]
        self.range = spell["range"]["type"]
        print(spell["name"])
        self.rangetype = spell["range"]["distance"]["type"]
        self.rangecount = "" if self.rangetype in ["touch", "self", "special", "sight", "unlimited"] else str(spell["range"]["distance"]["amount"])
        self.v = "V " if "v" in spell["components"].keys() else ""
        self.s = "S " if "s" in spell["components"].keys() else ""
        self.m = ""
        if "m" in spell["components"].keys():
            if type(spell["components"]["m"]) is dict:
                self.m = "M (" + spell["components"]["m"]["text"] + ")"
            else:
                self.m = "M (" + spell["components"]["m"] + ")"
        self.r = "R (" + spell["components"]["r"] + ")" if "r" in spell["components"].keys() else ""
        self.durationtype = spell["duration"][0]["type"]
        self.duration = self.durationtype if self.durationtype in ["instant", "permanent", "special"] else str(spell["duration"][0]["duration"]["amount"]) + " " + spell["duration"][0]["duration"]["type"]
        self.concentration = " (Concentration)" if "concentration" in spell["duration"][0].keys() else ""
        self.classes = spell["classes"]["fromClassList"] if "fromClassList" in spell["classes"].keys() else None
        self.subclasses = spell["classes"]["fromSubClass"] if "fromSubClass" in spell["classes"].keys() else None
        self.source = spell["source"]
        self.entries = entriesParsing(spell["entries"])
        self.entriesHL = entriesParsing(spell["entriesHigherLevel"]) if "entriesHigherLevel" in spell.keys() else ""
        self.ritual = " (Ritual)" if "meta" in spell.keys() and "ritual" in spell["meta"].keys() else ""

    def spellText(self):
        return "**Name:** " + self.name + "\n" + \
        "**Type:** Level " + self.level + " " + schools[self.school] + self.ritual + "\n" + \
        "**Casting Time:** " + self.time + "\n" + \
        "**Range:** " + self.rangecount + self.rangetype + "\n" + \
        "**Components:** " + self.v + self.s + self.m + self.r + "\n" + \
        "**Duration:** " + self.duration + self.concentration + "\n" + \
        "**Description:** " + self.entries + self.entriesHL + \
        "**Classes:** " + ", ".join([c for c in ([cclass["name"] for cclass in self.classes if cclass["source"] in ["PHB", "XGE"]] + \
        ([subclass["class"]["name"] + "-" + subclass["subclass"]["name"] + ("-" + subclass["subclass"]["subSubclass"] \
        if "subSubclass" in subclass["subclass"].keys() else "") for subclass in self.subclasses \
        if subclass["class"]["source"] in ["PHB", "XGE"] and subclass["subclass"]["source"] in ["PHB", "XGE"]] \
        if self.subclasses else [])) if c]) + "\n" + \
        "**Book:** " + self.source


def spellFinder(spells, spellName):
    savedSpell = None
    text = []
    for spell in spells:
        if spell.id == spellName.lower().replace("'", "").replace(" ", ""):
            return True, spell
        elif spellName.lower().replace("'", "").replace(" ", "") in spell.id:
            if not savedSpell:
                savedSpell = spell
            else:
                text.append(spell.name)
    if not savedSpell:
        return False, "Spell not found"
    elif text == []:
        return True, savedSpell
    else:
        text.append(savedSpell.name)
        return False, "? ".join(sorted(text)) + "?"

def spellSearchAssistant(spell, left, right):
    if left == "level":
        if spell.level != right:
            return False
    elif left == "school":
        if right not in [schools[spell.school].lower(), spell.school.lower()]:
            return False
    elif left == "source":
        if right not in spell.source.lower():
            return False
    elif left == "v":
        if right in ["t", "true"] and not spell.v:
            return False
        elif right in ["f", "false"] and spell.v:
            return False
    elif left == "s":
        if right in ["t", "true"] and not spell.s:
            return False
        elif right in ["f", "false"] and spell.s:
            return False
    elif left == "m":
        if right in ["t", "true"] and not spell.m:
            return False
        elif right in ["f", "false"] and spell.m:
            return False
    elif left == "class":
        if right not in [c["name"].lower().replace(" ", "") for c in spell.classes]:
            return False
    elif left == "subclass":
        if spell.subclasses:
            if right in [c["subclass"]["name"].lower().replace(" ", "") for c in spell.subclasses]:
                return True
            elif right in [c["subclass"]["subSubclass"].lower() for c in spell.subclasses if "subSubclass" in c["subclass"].keys()]:
                return True
            else:
                return False
        else:
            return False
    elif left == "concentration":
        if right in ["t", "true"] and not spell.concentration:
            return False
        elif right in ["f", "false"] and spell.concentration:
            return False
    elif left == "ritual":
        if right in ["t", "true"] and not spell.ritual:
            return False
        elif right in ["f", "false"] and spell.ritual:
            return False
    elif left == "name":
        if right.replace(" ", "") not in spell.id:
            return False
    return True

def spellSearch(spells, filterList):
    try:
        returnList = list()
        for spell in spells:
            valid = True
            for f in filterList:
                if "=" in f:
                    left, right = f[:f.index("=")].lower(), f[f.index("=")+1:].lower()
                    if "|" in right:
                        valid = False
                        right = right.split("|")
                        for value in right:
                            if spellSearchAssistant(spell, left, value):
                                valid = True
                                break
                        if not valid:
                            break
                    else:
                        if spellSearchAssistant(spell, left, right):
                            continue
                        else:
                            valid = False
                            break
            if valid:
                returnList.append(spell.name)
        return sorted(returnList)
    except Exception as e:
        print(e)
        return ["Filter command exception"]