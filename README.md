#### Tim The Enchanter is a Discord Bot designed to play D&D.

Requires Python >=3.5 and Discord.py >=1.0

#### To run: python3 TimTheEnchanter.py

#### It expects the following files in the directory you are running from

    spells.json:

    a json file with a specific format of spells for D&D 5e

    token.txt:

    a text file with a discord bot token

    spellbooks: (a folder)

    Tim will save spellbooks to this folder in .pickle files

#### What can Tim do?

Tim will read from every chat he is in and respond to any message that doesn't begin with "#"

Tim can roll dice. (ex. "roll 8d8 +6d6 -2d4 +3 -1")

Tim knows all the spells. (from PHB and XGE, found by typing in the name or part of the name of a spell. ex. "firebolt" "Fire Bolt" "firebo")

Tim can track spellbooks. (lists of spells. ex. see sb command list)

Tim can search through the spells based on filters. (see "search level=0|1 class=wizard")

You'll need your own discord bot token if you want to use Tim.

#### I highly recommend you use this image:

![alt text](timtheenchanter.jpg "Tim The Enchanter")

#### full sb command list:

sb list

sb new _book_

sb delete _book_

sb save _book_

sb load _book_

sb saveall

sb loadall

sb _book_ list

sb _book_ add spellName

sb _book_ remove spellName

sb _book_ multiadd spellName|spellName...

sb _book_ multiremove spellName|spellName...

sb _book_ bulkadd filters

sb _book_ bulkremove filters

sb _book_ search filters


#### full filter list:

name

level

school

class

subclass

concentration

ritual

source

v

s

m
