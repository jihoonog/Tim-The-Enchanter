from parsers import *

moneyvalue = {"pp":1000, "gp":100, "ep":50, "sp":10, "cp":1}

class Item:
    def __init__(self, item):
        self.fullString = str(item)
        self.id = item["name"].lower().replace(" ", "").replace("'", "")
        self.attrlist = set(["weight", "value"])
        for k, v in item.items():
            if k in ["weight", "value", "type"]:
                continue
            elif k == "entries":
                self.entries = entriesParsing(v)
                self.attrlist.add("entries")
            else:
                self.attrlist.add(k)
                setattr(self, k, v)
        try:
            num, value = item["value"][:-2], item["value"][-2:]
            self.value = int(num) * moneyvalue[value]
        except:
            self.value = 0
        try:
            self.weight = float(item["weight"])
        except:
            self.weight = 0.0

        try:
            self.type = item["type"]
        except:
            self.type = ""

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
        if "quantity" in self.attrlist:
            text += "**Quantity**: " + str(self.quantity) + "\n"
        if self.weight > 0:
            text += "**Weight**: " + str(self.weight) + "\n"
        if self.value > 0:
            text += "**Value**: " + str(self.value/100) + "gp\n"
        if "uses" in self.attrlist:
            text += "**Uses Left**: " + str(self.uses) + "\n"
        if "entries" in self.attrlist or "description" in self.attrlist:
            text += "**Description**: "
            if "entries" in self.attrlist:
                text += self.entries + "\n"
            if "description" in self.attrlist:
                text += self.description + "\n"
        if "notes" in self.attrlist:
            text += "**Notes**: " + self.notes + "\n"
        for x in self.attrlist:
            if x in ["name", "weight", "value", "entries", "uses", "notes", "quantity", "description"]:
                continue
            else:
                text += "**" + x + "**: " + str(getattr(self, x)) + "\n"
        return text

def itemFinder(items, itemName):
    savedItem = None
    text = []
    for item in items:
        if item.id == itemName.lower().replace("'", "").replace(" ", ""):
            return True, item
        elif itemName.lower().replace("'", "").replace(" ", "") in item.id:
            if "hidden" in item.attrlist and item.hidden == "True":
                continue
            if not savedItem:
                savedItem = item
            else:
                text.append(item.name)
    if not savedItem:
        return False, "Item not found"
    elif text == []:
        return True, savedItem
    else:
        text.append(savedItem.name)
        return False, "? ".join(sorted(text)) + "?"

def itemBuilder(text):
    segments = text.split("|")
    item = dict()
    for attr in segments:
        try:
            key, value = attr.split(":")
            item[key.lower().replace(" ", "")] = value
        except:
            print("Error", attr)
    if "name" not in item.keys():
        return False, "Missing Name"
    else:
        return True, item