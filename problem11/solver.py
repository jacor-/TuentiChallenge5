import scipy.misc
import fileinput
import operator
 
'''
This function loads all the scenarios from the provided file.
The data is prepared to work with indexs and not with keys because of:
- it improves speed
- the length of the keys can be a problem and many long values can appear as
keys and values
- more clear and easy to understand and work with
'''

def loadDataFromFile():
    def getIndexFromRoom(key, room_indexs, a, b, c):
        now_index = room_indexs.get(key, -1)
        if now_index == -1:
            now_index = len(room_indexs)
            room_indexs[key] = now_index
            a.append([])
            b.append([])
            c.append([])
        return now_index
    
    f = open("scenarios.txt")
    cases = int(f.readline()[:-1])
    scenarios = []
    for i_case in range(cases):
        initial_stamina, num_rooms = map(int,f.readline()[:-1].split(" "))
        room_indexs = {}
        doors_per_index = []
        req_keys_per_index = []
        cost_path_per_index = []
        for i_room in range(num_rooms):
            room_label, num_doors = f.readline()[:-1].split(" ")
            room_index = getIndexFromRoom(room_label, room_indexs, doors_per_index, req_keys_per_index, cost_path_per_index)
            for i_door in range(int(num_doors)):
                destination_room, req_keys, stamina_cost = f.readline()[:-1].split(" ")
                destination_indexs = getIndexFromRoom(destination_room, room_indexs, doors_per_index, req_keys_per_index, cost_path_per_index)
                req_keys_per_index[room_index].append( int(req_keys) )
                cost_path_per_index[room_index].append( int(stamina_cost) )
                doors_per_index[room_index].append(destination_indexs)
        now_scenario = (doors_per_index, req_keys_per_index, cost_path_per_index, room_indexs['start'], room_indexs['exit'], initial_stamina)
        scenarios.append(now_scenario)
    f.close()
    return scenarios

try:
    _ = len(scenarios)
except:
    scenarios = loadDataFromFile()


'''
Dijkstra function. Computes the distance from a node to all the other nodes.
The way we use it implies we could have done it more efficient setting an end 
node, so we can stop computing once the node reaches the end node (we dont really
care the others).
'''
    
def distances(start_node, node_list, node_relationship):
    nodes = node_list
    distances = node_relationship

    unvisited = {node: -1 for node in nodes}
    candidates = [start_node]
    unvisited[start_node] = 0
    
    while len(candidates) != 0:
        current_node = candidates.pop()
        current_dist = unvisited[current_node]
        for neighbour in distances[current_node]:
            if unvisited[neighbour] != -1:
                continue
            newDistance = current_dist + 1
            unvisited[neighbour] = newDistance
            candidates.append(neighbour)
        candidates = sorted(candidates, key = lambda x: unvisited[x])
    return unvisited

'''
This code implements the algorithm described in the problem. We have implemented
an optimization based on the distances to the end node.
We attend the nodes deppending on its distances to the end node. This way, we can
detect when two paths are equivalents and join them in the same one, avoiding the
generation of N exponential paths (we only do it once).

This implementation is the key point to compute the 'big test' in a reasonable time.
'''

def solve_scenario(now_scenario):
    doors_per_index, req_keys_per_index, cost_path_per_index, start, exit, initial_stamina = scenarios[now_scenario]
    stack = [[start, 1, initial_stamina]]

    distances_to_end = []
    for i in range(len(doors_per_index)):
        distances_to_end.append( distances(i, range(len(doors_per_index)), doors_per_index)[exit] )

    ways = 0
    while len(stack) > 0:
        current_place, current_ways, current_stamina = stack.pop(-1)
        num_doors = len(doors_per_index[current_place])
        for i_next_door in range(len(doors_per_index[current_place])):
            next_place = doors_per_index[current_place][i_next_door]
            keys_needed = req_keys_per_index[current_place][i_next_door]
            max_achievable_stamina = min([current_stamina+num_doors, initial_stamina])
            
            if keys_needed > num_doors:
                #I cannot get enough keys
                #print str((current_place, current_ways, current_stamina)) + " --> keys i need " + str((keys_needed))
                continue
            elif max_achievable_stamina < cost_path_per_index[current_place][i_next_door]:
                #print str((current_place, current_ways, current_stamina)) + " --> max stamina i can have " + str((max_achievable_stamina))
                continue
            else:
                stamina_now, minions_killed = min([current_stamina+max([1,keys_needed]), initial_stamina]), max([1,keys_needed]) 
                stamina_now = stamina_now - cost_path_per_index[current_place][i_next_door]
                if stamina_now < 0 :
                    minions_killed -= stamina_now
                    stamina_now = 0
                
                #print str(num_doors) + "  killed minions " + str(minions_killed) + "  " + str(keys_needed)
                if minions_killed > 1:            
                    combinations_out = scipy.misc.comb(num_doors - 1, minions_killed-1, exact = True)            
                else:
                    combinations_out = 1
                
                #print str((current_place, current_ways, current_stamina)) + " --> " + str((next_place, current_ways * combinations_out, stamina_now))

                if next_place == exit:
                    ways += current_ways * combinations_out
                    ways = ways % 1000000007
                else:
                    stack.append( [next_place, current_ways * combinations_out, min([stamina_now, initial_stamina])])
        if now_scenario > 46:
            if len(stack) > 200:
                import numpy
                f = open('perro.out', 'w')
                numpy.save(f, stack)
                f.close()
                break

        stack = sorted(stack, key = lambda x: x[2])
        stack = sorted(stack, key = lambda x: distances_to_end[x[0]], reverse = True)
        
        for now_index in range(len(stack)-2,-1,-1):
            if stack[now_index+1][0] == stack[now_index][0]:
                if stack[now_index+1][2] == stack[now_index][2]:
                    stack[now_index][1] = stack[now_index][1] + stack[now_index+1][1]
                    _ = stack.pop(now_index+1)
    return ways
                

inp = fileinput.input()
for inp_line in inp:
    now_scenario = int(inp_line[:-1])
    print "Scenario %d: %d" % (now_scenario, solve_scenario(now_scenario))
 