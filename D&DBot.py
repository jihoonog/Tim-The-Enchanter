import discord, json, random, re

schools = {"A":"Abjuration", "C":"Conjuration", "D":"Divination", "E":"Enchantment", "V":"Evocation", "I":"Illusion", "N":"Necromancy", "T":"Transmutation"}

def cleanText(text):
    p = re.compile(r'<.*?>')
    return p.sub('', text)

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

        if message.content.startswith("roll"):
            try:
                command = message.content[4:]
                count, die = int(command[:command.index("d")]), int(command[(command.index("d")+1):])
                rolls = list()
                sum = 0
                for i in range(count):
                    roll = random.randrange(die) + 1
                    rolls.append(roll)
                    sum += roll
                toSend = "Result: " + str(sum) + "\n" + str(rolls)
            except:
                await client.send_message(channel, "Unknown Roll Command")
                return

        elif message.content.lower() in ["random", "r"]:
            toSend = spellText(randomSpell(spells))

        else:
            savedSpell = ""
            for spell in spells:
                if spell["name"].lower().replace("'", "").replace(" ", "") == message.content.lower().replace("'", "").replace(" ", ""):
                    toSend = spellText(spell)
                    break
                elif message.content.lower().replace("'", "").replace(" ", "") in spell["name"].lower().replace("'", "").replace(" ", ""):
                    if toSend == "":
                        toSend = spellText(spell)
                        savedSpell = spell["name"]
                    elif toSend[-2:] == "? ":
                        toSend = toSend + spell["name"] + "? "
                    else:
                        toSend = savedSpell + "? " + spell["name"] + "? "

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
