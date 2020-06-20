from parsers import *

class Feat:
    def __init__(self, feat):
        self.fullString = str(feat)
        self.id = feat["name"].lower().replace(" ", "").replace("'", "")
        self.attrlist = set(['prerequisite', "ability"])
        for k, v in feat.items():
            if k in ['prerequisite', 'ability']:
                continue
            elif k == "entries":
                self.entries = entriesParsingFeats(v)
                self.attrlist.add("entries")
            else:
                self.attrlist.add(k)
                setattr(self, k, v)

        if 'ability' in feat:
            for ab in feat['ability']:
                if 'choose' in ab:
                    self.ability = ', '.join(ab['choose']['from']) + ", choose one to increase by one"
                else:
                    self.ability = ', '.join(ab.keys()) + " increase by one"
            self.attrlist.add('ability')
        else:
            self.ability = ""

        try: 
            for prereq in feat['prerequisite']:
                if 'race' in prereq:
                    name = "race: "
                    for race in prereq['race']:
                        name = name + race['name']
                        if 'subrace' in race:
                            name = name + '-' + race['subrace']
                        name += ', '
                    self.prereq_races = name
                    self.attrlist.add("prereq_races")

                if 'ability' in prereq:
                    abl = "ability: "
                    for ability in prereq['ability']:
                        abl = abl + str(ability) + ', '
                    self.prereq_ability = abl
                    self.attrlist.add('prereq_ability')

                if 'other' in prereq or 'spellcasting' in prereq:
                    self.prereq_other = "See Source Material"
                    self.attrlist.add('prereq_other')

        except:
            self.prereq = ""

    def editAttr(self, key, value):
        setattr(self, key, value)
        self.attrlist.add(key)

    def removeAttr(self, key):
        self.attrlist.discard(key)

    def debugText(self):
        return "\n".join([str(k) + ": " + str(vars(self)[k]) for k in vars(self).keys()])

    def fullText(self):
        text = ""
        text += "**Name**: " + self.name + "\n"
        if "entries" in self.attrlist or "description" in self.attrlist:
            text += "**Description**: "
            if "entries" in self.attrlist:
                text += self.entries + "\n"
        if 'prerequisite' in self.attrlist:
            text += "**Prerequisite**: "
            if 'prereq_races' in self.attrlist:
                text += self.prereq_races + "\n"
            if 'prereq_ability' in self.attrlist:
                text += self.prereq_ability + "\n"
            if 'prereq_other' in self.attrlist:
                text += self.prereq_other + '\n'
            text += '\n'
        if 'ability' in self.attrlist:
            text += "**Ability**: "
            text += self.ability + '\n'
        for x in self.attrlist:
            if x in ["name", "entries", "description", 'prerequisite', 'prereq_races', 'prereq_ability', 'prereq_other', 'ability']:
                continue
            else:
                text += "**" + x + "**: " + str(getattr(self, x)) + "\n"
        return text

def featFinder(feats, itemName):
    savedItem = None
    text = []
    for feat in feats:
        if feat.id == itemName.lower().replace("'", "").replace(" ", ""):
            return True, feat
        elif itemName.lower().replace("'", "").replace(" ", "") in feat.id:
            if "hidden" in feat.attrlist and feat.hidden == "True":
                continue
            if not savedItem:
                savedItem = feat
            else:
                text.append(feat.name)
    if not savedItem:
        return False, "Feat not found"
    elif text == []:
        return True, savedItem
    else:
        text.append(savedItem.name)
        return False, "? ".join(sorted(text)) + "?"

def featBuilder(text):
    segments = text.split("|")
    feat = dict()
    for attr in segments:
        try:
            key, value = attr.split(":")
            feat[key.lower().replace(" ", "")] = value
        except:
            print("Error", attr)
    if "name" not in feat.keys():
        return False, "Missing Name"
    else:
        return True, feat
