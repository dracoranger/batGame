#batBot.py
#By DracoRanger
#based on chatBot by DracoRanger

#Fuck it, school demanded that I cite myself, doing it here.

import asyncio
import math
import random

import discord
from discord.ext import commands

client = discord.Client()
bot = commands.Bot(command_prefix='!', help_command = None)


config = open('botData.txt', 'r')
conf = config.readlines() #push to array or do directly
token = conf[0][:-1]
channel_id = int(conf[1][:-1])
numBats = int(conf[2][:-1])
batStupidity = float(conf[3][:-1])


#game logic
players = []
playerData = [] #currently not used.
game_started = False
house = ""

class room():
    currentPlayer = ""
    location = (0,0)
    hasPlayer = False
    hasBat = False
    canHoldPlayer = False
    description = "is a wall"
    contiguousMarker = -1000
    name = "Wall"
    batMoved = False

    currentPlayer = "none"

    def updateType(self, nam, desc):
        self.canHoldPlayer = True
        self.description = desc
        self.name = nam

    def moveTo(self, player):
        self.currentPlayer = player
        self.hasPlayer = True

    def moveFrom(self):
        ret = self.currentPlayer
        self.hasPlayer = False
        self.currentPlayer = ""
        return ret

    def moveBatTo(self):
        self.hasBat = True

    def moveBatFrom(self):
        self.hasBat = False

    def updateLocl(self, x, y):
        self.location=(x,y)

def _send_error_message(error):
    return

#discord.ext.commands.errors.command_not_found = _send_error_message

def markRooms(house, location, marker):
    currentX, currentY = location
    if house[currentX][currentY].contiguousMarker != marker and house[currentX][currentY].canHoldPlayer:
        house[currentX][currentY].contiguousMarker = marker
        markRooms(house, (currentX-1, currentY), marker)
        markRooms(house, (currentX+1, currentY), marker)
        markRooms(house, (currentX, currentY-1), marker)
        markRooms(house, (currentX, currentY+1), marker)

def generateHouse(players, numBats):
    roomNames = ["Kitchen","Bathroom","Bedroom","Living room","Hallway","Powder room","Closet","Dining room", "Library", "Pantry", "Sauna"]
    roomDescriptions = ["has a nice stove","has a shower, toilet, the works","has a four poster bed and wardrobe","has a couch and TV","has wall to all hardwood floor","has a toilet but no bathtub","'s a walk in","has a big table, and fine silverware","has a lot of books. A purple pony has built a book fort in there","has gems, hay, and other snacks", "'s 135 degrees and has a glowing rock stove"]

    sizeOfHouse = len(players)*10
    side = 1
    while side * side < sizeOfHouse:
        side = side + 1
    side = side + 1

    isValidHouse = False

    while not isValidHouse:
        house = []
        for i in range(0, side):
            house.append([room()])
            for j in range(0,side):
                house[i].append(room())

        randCutoff = sizeOfHouse/((side-1)*(side-1))
        for i in range(1, side - 1):
            for j in range(1, side - 1):
                rand = random.random()
                if rand < randCutoff:
                    num = random.randint(0,len(roomNames)-1)
                    newRoom = (roomNames[num],roomDescriptions[num])
                    house[i][j].updateType(newRoom[0],newRoom[1])
                    house[i][j].updateLocl(i,j)

        marker = 1
        for length in house:
            for width in length:
                if width.canHoldPlayer and width.contiguousMarker == -1000:
                    markRooms(house, width.location, marker)
                    marker = marker + 1

        if marker == 2:
            isValidHouse = True

    roomsWithPeople = []
    for player in players:
        notPlaced = True
        while notPlaced:
            randomX = random.randint(1,side-2)
            randomY = random.randint(1,side-2)
            if house[randomX][randomY].canHoldPlayer and not house[randomX][randomY].hasPlayer:
                house[randomX][randomY].moveTo(player)
                roomsWithPeople.append(house[randomX][randomY])
                notPlaced = False

    for bat in range(0,numBats):
        notPlaced = True
        while notPlaced:
            randomX = random.randint(1,side-2)
            randomY = random.randint(1,side-2)
            if house[randomX][randomY].canHoldPlayer and not house[randomX][randomY].hasPlayer and not house[randomX][randomY].hasBat:
                house[randomX][randomY].moveBatTo()
                notPlaced = False

    return house, roomsWithPeople

def moveInsideHouse(roomContainingPerson, house, command):
    locl = roomContainingPerson
    moveSuccessful = False
    newRoom = house[roomContainingPerson[0]][roomContainingPerson[1]]
    if command < 3:
        if command == 1:
            if house[locl[0]-1][locl[1]].canHoldPlayer and not house[locl[0]-1][locl[1]].hasPlayer:
                house[locl[0]-1][locl[1]].moveTo(house[locl[0]][locl[1]].moveFrom())
                moveSuccessful = True
                newRoom = house[locl[0]-1][locl[1]]
        else:
            if house[locl[0]+1][locl[1]].canHoldPlayer and not house[locl[0]+1][locl[1]].hasPlayer:
                house[locl[0]+1][locl[1]].moveTo(house[locl[0]][locl[1]].moveFrom())
                moveSuccessful = True
                newRoom = house[locl[0]+1][locl[1]]
    else:
        if command == 3:
            if house[locl[0]][locl[1]-1].canHoldPlayer and not house[locl[0]][locl[1]-1].hasPlayer:
                house[locl[0]][locl[1]-1].moveTo(house[locl[0]][locl[1]].moveFrom())
                moveSuccessful = True
                newRoom = house[locl[0]][locl[1]-1]
        else:
            if house[locl[0]][locl[1]+1].canHoldPlayer and not house[locl[0]][locl[1]+1].hasPlayer:
                house[locl[0]][locl[1]+1].moveTo(house[locl[0]][locl[1]].moveFrom())
                moveSuccessful = True
                newRoom = house[locl[0]][locl[1]+1]
    return moveSuccessful, newRoom

#Breath first pathfinding algorithm
def batAI(house, playerLocl, currentLocl):
    markRooms(house, currentLocl, -1)
    storage = [currentLocl]
    house[currentLocl[0]][currentLocl[1]].contiguousMarker = 0
    while storage:
        location = storage.pop(0)
        if playerLocl == location:
            lastLocl = location
            nextLocl = location
            while nextLocl != currentLocl:
                if house[nextLocl[0]-1][nextLocl[1]].contiguousMarker < house[lastLocl[0]][lastLocl[1]].contiguousMarker and house[nextLocl[0]-1][nextLocl[1]].contiguousMarker >= 0:
                    lastLocl = nextLocl
                    nextLocl = (nextLocl[0]-1, nextLocl[1])
                elif house[nextLocl[0]+1][nextLocl[1]].contiguousMarker < house[lastLocl[0]][lastLocl[1]].contiguousMarker and house[nextLocl[0]+1][nextLocl[1]].contiguousMarker >= 0:
                    lastLocl = nextLocl
                    nextLocl = (nextLocl[0]+1, nextLocl[1])
                elif house[nextLocl[0]][nextLocl[1]-1].contiguousMarker < house[lastLocl[0]][lastLocl[1]].contiguousMarker and house[nextLocl[0]][nextLocl[1]-1].contiguousMarker >= 0:
                    lastLocl = nextLocl
                    nextLocl = (nextLocl[0], nextLocl[1]-1)
                elif house[nextLocl[0]][nextLocl[1]+1].contiguousMarker < house[lastLocl[0]][lastLocl[1]].contiguousMarker and house[nextLocl[0]][nextLocl[1]+1].contiguousMarker >= 0:
                    lastLocl = nextLocl
                    nextLocl = (nextLocl[0], nextLocl[1]+1)
                else:
                    print("Made it to zero, didn't make it to correct location")
            return lastLocl
        else:
            if house[location[0]-1][location[1]].canHoldPlayer and not house[location[0]-1][location[1]].contiguousMarker >= 0:
                storage.append((location[0]-1,location[1]))
                house[location[0]-1][location[1]].contiguousMarker = house[location[0]][location[1]].contiguousMarker + 1

            if house[location[0]+1][location[1]].canHoldPlayer and not house[location[0]+1][location[1]].contiguousMarker >= 0:
                storage.append((location[0]+1,location[1]))
                house[location[0]+1][location[1]].contiguousMarker = house[location[0]][location[1]].contiguousMarker + 1

            if house[location[0]][location[1]-1].canHoldPlayer and not house[location[0]][location[1]-1].contiguousMarker >= 0:
                storage.append((location[0],location[1]-1))
                house[location[0]][location[1]-1].contiguousMarker = house[location[0]][location[1]].contiguousMarker + 1

            if house[location[0]][location[1]+1].canHoldPlayer and not house[location[0]][location[1]+1].contiguousMarker >= 0:
                storage.append((location[0],location[1]+1))
                house[location[0]][location[1]+1].contiguousMarker = house[location[0]][location[1]].contiguousMarker + 1



def moveBat(house, target, bat):
    move = batAI(house, target.location, bat.location)

    if random.random() < batStupidity:  #Random directions, might make too annoying
        movement = random.randint(1,4)
        if movement == 1 and house[bat.location[0]+1][bat.location[1]].canHoldPlayer and not house[bat.location[0]+1][bat.location[1]].hasBat:
            move = (bat.location[0]+1, bat.location[1])
        if movement == 2 and house[bat.location[0]-1][bat.location[1]].canHoldPlayer and not house[bat.location[0]-1][bat.location[1]].hasBat:
            move = (bat.location[0]-1, bat.location[1])
        if movement == 3 and house[bat.location[0]][bat.location[1]+1].canHoldPlayer and not house[bat.location[0]][bat.location[1]+1].hasBat:
            move = (bat.location[0], bat.location[1]+1)
        if movement == 4 and house[bat.location[0]][bat.location[1]-1].canHoldPlayer and not house[bat.location[0]][bat.location[1]-1].hasBat:
            move = (bat.location[0], bat.location[1]-1)

    print(move)
    bat.moveBatFrom()
    house[move[0]][move[1]].moveBatTo()
    house[move[0]][move[1]].batMoved = True


def resetBat(house, numBats):
    side = len(house)
    for bat in range(0,numBats):
        notPlaced = True
        while notPlaced:
            randomX = random.randint(1,side-1)
            randomY = random.randint(1,side-1)
            if house[randomX][randomY].canHoldPlayer and not house[randomX][randomY].hasPlayer and not house[randomX][randomY].hasBat:
                #print(randomX)
                #print(randomY)
                house[randomX][randomY].moveBatTo()
                notPlaced = False

def getSurroundings(house, room):
    message = str(room.location)
    message = message + "\nTo the north there is a " + house[room.location[0]-1][room.location[1]].name + ". It " + house[room.location[0]-1][room.location[1]].description
    message = message + "\nTo the south there is a " + house[room.location[0]+1][room.location[1]].name + ". It " + house[room.location[0]+1][room.location[1]].description
    message = message + "\nTo the west there is a " + house[room.location[0]][room.location[1]-1].name + ". It " + house[room.location[0]][room.location[1]-1].description
    message = message + "\nTo the east there is a " + house[room.location[0]][room.location[1]+1].name + ". It " + house[room.location[0]][room.location[1]+1].description +"\n"
    return message

def print_house(house):
    final = "```"
    for i in house:
        for j in i:
            if j.name == "Wall":
                final = final + "#"
            elif j.hasPlayer:
                final = final + j.currentPlayer.name[:1]
            #elif j.hasBat: #debug, comment out before using on prod
            #    final = final + "b"
            else:
                final = final + "."
        final = final + "\n"
    final = final + "```"
    return(final)

def find_player(player, house):
    for length in house:
        for width in length:
            if player == width.currentPlayer:
                return width

@client.event
async def on_ready():
    global channel_id
    print('Logged in as ' + client.user.name)
    print('------')
    message = client.user.name + " is up and running!"
    await client.get_channel(channel_id).send(message)

@client.event
@asyncio.coroutine
async def on_message(message):
    global house
    global playerData
    global players
    global game_started

    JOIN = "JOIN"
    START_GAME = "START"
    GET_HOUSE_MAP = "HOUSE"
    RESTART = "RESTART"
    HELP = "HELP"
    MOVE = "MOVE"
    CATCH = "CATCH"
    BAT_TURN = "MANGO"

    command = ""
    killIt = 0

    if message.author == client.user:
        return
    elif message.content.startswith('!'):
        command = message.content.split(" ")[0][1:].upper()
    else:
        killIt = killIt + 1

    #Message to everyone
    if command == HELP:
        help_reply = ""
        help_reply = help_reply + "**Start** - after everyone has joined type !start in the main channel\n"
        help_reply = help_reply + "**Join** - type !join in the main channel\n"
        help_reply = help_reply + "**Restart** - type !restart in the main channel\n"
        help_reply = help_reply + "**Get the Map** - !house in a DM\n"
        help_reply = help_reply + "**Move** - !move [1. North, 2. South, 3. West, 4. East], so !move 1 will move north, in a DM\n"
        help_reply = help_reply + "**Catch** - !catch attempts to catch the bat, in the main channel\n"
        help_reply = help_reply + "**Attract bat** - !mango in the main channel\n"
        await message.author.send(help_reply)
        return

    if message.channel == client.get_channel(channel_id) and message.content.startswith('!'):
        if command == JOIN and not game_started:
            if message.author not in players:
                players.append(message.author)
            await client.get_channel(channel_id).send("Got it! " + message.author.name +" has joined!")

        elif command == START_GAME and not game_started and players != []:
            house, playerData = generateHouse(players, numBats)
            for length in house:
                for width in length:
                    if width.hasPlayer:
                        #send description of location
                        message = getSurroundings(house, width)
                        #send message in a DM
                        await width.currentPlayer.send(message)
            game_started = True
            await client.get_channel(channel_id).send("Starting the game!")
            await client.get_channel(channel_id).send(print_house(house))

        elif command == RESTART and game_started:
            house = ""
            playerData = []
            players = []
            game_started = False
            await client.get_channel(channel_id).send("Restarted")

        elif command == BAT_TURN and game_started:
            called_width = ""

            for bat_length in house:  #clear board
                for bat_width in bat_length:
                    bat_width.batMoved = False

            for length in house: #find calling player
                for width in length:
                    if message.author == width.currentPlayer:
                        called_width = width

            for length in house: #Make noise
                for width in length:
                    if width.hasPlayer:
                        for bat_length in house:
                            for bat_width in bat_length:
                                if bat_width.hasBat:
                                    distance = math.sqrt((width.location[0] - bat_width.location[0])**2 + (width.location[1] - bat_width.location[1])**2)
                                    message = "You heard nothing in reply"
                                    if distance == 0:
                                        message = "CHOMP \nThe bat ate your mango and ran off"
                                        for bat_length_rem in house: #Move bats
                                            for bat_width_rem in bat_length_rem:
                                                bat_width_rem.moveBatFrom()
                                        resetBat(house, numBats)
                                        await width.currentPlayer.send(message)
                                        return
                                    elif distance < 2:
                                        message = "EEEEE"
                                    elif distance < 4:
                                        message = "eeeee"
                                    elif distance < 6:
                                        message = "....."
                                    await width.currentPlayer.send(message)

            for bat_length in house: #Move bats
                for bat_width in bat_length:
                   if bat_width.hasBat and not bat_width.batMoved:
                       distance = math.sqrt((width.location[0] - bat_width.location[0])**2 + (width.location[1] - bat_width.location[1])**2)
                       if distance < 6:
                           moveBat(house, called_width, bat_width)

        elif command == CATCH:
            width = find_player(message.author, house)
            caughtBat = house[width.location[0]][width.location[1]].hasBat
            if caughtBat:
                await client.get_channel(channel_id).send("Victory!  You caught the bat")
                width.moveBatFrom()
                resetBat(house, numBats)
            else:
                await client.get_channel(channel_id).send("swing and miss")
            validCommand = True
        else:
            await client.get_channel(channel_id).send("Invalid Command " + str(command))
    #message thru DM
    elif isinstance(message.channel, discord.abc.PrivateChannel) and game_started:
        if command == MOVE:
            width = find_player(message.author, house)
            direction = int(message.content.split(" ")[1])
            if direction > 0 and direction < 5:
                success, newRoom = moveInsideHouse(width.location, house, direction)
                validCommand = success
                width = find_player(message.author, house)
                if success:
                    await width.currentPlayer.send(getSurroundings(house, newRoom))
                elif not success:
                    await width.currentPlayer.send("You walked into a wall")
                else:
                    await width.currentPlayer.send("Invalid Command" + str(command))
        elif command == GET_HOUSE_MAP and game_started:
            width = find_player(message.author, house)
            await width.currentPlayer.send(print_house(house))
        else:
            width = find_player(message.author, house)
            await width.currentPlayer.send("Invalid Command " + str(command))



client.run(token)
