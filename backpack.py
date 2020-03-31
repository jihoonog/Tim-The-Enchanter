import copy, pickle, os

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


class Backpack:
    def __init__(self, name, strength, hidden):
        self.itemlist = []
        self.name = name
        self.strength = strength
        self.hidden = hidden
        self.pp = 0
        self.gp = 0
        self.ep = 0
        self.sp = 0
        self.cp = 0
        self.foodcount = 0
        self.weight = 0

    def shiftDown(self):
        types = ["cp", "sp", "gp", "pp"]
        for i in range(3):
            while getattr(self, types[i]) < 0:
                setattr(self, types[i+1], getattr(self, types[i+1])-1)
                setattr(self, types[i], getattr(self, types[i])+10)
        self.weigh()
        return "Made change"

    def shiftUp(self):
        types = ["cp", "sp", "gp", "pp"]
        for i in range(3):
            while getattr(self, types[i]) > 9:
                setattr(self, types[i+1], getattr(self, types[i+1])+1)
                setattr(self, types[i], getattr(self, types[i])-10)
        self.weigh()
        return "Condensed money"

    def buy(self, itemName, items):
        found, result = itemFinder(items, itemName)
        if found:
            if (self.cp + (self.sp*10) + (self.gp*100) + (self.pp*1000)) >= result.value:
                self.cp -= result.value
                self.shiftDown()
                found2, result2 = itemFinder(self.itemlist, result.name)
                if found2:
                    if "quantity" in result2.attrlist:
                        result2.quantity = int(result2.quantity) + 1
                    else:
                        result2.editAttr("quantity", 2)
                else:
                    self.itemlist.append(copy.deepcopy(result))
                self.weight += result.weight
                self.itemlist.sort(key=lambda x:x.name)
                return "Purchased " + result.name
            else:
                return "Insufficient Funds"
        else:
            return result

    def find(self, itemName, items):
        found, result = itemFinder(items, itemName)
        if found:
            found2, result2 = itemFinder(self.itemlist, result.name)
            if found2:
                if "quantity" in result2.attrlist:
                    result2.quantity = int(result2.quantity) + 1
                else:
                    result2.editAttr("quantity", 2)
            else:
                self.itemlist.append(copy.deepcopy(result))
            self.weight += result.weight
            self.itemlist.sort(key=lambda x:x.name)
            return "Added " + result.name
        else:
            return result

    def bulkfind(self, itemNames, items):
        text = ""
        for item in itemNames:
            text += self.find(item, items) + "\n"
        return text

    def sell(self, itemName):
        found, result = itemFinder(self.itemlist, itemName)
        if found:
            if "quantity" in result.attrlist and result.quantity > 1:
                result.quantity = int(result.quantity) - 1
            else:
                self.itemlist.remove(result)
            value = result.value
            if result.type not in ["$", "TG"]:
                value == value // 2
            text = "Sold " + result.name + " for " + str(float(value)/100) + "gp"
            while value >= 1000:
                value -= 1000
                self.pp += 1
            while value >= 100:
                value -= 100
                self.gp += 1
            while value >= 10:
                value -= 10
                self.sp += 1
            self.cp += value
            self.weigh()
            return text
        else:
            return result

    def ditch(self, itemName):
        found, result = itemFinder(self.itemlist, itemName)
        if found:
            if "quantity" in result.attrlist and int(result.quantity) > 1:
                result.quantity = int(result.quantity) - 1
            else:
                self.itemlist.remove(result)
            self.weight -= result.weight
            return "Removed " + result.name
        else:
            return result

    def money(self, change):
        values = change.split()
        for v in values:
            try:
                sign = 1 if v[:1] == "-" else -1
                v = v[1:]
                coin = v[-2:]
                v = v[:-2]
                amount = int(v) * sign
                setattr(self, coin, getattr(self, coin) + amount)
            except:
                pass
        self.weigh()
        return "Changed money"

    def move(self, itemName, destination):
        found, result = itemFinder(self.itemlist, itemName)
        if found:
            self.itemlist.remove(result)
            destination.itemlist.append(result)
            destination.weigh()
            self.weigh()
            return "Moved " + result.name + " to " + destination.name
        else:
            return result

    def edit(self, itemName, attributes):
        found, result = itemFinder(self.itemlist, itemName)
        if found:
            attributes = attributes.split("|")
            for a in attributes:
                try:
                    key, value = a.split(":")
                    result.editAttr(key, value)
                except Exception as e:
                    print(e)
            result.weight = float(result.weight)
            self.weigh()
            return result.itemText()
        else:
            return result

    def use(self, itemName):
        found, result = itemFinder(self.itemlist, itemName)
        if found:
            if "uses" in result.attrlist:
                setattr(result, "uses", int(getattr(result, "uses"))-1)
                return str(getattr(result, "uses")) + " uses left"
            elif "quantity" in result.attrlist and int(result.quantity) > 1:
                result.quantity = int(result.quantity)-1
                return str(result.quantity) + " left"
            else:
                return self.ditch(result.name)
        else:
            return result

    def weigh(self):
        self.weight = 0.0
        self.weight += (self.pp+self.gp+self.ep+self.sp+self.cp)*0.02
        self.weight += self.foodcount * 2.0
        for item in self.itemlist:
            self.weight += item.weight * (int(item.quantity) if "quantity" in item.attrlist else 1)
        return str(self.weight) + " pounds of weight. (Encumberance Capacity: " + str(self.strength*5) + " pounds)"

    def food(self, command):
        action = command.split()
        if action[0] == "eat":
            if self.foodcount > 0:
                self.foodcount -= 1
                self.weight -= 2
                return "Ate food. " + str(self.foodcount) + " left"
            else:
                return "No food"
        elif action[0] == "buy":
            count = int(action[1])
            if (self.cp + (self.sp*10) + (self.gp*100) + (self.pp*1000)) >= count*50:
                self.foodcount += count
                self.cp -= count*50
                self.shiftDown()
                self.weigh()
                return "Bought " + str(count) + " food"
        elif action[0] == "add":
            count = int(action[1])
            self.foodcount += count
            self.weigh()
            return "Added " + str(count) + " food"

    def list(self):
        return str(self.pp) + "pp " + str(self.gp) + "gp " + str(self.ep) + "ep " + str(self.sp) + "sp " + str(self.cp) + "cp " + str(self.foodcount) + " food\n" + ", ".join([item.name + (" x" + str(item.quantity) if "quantity" in item.attrlist else "") for item in self.itemlist]) + "\nWeight: " + str(self.weight) + " (Encumberance Capacity: " + str(self.strength*10) + " pounds)"

    def info(self, itemName):
        self.weigh()
        found, result = itemFinder(self.itemlist, itemName)
        if found:
            return result.fullText()
        else:
            return result

def backpackFinder(backpacks, backpackName):
    savedBackpack = None
    text = []
    for backpack in backpacks.keys():
        if backpack.lower().replace("'", "").replace(" ", "") == backpackName.lower().replace("'", "").replace(" ", ""):
            return True, backpack
        elif backpackName.lower().replace("'", "").replace(" ", "") in backpack.lower().replace("'", "").replace(" ", ""):
            if backpacks[backpack].hidden:
                continue
            if not savedBackpack:
                savedBackpack = backpack
            else:
                text.append(backpack)
    if not savedBackpack:
        return False, "Backpack not found"
    elif text == []:
        return True, savedBackpack
    else:
        text.append(savedBackpack)
        return False, "? ".join(sorted(text)) + "?"

def backpackParser(items, backpacks, command):
    originalcommand = command.copy()
    command = [item.lower() for item in command]
    try:
        if command[0] == "list":
            if len(command) > 1:
                bpfound, bpresult = backpackFinder(backpacks, command[1])
                if bpfound:
                    return backpacks[bpresult].list()
                else:
                    return bpresult
            text = ", ".join([bp for bp in backpacks.keys() if backpacks[bp].hidden == False])
            return text if text else "No backpacks found"
        elif command[0] == "new":
            if command[1].isalpha():
                if command[1] not in backpacks.keys():
                    backpacks[command[1]] = Backpack(command[1], int(command[2]) if len(command) >= 3 else 0, True if len(command) >= 4 and command[3] == "true" else False)
                    return "Created backpack " + command[1]
                else:
                    return "Backpack already exists"
            else:
                return "Please use letters exclusively for the backpack name"
        elif command[0] == "delete":
            try:
                del backpacks[command[1]]
                return "Deleted backpack " + command[1]
            except:
                return "Backpack doesn't exist"
        elif command[0] == "save":
            bpfound, bpresult = backpackFinder(backpacks, command[1])
            if bpfound:
                pickle.dump(backpacks[bpresult], open("backpacks/" + bpresult + '.pickle', 'wb'))
                return "Sucessfully saved " + bpresult
            else:
                return bpresult
        elif command[0] in ["fullsave", "saveall"]:
            for backpack in backpacks.keys():
                pickle.dump(backpacks[backpack], open("backpacks/" + backpack + '.pickle', 'wb'))
            return "Saved all backpacks"
        elif command[0] == "load":
            try:
                backpacks[command[1]] = pickle.load(open("backpacks/" + command[1] + '.pickle', 'rb'))
                return "Sucessfully loaded " + command[1]
            except:
                return "Backpack not found"
        elif command[0] in ["fullload", "loadall"]:
            for file in [file for file in os.listdir("backpacks/") if os.path.isfile("backpacks/" + file) and file[-7:] == ".pickle"]:
                backpacks[file[:-7]] = pickle.load(open("backpacks/" + file, 'rb'))
            return "Loaded all backpacks"
        else:
            bpfound, bpresult = backpackFinder(backpacks, command[0])
            if bpfound:
                bp = backpacks[bpresult]
                if len(command) == 1:
                    return bp.list()
                elif command[1] == "list":
                    return bp.list()
                elif command[1] == "buy":
                    if command[2].isnumeric():
                        text = ""
                        for x in range(int(command[2])):
                            text = bp.buy(" ".join(command[3:]), items)
                        return text
                    else:
                        return bp.buy(" ".join(command[2:]), items)
                elif command[1] in ["add", "find"]:
                    if command[2].isnumeric():
                        text = ""
                        for x in range(int(command[2])):
                            text = bp.find(" ".join(command[3:]), items)
                        return text
                    elif command[2] == "bulk":
                        return bp.bulkfind(command[3:], items)
                    else:
                        return bp.find(" ".join(command[2:]), items)
                elif command[1] == "sell":
                    if command[2].isnumeric():
                        text = ""
                        for x in range(int(command[2])):
                            text = bp.find(" ".join(command[3:]), items)
                        return text
                    else:
                        return bp.sell(" ".join(command[2:]))
                elif command[1] in ["remove", "ditch", "delete"]:
                    if command[2].isnumeric():
                        text = ""
                        for x in range(int(command[2])):
                            text = bp.ditch(" ".join(command[3:]))
                        return text
                    else:
                        return bp.ditch(" ".join(command[2:]))
                elif command[1] == "money":
                    return Backpack.money(bp, " ".join(command[2:]))
                elif command[1] == "move":
                    return bp.move(command[2], backpacks[command[3]])
                elif command[1] == "weigh":
                    return bp.weigh()
                elif command[1] == "info":
                    return bp.info(" ".join(command[2:]))
                elif command[1] == "use":
                    return bp.use(" ".join(command[2:]))
                elif command[1] == "edit":
                    return bp.edit(originalcommand[2], " ".join(originalcommand[3:]))
                elif command[1] == "thin":
                    return bp.shiftUp()
                elif command[1] == "food":
                    return bp.food(command[2] + (" " + command[3] if len(command) > 3 else ""))
                elif command[1] == "strength":
                    bp.strength = int(command[2])
                    return "Changed strength of " + bp.name + " to " + command[2]
                else:
                    found, result = itemFinder(bp.itemlist, " ".join(command[1:]))
                    if found:
                        return result.itemText()
                    else:
                        return result
            else:
                return "Backpack not found"
    except Exception as e:
        print(e)
        return "Backpack command exception"