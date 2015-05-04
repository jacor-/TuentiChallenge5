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


'''
Lets read the data and print the solution!
'''

if __name__ == "__main__":
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
       
                
    directly_reachable = createDirectlyReachableMaps(ships)
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