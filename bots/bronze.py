import sys
import math

entities = []
GRIDSIZE = {
    'x': 22,
    'y': 20,
}


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
        return Grid.distance(self, entity)

    def getPosition(self):
        return {'x': self.x, 'y': self.y}

    def getNearest(self, entities):
        if len(entities):
            return sorted(entities, key=lambda e: self.distanceTo(e))[0]
        else:
            return None


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
        if isinstance(entity, Entity):
            x = entity.x
            y = entity.y
        else:
            x = entity['x']
            y = entity['y']
        print('MOVE {} {}'.format(x, y))

    def attackPosition(self, pos):
        print('FIRE {} {}'.format(pos['x'], pos['y']))

    def turn(self, direction):
        print('PORT' if direction == 'left' else 'STARBOARD')

    def wait(self):
        print('WAIT')

    def __str__(self):
        return '{} SHIP #{} @ ({}, {}) @ speed [{}] oriented @ {} with {} RUM'.format(
            'MY' if self.owner else 'ENEMY',
            self.id,
            self.x,
            self.y,
            self.speed,
            self.orientation,
            self.rum
        )

    def predictPosition(self, rounds=1):
        pos = self.getPosition()
        for r in range(rounds):
            self.calculateNextPosition(pos)
        return pos

    def calculateNextPosition(self, pos=None, orientation=None, speed=None):
        position = pos if pos else self.getPosition()
        orientation = orientation if orientation else self.orientation
        speed = speed if speed else self.speed

        for i in range(0, self.speed):
            lineType = 'odd' if position['y'] % 2 else 'even'
            if lineType == 'odd':
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

    def goingTowardsMine(self):
        for i in range(1, 6):
            predictedPosition = self.predictPosition(i)
            if Grid.mineAt(predictedPosition):
                return Grid.mineAt(predictedPosition)
        return False


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
        return entity if (entity and entity.type == 'mine') else None

    @staticmethod
    def distance(a, b):
        src = a.getPosition() if isinstance(a, Entity) else a
        dst = b.getPosition() if isinstance(b, Entity) else b
        # return math.sqrt((p1['x']-p2['x'])**2 + (p1['y']-p2['y'])**2)
        return max([
            abs(dst['y'] - src['y']),
            abs(math.ceil(dst['y'] / -2) + dst['x'] - math.ceil(src['y'] / -2) - src['x']),
            abs(-dst['y'] - math.ceil(dst['y'] / -2) - dst['x'] + src['y'] + math.ceil(src['y'] / -2) + src['x'])
        ])






# game loop
while True:
    my_ship_count = int(input())
    entities = parseEntities()
    for i in range(my_ship_count):
        myship = entities['myships'][i]
        shipid = myship.id
        debugPrint('[SHIP #{}] {}'.format(shipid, myship))
        nearestEnemy = myship.getNearest(entities['enemyships'])
        debugPrint('[SHIP #{}] nearestEnemy: {}'.format(shipid, nearestEnemy))
        barrelsLeft = len(entities['barrels'])
        actionTaken = False

        mine = myship.goingTowardsMine()
        if mine:
            debugPrint('[SHIP #{}] going towards mine'.format(shipid))
            myship.turn('right')
            actionTaken = True

        distanceToNearestEnemy = myship.distanceTo(nearestEnemy)
        nearestBarrel = myship.getNearest(entities['barrels'])
        distanceToNearestBarrel = myship.distanceTo(nearestBarrel) if nearestBarrel else 9999

        # ucieczka awaryjna - kiedy nie dolecimy do wroga, a dolecimy do beczki
        if not actionTaken:
            if nearestBarrel:
                if distanceToNearestBarrel <= 5 and distanceToNearestEnemy >= 5:
                    if 100 - (myship.rum - distanceToNearestBarrel) >= nearestBarrel.rum:
                        myship.moveTo(nearestBarrel)
                        debugPrint('[SHIP #{}] move to barrels {}'.format(shipid, nearestBarrel.getPosition()))
                        actionTaken = True

        # if not actionTaken:
        #     if (distanceToNearestBarrel <= (myship.rum - 5) <= distanceToNearestEnemy and distanceToNearestBarrel > 7) or myship.rum < 15 and nearestEnemy.rum > 30:
        #         myship.moveTo(nearestBarrel)
        #         actionTaken = True
        #         debugPrint('[SHIP #{}] emergency move to barrel {}'.format(shipid, nearestBarrel.getPosition()))

        if not actionTaken and nearestEnemy:
            # attack
            for roundNumber in range(8):
                position = nearestEnemy.predictPosition(roundNumber + 2)
                ship_front_position = nearestEnemy.predictPosition(roundNumber)
                distanceToEnemy = myship.distanceTo(ship_front_position)
                shootTime = math.ceil(1 + distanceToEnemy/3)
                debugPrint('[SHIP #{}] R[{}] predictedPosition: ({}, {}) shoot time {}, distance {}'.format(shipid, roundNumber, position['x'], position['y'], shootTime, distanceToEnemy))
                if distanceToEnemy < 10 and roundNumber <= shootTime <= roundNumber + 1:
                    if position['x'] < 0:
                        position['x'] = 0
                    elif position['x'] > GRIDSIZE['x']:
                        position['x'] = GRIDSIZE['x']

                    if position['y'] < 0:
                        position['y'] = 0
                    elif position['y'] > GRIDSIZE['y']:
                        position['y'] = GRIDSIZE['y']

                    debugPrint('[SHIP #{}] attack ({}, {})'.format(shipid, position['x'], position['y']))
                    myship.attackPosition(position)
                    actionTaken = True
                    break

        if not actionTaken:
            myship.moveTo(nearestEnemy)
            actionTaken = True
            debugPrint('[SHIP #{}] move {}'.format(shipid, nearestEnemy.getPosition()))