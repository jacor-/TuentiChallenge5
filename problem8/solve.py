
import fileinput
import numpy
import itertools

'''
Function to propose changes at each step in the recursion
'''
def proposeChanges(inventario, recetas, is_ingredient_of):
    ingredients_for = []
    for inv_index,_ in inventario:
        ingredients_for += is_ingredient_of[inv_index]
    ingredients_for = list(set(ingredients_for))
    
    new_states = []
    for i_posible_generated in ingredients_for:
        index_to_be_used = []
        can_be_done = True
        for elem_required in recetas[i_posible_generated]:
            #lo tengo? lo puedo usar? (ya lo he usado antes en le bucle raro
            index_existences = [index_x for index_x in range(len(inventario)) if inventario[index_x][0] == elem_required and i_posible_generated not in inventario[index_x][1]]
            if len(index_existences) < recetas[i_posible_generated][elem_required]:
                #no podemos generarlo
                can_be_done = False
                break
            else:
                #necesito coger unos cuantos de los que tengo... los cogere todos aunque es poco eficiente. A ver sino como demonios ordeno eso!
                indexs_iter = itertools.combinations(index_existences, recetas[i_posible_generated][elem_required])
                index_to_be_used += [[now_indexs for now_indexs in indexs_iter]]
        if can_be_done:
            #tengo que combinar todos los index_to_be_used para generar nuevos candidatos
            #   --> index to be used[0] --> maneras de coger elementos equivalentes...
            all_possible_permutations = getAllThePossiblePermutations(index_to_be_used)
            for permutation in all_possible_permutations:
                permutation = sorted(permutation, reverse = True)
                new_inventario = list(inventario)
                #trec els elements que vaig a utilitzar
                i_have_been = []
                for el in permutation:
                    i_am, i_was = new_inventario.pop(el)
                    i_have_been += i_was + [i_am]
                #afegeixo el que fabrico i li indico que he estat en el passat!!!
                new_inventario.append((i_posible_generated,list(set(i_have_been))))
                if len(new_inventario) <= 20 and new_inventario not in new_states:
                    #print str(inventario) + " --> " + str(new_inventario)
                    new_states.append(new_inventario)
    return new_states

'''
Compute the gold value of a given inventary
'''
def getValue(inventario, element_value):
    aux = 0
    for object_inv, _ in inventario:
        aux += element_value[object_inv]
    return aux

'''
Lets see all the ways I can to chose my candidates from the list... the history
of each element is important in this problem, so I do not see any simpler way
to do it!
'''
def getAllThePossiblePermutations(inp_comb, current_comb = [], current_index = 0):
    if current_index >= len(inp_comb):
        return [current_comb]
    s = []
    for elem in inp_comb[current_index]:
        s += getAllThePossiblePermutations(inp_comb, current_comb + list(elem), current_index+1)
    return s


'''
Read the data and prepare data structures
'''
element_indexs = {}
element_value = []
recetas = {}
is_ingredient_of = {}
f = open('book.data')
line = f.readline()
line = line.replace("compound_element_","c")
line = line.replace("basic_element_","b")
line = line[:-1].split(" ")
while len(line[0]) != 0:
    name = line[0]
    value = line[1]
    ingredients = line[2:]
    element_index = element_indexs.get(name, -1)
    if element_index == -1:
        element_indexs[name] = len(element_indexs)
        element_value.append(int(value))
        element_index = len(element_value)-1
    else:
        element_value[element_index] = int(value)
    
    recetas[element_index] = {}
    for ingredient in ingredients:
        ingredient_index = element_indexs.get(ingredient, -1)
        if ingredient_index == -1:
            element_indexs[name] = len(element_indexs)
            element_value.append(0)
            ingredient_index = len(element_indexs)-1
        if ingredient_index not in recetas[element_index]:
            recetas[element_index][ingredient_index] = 1
        else:
            recetas[element_index][ingredient_index] += 1
    line = f.readline()
    line = line.replace("compound_element_","c")
    line = line.replace("basic_element_","b")
    line = line[:-1].split(" ")

for producte_index in recetas:
    for reactiu_index in recetas[producte_index]:
        if reactiu_index not in is_ingredient_of:
            is_ingredient_of[reactiu_index] = []
        if producte_index not in is_ingredient_of[reactiu_index]:
            is_ingredient_of[reactiu_index].append(producte_index)

for i_element in range(len(element_value)):
    if i_element not in is_ingredient_of:
        is_ingredient_of[i_element] = []
    
f.close()

'''
Read input data
'''
inp = fileinput.input()
cases = int(inp.next()[:-1])
for case in range(cases):
    line = inp.next()
    line = line.replace("compound_element_","c")
    line = line.replace("basic_element_","b")
    line = line[:-1].split(" ")
    initial_inventary = line


    


#cases = 1
#for case in range(cases):
#    line = "healing_potion healing_potion healing_potion dragon_scale steel_shield\n"
#    line = line.replace("compound_element_","c")
#    line = line.replace("basic_element_","b")
#    line = line[:-1].split(" ")
#    initial_inventary = line 
 
    
    #The inventary is a list of tuples:
    ## 1) Index of the element
    ## 2) What this object has been in the past (restriction of the problem)
    inventario = [(element_indexs[object_o], []) for object_o in initial_inventary]

    max_gold = -1
    current_inventario = [inventario]
    
    while len(current_inventario) > 0:
        now_inventario = current_inventario.pop(0)
        now_value = getValue(now_inventario, element_value)
        if now_value > max_gold:
            max_gold = now_value
        current_inventario += proposeChanges(now_inventario, recetas, is_ingredient_of)
 
    print max_gold