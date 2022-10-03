import random
from main import Action
from main import GameState
from main import MapType

def getStepTowards(source:tuple[int,int],destination:tuple[int,int]) -> Action:
    if source[0] < destination[0]:
        return Action.MOVE_DOWN
    elif source[0] > destination[0]:
        return Action.MOVE_UP

    if source[1] < destination[1]:
        return Action.MOVE_RIGHT
    elif source[1] > destination[1]:
        return Action.MOVE_LEFT

    return Action.STAY

def getValidChoices(view:GameState) -> list:
    result:list = []
    possible_choices = [list(i) for i in [view.location,view.location,view.location,view.location,view.location]]

    possible_choices[0][0]-=1
    possible_choices[1][0]+=1
    possible_choices[2][1]-=1
    possible_choices[3][1]+=1


    for i in view.map.grid:
        if i.coordinates in possible_choices:
            if i.data not in [MapType.OUT_OF_MAP,MapType.OUT_OF_SIGHT,MapType.WALL]:

                if i.coordinates[0]>view.location[0]:
                    result.append(Action.MOVE_DOWN)
                if i.coordinates[0]<view.location[0]:
                    result.append(Action.MOVE_UP)

                if i.coordinates[1]>view.location[1]:
                    result.append(Action.MOVE_RIGHT)
                if i.coordinates[1]<view.location[1]:
                    result.append(Action.MOVE_LEFT)



    return result



def getAction(view:GameState) -> Action:
    choices = getValidChoices(view)

    if len(choices)!=0:
        return random.choice(choices)

    return Action.MOVE_DOWN
