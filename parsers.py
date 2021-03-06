def entriesParsing(entries):
    text = ""
    for obj in entries:
        if isinstance(obj, str):
            text = text + obj + "\n"
        else:
            try:
                if obj["type"] == "entries":
                    text = text + "**" + obj["name"] + "** - " + "\n".join(obj["entries"]) + "\n"
                else:
                    text = text + "****Special, See Guide****\n"
            except:
                text = text + "****Special, See Guide****\n"
    return text

def entriesParsingFeats(entries):
    text = ""
    for obj in entries:
        if isinstance(obj, str):
            text = text + obj + '\n'
        else:
            try:
                if obj['type'] == 'list':
                    text = text + '**list** - ' + '\n'.join(obj['items']) + '\n'
                elif obj["type"] == "entries":
                    text = text + "**" + obj["name"] + "** - " + "\n".join(obj["entries"]) + "\n"
                else:
                    text = text + '****Special, See Guide****\n'
            except:
                text + text + "****Special, See Guide****\n"
    return text