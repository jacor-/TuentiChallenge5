"""
To solve this problem we have used the software
The Full Whiskas Model example in the package PuLP for python.

I have no clue about linear optimization... so this package has been intinitely
helpful. The code do not require much explanation and there is no much time 
remaining in the contest... so I wont comment anything else!
"""

# Import PuLP modeler functions
from pulp import *

# Creates a list of the Ingredients

import numpy
import fileinput



inp = fileinput.input()
num_cases = int(inp.next()); 
for case in range(num_cases):
    arboles, prediccio, lenadores = map(int,inp.next()[:-1].split(" ")[:3])
    Treball_maxim = []
    Work_required = []
    for jj in range(lenadores):
        work_list = [int(i) for i in inp.next()[:-1].split(" ") if len(i) > 0]
        Treball_maxim.append(work_list[0])
        Work_required.append(work_list[1:])

    Dedicacio = []
    for arbolito in range(arboles):
        for lenador in range(lenadores):
            Dedicacio.append("%d:%d"%(arbolito, lenador))
                    
    ArbolAssolible = []
    for lenador in range(lenadores):
        ArbolAssolible.append([])
        for arbol in range(arboles):
            ArbolAssolible[-1].append(float(Treball_maxim[lenador])/Work_required[lenador][arbol])
    
    
    prob = LpProblem("My paranoia problem", LpMinimize)
    ingredient_vars = LpVariable.dicts("Dedicacio ",Dedicacio,lowBound=0.,upBound=1.)#,0)
    main_cost = []

    ### El coste total tiene buena pinta...
    for lenador in range(lenadores):
        main_cost.append(lpSum([ingredient_vars["%d:%d"%(arbolito, lenador)] for arbolito in range(arboles)]) *Treball_maxim[lenador])
    prob += lpSum(main_cost)#, "Total Cost of Ingredients per can"


    for arbolito in range(arboles):
        for lenador in range(lenadores):
            prob += lpSum([ingredient_vars["%d:%d"%(arbolito, lenador)] * ArbolAssolible[lenador][arbolito] ]) <= 1, ' garantizando que no curro por encima de mis posibilidades %d %d menor que uno' % (arbolito, lenador)
    
    for lenador in range(lenadores):
        prob += lpSum([ingredient_vars["%d:%d"%(arbolito, lenador)] for arbolito in range(arboles)]) <= 1

    for arbol in range(arboles):
        prob += lpSum([ingredient_vars["%d:%d"%(arbol, lenador)]*ArbolAssolible[lenador][arbol] for lenador in range(lenadores)]) == 1, ' totalidad arbol %d cortado' % arbol

    for arbolito in range(arboles):
        for lenador in range(lenadores):
            prob += lpSum([ingredient_vars["%d:%d"%(arbolito, lenador)]]) >= 0, ' garantizando dedicacion %d %d positivo' % (arbolito, lenador)

    # The problem data is written to an .lp file
    prob.writeLP("WhiskasModel2.lp")
    
    # The problem is solved using PuLP's choice of Solver
    prob.solve()

    if LpStatus[prob.status] == "Infeasible":
        print "Test case #%d: IMPOSSIBLE" % (case+1)
    elif numpy.around(prediccio,2) < numpy.around(value(prob.objective),2):
        print "Test case #%d: %0.2f" % (case+1, value(prob.objective)-prediccio)
    else:
        print "Test case #%d: RIGHT" % (case+1)

