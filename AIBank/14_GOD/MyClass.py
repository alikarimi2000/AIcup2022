
import random
from main import GameState
from main import Action
from main import MapType
import Astar

permanentTypes = [i.value for i in [MapType.WALL, MapType.EMPTY, MapType.TREASURY, MapType.FOG]]
temporaryTypes = [i.value for i in [MapType.GOLD, MapType.AGENT]]
blockingTypes = [i.value for i in [MapType.WALL, MapType.AGENT, MapType.OUT_OF_MAP]]


class Tile:
    def __init__(self, pos: tuple[int, int], Type: MapType, tempType: MapType, data: int):
        self.pos: tuple[int, int] = pos
        self.Type = Type
        self.tempType = tempType
        self.data: int = data
        self.isOverRidden: bool = False

    def __str__(self):
        return "Tile : <" + str(self.pos) + "," + str(self.Type) + "," + str(self.tempType) + "," + str(self.data) + ">"


class Agent:
    def __init__(self, pos: tuple[int, int], agentId: int, wallet: int, team: int):
        self.isVisible: bool = False
        self.pos: tuple[int, int] = pos
        self.agentId: int = agentId
        self.wallet: int = wallet
        self.team = team

    def __str__(self):
        return "Agent : < pos : " + str(self.pos) + ", id : " + str(self.agentId) + ", wallet : " + \
               str(self.wallet) + "," + str(
            self.isVisible) + \
               ", team : " + str(self.team) + " >"


class Brain:
    firstIteration: bool = True

    def __init__(self):
        self.everyAgent = None
        self.everyTile = None
        self.everyFog = None
        self.everyGold = None
        self.last_tested_fog = None
        self.everyTileAsPos = None

    def initTiles(self, mapDimensions: tuple[int, int], view: GameState) -> None:
        self.everyAgent = {}
        for i in range(0, 4):
            team = 1
            if i > 1: team = 2

            self.everyAgent[i] = Agent((0, 0), i, 0, team)
        self.everyFog = []
        self.everyGold = []
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
                    if c.type.value in permanentTypes and not self.everyTile[i].isOverRidden:
                        if self.everyTile[i].Type != MapType.UNKNOWN.value \
                                and self.everyTile[
                            i].Type != c.type.value:  # This ensures treasuries behind fogs are found
                            view.debug_log += "\n Found new MapType ! , previous type : " + \
                                              str(self.everyTile[i].Type) + " , new type : " + str(c.type.value) + "\n"
                            self.everyTile[i].isOverRidden = True

                        if c.type.value == MapType.FOG.value \
                                and self.everyTile[i].pos not in self.everyFog:
                            self.everyFog.append(self.everyTile[i].pos)

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

                        if c.type.value == MapType.GOLD.value:
                            self.everyGold.append(self.everyTile[i])

                    self.everyTile[i].data = c.data

                    # if c.data!=-1:
                    #     self.everyTile[i].tempType = MapType.AGENT.value

    def flushTiles(self):
        if self.everyTile is None: return
        for i in range(0, len(self.everyTile)):
            self.everyTile[i].tempType = MapType.UNKNOWN.value
        brain.everyGold.clear()

    def getVisiblePlacesString(self) -> str:
        text: str = ""

        last_row = 0

        for i in self.everyTile:
            if i.pos[0] != last_row: text += "\n"
            last_row = i.pos[0]
            text += str(i.Type)

        last_row = 0
        text += "\ntempType included:\n"
        for i in self.everyTile:
            if i.pos[0] != last_row: text += "\n"
            last_row = i.pos[0]
            if i.tempType != MapType.UNKNOWN.value:
                text += str(i.tempType)
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

    src = tuple(src)
    dst = tuple(dst)

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


def find_best_gold(view: GameState) -> tuple[int, int] or None:
    best_gold = None
    best_value = 0

    for i in brain.everyGold:
        dist = len(getShortestPath(brain.everyTile, view.location, i.pos))
        count = i.data
        value = count

        for c in brain.everyGold:
            if c == i: break
            dist2 = len(getShortestPath(brain.everyTile, i.pos, c.pos))
            count2 = c.data

            if dist2 != 0:
                value2 = count2 / dist2
            else:
                value2 = 0

            value += value2

        if dist != 0:
            value /= dist
        else:
            value = 0
        if best_gold is None or value > best_value:
            best_value = value
            best_gold = i.pos

    return best_gold


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
        if i.Type == targetType.value and i.pos == selfPos:
            closets_target = i.pos
            break

        if (i.Type == targetType.value and (i.tempType not in blockingTypes or i.pos == selfPos)) \
                or i.tempType == targetType.value:

            dist = getAverageDistance(selfPos, [i.pos], isExtreme=True)
            if first_iteration or dist < closets_target_dist:
                closets_target = i.pos
                closets_target_dist = dist

            first_iteration = False

    if closets_target is not None:
        last_closest_target_dist = closets_target_dist
        return tuple(closets_target)

    return None


ally_pre_visible = False


def Update(view: GameState) -> None:
    global ally_pre_visible
    if Brain.firstIteration:
        brain.initTiles((view.map.height, view.map.width), view)
        Brain.firstIteration = False

    brain.updateTiles(view.map.grid, view)

    team = 1
    if view.agent_id > 1:
        team = 2
    ally_visible = False
    ally_id = 0

    for c in brain.everyAgent:
        i = brain.everyAgent[c]
        if i.agentId != view.agent_id and i.team == team and i.isVisible:
            ally_visible = True
            ally_id = i.agentId
            break

    if ally_visible:
        # tail.clear()
        for i in range(0,TAIL_MAX_SIZE):
            tail.append(tuple(brain.everyAgent[ally_id].pos))
    else:
        tail.append(tuple(view.location))

    if ally_pre_visible:

        while len(tail) > TAIL_MAX_SIZE:
            tail.pop(0)
    else:
        if len(tail) > TAIL_MAX_SIZE:
            tail.pop(0)

    ally_pre_visible = ally_visible



    if brain.last_tested_fog is not None:
        view.debug_log += "\n" + "Last goal was a fog , result : " + str(view.last_action) + "\n"
        if view.last_action == -1:
            for i in range(0, len(brain.everyTile)):
                if tuple(brain.everyTile[i].pos) == tuple(brain.last_tested_fog):
                    brain.everyTile[i].Type = MapType.WALL.value
                    brain.everyTile[i].isOverRidden = True


def Dispose(view: GameState) -> None:
    if brain.everyGold is not None:
        view.debug_log += "\neveryGold : " + str([str(i) for i in brain.everyGold]) + "\n"

    brain.flushTiles()


def Patrol(view: GameState) -> tuple[int, int]:
    choices = get_connected_nodes_hard(brain.everyTile, (view.location[0], view.location[1]))

    if len(choices) != 0:
        goal = getFurthestOptionFromTail(choices, tail)
    else:
        goal = view.location

    return goal


def goTo(view: GameState, dstPos: tuple[int, int]) -> tuple[int, int]:
    pathList = getShortestPath(brain.everyTile, view.location, dstPos)

    if len(pathList) != 0:
        return pathList[len(pathList) - 2].cPos

    return view.location


def percent(All: float or int, Some: float or int) -> float:
    if All == 0: return 0
    return Some * (100 / All)


def retrieveGold(view: GameState, triggerRange=5) -> bool or tuple[int, int]:
       
    if view.wallet == 0: return False
    closest_treasury = find_closest_type(view.location, MapType.TREASURY)
    if closest_treasury is None: return False
   
    remaining_steps = (view.rounds - view.current_round)

    map_boundaries_size = view.map.width + view.map.height

    if remaining_steps <= map_boundaries_size + triggerRange:
        if remaining_steps <= last_closest_target_dist + triggerRange:
            return closest_treasury

 
    
    pathList = getShortestPath(brain.everyTile, view.location, closest_treasury)
    max_path_size = (view.map.width + view.map.height) / 2
    path_percent = percent(max_path_size,len(pathList)-1)
    gold_percent = percent(view.map.gold_count  , view.wallet) * 1
    pathList = Astar.a_star_algorithm(view,str(list(view.location)),str(list(closest_treasury)),1)
    if len(pathList)!=0 and gold_percent > path_percent:
        return pathList[1]

    
    gold_percent = percent(view.map.gold_count  , view.wallet) * 1.5
    pathList = Astar.a_star_algorithm(view,str(list(view.location)),str(list(closest_treasury)),3)
    if len(pathList)!=0 and gold_percent > path_percent:
        return pathList[1]
    


    return False


def shouldAttack(view: GameState, minimumAttackRatio: float = 0.8) -> False or Action:
    target = find_fattest_enemy(view)

    if target is not None:
        # a=view.map.width*view.map.height
        if target.wallet < view.map.gold_count / 8 or view.attack_ratio <= minimumAttackRatio:
        # if view.attack_ratio <= minimumAttackRatio or target.wallet < 5:
            return False

        dist = abs(view.location[0] - target.pos[0]) + abs(view.location[1] - target.pos[1])

        if dist <= view.ranged_attack_radius:
            return Action.RANGED_ATTACK

        if dist <= view.linear_attack_range and (view.location[0] == target.pos[0] or
                                                 view.location[1] == target.pos[1]):
            if view.location[0] > target.pos[0]:
                return Action.LINEAR_ATTACK_UP

            if view.location[0] < target.pos[0]:
                return Action.LINEAR_ATTACK_DOWN

            if view.location[1] < target.pos[1]:
                return Action.LINEAR_ATTACK_RIGHT

            if view.location[1] > target.pos[1]:
                return Action.LINEAR_ATTACK_LEFT

        target.attacked_round = -1

    return False


def shouldUpgradeDefence(view: GameState, activationThreshold: float) -> bool:
    if percent(view.rounds, view.current_round) < activationThreshold \
            and view.wallet >= view.def_upgrade_cost:
        return True
    return False


def shouldUpgradeAttack(view: GameState, activationThreshold: float) -> bool:
    if percent(view.rounds, view.current_round) < activationThreshold \
            and view.wallet >= view.atk_upgrade_cost:
        return True
    return False


#
def shouldUpgrade(view: GameState, activationThreshold: float) -> Action or bool:
    if view.deflvl > view.atklvl:
        x = shouldUpgradeAttack(view, activationThreshold)
        if x: return Action.UPGRADE_ATTACK

    x = shouldUpgradeDefence(view, activationThreshold)
    if x: return Action.UPGRADE_DEFENCE

    return False


# 1 _ add linear attack block detection ****
# 2 _ find the proper time to attack ****
# 3 _ find the right balance between upgrades ** , DONE - RESULTS ARE FUCKING FANTASTIC!
# 4 _ add find_best_gold and find_fattest_gold *** , DONE
# 5 _ try to divide agents path's * , Checkpoint
# 6 _ collect golds when retrieving *
# 7 _ add permanent MapType override **** , DONE
# 8 _ add wall in fog detection **** , DONE
# 9 - add ability to determine whether upgrades are needed or not , ( gold density of the map)
# 10 - add wallet watcher -> estimate of upgrades and safe wallet ****

def getAction(view: GameState) -> Action:
    
    Dispose(view)
    Update(view)
   
    goal = Patrol(view)

    # x = shouldUpgrade(view, 15)
    # if x: return x
   
    x = shouldUpgradeAttack(view, 8)
    if x: return Action.UPGRADE_ATTACK
    x = shouldUpgradeDefence(view, 16)
    if x: return Action.UPGRADE_DEFENCE
    # go_g = find_closest_type(view.location, MapType.GOLD)
    go_g = find_best_gold(view)
    if go_g is not None:
        goal = goTo(view, go_g)

    go_t = retrieveGold(view)
    if go_t:
      
        if type(go_t)==str:
            goal=Astar.convert_strlist_to_int(go_t)
        else:
            goal=goTo(view, go_t)

    for i in brain.everyAgent:
        view.debug_log += str(brain.everyAgent[i]) + "\n"

    attack = shouldAttack(view)
    if attack and not go_t:
        return attack

    view.debug_log += "" + brain.getVisiblePlacesString() + "\n"

    view.debug_log += "\n everyFog : " + str(brain.everyFog) + "\n"
    view.debug_log += "\n goal : " + str(goal) + "\n"

    if goal in brain.everyFog:
        view.debug_log += "\n goal is a fog! \n"
        brain.last_tested_fog = goal
    else:
        brain.last_tested_fog = None
    a=[i for i in brain.everyTile  if i.Type not in blockingTypes and i.tempType not in blockingTypes]
   
    return getStepTowards(view.location, goal)
