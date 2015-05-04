from base64 import *
import fileinput
import numpy

'''
We compute all the possible routes between original and the destination node.
We start with this list of candidates because our search space has a clear restriction,
all the routes start in a node and ends in another fixed node. Furthermore, the destination
node must be reachable from the origin one.
Starting our backtrack with this specific cases is a way of prunning this space.
We also take into account that a given route has a maximum length (our ship must
be the first one to reach the destination).
'''
def all_routes(origin, destination, route_cost, max_length):
    distances = route_cost
    result_paths = []
    candidates = [(origin, [origin])]       
    while len(candidates) != 0:
        current_node, current_path = candidates.pop(0)
        for neighbour, route_cost in distances[current_node].items():
            if neighbour not in current_path:
                if neighbour == destination:
                    result_paths.append(list(current_path) + [neighbour])
                else:
                    if len(current_path) + 1 < max_length:                        
                        candidates.append((neighbour, list(current_path) + [neighbour]))
    return result_paths

'''
This function computes the path followed by each other ship. They always choose 
the lower/highest possible path (depending on the parity of its index).
We consider the situation where a ship does never reach its objective (it gets
eternally looping). 
We save a base path which potentially ends in the destiny island and a bucle path
where the ship loops once this has finished.
'''
def compute_path(ship_index, origin, destiny, num_nodes, route_cost):
    path = []
    current_node = origin
    while True:
        if current_node == destiny or current_node in path:
            break
        path.append(current_node)
        if ship_index % 2 != 0:
            current_node = sorted(sorted(route_cost[current_node].items(), key = lambda x: x[1]['order']), key = lambda x: x[1]['cost'])[0][0]
        else:
            current_node = sorted(sorted(route_cost[current_node].items(), key = lambda x: x[1]['order'], reverse = True), key = lambda x: x[1]['cost'])[-1]  [0]          
    if current_node == destiny:
        path.append(destiny)
        bucle_path = []
    else:
        bucle_path = path[path.index(current_node):]
        path = path[:path.index(current_node)]
    return path, bucle_path

'''
Given a time step, returns the position of the ship given a main route and a
looping part. This allows us to deal with ships which do not reach the final island
and just stay looping eternally.
'''
def location_at_step(ruta, bucle, now_step):
    if now_step >= len(ruta):
        now_step = (now_step - len(ruta)) 
        if len(bucle) > 0:
            now_node = bucle[ now_step % len(bucle)]
        else:
            now_node = ruta[-1]
    else:
        now_node = ruta[now_step]
    return now_node

'''
Returns the cost of a route (path).
It requires to know:
- Cost of arriving each island
- Cost of moving from a island to the next
- Which ships arrives to each island in each time step
'''
def computeCost(initial_gold, path, cost_per_path, extra_cost_per_ships, cost_per_island):
    gold = initial_gold
    
    
    for i_step in range(1,len(path)-1):
        if path[i_step] != path[i_step-1]:    
            gold = gold - cost_per_island[path[i_step]] - cost_per_path[path[i_step-1]][path[i_step]] - extra_cost_per_ships[i_step-1,path[i_step]]
        else:
            gold = gold + 10  - extra_cost_per_ships[i_step-1,path[i_step]]
        
        if gold <= 0:
            return -1, i_step, path
    #last step
    gold = gold - cost_per_island[path[-1]] - cost_per_path[path[-2]][path[-1]]
    return max(gold, 0), len(path), path

'''
Given a set of paths, it generate new paths with the only 'tool' we have, staying
at a given island (increasing this way the gold). We generate all the possible
combinations of paths obtained by modifying the original one by staying in a different
island (we only add one single step to the sequence).
It takes an argument "max_index" which allow us to not take into account the whole sequence
but only until the gold become negative (so the rest of the sequence cannot be done by the ship). 
'''
def generateNewCandidates(path, max_index, max_length):
    new_candidates = []
    if len(path) < max_length:
        for i in range(1,min(len(path)-1, max_index)):
            new_candidates.append(path[:i]+[path[i]]+path[i:])
    return new_candidates

'''
It computes all the possible routes by using the previous defined functions and
returns the highest quantity of gold when a route reaches the destination island.
'''
def bestRoute(initial_gold, my_ship_start_position, my_ship_end_position, cost_per_path, extra_cost_per_ships, cost_per_island, initial_candidates, max_length):
    alive_candidates = map(lambda path: computeCost(initial_gold, path, cost_per_path, extra_cost_per_ships, cost_per_island), initial_candidates)
    max_gold = -1
    while len(alive_candidates) != 0:
        new_gold, new_limit, new_path = alive_candidates.pop(0)
        if new_gold > max_gold:
            max_gold = new_gold
        alive_candidates += map(lambda path: computeCost(initial_gold, path, cost_per_path, extra_cost_per_ships, cost_per_island), generateNewCandidates(new_path, new_limit, max_length))
    return int(max_gold)

def __execute__(inp, get_next):
    '''
    Read the input
    '''
    num_islands = int(get_next(inp))
    index_islands = {}
    islands_cost = numpy.zeros(num_islands)
    for i in range(num_islands):
        island = get_next(inp)
        island_name, island_cost = island.split(" ")
        index_islands[island_name] = i
        islands_cost[i] = int(island_cost)
    
    num_routes = int(get_next(inp))
    routes = {}
    for _ in range(num_routes):
        route = get_next(inp)
        island_name_origin, island_name_dest, route_cost = route.split(" ")
        now_route = routes.get(index_islands[island_name_origin],-1)
        if now_route == -1:
            now_route = {}
        now_route[index_islands[island_name_dest]] = {'cost':int(route_cost), 'order': len(now_route)}
        routes[index_islands[island_name_origin]] = now_route
    routes[index_islands['Raftel']] = {}
    
    num_ships = int(get_next(inp))
    ships = {}
    for _ in range(num_ships):
        ship = get_next(inp)
        ship_ind, ship_name, ship_gold, start_island = ship.split(" ")
        ships[int(ship_ind)] = {'name':ship_name, 'gold':int(ship_gold), 'start_position':index_islands[start_island]}

    '''
    Lets see what the other ships will be doing during until they reach the destination island.
    We will have to reach this island before the first of them does!
    '''    
    rutes_barquitus = [(key,compute_path(key, ships[key]['start_position'], index_islands["Raftel"], num_islands, routes)) for key in range(2,len(ships)+1)]
    max_length = -1
    for key,(ruta, bucle) in rutes_barquitus:
        if (max_length == -1 and len(bucle) == 0) or (max_length != -1 and len(bucle) == 0 and len(ruta) > max_length):
            max_length = len(ruta)
    extra_cost_path = numpy.zeros((max_length-1,num_islands), dtype=numpy.int32)
    for key,(ruta, bucle) in rutes_barquitus:
        for i_step in range(max_length-1):
            extra_cost_path[i_step, location_at_step(ruta, bucle, i_step+1)] += ships[key]['gold']

    '''
    Prepare parameters (just making them more readible)
    '''
    cost_per_island = islands_cost
    extra_cost_per_ships = extra_cost_path
    cost_per_path = {}
    for key in routes:
        cost_per_path[key] = {}
        for key2 in routes[key]:
            cost_per_path[key][key2] = routes[key][key2]['cost']
    my_ship_start_position = ships[1]["start_position"]
    my_ship_end_position = index_islands["Raftel"]
    
    '''
    Compute the most simple sequences starting at origin and finishing at the end position.
    '''    
    initial_candidates = [route for route in all_routes(my_ship_start_position, my_ship_end_position, cost_per_path, max_length)]
    '''
    Compute the best path given the initial candidates and applying modifications in each of them
    until we cover all the space.
    The way we do it prunes the space of paths with non correct origin or destination,
    paths which reaches the final island later than the other pirates and paths with loops. 
    '''    
    best_step_gold = bestRoute(ships[1]['gold'], my_ship_start_position, my_ship_end_position, cost_per_path, extra_cost_per_ships, cost_per_island, initial_candidates, max_length)
    print best_step_gold

if __name__ == "__main__":
    import fileinput
    inp = fileinput.input()    
    __execute__(inp, lambda x: x.next()[:-1])
