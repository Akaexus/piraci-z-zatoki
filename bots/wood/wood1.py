import sys
import math

entities = []


def debugPrint(e):
    print(e, file=sys.stderr)


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
        return {'x': self.x, 'y': self.y}

    def getNearest(self, entities):
        return sorted(entities, key=lambda e: self.distanceTo(e))[0]


class Mine(Entity):
    def __init__(self, id, x, y):
        super().__init__(id, 'mine', x, y)


class Barrel(Entity):
    def __init__(self, id, x, y, rum):
        super().__init__(id, 'barrel', x, y)
        self.rum = rum


class Ship(Entity):
    def __init__(self, id, x, y, orientation, speed, rum, owner):
        super().__init__(id, 'ship', x, y)
        self.rum = rum
        self.orientation = orientation
        self.speed = speed
        self.owner = owner

    def moveTo(self, entity):
        print('MOVE {} {}'.format(entity.x, entity.y))

    def attack(self, entity):
        p = entity.predictPosition()
        print('FIRE {} {}'.format(p['x'], p['y']))

    def wait(self):
        print('WAIT')

    def __str__(self):
        return '{} SHIP @ ({}, {}) @ speed [{}] oriented @ {} with {} RUM'.format(
            'MY' if self.owner else 'ENEMY',
            self.x,
            self.y,
            self.speed,
            self.orientation,
            self.rum
        )

    def predictPosition(self, pos=None):
        if not pos:
            p = self.getPosition()
            speed = self.speed
        else:
            p = pos
        return self.calculateNextPosition(pos)

    def grabBarrels(self, barrels):
        nearestBarrel = self.getNearest(barrels)
        entities['barrels'].pop(entities['barrels'].index(nearestBarrel))
        myship.moveTo(nearestBarrel)

    def attackNearest(self, entities):
        self.attack(self.getNearest(entities))

    def calculateNextPosition(self, pos=None, orientation=None, speed=None):
        position = pos if pos else self.getPosition()
        orientation = orientation if orientation else self.orientation
        speed = speed if speed else self.speed

        for i in range(0, self.speed):
            lineType = 'odd' if position['y'] % 2 else 'even'
            if lineType == 'even':
                offsets = {
                    0: [1, 0],
                    1: [1, -1],
                    2: [0, -1],
                    3: [-1, 0],
                    4: [0, 1],
                    5: [1, 1],
                }
            else:
                offsets = {
                    0: [1, 0],
                    1: [0, -1],
                    2: [-1, -1],
                    3: [-1, 0],
                    4: [-1, 1],
                    5: [0, 1],
                }
            offset = offsets[self.orientation]
            position['x'] += offset[0]
            position['y'] += offset[1]
        return position


def parseEntities():
    entities = {
        'barrels': [],
        'myships': [],
        'enemyships': [],
        'mines': []
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
            owner = 'myships' if arg_4 else 'enemyships'
            entities[owner].append(Ship(entity_id, x, y, arg_1, arg_2, arg_3, arg_4))
        elif entity_type == 'MINE':
            entities['mines'].append(Mine(entity_id, x, y))

    return entities


class Grid:
    @staticmethod
    def at(pos):
        for entityGroup in entities:
            for entity in entities[entityGroup]:
                if entity.getPosition() == pos:
                    return entity
        return None

    @staticmethod
    def mineAt(pos):
        entity = Grid.at(pos)
        return entity and entity.type == 'mine'


# game loop
while True:
    my_ship_count = int(input())
    entities = parseEntities()
    for i in range(my_ship_count):
        myship = entities['myships'][i]
        debugPrint(myship)
        nearestEnemy = myship.getNearest(entities['enemyships'])
        barrelsLeft = len(entities['barrels'])

        # bypass mines
        nextPosition = myship.calculateNextPosition(myship.getPosition(), myship.orientation, 2)
        if Grid.mineAt(nextPosition):
            debugPrint('mine!')
            orientation = myship.orientation
            for rotateOffset in range(0, 5):
                orientation = (orientation + rotateOffset) % 6
                nextPosition = myship.calculateNextPosition(myship.getPosition(), orientation)
                if not Grid.mineAt(nextPosition):
                    myship.moveTo(nextPosition)
                    break

        if myship.distanceTo(nearestEnemy) <= 8:
            if myship.rum < 15 and barrelsLeft:
                # tactical retreat when low on rum
                myship.grabBarrels(entities['barrels'])
            elif myship.speed == 0 and myship.distanceTo(nearestEnemy) > 4:
                # move to enemy when distance is quite long and we are not moving
                myship.moveTo(nearestEnemy)
            else:
                myship.attack(nearestEnemy)
        elif myship.distanceTo(nearestEnemy) <= 12:
            myship.moveTo(nearestEnemy)
        else:
            # find barrels
            if barrelsLeft:
                myship.grabBarrels(entities['barrels'])
            else:
                myship.attackNearest(entities['enemyships'])
