import discord, json, random, re

def cleanText(text):
    p = re.compile(r'<.*?>')
    return p.sub('', text)

def printSpell(spell):
    print("Name:", spell["name"], "\n")
    print("Description:", spell["desc"])
    print("Range:", spell["range"], "\n")
    print("Duration:", spell["duration"], "\n")
    print("Page:", spell["page"], spell["source"], "\n")

def printSpellDetailed(spell):
    for key in spell.keys():
        print(key, "-", spell[key])

def randomSpell(spells):
    return random.choice(spells)

def runServer():
    spells = json.load(open("spells.json"))
    print("Loaded all availible spells")

    PHBSpells = [spell for spell in spells if spell["source"] == "PHB"]
    print("Filtered to Player's Hand Book")

    for spell in PHBSpells:
        spell["desc"] = spell["desc"].replace("<p>", "").replace("</p>", "\n")
    print("Cleaned spell descriptions")

    token = "NDg3ODAzODkwNDExMjQxNDgy.DnTAOg.bBEPj7Lg7UBv9LV0_ARbQht3akI"
    client = discord.Client()
    print("Client delared")

    @client.event
    async def on_message(message):
        channel = message.channel

        print("Got Command:", message.content)
        toSend = ""

        if message.author == client.user:
            return

        elif message.content.startswith('#'):
            return

        elif message.content.startswith("roll"):
            try:
                command = message.content[4:]
                count, die = int(command[:command.index("d")]), int(command[command.index("d")+1:])
                rolls = list()
                sum = 0
                for i in range(count):
                    roll = random.randrange(die) + 1
                    rolls.append(roll)
                    sum += roll
                toSend = "Result: " + sum + "\n" + rolls

            except:
                await client.send_message(channel, "Unknown Roll Command")
                return

        elif message.content in ["random", "r", "Random"]:
            toSend = str(randomSpell(PHBSpells))

        else:
            for spell in spells:
                if spell["name"] == message.content:
                    toSend = str(spell)

        print("Responding With:", toSend)
        toSend = cleanText(toSend)
        if len(toSend) == "":
            await client.send_message(channel, "Unknown Command")
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
