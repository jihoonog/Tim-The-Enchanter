import discord, json, random, re

schools = {"A":"Abjuration", "C":"Conjuration", "D":"Divination", "E":"Enchantment", "V":"Evocation", "I":"Illusion", "N":"Necromancy", "T":"Transmutation"}

class Spellbook:
    spells = list()
    def __init__(self, owner):
        self.name = name

    def listSpells(self):
        return spells

    def spellNames(self):
        text = ""
        for spell in spells:
            text = text + spell["name"] + ", "
        return text

    def addSpell(self):
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

def parseDice(rolls, multiplier):
    try:
        sum = 0
        results = list()
        rolls = rolls.replace(" ", "").replace("-", "+-").split("+")
        for roll in rolls:
            if "d" in roll:
                if roll[0] == "-":
                    roll = roll[1:]
                    count, die = int(roll[:roll.index("d")] if roll.index("d") > 0 else 1), int(roll[(roll.index("d")+1):])
                    subresults = list()
                    for i in range(count):
                        num = random.randrange(die) + 1
                        subresults.append(num)
                        sum -= num
                    results.append(subresults)
                else:
                    count, die = int(roll[:roll.index("d")] if roll.index("d") > 0 else 1), int(roll[(roll.index("d")+1):])
                    subresults = list()
                    for i in range(count):
                        num = random.randrange(die) + 1
                        subresults.append(num)
                        sum += 2 * num
                    results.append(subresults)
            elif roll == "":
                pass
            else:
                sum += int(roll)
                results.append(roll)
        finalresults = list()
        for result in results:
            finalresults.append(str(result))
        return "**Result:** " + str(sum) + " (" + str(sum//2) + ")\n" + "\n".join(finalresults)
    except:
        return "Invalid dice roll command"

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
    spells = json.load(open("spells.json"))
    print("Loaded all availible spells")

    spells = [spell for spell in spells if spell["source"] == "PHB" or spell["source"] == "XGE"]
    print("Filtered to Player's Hand Book and Xanathar's Guide To Everything")

    token = "NDg3ODAzODkwNDExMjQxNDgy.DnUGPQ.g7DNgBqhJqhnJ5XVY2Ci_eWrEB8"
    client = discord.Client()
    print("Client delared")

    @client.event
    async def on_message(message):
        channel = message.channel

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

        else:
            found, result = spellFinder(spells, message.content)
            if found:
                toSend = spellText(result)
            else:
                toSend = result

        print("Responding With:", toSend)
        if toSend == "":
            await client.send_message(channel, "Can't find spell or command")
            return
        elif len(toSend) < 2000:
            await client.send_message(channel, toSend)
        else:
            msgs = list()
            while (len(toSend) >= 2000):
                front, toSend = toSend[:1980], toSend[1980:]
                msgs.append(front)
            msgs.append(toSend)
            for msg in msgs:
                await client.send_message(channel, msg)

    @client.event
    async def on_ready():
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')

    print("events loaded")

    client.run(token)
    print("Done")

if __name__ == "__main__":
    runServer()
