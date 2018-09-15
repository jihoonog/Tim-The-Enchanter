import discord, json, os, pickle, random, re

schools = {"A":"Abjuration", "C":"Conjuration", "D":"Divination", "E":"Enchantment", "V":"Evocation", "I":"Illusion", "N":"Necromancy", "T":"Transmutation"}

class Item:
    def __init__(self, item):
        self.fullString = str(item)
        self.id = item["name"].lower().replace(" ", "").replace("'", "")
        self.attrlist = []
        for k, v in item.items():
            self.arrrlist.append(k)
            setattr(self, k, v)

    def itemText(self):
        return "\n".join([str(k) + " : " + str(getattr(self, k)) for k in self.attrlist])

class Backpack:
    def __init__(self, name):
        self.name = name
        self.items = list()
        self.weight = 0

class Spell:
    def __init__(self, spell):
        self.name = spell["name"]
        self.id = spell["name"].lower().replace(" ", "").replace("'", "")
        self.level = str(spell["level"])
        self.school = spell["school"]
        self.time = str(spell["time"][0]["number"]) + " " + spell["time"][0]["unit"]
        self.range = spell["range"]["type"]
        self.rangetype = spell["range"]["distance"]["type"]
        self.rangecount = "" if self.rangetype in ["touch", "self", "special", "sight", "unlimited"] else str(spell["range"]["distance"]["amount"])
        self.v = "V " if "v" in spell["components"].keys() else ""
        self.s = "S " if "s" in spell["components"].keys() else ""
        self.m = "M (" + spell["components"]["m"] + ")" if "m" in spell["components"].keys() else ""
        self.durationtype = spell["duration"][0]["type"]
        self.duration = self.durationtype if self.durationtype in ["instant", "permanent", "special"] else str(spell["duration"][0]["duration"]["amount"]) + " " + spell["duration"][0]["duration"]["type"]
        self.concentration = " (Concentration)" if "concentration" in spell["duration"][0].keys() else ""
        self.classes = spell["classes"]["fromClassList"]
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
        "**Components:** " + self.v + self.s + self.m + "\n" + \
        "**Duration:** " + self.duration + self.concentration + "\n" + \
        "**Description:** " + self.entries + self.entriesHL + \
        "**Classes:** " + ", ".join([c for c in ([cclass["name"] for cclass in self.classes if cclass["source"] in ["PHB", "XGE"]] + \
        ([subclass["class"]["name"] + "-" + subclass["subclass"]["name"] + ("-" + subclass["subclass"]["subSubclass"] \
        if "subSubclass" in subclass["subclass"].keys() else "") for subclass in self.subclasses \
        if subclass["class"]["source"] in ["PHB", "XGE"] and subclass["subclass"]["source"] in ["PHB", "XGE"]] \
        if self.subclasses else [])) if c]) + "\n" + \
        "**Book:** " + self.source

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

def itemFinder(items, itemName):
    savedItem = None
    text = []
    for item in items:
        if item.id == itemName.lower().replace("'", "").replace(" ", ""):
            return True, item
        elif itemName.lower().replace("'", "").replace(" ", "") in item.id:
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

def parseDice(rolls, multiplier):
    try:
        sum = 0
        results = list()
        rolls = rolls.replace(" ", "").replace("-", "+-").split("+")
        for roll in rolls:
            if "d" in roll:
                sign = 1
                if roll[0] == "-":
                    roll = roll[1:]
                    sign = -1
                count, die = int(roll[:roll.index("d")] if roll.index("d") > 0 else 1), int(roll[(roll.index("d")+1):])
                subresults = list()
                for i in range((multiplier if sign == 1 else 1) * count):
                    num = random.randrange(die) + 1
                    subresults.append(num)
                    sum += sign * num
                results.append(subresults)
            elif roll == "":
                pass
            else:
                sum += int(roll)
                results.append(roll)
        finalresults = list()
        for result in results:
            finalresults.append(str(result))
        return ("" if multiplier == 1 else "**Crit** ") + "**Result:** " + str(sum) + " (" + str(sum//2) + ")\n" + "\n".join(finalresults)
    except Exception as e:
        print(e)
        return "Dice roll command exception"

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
                        return spellText(result)
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

def componentParsing(components):
    text = ""
    materialtext = ""
    for key in components.keys():
        if isinstance(components[key], str):
            materialtext = "M (" + components[key] + ")"
        else:
            text = text + key.upper() + " "
    return text + materialtext

def entriesParsing(entries):
    text = ""
    for obj in entries:
        if isinstance(obj, str):
            text = text + obj + "\n"
        else:
            if obj["type"] == "entries":
                text = text + "**" + obj["name"] + "** - " + "\n".join(obj["entries"]) + "\n"
            else:
                text = text + "****Special, See Guide****\n"
    return text

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

def runServer():
    spells = [Spell(spell) for spell in json.load(open("spells.json")) if spell["source"] in ["PHB", "XGE"]]
    print("Loaded", len(spells), "spells")

    spellbooks = dict()
    for file in [file for file in os.listdir("spellbooks/") if os.path.isfile("spellbooks/" + file) and file[-7:] == ".pickle"]:
        spellbooks[file[:-7]] = pickle.load(open("spellbooks/" + file, 'rb'))
    print("Loaded", len(spellbooks.keys()), "spellbooks")

    items = [Item(item) for item in json.load(open("items.json"))["item"]]
    print("Loaded", len(items), "items")

    backpacks = dict()
    print("Loaded", len(backpacks.keys()), "backpacks")

    token = open("token.txt").readline().strip()
    print("Loaded token", token)

    client = discord.Client()
    print("Loaded client")

    @client.event
    async def on_message(message):

        if message.author == client.user:
            return

        elif message.content.startswith('#'):
            return

        elif len(message.embeds) > 0:
            return

        elif len(message.attachments) > 0:
            return

        elif len(message.content) == 0:
            return

        print("Got Command:", message.content)
        toSend = ""

        if message.content[:4].lower() == "roll":
            toSend = parseDice(message.content[4:], 1)

        elif message.content[:5].lower() == "croll":
            toSend = parseDice(message.content[5:], 2)

        elif message.content[:6].lower() == "random":
            for x in range(int(message.content[6:]) if message.content[6:] else 1):
                toSend += random.choice(spells).spellText() + "\n\n"

        elif message.content[:2].lower() == "sb":
            toSend = spellbookParser(spells, spellbooks, message.content[2:].lower().split())

        elif message.content.lower().replace(" ", "") == "whoareyou?":
            toSend = "There are some who call me... ***Tim***"

        elif message.content.lower().replace(" ", "") == "gotosleeptim":
            if "admin" in [name for name in map(str, message.author.roles)]:
                await message.channel.send("Ok, Good Night")
                for spellbook in spellbooks.keys():
                    pickle.dump(spellbooks[spellbook], open("spellbooks/" + spellbook + '.pickle', 'wb'))
                client.logout()
                client.close()
                quit()
            else:
                toSend = "I'm not tired"

        elif message.content[:6].lower() == "search":
            if message.content[:11].lower() == "search help":
                toSend = "**Valid Search Filters:**\nname, level, school, class, subclass, concentration, ritual, source, v, s, m\n**Usage**: \
                \nfilter=value or filter=value1|value2"
            elif message.content[:13].lower() == "search random":
                filterList = message.content[13:].lower().split()
                count = int(filterList.pop(0))
                returnList = spellSearch(spells, filterList)
                if len(returnList) == 0:
                    toSend = "No valid spells found"
                elif len(returnList) == 1:
                    found, result = spellFinder(spells, returnList[0])
                    toSend = result.spellText()
                else:
                    tempList = []
                    for x in range(count):
                         tempList.append(random.choice(returnList))
                    toSend = ", ".join(tempList)
            else:
                returnList = spellSearch(spells, message.content[6:].lower().split())
                if len(returnList) == 0:
                    toSend = "No valid spells found"
                elif len(returnList) == 1:
                    found, result = spellFinder(spells, returnList[0])
                    toSend = result.spellText()
                else:
                    toSend = ", ".join(returnList)

        elif message.content[:4].lower() == "item":
            if message.content[:10].lower() == "itemrandom":
                for x in range(int(message.content[10:]) if message.content[10:] else 1):
                    toSend += random.choice(items).itemText() + "\n\n"
            else:
                found, result = itemFinder(items, message.content[4:])
                if found:
                    toSend = result.itemText()
                else:
                    toSend = result

        else:
            found, result = spellFinder(spells, message.content)
            if found:
                toSend = result.spellText()
            else:
                toSend = result

        print("Responding With:", toSend)
        if toSend == "":
            await message.channel.send("Can't find spell, spellbook or command")
            return
        elif len(toSend) < 2000:
            await message.channel.send(toSend)
        else:
            msgs = list()
            while (len(toSend) >= 2000):
                front, toSend = toSend[:1980], toSend[1980:]
                msgs.append(front)
            msgs.append(toSend)
            for msg in msgs:
                await message.channel.send(msg)

    @client.event
    async def on_ready():
        print("Logged in as", client.user.name, client.user.id, end="\n")
        for guild in client.guilds:
            for channel in guild.channels:
                try:
                    await channel.send("There are some who call me... ***Tim***")
                except:
                    pass

    client.run(token)

if __name__ == "__main__":
    runServer()
