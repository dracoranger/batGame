import math
import random

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
        return ret

    def moveBatTo(self):
        self.hasBat = True

    def moveBatFrom(self):
        self.hasBat = False

    def updateLocl(self, x, y):
        self.location=(x,y)
        print(self.location)

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
        print(str(isValidHouse) + " " + str(marker))
        print_house(house)

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

    return house,roomsWithPeople

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
    #if random.random() < batStupidity:  #Random directions, might make too annoying
    #    movement = random.randint(1,4)
    move = batAI(house, target.location, bat.location)
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
                house[randomX][randomY].moveBatTo()
                house[randomX][randomY].batMoved = True
                notPlaced = False

def getSurroundings(house, room):
    print(room.location)
    message = "To the west there is a " + house[room.location[0]-1][room.location[1]].name + ". It " + house[room.location[0]-1][room.location[1]].description
    message = message + "\nTo the east there is a " + house[room.location[0]+1][room.location[1]].name + ". It " + house[room.location[0]+1][room.location[1]].description
    message = message + "\nTo the north there is a " + house[room.location[0]][room.location[1]-1].name + ". It " + house[room.location[0]][room.location[1]-1].description
    message = message + "\nTo the south there is a " + house[room.location[0]][room.location[1]+1].name + ". It " + house[room.location[0]][room.location[1]+1].description
    return message

def print_house(house):
    final = ""
    for i in house:
        for j in i:
            if j.name == "Wall":
                final = final + "N"
            else:
                final = final + "O"
        final = final + "\n"
    print(final)

def main():
    numBats = 1
    batStupidity = .25

    #player object is the user calling an activity
    players = ["Alpha","Bravo", "Charlie", "Delta", "Echo"]
    #should be a 2d array storing "room" objects, with a loop around the outside of walls
    #playerData contains the rooms players are in
    #might want to make it a queue
    house, playerData = generateHouse(players, numBats)

    for length in house:
        for width in length:
            if width.hasPlayer:
                #send description of location
                print(width.currentPlayer)
                message = getSurroundings(house, width)
                #send message in a DM
                print(message)

       #debug commands for testing
       #will use async for later, so, people can act in any order and Mango is the only thing that triggers a solid change
    while True:
        for length in house:
            for width in length:
                if width.hasPlayer:
                    print(width.currentPlayer)
                    validCommand = False
                    while not validCommand:
                        command = int(input("1. move 2. catch 3. MANGO! 4. continue\n"))
                        if command == 1:
                            command = int(input("1. west, 2. east, 3. north, 4. south\n"))
                            if command > 0 and command < 5:
                                success, newRoom = moveInsideHouse(width.location, house, command)
                                print(getSurroundings(house, newRoom))
                                validCommand = success
                                if not success:
                                    print("You walked into a wall")
                            else:
                                print("invalid command")
                        elif command == 2:
                            caughtBat = house[width.location[0]][width.location[1]].hasBat
                            if caughtBat:
                                print("Victory!  You caught the bat")
                                width.moveBatFrom()
                                resetBat(house, numBats)
                            else:
                                print("swing and miss")
                            validCommand = True
                        elif command == 3:
                            for bat_length in house:
                                for bat_width in bat_length:
                                    bat_width.batMoved = False

                            for bat_length in house:
                                for bat_width in bat_length:
                                   if bat_width.hasBat and not bat_width.batMoved:
                                       print(str(width.location) + "<- player bat-> " + str(bat_width.location))
                                       distance = math.sqrt((width.location[0] - bat_width.location[0])**2 + (width.location[1] - bat_width.location[1])**2)
                                       #might want to revise hearing distance
                                       message = "You heard nothing in reply"
                                       if distance == 0:
                                           message = "CHOMP \nThe bat ate your mango and ran off"
                                           bat_width.moveBatFrom()
                                           resetBat(house, numBats)
                                       elif distance < 2:
                                           message = "EEEEE"
                                           moveBat(house, width, bat_width)
                                       elif distance < 4:
                                           message = "eeeee"
                                           moveBat(house, width, bat_width)
                                       elif distance < 6:
                                           message = "....."
                                           moveBat(house, width, bat_width)
                                       print(message)
                            validCommand = True
                        elif command == 4:
                            validCommand = True
                        else:
                            print("Invalid command " + str(command))

main()
