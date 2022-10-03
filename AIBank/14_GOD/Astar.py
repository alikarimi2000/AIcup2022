import math
from main import GameState
from main import MapType
import MyClass


def a_star_algorithm(self:GameState, start_node:str('[int,int]'), stop_node:str('[int,int]'),Collect_gold=1):
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

        for (m, weight) in Connected_nodes2dictionary(self, n,Collect_gold):
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
   
    return math.sqrt(math.dist(a, b))

def get_connected_nodes(self:GameState,coordinates:tuple([int,int])):
    map_gride=self.map.grid
    i,j=coordinates
    tupel_coordinates=[(i,j+1),(i,j-1),(i-1,j),(i+1,j)]
    
    for i in MyClass.brain.everyTile:
        if i.pos in tupel_coordinates and (i.Type in  MyClass.blockingTypes or i.tempType  in MyClass.blockingTypes) :
           tupel_coordinates.remove(i.pos)
    

    list_coordinates=[list(i) for i in tupel_coordinates ]
    return  list_coordinates


def Connected_nodes2dictionary(self:GameState, coordinates:tuple,Collect_gold:int):
    c, w = convert_strlist_to_int(coordinates)
    loc_gold=[i.coordinates for i in self.map.grid if i.type.value==MapType.GOLD.value]
    poslist = get_connected_nodes(self, (c, w))
    res = []
    for element in (poslist):
        if element in loc_gold:
            res.append((f'{element}', 1/Collect_gold))
        else:
            res.append((f'{element}', 1))

    dic = {
        f'{coordinates}': res
    }
    return dic[coordinates]


def convert_strlist_to_int(str):  # '[3,4]'--->(3,4)
    a = str.split(',')
    b = a[0]
    c = b.split('[')
    d = a[1]
    e = d.split(']')
    return int(c[1]), int(e[0])