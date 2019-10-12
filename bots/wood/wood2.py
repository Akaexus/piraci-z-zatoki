import sys
import math


# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

class Entity:
    def __init__(self, id, type, x, y):
        self.id = id
        self.type = type
        self.x = x
        self.y = y

    def distanceTo(self, entity):
        return math.sqrt((self.x - entity.x) ** 2 + (self.y - entity.y) ** 2)

    def getPosition(self):
        return [self.x, self.y]


class Barrel(Entity):
    def __init__(self, id, x, y, rum):
        super().__init__(id, 'barrel', x, y)
        self.rum = rum


class Ship(Entity):
    def __init__(self, id, x, y, orientation, speed, rum, action):
        super().__init__(id, 'ship', x, y)
        self.rum = rum
        self.orientation = orientation
        self.speed = speed
        self.action = action

    def moveTo(self, entity):
        print('MOVE {} {}'.format(entity.x, entity.y))

    def attack(self, entity):
        print('FIRE {} {}'.format(entity.x, entity.y))

    def wait(self):
        print('WAIT')


def parseEntities():
    entities = {
        'barrels': [],
        'ships': []
    }
    entity_count = int(input())  # the number of entities (e.g. ships, mines or cannonballs)
    for i in range(entity_count):
        entity_id, entity_type, x, y, arg_1, arg_2, arg_3, arg_4 = input().split()
        entity_id = int(entity_id)
        x = int(x)
        y = int(y)
        arg_1 = int(arg_1)
        arg_2 = int(arg_2)
        arg_3 = int(arg_3)
        arg_4 = int(arg_4)
        if entity_type == 'BARREL':
            entities['barrels'].append(Barrel(entity_id, x, y, arg_1))
        elif entity_type == 'SHIP':
            entities['ships'].append(Ship(entity_id, x, y, arg_1, arg_2, arg_3, arg_4))
    return entities


# game loop
while True:
    my_ship_count = int(input())
    entities = parseEntities()
    for i in range(my_ship_count):
        myship = entities['ships'][0]
        enemyShip = entities['ships'][1]

        if myship.distanceTo(enemyShip) <= 3:
            myship.attack(enemyShip)
        else:
            # find barrels
            if len(entities['barrels']):
                nearestBarrel = sorted(entities['barrels'], key=lambda b: myship.distanceTo(b))[0]
            else:
                nearestBarrel = None
            if nearestBarrel:
                myship.moveTo(nearestBarrel)
            else:
                myship.wait()

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)

        # Any valid action, such as "WAIT" or "MOVE x y"