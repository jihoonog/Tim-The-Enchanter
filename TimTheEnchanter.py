import copy
import discord
import json
import os
import pickle
import random
import re
import texttable
import time
from backpack import *
from spell import *
from item import *
from spellbook import *

spellsources = ["spells-ai.json", "spells-egw.json", "spells-ggr.json",
                "spells-phb.json", "spells-scag.json", "spells-xge.json"]
itemsources = ["items.json","roll20-items.json","fluff-items.json","items-base.json"]
criticaltexts = ["*Tubular!*", "*Nailed it!*", "*We did it lads!*",
                 "*We did it Reddit*", "critxyz", "*UwU*", "*Hell yeah brother*", "*God Bless America*"]
failtexts = ["*That's a real ouchy bro*", "*That's a real kick in the knackers bro*", "*The Dark Elf laughs at your misfortune*", "*Big oof.*",
             "*No says the man in red*", "*That was a CRIT (ical fail)*", "You crit shit the bed", "failxyz", "*UwU*", "*Welcome to Trump's America*", "*You hate to see it happen*"]


def manpage():
    return """
Commands:
**Rolls**: e.x. roll|r 8d8 + 6d6 - 2d4 + 3 - 1
**Critical Rolls**: e.x. croll|cr 8d8 + 6d6 - 2d4 + 3 - 1
**Spellbook**: sp []
**Backpack**: bp []
**Querying Spells**: search [help|random]
**Items**: item[random|new|delete|save|reload]
**Spells**: <Spell's name>  
"""


def parseDice(rolls, multiplier, user, diceStats, diceStatsDaily):
    try:
        simpleroll = True
        extras = ""
        sum = 0
        results = []
        rolls = rolls.replace(" ", "").replace("-", "+-").split("+")
        for roll in rolls:
            if "d" in roll:
                sign = 1
                if roll[0] == "-":
                    roll = roll[1:]
                    sign = -1
                count, die = int(roll[:roll.index("d")] if roll.index(
                    "d") > 0 else 1), roll[(roll.index("d")+1):]

                dropHigh = "0"
                dropLow = "0"
                if "d" in die:
                    die, dropLow = die[:die.index(
                        "d")], die[(die.index("d")+1):]
                if "D" in die:
                    die, dropHigh = die[:die.index(
                        "D")], die[(die.index("D")+1):]
                if "D" in dropLow:
                    dropLow, dropHigh = dropLow[:dropLow.index(
                        "D")], dropLow[(dropLow.index("D")+1):]

                dropHigh = int(dropHigh)
                dropLow = int(dropLow)
                die = int(die)

                if ((count-dropHigh)-dropLow) != 1 or die != 20:
                    simpleroll = False
                subresults = list()
                for i in range((multiplier if sign == 1 else 1) * count):
                    num = random.randrange(die) + 1
                    if die == 20:
                        if user not in diceStats:
                            diceStats[user] = [0]*5
                        if user not in diceStatsDaily:
                            diceStatsDaily[user] = [0]*5

                        diceStats[user][3] += num
                        diceStats[user][4] += 1
                        diceStats[user][0] = diceStats[user][3] / \
                            diceStats[user][4]
                        if num == 20:
                            diceStats[user][1] += 1
                        elif num == 1:
                            diceStats[user][2] += 1

                        diceStatsDaily[user][3] += num
                        diceStatsDaily[user][4] += 1
                        diceStatsDaily[user][0] = diceStatsDaily[user][3] / \
                            diceStatsDaily[user][4]
                        if num == 20:
                            diceStatsDaily[user][1] += 1
                        elif num == 1:
                            diceStatsDaily[user][2] += 1

                    subresults.append(num)
                    sum += sign * num

                subresults.sort(reverse=True)

                subtotal = 0

                for index in range(len(subresults)):
                    if index < dropHigh:
                        sum -= sign*subresults[index]
                        subresults[index] = str(subresults[index])
                    elif index >= len(subresults) - dropLow:
                        sum -= sign*subresults[index]
                        subresults[index] = str(subresults[index])
                    else:
                        if simpleroll:
                            if subresults[index] == 20:
                                extras = random.choice(criticaltexts)
                            if subresults[index] == 1:
                                extras = random.choice(failtexts)
                        subtotal += subresults[index]
                        subresults[index] = "**" + \
                            str(subresults[index]) + "**"
                subresults.append("(" + str(subtotal) + ")")
                results.append(subresults)
            elif roll == "":
                pass
            else:
                sum += int(roll)
                results.append(roll)
        finalresults = []
        for index in range(len(results)):
            finalresults.append(
                ((str(rolls[index]) + ": ") if "d" in rolls[index] else "") + ", ".join(results[index]))
        if simpleroll and extras != "":
            finalresults.append(extras)
        return ("**Crit** " if multiplier == 2 else "") + "**Result:** " + str(sum) + " (" + str(sum//2) + ")\n" + "\n".join(finalresults)
    except Exception as e:
        print(e)
        return "Dice roll command exception"


def evaluateStats(diceStats, server):
    table = texttable.Texttable()
    table.add_row(["Person", "Average", "20s", "1s", "Total", "Rolls"])
    for user in diceStats.keys():
        if user[0] == server:
            row = [user[1]]
            row.extend(diceStats[user])
            table.add_row(row)
    return "`" + table.draw() + "`"


def runServer():
    spells = []
    for source in spellsources:
        with open("spell_data/{}".format(source)) as f:
            spells.extend([Spell(spell) for spell in json.load(f)])
    print("Loaded", len(spells), "spells")

    spellbooks = dict()
    for file in [file for file in os.listdir("spellbooks/") if os.path.isfile("spellbooks/" + file) and file[-7:] == ".pickle"]:
        spellbooks[file[:-7]] = pickle.load(open("spellbooks/" + file, 'rb'))
    print("Loaded", len(spellbooks.keys()), "spellbooks")

    diceStats = dict()
    try:
        with open("stats.pickle", "rb") as f:
            diceStats = pickle.load(f)
    except:
        diceStats = dict()
    diceStatsDaily = dict()

    itemsjson = None
    items = []
    for source in itemsources:
        with open("item_data/{}".format(source)) as f:
            itemsjson = json.load(f)
        items.extend([Item(item) for item in itemsjson["item"]])
    print("Loaded", len(items), "items")

    backpacks = dict()
    for file in [file for file in os.listdir("backpacks/") if os.path.isfile("backpacks/" + file) and file[-7:] == ".pickle"]:
        backpacks[file[:-7]] = pickle.load(open("backpacks/" + file, 'rb'))
    print("Loaded", len(backpacks.keys()), "backpacks")

    token = open("token.txt").readline().strip()
    print("Loaded token", token)

    client = discord.Client()
    print("Loaded client")

    startuptime = time.time()

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        if time.time() - startuptime > 86400:
            await message.channel.send("Please wait for me to reboot, then query me again.")
            for spellbook in spellbooks.keys():
                pickle.dump(spellbooks[spellbook], open(
                    "spellbooks/" + spellbook + '.pickle', 'wb'))
            for backpack in backpacks.keys():
                pickle.dump(backpacks[backpack], open(
                    "backpacks/" + backpack + '.pickle', 'wb'))
            with open("items.json", "w") as f:
                json.dump(itemsjson, f, indent=4)
            with open("stats.pickle", "wb") as f:
                pickle.dump(diceStats, f)
            client.logout()
            client.close()
            quit()

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

        if message.content[:7].lower() == "manpage":
            toSend = manpage()

        elif message.content[:4].lower() == "roll":
            toSend = parseDice(message.content[4:], 1, (str(message.guild), str(
                message.author.nick)), diceStats, diceStatsDaily)

        elif message.content[:2].lower() == "r ":
            toSend = parseDice(message.content[2:], 1, (str(message.guild), str(
                message.author.nick)), diceStats, diceStatsDaily)

        elif message.content[:5].lower() == "croll":
            toSend = parseDice(message.content[5:], 2, (str(message.guild), str(
                message.author.nick)), diceStats, diceStatsDaily)

        elif message.content[:3].lower() == "cr ":
            toSend = parseDice(message.content[2:], 2, (str(message.guild), str(
                message.author.nick)), diceStats, diceStatsDaily)

        elif message.content[:6].lower() == "random":
            for x in range(int(message.content[6:]) if message.content[6:] else 1):
                toSend += random.choice(spells).spellText() + "\n\n"

        elif message.content[:2].lower() == "sb":
            toSend = spellbookParser(
                spells, spellbooks, message.content[2:].lower().split())

        elif message.content[:2].lower() == "bp":
            toSend = backpackParser(
                items, backpacks, message.content[2:].split())

        elif message.content[:5].lower() == "stats":
            toSend = evaluateStats(diceStats, str(message.guild))

        elif message.content[:5].lower() == "daily":
            toSend = evaluateStats(diceStatsDaily, str(message.guild))

        elif message.content.lower().replace(" ", "") == "whoareyou?":
            toSend = "There are some who call me... ***Tim***"

        elif message.content.lower().replace(" ", "") == "gotosleeptim":
            if "admin" in [name.lower() for name in map(str, message.author.roles)]:
                await message.channel.send("Ok, Good Night")
                for spellbook in spellbooks.keys():
                    pickle.dump(spellbooks[spellbook], open(
                        "spellbooks/" + spellbook + '.pickle', 'wb'))
                for backpack in backpacks.keys():
                    pickle.dump(backpacks[backpack], open(
                        "backpacks/" + backpack + '.pickle', 'wb'))
                with open("items.json", "w") as f:
                    json.dump(itemsjson, f, indent=4)
                with open("stats.pickle", "wb") as f:
                    pickle.dump(diceStats, f)
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
                returnList = spellSearch(
                    spells, message.content[6:].lower().split())
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

            elif message.content[:7].lower() == "itemnew":
                success, result = itemBuilder(message.content[7:])
                if success:
                    itemsjson["item"].append(result)
                    items.append(Item(result))
                    toSend = result["name"] + " created"
                else:
                    toSend = result

            elif message.content[:10].lower() == "itemdelete":
                try:
                    for item in itemsjson["item"]:
                        if item["name"] == message.content[10:].strip():
                            del item
                    toSend = "Item deleted"
                except:
                    toSend = "Delete failed"

            elif message.content[:8].lower() == "itemsave":
                try:
                    with open("items.json", "w") as f:
                        json.dump(itemsjson, f, indent=4)
                    toSend = "Saved items"
                except:
                    toSend = "Failed to save items"

            elif message.content.lower() == "itemreload":
                del items[:]
                items.extend([Item(item) for item in itemsjson["item"]])
                toSend = "Items reloaded"

            else:
                found, result = itemFinder(items, message.content[4:])
                if found:
                    toSend = result.fullText()
                else:
                    toSend = result

        elif message.content[:5].lower() == "spell":
            found, result = spellFinder(spells, message.content[5:])
            if found:
                toSend = result.spellText()
            else:
                toSend = result

        print("Responding With:", toSend)
        if toSend == "":
            await message.channel.send("Can't find spell, spellbook or command")
            return
        elif len(toSend) < 2000:
            if toSend[-7:] == "failxyz":
                await message.channel.send(toSend[:-7])
                await message.channel.send(file=discord.File("fail.png"))
            elif toSend[-7:] == "critxyz":
                await message.channel.send(toSend[:-7])
                await message.channel.send(file=discord.File("crit.gif"))
            else:
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
