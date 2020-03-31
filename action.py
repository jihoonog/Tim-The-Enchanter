from parsers import *

class Action:
    def __init__(self, action):
        self.name = action["name"]
        self.id = action["name"].lower().replace(" ","")
        self.source = action["source"]
        self.page = action["page"]
        self.time = "" if "time" not in action.keys() else action["time"]
        self.entries = entriesParsing(action["entries"])

    def fullText(self):
        time_text = ""
        for time in self.time:
            if type(time) is dict:
                time_text += str(time["number"]) + " " + time["unit"] + " | "
            else:
                time_text += time + " | "
        return """
**Name:** {} 
**Time:** {}
**Description:** {}
**Source:** {} page {}
""".format(self.name, time_text[:-2], self.entries, self.source, self.page)

def actionParser(actions, action_name):
    action_name = action_name.strip()
    if action_name == "list":
        return "? ".join([action.name for action in actions])
    for action in actions:
        if action.id == action_name.lower().replace(" ",""):
            return action.fullText()
    
    return "Action not found"