import discord, json, os, pickle, random, re

schools = {"A":"Abjuration", "C":"Conjuration", "D":"Divination", "E":"Enchantment", "V":"Evocation", "I":"Illusion", "N":"Necromancy", "T":"Transmutation"}

class Spellbook:
    def __init__(self, name):
        self.name = name
        self.spells = list()

    def listSpells(self):
        return spells

    def addSpell(self, spell):
        self.spells.append(spell)
        self.spells.sort(key=lambda k: k['name'])

    def removeSpell(self, spell):
        try:
            self.spells.remove(spell)
        except:
            pass

def spellFinder(spells, spellName):
    savedSpell = None
    text = ""
    for spell in spells:
        if spell["name"].lower().replace("'", "").replace(" ", "") == spellName.lower().replace("'", "").replace(" ", ""):
            return True, spell
        elif spellName.lower().replace("'", "").replace(" ", "") in spell["name"].lower().replace("'", "").replace(" ", ""):
            if not savedSpell:
                savedSpell = spell
            else:
                text = text + spell["name"] + "? "
    if not savedSpell:
        return False, ""
    elif text == "":
        return True, savedSpell
    else:
        text = savedSpell["name"] + "? " + text
        return False, text

def spellbookFinder(spellbooks, spellbookName):
    savedSpellbook = None
    text = ""
    for spellbook in spellbooks.keys():
        if spellbook.lower().replace("'", "").replace(" ", "") == spellbookName.lower().replace("'", "").replace(" ", ""):
            return True, spellbook
        elif spellbookName.lower().replace("'", "").replace(" ", "") in spellbook.lower().replace("'", "").replace(" ", ""):
            if not savedSpellbook:
                savedSpellbook = spellbook
            else:
                text = text + spellbook + "? "
    if not savedSpellbook:
        return False, ""
    elif text == "":
        return True, savedSpellbook
    else:
        text = savedSpellbook + "? " + text
        return False, text

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
    except:
        return "Invalid dice roll command"

def spellbookParser(spells, spellbooks, command):
    try:
        if command[0] == "list":
            if len(command) > 1:
                sbfound, sbresult = spellbookFinder(spellbooks, command[1])
                if sbfound:
                    spellList = spellbooks[sbresult].spells
                    return ", ".join([spell["name"] for spell in spellList]) if len(spellList) > 0 else "Spellbook is empty"
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
            if command[1] in spellbooks.keys():
                pickle.dump(spellbooks[command[1]], open("spellbooks/" + command[1] + '.pickle', 'wb'))
                return "Sucessfully saved " + command[1]
            else:
                return "Spellbook doesn't exist"
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
                    return "Added " + result["name"] + " to " + sbresult
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
                    return "Removed " + result["name"] + " from " + sbresult
                else:
                    return result
            else:
                return sbresult
        elif command[1] == "list":
            sbfound, sbresult = spellbookFinder(spellbooks, command[0])
            if sbfound:
                spellList = spellbooks[sbresult].spells
                return ", ".join([spell["name"] for spell in spellList]) if len(spellList) > 0 else "Spellbook is empty"
            else:
                return sbresult
        else:
            return "Invalid spellbook command"
    except Exception as e:
        print(e)
        return "Spellbook command exception"

def componentParsing(components):
    text = ""
    for key in components.keys():
        if isinstance(components[key], str):
            text = text + "M (" + components[key] + ")"
        else:
            text = key.upper() + " " + text
    return text

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

def spellText(spell):
    return "**Name:** " + spell["name"] + "\n" + \
        "**Type:** Level " + str(spell["level"]) + " " + schools[spell["school"]] + "\n" + \
        "**Casting Time:** " + str(spell["time"][0]["number"]) + " " + spell["time"][0]["unit"] + "\n" + \
        "**Range:** " + \
        ("" if spell["range"]["distance"]["type"] in ["touch", "self", "special", "sight", "unlimited"] else str(spell["range"]["distance"]["amount"])) + \
        " " + spell["range"]["distance"]["type"] + "\n" + \
        "**Components:** " + componentParsing(spell["components"]) + "\n" + \
        "**Duration:** " + (spell["duration"][0]["type"] if spell["duration"][0]["type"] in ["instant", "permanent", "special"] \
        else str(spell["duration"][0]["duration"]["amount"]) + " " + spell["duration"][0]["duration"]["type"]) + "\n" + \
        "**Description:** " + entriesParsing(spell["entries"]) + \
        (entriesParsing(spell["entriesHigherLevel"]) if "entriesHigherLevel" in spell.keys() else "") + \
        "**Book:** " + spell["source"]

def randomSpell(spells):
    return random.choice(spells)

def runServer():
    spells = [spell for spell in json.load(open("spells.json")) if spell["source"] == "PHB" or spell["source"] == "XGE"]
    print("Loaded", len(spells), "spells")

    spellbooks = dict()
    for file in [file for file in os.listdir("spellbooks/") if os.path.isfile("spellbooks/" + file) and file[-7:] == ".pickle"]:
        spellbooks[file[:-7]] = pickle.load(open("spellbooks/" + file, 'rb'))
    print("Loaded", len(spellbooks.keys()), "spellbooks")

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

        print("Got Command:", message.content)
        toSend = ""

        if message.content[:4].lower() == "roll":
            toSend = parseDice(message.content[4:], 1)

        elif message.content[:5].lower() == "croll":
            toSend = parseDice(message.content[5:], 2)

        elif message.content.lower() in ["random", "r"]:
            toSend = spellText(randomSpell(spells))

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
        else:
            found, result = spellFinder(spells, message.content)
            if found:
                toSend = spellText(result)
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
