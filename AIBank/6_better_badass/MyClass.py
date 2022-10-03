from ast import Return
import math
import random
from main import GameState
from main import Action
from main import MapType

permanentTypes = [i.value for i in [MapType.WALL, MapType.EMPTY, MapType.TREASURY, MapType.FOG]]
temporaryTypes = [i.value for i in [MapType.GOLD, MapType.AGENT]]
blockingTypes = [i.value for i in [MapType.WALL, MapType.AGENT, MapType.OUT_OF_MAP]]


class Tile:
    def __init__(self, pos: tuple[int, int], Type: MapType, tempType: MapType, data: int):
        self.pos: tuple[int, int] = pos
        self.Type = Type
        self.tempType = tempType
        self.data: int = data


class Agent:
    def __init__(self, pos: tuple[int, int], agentId: int, wallet: int, team: int):
        self.isVisible: bool = False
        self.pos: tuple[int, int] = pos
        self.agentId: int = agentId
        self.wallet: int = wallet
        self.team = team

    def __str__(self):
        return "Agent : <" + str(self.pos) + "," + str(self.agentId) + "," + str(self.wallet) + "," + str(
            self.isVisible) + \
               "," + str(self.team) + ">"


class Brain:
    firstIteration: bool = True

    def __init__(self):
        self.everyAgent = None
        self.everyTile = None
        self.everyTileAsPos = None

    def initTiles(self, mapDimensions: tuple[int, int], view: GameState) -> None:
        self.everyAgent = {}
        for i in range(0, 4):
            team = 1
            if i > 1: team = 2

            self.everyAgent[i] = Agent((0, 0), i, 0, team)

        self.everyTile = []
        self.everyTileAsPos = []
        for i in range(0, mapDimensions[0]):
            for c in range(0, mapDimensions[1]):
                Type = MapType.UNKNOWN.value
                self.everyTile.append(Tile((i, c), Type, Type, 0))
                self.everyTileAsPos.append((i, c))

    def updateTiles(self, visibleTiles: list, view: GameState) -> None:

        isInTreasury: bool = False
        for i in self.everyAgent:
            self.everyAgent[i].isVisible = False

        for i in range(0, len(self.everyTile)):
            for c in visibleTiles:
                isInTreasury = False
                if tuple(self.everyTile[i].pos) == tuple(c.coordinates):
                    if c.type.value in permanentTypes:
                        self.everyTile[i].Type = c.type.value
                        if c.type.value == MapType.TREASURY.value:
                            if c.data != -1:
                                isInTreasury = True

                    if c.type.value in temporaryTypes or isInTreasury:
                        self.everyTile[i].tempType = c.type.value
                        if c.type.value == MapType.AGENT.value or isInTreasury:
                            self.everyTile[i].tempType = MapType.AGENT.value

                            self.everyAgent[c.data].pos = c.coordinates
                            self.everyAgent[c.data].wallet = view.wallets[c.data]
                            self.everyAgent[c.data].isVisible = True

                    self.everyTile[i].data = c.data

                    # if c.data!=-1:
                    #     self.everyTile[i].tempType = MapType.AGENT.value

    def flushTiles(self):
        for i in range(0, len(self.everyTile)):
            self.everyTile[i].tempType = MapType.UNKNOWN.value

    def getVisiblePlacesString(self) -> str:
        text: str = ""

        last_row = 0

        for i in self.everyTile:
            if i.pos[0] != last_row: text += "\n"
            last_row = i.pos[0]
            if i.Type == MapType.UNKNOWN:
                text += str(i.Type)
            else:
                text += str(i.Type)

        return text + "\n"


class Step:
    def __init__(self, currentPos: tuple[int, int], parentPos: tuple[int, int], layer: int):
        self.cPos = currentPos
        self.pPos = parentPos
        self.layer = layer

    def __str__(self):
        return "[ " + str(self.cPos) + " , " + str(self.pPos) + " , " + str(self.layer) + " ]"


# BFS algorithm
# If the result list is empty it means the algorithm could not find the answer
# Either way, the second element in the list is your next turn
def getShortestPath(everyTile: list, src: tuple[int, int], dst: tuple[int, int]) -> list:
    # layer 0
    # layer 1
    validTiles: list = [i.pos for i in everyTile if (i.Type not in blockingTypes and
                                                     i.tempType not in blockingTypes)]
    result: list = []
    stack: list = [Step(src, src, 0)]  # initial layer
    stackPos: list = [src]

    if src == dst:
        return [stack[0], stack[0]]

    ATL_init = get_connected_nodes_soft(validTiles, src)  # first layer

    for i in ATL_init:
        stack.append(Step(i, src, 1))
        if i == dst:
            return [stack[len(stack) - 1], stack[0]]
        stackPos.append(i)

    end: int = len(stack)
    breaker: bool = False

    i = 0
    while True:  # other layers
        if i >= end: break
        ATL_iter = get_connected_nodes_soft(validTiles, stack[i].cPos)
        for c in ATL_iter:
            if c not in stackPos:
                stack.append(Step(c, stack[i].cPos, stack[i].layer + 1))
                stackPos.append(c)
                end += 1
                if c == dst:
                    breaker = True
                    break

        i += 1
        if breaker: break

    if breaker:  # Collecting the path
        trackPos = dst
        for i in list(range(0, end))[::-1]:
            if stack[i].cPos == trackPos:
                result.append(stack[i])
                trackPos = stack[i].pPos

    return result


firstIteration: bool = True
brain: Brain = Brain()


def getFurthestOptionFromTail(options: list, p_tail: list) -> tuple[int, int]:
    aveDist: float = 0.0
    maxAveDist: float = 0.0
    maxAveDistIndexList: list = []

    for i in range(0, len(options)):
        aveDist = getAverageDistance(options[i], p_tail)
        if i == 0 or aveDist > maxAveDist:
            maxAveDist = aveDist

    for i in range(0, len(options)):
        aveDist = getAverageDistance(options[i], p_tail)
        if aveDist == maxAveDist:
            maxAveDistIndexList.append(i)

    return options[random.choice(maxAveDistIndexList)]


def get_connected_nodes_soft(validTiles: list, pos: tuple[int, int]) -> list:
    list_coordinates = [(pos[0], pos[1] + 1), (pos[0], pos[1] - 1), (pos[0] - 1, pos[1]), (pos[0] + 1, pos[1])]

    return [i for i in list_coordinates if i in validTiles]


def get_connected_nodes_hard(everyTile: list, pos: tuple[int, int]) -> list:
    list_coordinates = [(pos[0], pos[1] + 1), (pos[0], pos[1] - 1), (pos[0] - 1, pos[1]), (pos[0] + 1, pos[1])]

    # return list_coordinates
    return [i.pos for i in everyTile if i.pos in list_coordinates and (i.Type not in blockingTypes
                                                                       and i.tempType not in blockingTypes)]


def getAverageDistance(point: tuple[int, int], pointList: list, isExtreme: bool = False) -> float or None:
    distSum: int = 0
    distCounter: int = 0

    for i in range(0, len(pointList)):
        distCounter += 1
        p2 = pointList[i]
        dist = abs(point[0] - p2[0]) + abs(point[1] - p2[1])
        if isExtreme:
            shortest_path = getShortestPath(brain.everyTile, point, p2)
            if len(shortest_path) != 0:
                dist = len(shortest_path)

        distSum += dist

    if distCounter == 0: return 0

    return distSum / distCounter


def getStepTowards(source: tuple[int, int], destination: tuple[int, int]) -> Action:
    if source[0] < destination[0]:
        return Action.MOVE_DOWN
    if source[0] > destination[0]:
        return Action.MOVE_UP

    if source[1] < destination[1]:
        return Action.MOVE_RIGHT
    if source[1] > destination[1]:
        return Action.MOVE_LEFT

    return Action.STAY


tail: list = []
TAIL_MAX_SIZE: int = 5
last_closest_target_dist: float = 0


def find_closest_enemy(view: GameState) -> Agent or None:
    self_team = 1
    if view.agent_id > 1: self_team = 2

    closest_enemy = None
    closest_enemy_dist: float = 0
    dist: float = 0

    for i in brain.everyAgent:
        if brain.everyAgent[i].isVisible and brain.everyAgent[i].team != self_team:
            dist = len(getShortestPath(brain.everyTile, view.location, brain.everyAgent[i].pos))
            if closest_enemy is None or dist < closest_enemy_dist:
                closest_enemy = brain.everyAgent[i]
                closest_enemy_dist = dist

    if closest_enemy is not None: return closest_enemy
    return None


def find_fattest_enemy(view: GameState) -> Agent or None:
    # not tested
    self_team = 1
    if view.agent_id > 1: self_team = 2

    fattest_enemy = None
    fattest_enemy_size: float = 0
    Size: float = 0

    for i in brain.everyAgent:
        if brain.everyAgent[i].isVisible and brain.everyAgent[i].team != self_team:
            Size = brain.everyAgent[i].wallet
            if fattest_enemy is None or Size > fattest_enemy_size:
                fattest_enemy = brain.everyAgent[i]
                fattest_enemy_size = Size

    if fattest_enemy is not None: return fattest_enemy
    return None


def find_closest_type(selfPos: tuple[int, int], targetType: MapType) -> tuple[int, int] or None:
    global last_closest_target_dist

    closets_target = None
    closets_target_dist: float = 0
    first_iteration: bool = True

    for i in brain.everyTile:
        if i.Type == targetType.value or i.tempType == targetType.value:

            dist = getAverageDistance(selfPos, [i.pos], isExtreme=True)
            if first_iteration or dist < closets_target_dist:
                closets_target = i.pos
                closets_target_dist = dist

            first_iteration = False

    if closets_target is not None:
        last_closest_target_dist = closets_target_dist
        return tuple(closets_target)

    return None


def Update(self: GameState) -> None:
    if Brain.firstIteration:
        brain.initTiles((self.map.height, self.map.width), self)
        Brain.firstIteration = False

    brain.updateTiles(self.map.grid, self)

    tail.append(list(self.location))

    if len(tail) > TAIL_MAX_SIZE:
        tail.pop(0)


def Dispose(self: GameState) -> None:
    brain.flushTiles()


def Patrol(self: GameState) -> tuple[int, int]:
    choices = get_connected_nodes_hard(brain.everyTile, (self.location[0], self.location[1]))

    if len(choices) != 0:
        goal = getFurthestOptionFromTail(choices, tail)
    else:
        goal = self.location

    return goal


def goTo(self: GameState, dstPos: tuple[int, int]) -> tuple[int, int]:
    pathList = getShortestPath(brain.everyTile, self.location, dstPos)

    if len(pathList) != 0:
        return pathList[len(pathList) - 2].cPos

    return self.location


def percent(All: float or int, Some: float or int) -> float:
    if All == 0: return 0
    return Some * (100 / All)


def go_trasury(self: GameState, triggerRange=5) -> bool or tuple[int, int]:
    remaining_steps = (self.rounds - self.current_round)

    map_boundaries_size = self.map.width + self.map.height

    if remaining_steps <= map_boundaries_size + triggerRange:
        closest_treasury = find_closest_type(self.location, MapType.TREASURY)
        if remaining_steps <= last_closest_target_dist + triggerRange:
            return closest_treasury

    else:
        # is attacked by the opponent, how many coins will he lose?
        lost_coins = self.wallet * self.attack_ratio * (self.atklvl / (self.atklvl + self.deflvl) + 1)

        if lost_coins > self.map.gold_count:
            closest_treasury = find_closest_type(self.location, MapType.TREASURY)
            return closest_treasury

    return False


def check_attack(self: GameState) -> False or Action:
    agent = find_fattest_enemy(self)
    if agent is not None:
        x, y = self.location
        x2, y2 = agent.pos
        distance_Manhattan = abs(x - x2) + abs(y - y2)
        attack_efficiency = agent.wallet * self.attack_ratio * (self.atklvl / (self.atklvl + 1))
        self.debug_log += f'attack_efficiency=attack_efficiency=: {str(attack_efficiency)}\n'

        if attack_efficiency >= self.map.gold_count / 5:

            if x != x2 and y != y2 or distance_Manhattan <= self.ranged_attack_radius:
                # if distance_Manhattan <= self.ranged_attack_radius:
                return Action.RANGED_ATTACK

            if distance_Manhattan <= self.linear_attack_range:
                if x > x2:
                    return Action.LINEAR_ATTACK_UP

                if x < x2:
                    return Action.LINEAR_ATTACK_DOWN

                if y < y2:
                    return Action.MOVE_RIGHT

                if y > y2:
                    return Action.LINEAR_ATTACK_LEFT
    return False


def shouldAttack(self: GameState, attackThreshold: float) -> bool:
    closest_enemy = find_closest_enemy(self)
    self.debug_log += "closest_enemy!!:" + str(closest_enemy) + "\n" + "attack ratio : " + str(self.attack_ratio) + "\n"

    if closest_enemy is not None and self.attack_ratio > attackThreshold:
        return True

    return False


def getAction(self: GameState) -> Action:
    Update(self)

    goal = Patrol(self)

    go_g = find_closest_type(self.location, MapType.GOLD)
    if go_g is not None:
        goal = goTo(self, go_g)
    go_t = go_trasury(self)
    if go_t:
        goal = goTo(self, go_t)

    for i in brain.everyAgent:
        self.debug_log += str(brain.everyAgent[i]) + "\n"

    attack = check_attack(self)
    if attack and not go_t:
        return attack

    self.debug_log += "" + brain.getVisiblePlacesString() + "\n"
    Dispose(self)

    return getStepTowards(self.location, goal)
