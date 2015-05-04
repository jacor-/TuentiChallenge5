import numpy
import fileinput
import time

'''
This function tell us if a point is inside a given polygon
'''
def point_in_poly(x,y,poly):

    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside

'''
Lets build a map which tell us which set of ships is destroyed if we shot the i-th
ship. (a 1 in the position i,j will mean that the ship j will be destroyed by the
chain generated when i is destroyed.
'''

def createInverseReachableMaps(sparse_ship_reachs):
    inverse_map = [[] for i in range(len(sparse_ship_reachs))]
    for i_reaches in range(len(sparse_ship_reachs)):
        for i_is_reached in sparse_ship_reachs[i_reaches]:
            inverse_map[i_is_reached].append(i_reaches)
    return inverse_map
    
    
def createDirectlyReachableMaps(ships):
    directly_reachable = [[] for _ in ships]
    for i_ship in range(len(ships)):
        if i_ship % 500 == 0: 
            print str(i_ship) + "   of   " + str(len(ships))
        (x1,y1),poly1  = ships[i_ship]
        for j_ship in range(len(ships)):
            (x2,y2),poly2  = ships[j_ship]
            if point_in_poly(x2,y2,poly1):
                directly_reachable[i_ship].append(j_ship)
    return directly_reachable

def createSparseReachableMaps(directly_reachable):
    def canReach(i,directly):
        is_reachable_reach = []
        now_reachable = [i]
        while len(now_reachable) != 0:
            reaching = now_reachable.pop()
            for j in directly[reaching]:
                if j not in is_reachable_reach:
                    now_reachable.append(j)
                    is_reachable_reach.append(j)
        return is_reachable_reach
    reachable = [canReach(i,directly_reachable) for i in range(len(directly_reachable))]
    return reachable


def createDenseReachableMaps(directly_reachable):
    def canReach(i,directly):
        is_reachable_reach = numpy.zeros(len(directly))
        now_reachable = [i]
        while len(now_reachable) != 0:
            reaching = now_reachable.pop()
            for j in range(len(is_reachable_reach)):
                if j in directly[reaching]:
                    if is_reachable_reach[j] != True:
                        now_reachable.append(j)
                        is_reachable_reach[j] = True
        return is_reachable_reach
    reachable = numpy.array([canReach(i,directly_reachable) for i in range(len(directly_reachable))])
    return reachable

'''
Recursively lets shot the ships and see what is the minimum number of shots we
can do before all of them are destroyed. 
'''
def makeYourShot(now_reachable):
    aux = now_reachable.sum(axis=0)
    isolated_ships = numpy.array([i for i,x in enumerate(aux) if x == 1])
    if len(isolated_ships) > 0:
        '''
        There are some ships which are not reachable by anyone... I will need at least
        one shot for each one of them.
        '''
        directly_destroyed = len(isolated_ships)
        non_destroyed = [i for i,x in enumerate(numpy.sum(now_reachable[isolated_ships], axis=0) >= 1) if x == 0]
        if len(non_destroyed) == 0:
            '''
            There is nobody else to be destroyed, exit condition
            '''
            return directly_destroyed
        new_reachable = now_reachable[non_destroyed,:][:,non_destroyed]
        return directly_destroyed + makeYourShot(new_reachable)

    else:
        '''
        I will avoid destroying the ships which will only generate they own destruction.
        Actually, if this is the case:
        - They are reachable
        - They wont start any extra chain...
        Lets wait and they will eventually be destroyed.
        All the others will be candidates to be destroyed.
        '''
        candidates = [i for i,x in enumerate(now_reachable.sum(axis=1)) if x != 1]
        '''
        Which ships will remain undestroyed if I shot each one of the candidates?
        '''
        non_destroyed_by_candidate = [[i for i,x in enumerate(now_reachable[candidate]) if x == False] for candidate in candidates]
        '''
            There is a candidate which will start a reaction which will kill all
            the others... I only need to shot once
        '''    
        if min(map(len, non_destroyed_by_candidate)) == 0:
            return 1
        '''
            Otherwise I will try to destroy each candidate... backrpop; I cannot
            do much more.
            An extra prunning has been done: if I can destroy them all with 2 ships,
            I stop exploring the space (I know with one is impossible, 2 is the next
            minimum possible required value).
        '''    
        min_destroyed_now = len(candidates)
        for non_destroyed in non_destroyed_by_candidate:
            new_reachable = now_reachable[non_destroyed,:][:,non_destroyed]
            new_destroyed = 1 + makeYourShot(new_reachable)
            if new_destroyed < min_destroyed_now:
                min_destroyed_now = new_destroyed
                if new_destroyed == 2:
                    break
        return min_destroyed_now


'''
Recursively lets shot the ships and see what is the minimum number of shots we
can do before all of them are destroyed. 
'''
def destroyTheIsolatedShips(now_reachable):    
    '''
    There are some ships which are not reachable by anyone... I will need at least
    one shot for each one of them.
    '''
    aux = now_reachable.sum(axis=0)
    isolated_ships = numpy.array([i for i,x in enumerate(aux) if x == 1])
    if len(isolated_ships) > 0:
        directly_destroyed = len(isolated_ships)
        non_destroyed = [i for i,x in enumerate(numpy.sum(now_reachable[isolated_ships], axis=0) >= 1) if x == 0]
        now_reachable = now_reachable[non_destroyed,:][:,non_destroyed]
        return directly_destroyed, now_reachable
    else:
        return 0, now_reachable

def destroySuperfluousTargets(now_reachable):
    '''
    There are some ships which are reachable but the destruction of which wont start
    any chain... they will die by themselves if we destro the others... we wont care
    about them.
    '''
    stop = True
    aux = now_reachable.sum(axis=1)
    superfluous_ships = numpy.array([i for i,x in enumerate(aux) if x == 1])
    if len(superfluous_ships) > 0:
        print "deleting %d" % len(superfluous_ships)
        non_superfluous_ships = numpy.array([i for i,x in enumerate(aux) if x != 1])
        now_reachable = now_reachable[non_superfluous_ships,:][:,non_superfluous_ships]
        stop = False
    return 0, now_reachable, stop
    
def makeYourShot2(now_reachable, shots_in_the_past, minimum_shots):
    if shots_in_the_past + 1 >= minimum_shots:
        return minimum_shots
    '''
        There is a candidate which will start a reaction which will kill all
        the others... I only need to shot once
    '''    
    destroyed_by_candidate = numpy.sum(now_reachable, axis=1)
    if numpy.max(destroyed_by_candidate) == now_reachable.shape[0]:
        return shots_in_the_past + 1
    '''
        Otherwise I will try to destroy each candidate... backrpop; I cannot
        do much more.
        An extra prunning has been done: if I can destroy them all with 2 ships,
        I stop exploring the space (I know with one is impossible, 2 is the next
        minimum possible required value).
    '''
    if shots_in_the_past + 2 >= minimum_shots:
        return minimum_shots

    #non_destroyed_by_candidate = sorted(non_destroyed_by_candidate, key = lambda x: len(x), reverse=True)
    for i_candidate in range(now_reachable.shape[0]):
        non_destroyed = numpy.array([i for i,x in enumerate(now_reachable[i_candidate]) if x == False])
        new_reachable = now_reachable[non_destroyed,:][:,non_destroyed]
        new_shots = makeYourShot2(new_reachable, shots_in_the_past + 1, minimum_shots)
        if new_shots < minimum_shots:
            minimum_shots = new_shots
            if minimum_shots == shots_in_the_past + 2:
                return minimum_shots
    return minimum_shots


'''
Lets read the data and print the solution!
'''

if __name__ == "__main__":
    '''
    print "Reading data"    
    ships = []    
    inp = fileinput.input()
    num_ships = int(inp.next()[:-1])
    for _ in range(num_ships):
        x,y = map(int, inp.next()[:-1].split(" "))
        ships.append(((x,y),[]))
        num_vertex = int(inp.next()[:-1])
        vertexs = inp.next()[:-1].split(" ")
        for j in range(num_vertex):
            ships[-1][-1].append((int(vertexs[2*j]),int(vertexs[2*j+1])))
       
    '''         
                
    print "Building directly reachable"
    #directly_reachable = createDirectlyReachableMaps(ships)
    #f = open('directly_reachable_big', 'w')
    #numpy.save(f, directly_reachable)
    #f.close()
    # TO LOAD
    #f = open('directly_reachable_big')
    #directly_reachable = numpy.load(f)
    #f.close()

    print "Building reachable"
    #sparse_ship_reachs = createSparseReachableMaps(directly_reachable)
    #f = open('sparse_ship_reachs_big', 'w')
    #numpy.save(f, sparse_ship_reachs)
    #f.close()
    # TO LOAD
    #f = open('sparse_ship_reachs_big')
    #sparse_ship_reachs = numpy.load(f)
    #f.close()
    print "Building inverse reachable"
    #sparse_ship_is_reachable_by = createInverseReachableMaps(sparse_ship_reachs)
    #f = open('sparse_ship_is_reachable_by_big', 'w')
    #numpy.save(f, sparse_ship_is_reachable_by)
    #f.close()
    # TO LOAD
    #f = open('sparse_ship_is_reachable_by_big')
    #sparse_ship_is_reachable_by_big = numpy.load(f)
    #f.close()

    def deleteShips(ships, sparse_ship_is_reachable_by, sparse_ship_reachs):
        to_be_destroyed = [i_ship for i_ship in ships]
        destroyed_until_now = []
        total_ships_number = len(sparse_ship_is_reachable_by)
        deleted = 0
        while len(to_be_destroyed) > 0:
            i_ship = to_be_destroyed.pop(0)
            destroyed_until_now.append(i_ship)
            for i in range(total_ships_number):
                if i_ship in sparse_ship_is_reachable_by[i]:
                    sparse_ship_is_reachable_by[i].remove(i_ship)
                if i_ship in sparse_ship_reachs[i]:
                    sparse_ship_reachs[i].remove(i_ship)
                    
            for i in range(total_ships_number):                    
                if i in sparse_ship_reachs[i_ship]:
                    if i not in destroyed_until_now and i not in to_be_destroyed:
                        to_be_destroyed.append(i)
                        
        destroyed_until_now = sorted(destroyed_until_now, reverse = True)
        for i_ship in destroyed_until_now:
            sparse_ship_reachs[i_ship] = []
            sparse_ship_is_reachable_by[i_ship] = []
        return len(destroyed_until_now), 0, sparse_ship_is_reachable_by, sparse_ship_reachs

    def deleteIntermediateSteps(sparse_ship_is_reachable_by, sparse_ship_reachs):
        some_change = True
        total_nodes = len(sparse_ship_is_reachable_by)
        deleted = 0
        shots = 0
        while some_change:
            some_change = False
            for i in range(total_nodes):
                if len(sparse_ship_is_reachable_by[i]) == 2 and len(sparse_ship_reachs[i]) == 2:
                    some_change = True
                    node_previous = sparse_ship_is_reachable_by[i][0] if sparse_ship_is_reachable_by[i][0] != i else sparse_ship_is_reachable_by[i][1]
                    node_next = sparse_ship_reachs[i][0] if sparse_ship_reachs[i][0] != i else sparse_ship_reachs[i][1]
                    
                    #print "Node %d node can reach     : %s" % (i, str(sparse_ship_reachs[i]))
                    #print "--> Node %d can be reached : %s" % (node_next, str(sparse_ship_is_reachable_by[node_next]))
                    #print "--> Node %d can reah       : %s" % (node_previous, str(sparse_ship_reachs[node_previous]))

                    
                    if node_previous != node_next:
                        sparse_ship_is_reachable_by[i] = []
                        sparse_ship_reachs[i] = []
                        sparse_ship_is_reachable_by[node_next].remove(i)
                        sparse_ship_is_reachable_by[node_next].append(node_previous)
                        sparse_ship_reachs[node_previous].remove(i)
                        sparse_ship_reachs[node_previous].append(node_next)
                    else:
                        sparse_ship_is_reachable_by[i] = []
                        sparse_ship_reachs[i] = []
                        sparse_ship_is_reachable_by[node_next].remove(i)
                        sparse_ship_reachs[node_next].remove(i)
                    deleted += 1
        return deleted, shots, sparse_ship_is_reachable_by, sparse_ship_reachs

    def delete_isolated_ships(sparse_ship_is_reachable_by, sparse_ship_reachs): 
        isolated_ships = [i for i in range(len(sparse_ship_is_reachable_by)) if len(sparse_ship_is_reachable_by[i]) == 1]
        deleted, _, sparse_ship_is_reachable_by, sparse_ship_reachs= deleteShips(isolated_ships, sparse_ship_is_reachable_by, sparse_ship_reachs)
        return deleted, len(isolated_ships), sparse_ship_is_reachable_by, sparse_ship_reachs
    
    
    def delete_superfluous_ships(sparse_ship_is_reachable_by, sparse_ship_reachs): 
        superfluous_ships = [i for i in range(len(sparse_ship_reachs)) if len(sparse_ship_reachs[i]) == 1]    
        deleted, _, sparse_ship_is_reachable_by, sparse_ship_reachs= deleteShips(superfluous_ships, sparse_ship_is_reachable_by, sparse_ship_reachs)
        return deleted, 0, sparse_ship_is_reachable_by, sparse_ship_reachs
    
    def createDenseReachableMapFromSparse(sparse_ship_reachs):
        non_zero_keys = [i for i in range(len(sparse_ship_reachs)) if len(sparse_ship_reachs[i]) > 0]
        ships_alive = dict(zip(non_zero_keys,range(len(non_zero_keys))))
        dense_matrix = numpy.zeros((len(ships_alive), len(ships_alive)))
        for non_zero_key in ships_alive:
            index_current_ship = ships_alive[non_zero_key]
            for j in sparse_ship_reachs[non_zero_key]:
                index_reachable_ship = ships_alive[j]
                dense_matrix[index_current_ship][index_reachable_ship] = 1
        return dense_matrix


    t1 = time.time()

    print "Destroying isolated"
    #print numpy.sum(map(lambda x: len(x) > 0, sparse_ship_reachs))
    #isolated_ships = get_isolated_ships(sparse_ship_is_reachable_by)
    #shots_until_now = len(isolated_ships)
    #sparse_ship_is_reachable_by, sparse_ship_reachs = deleteShips(isolated_ships, sparse_ship_is_reachable_by, sparse_ship_reachs) 
    #print numpy.sum(map(lambda x: len(x) > 0, sparse_ship_reachs))

    print "Deleting superfluous"
    #print numpy.sum(map(lambda x: len(x) > 0, sparse_ship_reachs))
    #superfluous_ships = get_superfluous_ships(sparse_ship_reachs)
    #while len(superfluous_ships) > 0:
    #    sparse_ship_is_reachable_by, sparse_ship_reachs = deleteShips(superfluous_ships, sparse_ship_is_reachable_by, sparse_ship_reachs) 
    #    superfluous_ships = get_superfluous_ships(sparse_ship_reachs)
    #    print numpy.sum(map(lambda x: len(x) > 0, sparse_ship_reachs))



    #f = open('all_prepared_to', 'w')
    #numpy.save(f, sparse_ship_reachs)
    #numpy.save(f, sparse_ship_is_reachable_by)
    #numpy.save(f, shots_until_now)    
    #f.close()

    print " --------------------------------------------------------------------------"

    f = open('all_prepared_to')
    sparse_ship_reachs = numpy.load(f)
    sparse_ship_is_reachable_by = numpy.load(f)
    shots_until_now = numpy.load(f)    
    f.close()
    
    print "we have shot %d times" % (shots_until_now)

    iteration_deleted = -1    

    print numpy.sum(map(lambda x: len(x) > 0, sparse_ship_reachs))

    while iteration_deleted != 0:
        iteration_deleted = 0
        
        now_deleted, now_shots, sparse_ship_is_reachable_by, sparse_ship_reachs = delete_isolated_ships(sparse_ship_is_reachable_by, sparse_ship_reachs)
        shots_until_now += now_shots
        iteration_deleted += now_deleted
        now_deleted = -1
        while now_deleted != 0:
            now_deleted, now_shots, sparse_ship_is_reachable_by, sparse_ship_reachs = delete_superfluous_ships(sparse_ship_is_reachable_by, sparse_ship_reachs)
            shots_until_now += now_shots
            iteration_deleted += now_deleted

        now_deleted, now_shots, sparse_ship_is_reachable_by, sparse_ship_reachs = deleteIntermediateSteps(sparse_ship_is_reachable_by, sparse_ship_reachs)
        iteration_deleted += now_deleted
        shots_until_now += now_shots
                
        print "deleted %d ships in this iteration, we have shot %d times" % (iteration_deleted, shots_until_now)
    
    print numpy.sum(map(lambda x: len(x) > 0, sparse_ship_reachs))
    
    

    #print "going to dense"         
    #dense_reachable_map = createDenseReachableMapFromSparse(sparse_ship_reachs)


    #print makeYourShot2(dense_reachable_map, shots_until_now, shots_until_now+len(dense_reachable_map))
    #print time.time()-t1