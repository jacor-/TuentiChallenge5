import fileinput
import numpy

def distances(start_girl, girl_list, girl_relationship):
    nodes = girl_list
    distances = girl_relationship

    unvisited = {node: -1 for node in nodes}
    candidates = [start_girl]
    unvisited[start_girl] = 0
    
    while len(candidates) != 0:
        current_girl = candidates.pop()
        current_dist = unvisited[current_girl]
        for neighbour in distances[current_girl]:
            if unvisited[neighbour] != -1:
                continue
            newDistance = current_dist + 1
            unvisited[neighbour] = newDistance
            candidates.append(neighbour)
        candidates = sorted(candidates, key = lambda x: unvisited[x])
    return unvisited

def computeCost(girl, distances_to, girls):    
    #points = [0]
    current_points = 0
    #Criteria 1:
    if girls[girl][0] == 'Y':
        current_points += 7

    #points.append(current_points-numpy.sum(points))
    #Criteria 2:
    for someone in girls:
        if distances_to[girl][someone] == 1:
            friend = someone
            if girls[friend][1] == 'Y':
                current_points += 3
    
    #points.append(current_points-numpy.sum(points))
    #Criteria 3:
    for someone in girls:
        if distances_to[girl][someone] == 2:
            friend_of_friend = someone
            if girls[friend_of_friend][2] == 'Y':
                current_points += 6
                
    #points.append(current_points-numpy.sum(points))
    #Criteria 4:
    exist = False
    for someone in girls:
        if distances_to[girl][someone] == 1:
            friend = someone
            if girls[friend][3] == "Y":
                #like cats
                n_friends_like_cats = 0
                for someone in girls:
                    if distances_to[friend][someone] == 1 and someone != girl:
                        if girls[someone][3] == "Y":
                            n_friends_like_cats += 1
                            break
                if n_friends_like_cats == 0:
                    exist = True
                    break
    if exist:
        current_points += 4

    #points.append(current_points-numpy.sum(points))
    #Criteria 5:
    for someone in girls:
        if distances_to[girl][someone] == -1:
            if girls[someone][4] == 'Y':
                current_points += 5

    #points.append(current_points-numpy.sum(points))
    return current_points#, points


if __name__ == "__main__":
    '''
    Read Input Data
    '''
    inp = fileinput.input()
    num_girls, num_relation_chains = map(int,inp.next()[:-1].split(" "))
    girls = {}
    for _ in range(num_girls):
        girl_name, A, B, C, D, E = inp.next()[:-1].split(" ")
        girls[girl_name] = (A,B,C,D,E)
    relation_map = {}
    for _ in range(num_relation_chains):
        names = inp.next()[:-1].split(" ")
        for name in names:
            if name not in relation_map:
                relation_map[name] = []
        for i_name in range(len(names)):
            for j_name in range(i_name+1, len(names)):
                if names[j_name] not in relation_map[names[i_name]]:
                    relation_map[names[i_name]].append(names[j_name])
                if names[i_name] not in relation_map[names[j_name]]:
                    relation_map[names[j_name]].append(names[i_name])
    for girl in girls:
        if girl not in relation_map:
            relation_map[girl] = []
    
    '''
    Prepare the data structure we will use to solve the problem. It will tell us
    the minimum distance to any person (distance == 1, you are friends. distance == 2,
    you are friends of friends).
    '''
    
    distances_to = {}
    for girl in girls:
        distances_to[girl] = distances(girl, girls, relation_map)
        
    
    print sorted([(girl,computeCost(girl, distances_to, girls)) for girl in girls], key = lambda x: x[1])[-1][1]
            
    