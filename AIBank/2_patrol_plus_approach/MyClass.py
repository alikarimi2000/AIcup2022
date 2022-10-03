import random

from main import GameState
from main import Action
from main import MapType
from main import MapTile
import traceback
import math


def a_star_algorithm(self, map_gride, start_node, stop_node):
    open_list = set([start_node])
    closed_list = set([])
    g = {}
    g[start_node] = 0
    parents = {}
    parents[start_node] = start_node

    while len(open_list) > 0:
        n = None
        for v in open_list:
            if n == None or g[v] + h(v, stop_node, self) < g[n] + h(n, stop_node, self):
                n = v

        if n == None:
            return None
        if n == stop_node:
            reconst_path = []

            while parents[n] != n:
                reconst_path.append(n)
                n = parents[n]

            reconst_path.append(start_node)

            reconst_path.reverse()
            return reconst_path

        for (m, weight) in Connected_nodes2dictionary(self, n):
            if m not in open_list and m not in closed_list:
                open_list.add(m)
                parents[m] = n
                g[m] = g[n] + weight

            else:
                if g[m] > g[n] + weight:
                    g[m] = g[n] + weight
                    parents[m] = n

                    if m in closed_list:
                        closed_list.remove(m)
                        open_list.add(m)

        open_list.remove(n)
        closed_list.add(n)
    return None


def h(n, stop_node, self):
    a = convert_strlist_to_int(n)
    b = convert_strlist_to_int(stop_node)
    # a=(x-x1)**2 +(y-y1)**2
    # math.sqrt(a)
    # self.debug_log += f'nnnnnn {str(math.sqrt(a))}\n'
    return math.sqrt(math.dist(a, b))


def convert_strlist_to_int(str):  # '[3,4]'--->(3,4)
    a = str.split(',')
    b = a[0]
    c = b.split('[')
    d = a[1]
    e = d.split(']')
    return int(c[1]), int(e[0])


def getFurthestOptionFromTail(options: list, tail: list) -> tuple[int, int]:
    aveDist: float = 0.0
    maxAveDist: float = 0.0
    maxAveDistIndex: int = 0

    for i in range(0, len(options)):
        aveDist = getAverageDistance(options[i], tail)
        if i == 0 or aveDist > maxAveDist:
            maxAveDist = aveDist
            maxAveDistIndex = i

    return options[maxAveDistIndex]

def get_connected_nodes(self,coordinates):
    map_gride=self.map.grid
    i,j=coordinates
    list_coordinates=[[i,j+1],[i,j-1],[i-1,j],[i+1,j]]
    for i in map_gride:
        if i.coordinates in list_coordinates and i.type==4:
            list_coordinates.remove(i.coordinates)
    return list_coordinates

def get_connected_nodes_2(self:GameState, coordinates):
    i, j = coordinates
    list_coordinates = [[i, j + 1], [i, j - 1], [i - 1, j], [i + 1, j]]

    forbidden_types = [MapType.WALL.value,MapType.OUT_OF_MAP.value,MapType.AGENT.value]

    awesome_result =  [list(i.coordinates) for i in self.map.grid if list(i.coordinates) in
            list_coordinates and i.type not in forbidden_types]

    if len(awesome_result)==0: return list_coordinates

    return awesome_result



def Connected_nodes2dictionary(self, coordinates):
    c, w = convert_strlist_to_int(coordinates)
    poslist = get_connected_nodes(self, (c, w))
    res = []
    for element in (poslist):
        res.append((f'{element}', 1))

    dic = {
        f'{coordinates}': res
    }
    return dic[coordinates]


def getAverageDistance(point: tuple[int, int], pointList: list) -> float:
    distSum: int = 0
    distCounter: int = 0

    for i in range(0, len(pointList)):
        distCounter += 1
        p2 = pointList[i]
        dist = abs(point[0] - p2[0]) + abs(point[1] - p2[1])
        distSum += dist

    if distCounter == 0: return 0

    return distSum / distCounter

def getStepTowards(source, destination) -> Action:
    if source[0] < destination[0]:
        return Action.MOVE_DOWN
    if source[0] > destination[0]:
        return Action.MOVE_UP

    if source[1] < destination[1]:
        return Action.MOVE_RIGHT
    if source[1] > destination[1]:
        return Action.MOVE_LEFT

    return Action.STAY


def find_closest_gold(self):

    closets_gold = None
    closets_gold_dist:int = 0
    first_iteration:bool = True

    for i in self.map.grid:
        if i.type == MapType.GOLD.value:
            dist = getAverageDistance(self.location,[i.coordinates])
            if first_iteration or dist < closets_gold_dist:
                closets_gold = i.coordinates
                closets_gold_dist = dist

            first_iteration = False

    if closets_gold is not None: return list(closets_gold)

    return list(self.location)




tail: list = []
TAIL_MAX_SIZE: int = 10


def getAction(self: GameState) -> Action:
    tail.append(list(self.location))
    if len(tail) > TAIL_MAX_SIZE:
        tail.pop(0)

    start = list(self.location)

    gold_position = find_closest_gold(self)

    goal = None

    if gold_position == list(self.location):
        choices = get_connected_nodes_2(self,(self.location[0],self.location[1]))

        goal = getFurthestOptionFromTail(choices,tail)

    else:
        try:
            path = a_star_algorithm(self, self.map.grid, str(start), str(gold_position))
            if len(path)>=2:
                goal = convert_strlist_to_int(path[1])
            else:
                goal = list(self.location)

        except Exception as e:
            goal = self.location
            self.debug_log+="Error is : "+str(e)+"\n"



    return getStepTowards(self.location, goal)
