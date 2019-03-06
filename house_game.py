import sys

class Room:

    def __init__(self, name):
        
        self.name = name

class Door:

    def __init__(self, directions, status, rooms):
        
        self.direct = directions
        self.status = status
        self.rooms = rooms

    def unlock(self, backpack):

        if self.status == "locked":
            possible = False
            for thing in backpack.check_contents():
                if type(thing) == Key:
                    if thing.door == self.rooms:
                        possible = True
            if possible:
                self.status = "closed"
                print ("You unlocked the door")
            else:
                print ("You don't have the key for this door")
        elif self.status == "sealed":
            print ("This is the front door. It is sealed and can never be opened. You need to find another way out.")
        else:
            print ("This door is unlocked")
        return self

    def open_door(self, backpack):

        if self.status == "open":
            print ("This door is already open")
        elif self.status == "locked":
            print("You need a key to open this door")
        elif self.status == "sealed":
            print ("This is the front door. It is sealed and can never be opened. You need to find another way out.")
        else:
            self.status = "open"
            print ("You opened the door")
        return self

    def close_door(self, backpack):

        if self.status == "closed":
            print ("This door is already closed")
        elif self.status == "locked":
            print("This door is already closed and locked")
        elif self.status == "sealed":
            print ("This is the front door. It is sealed and can never be opened. You need to find another way out.")
        else:
            self.status = "closed"
            print ("You closed the door")
        return self

class Item:

    def __init__(self, name, position, kind, key):

        self.name = name
        self.position = position
        self.kind = kind
        self.key = key

    def get_name(self):
        return self.name

    def get_type(self):
        return self.kind

    def check_ifkey(self, backpack):
        if self.key:
            for it in backpack.contents:
                if self.key == it.name:
                    print("You've already found a key here")
                    return None
            print("You have found a key! You can use it to unlock one of the doors. It will be in your backpack when you need it.")
        else:
            print ("There's nothing here")
        return self.key


class Movable_item(Item):

    def __init__(self, name, position, kind, key):

        Item.__init__(self, name, position, kind, key)


class Usable_item(Item):

    def __init__(self, name, position, kind, key, action):

        Item.__init__(self, name, position, kind, key)
        self.action = action 


    def actions(self, house):
        print ("Well, this didn't help anything. Carry on!")


class Key:

    def __init__(self, name, door):
        
        self.name = name
        self.door = door

    def __str__(self):

        return self.name

class Backpack:

    def __init__(self):
        self.contents = []

    def check_contents(self):
        return self.contents

    def update_backpack(self, thing):
        self.contents.append(thing)


class Keypad:

    def __init__(self, text, hint, solution, letter, position):

        self.text = text
        self.hint = hint
        self.solution = solution
        self.letter = letter
        self.position = position

    def interact(self):

        print(self.text)
        print("Type 'hint' if you would like to get a hint.")
        t = input()
        c = True
        while c:
            if t == 'hint':
                print(self.hint)
                t = input()
            else:
                if self.solution in t.lower():
                    if self.letter != 'e':
                        print("You are correct! You get a letter added to your backpack")
                    return self.letter
                elif self.solution not in t.lower():
                    print("Sorry, that's not the correct answer. Type 'keypad' if you want to try again.")
                    return None

class House:

    def __init__(self, rooms, doors, items, keys, riddles, location):

        self.rooms = rooms
        self.doors = doors
        self.items = items
        self.keys = keys
        self.riddles = riddles
        self.location = location


    def update_location(self, new_room):
        self.location = new_room
        print ("You are now in the", new_room)


    def room_info(self):

        li = []
        print("You are in the", self.location)
        for door in self.doors:
            if door.rooms[0] == self.location:
                li.append(door.direct[0])
            elif door.rooms[1] == self.location:
                li.append(door.direct[1])
        print ("There are doors towards", ", ".join(door for door in li))
        li = []
        for item in self.items:
            if item.position == self.location:
                li.append(item.name)
        print ("There are the following items:", ", ".join(item for item in li))
        print("There is also a keypad on the wall. You can interact with it by typing 'keypad'.")
        
class HouseReader:

    def __init__(self, config):

        self.config = config

    def build_house(self):
        
        rooms = []
        doors = []
        items = []
        keys = []
        riddles = []
        
        with open(self.config, 'r') as fi:

            lines = fi.read().splitlines()
            
            for line in lines:
                if line.startswith('room'):
                    li = line.split()
                    rooms.append(Room(li[1]))
                elif line.startswith('door'):
                    line = line.strip('door ')
                    li = line.split()
                    li[0] = (li[0].split('-'))
                    doors.append(Door(li[0], li[1], (li[2],li[3])))
                elif line.startswith('item'):
                    line = line.strip('item ')
                    li = line.split()
                    items.append(li)
                elif line.startswith('key'):
                    li = line.split()
                    keys.append(Key(li[1],(li[2], li[3])))
                elif line.startswith('riddle'):
                    li = line.split('*')
                    riddles.append(Keypad(li[1], li[2], li[3], li[4], li[5]))
                elif line.startswith('start'):
                    line = line.strip('start ')
                    start = line
                    
        for i in range(len(items)):
            if "STATIONARY" in items[i]:
                items[i] = Item(items[i][0], items[i][1], items[i][2], items[i][3])
            elif "MOVE" in items[i]:
                items[i] = Movable_item(items[i][0], items[i][1], items[i][2], items[i][3])
            elif "USE" in items[i]:
                items[i] = Usable_item(items[i][0], items[i][1], items[i][2], items[i][3], items[i][4])

            
        this_house = House(rooms, doors, items, keys, riddles, start)
        return this_house

class Game_Engine:

    def build_commands(self):

        comm_dict = {'open': ("open_door","Door"),
                     'show': ("room_info","House"),
                     'search': ("check_ifkey","Key"),
                     'pick_up': ("", "Item"),
                     'close' : ("close_door", "Door"),
                     'go': ("update_location", "House"),
                     'release': ("update_position", "Release"),
                     'inventory': ("check_contents", "Backpack"),
                     'eat': ("actions", "Item"),
                     'read': ("actions", "Item"),
                     'wear': ("actions", "Item"),
                     'keypad':("interact", "Keypad"),
                     'unlock': ("unlock", "Door")}
        return comm_dict

    def play(self):
        
        reader = HouseReader(sys.argv[1])
        myHouse = reader.build_house()
        game_end = False
        d = self.build_commands()

        inventory = Backpack()
        holding = []
        print("Welcome to the House Game! You've just woken up and you don't know how you got here. You are in the master bedroom of an unfamiliar house. Type 'commands' to see what you can do, or type 'show' for information on the room you are in. You can also type 'inventory' if you want to see the items you have found; they are going to be in a backpack that you found and decided to take with you. If you pick up an object you will be holding it until you decide to release it. If you want to see which items you are currently holding, type 'holding'. You can type 'quit' to exit the game at any time. Good luck!")
        text = ''

        while text != "quit" and game_end == False:

            text = input()
            
            if text == 'quit':
                print ("Thank you for playing! Goodbye!")
                sys.exit(0)
                
            li = text.split()
            try:
                command = li[0]
            except:
                pass
            if command not in d:
                if command == 'commands':
                    print ("Valid commands are composed of an action and possibly a thing. If you want to open a door, you should type 'open' and then the direction that door leads to, for example 'open E' to open the door towards the east. If you want to pick up an item, you should type 'pick_up' followed by the item you want to pick up, for example 'pick_up lamp'. You can use the following commands:", ', '.join(k for k in d))
                elif command == 'holding':
                    a = []
                    for it in holding:
                        if isinstance(it, Movable_item):
                            a.append(it.name)
                    if a:
                        print("You are holding the following items:", *a)
                    else:
                        print("You are not holding any items")
                else:
                    print("Please type a valid command")
            else:
                tup = d[command]
                if tup[1] == "Door":
                    self.door_commands(tup[0],li[1], inventory, myHouse)
                elif tup[1] == "Item":
                    r = self.item_commands(tup[0],li[1], myHouse)
                    holding.append(r)
                elif tup[1] == "House":
                    try:
                        self.house_commands(tup[0], myHouse, holding, li[1])
                    except:
                        self.house_commands(tup[0], myHouse, holding)
                elif tup[1] == "Release":
                    holding = self.release(myHouse, holding, li[1])
                elif tup[1] == "Keypad":
                    letter = self.keypad_commands(myHouse)
                    if letter =='e':
                        game_end = True
                    if letter and letter not in inventory.contents:
                        inventory.update_backpack(letter)
                elif tup[1] == "Backpack":
                    content = inventory.check_contents()
                    print("You have the following items in your backpack:", *content)
                elif tup[1] == "Key":
                    f = self.key_commands(tup[0],li[1], myHouse, inventory)
                    if f != None:
                        for k in myHouse.keys:
                            if k.name == f:
                                k_object = k
                        inventory.update_backpack(k_object)
        print("Congratulations! You made it out on the balcony. The fire escape is to your right and you are free to go. Thank you for playing!")

    def door_commands(self, function, variable, backpack, house):

        if variable not in "WSNE":
            print ("You can only open doors. Doors are named E, W, S, N.")
        else:
            found = False
            for door in house.doors:
                if (door.direct[0] == variable and door.rooms[0] == house.location) \
                or (door.direct[1] == variable and door.rooms[1] == house.location):
                    var = door
                    method_to_use = getattr(var, function)
                    new_door = method_to_use(backpack)
                    for door in house.doors:
                        if door.rooms == new_door.rooms:
                            door = new_door
                            found = True
            
            if found == False:
                print("There is no door in that direction")

    def item_commands(self, function, item, house):

        var = None
        for it in house.items:
            if item == it.name:
                if it.position == house.location:
                    var = it
                    if function == "":
                        print ("You picked up the", item)
                        return var
                    else:
                        method_to_use = getattr(var, function)
                        method_to_use(house)
                        return []
                else:
                    var = 1
                    print ("There is no such thing in this room")
                    return []
        if var == None:
            print("There is no such thing in this room")
            return []

    def house_commands(self, function, house, holding, variable = None):
        
        if function == "update_location":
            is_door = False
            for door in house.doors:
                if (door.direct[0] == variable and door.rooms[0] == house.location) \
                or (door.direct[1] == variable and door.rooms[1] == house.location):
                    is_door = True
                    if door.status == 'open':
                        tup = door.rooms
                        for r in tup:
                            if r != house.location:
                                room = r
                        house.update_location(room)
                        break
                    else:
                        if door.status == "sealed":
                            print ("This is the front door. It is sealed and can never be opened. You need to find another way out.")
                        else:
                            print ("This door is", door.status)
            if is_door == False:
                print ("There is no door in this direction")
        else:
            var = house
            method_to_use = getattr(var, function)
            method_to_use()

    def release(self, house, holding, variable):

        found = False
        for it in house.items:
            if variable == it.name:
                found = True
                if it in holding:
                    it.position = house.location
                    print("You released the", variable)
                    holding.remove(it)
                else:
                    print("You are not holding this item")
        if found == False:
            print("You are not holding this item")
        return holding

    def keypad_commands(self, house):

        for k in house.riddles:
            if house.location == k.position:
                return k.interact()


    def key_commands(self, function, variable, house, backpack): 

        var = None
        for it in house.items:
            if variable == it.name:
                var = it
                method_to_use = getattr(var, function)
                return method_to_use(backpack)
        if not var:
            print ("There is no such item in the room")
            return None
        
        
def __main__():

    game = Game_Engine()
    game.play()

__main__()

""" Things to fix: if you apply a function to the wrong object, keypads, end of game """
