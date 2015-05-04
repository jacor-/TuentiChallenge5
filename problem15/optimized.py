import os
import random
import numpy
import time

NUM_CORES = 32

'''
Este iterador evitara que carguemos listas gigantescas en memoria cuando solo
necesitamos que vaya escupiendo numeritos
'''
def yrange(a,b):
    i = a
    while i < b:
        yield i
        i += 1


'''
Creamos la baraja
'''
def creaBaraja():
    card_numbers = ['1','2','3','4','5','6','7','8','9','10','11','12','13']
    card_palo = ['S','H','D','C']
    cards = []
    for j in card_palo:
        for i in card_numbers:
            cards.append(j+i)
    return cards

'''
Implementamos RANDU y shuffle que describe el algoritmo ruso de los ****
'''

def RANDU2(seed):
    Vj = seed
    modulus = 2**31
    while 1:
        yield Vj
        Vj = numpy.mod(65539 * Vj, modulus) 

def generateShuffle(seed, rand_func):
    current_shuffle = range(52)
    r = rand_func(seed)
    for i in range(52):
        aux_index = numpy.mod(r.next(),52)
        aux = current_shuffle[aux_index]
        current_shuffle[aux_index] = current_shuffle[i]
        current_shuffle[i] = aux
    return current_shuffle

'''
We will transform the pairs of numbers to a single integer (faster and memory
friendlier).
'''
get_new_codification = lambda old: old[1] * 52 + old[0]

'''
Guardamos para cada seed, el hash de las dos cartas que genera. Puesto que necesitamos
todos los hashes y todas las posibles secuencias varias veces, es buena idea guardarlos
en un fichero precalculado.
'''
def precomputeData():
   def yrange(a,b):
    i = a
    while i < b:
        yield i
        i += 1

'''
We build the precomputation step to be executed in many cores.
'''
def _precomputeStart(a_b):
    return _precompute(*a_b)

def _precompute(step, number_steps):
    END_VALUE = 86400000
    res = []
    for seed in yrange(END_VALUE/number_steps * step, END_VALUE/number_steps * (step+1)):
        aux = generateShuffle(seed, RANDU2)
        res.append(get_new_codification((aux[0],aux[2])))
    return res

def precompute():
    import multiprocessing
    import itertools
    steps = 100
    its = itertools.izip(range(steps), itertools.repeat(steps))
    pool = multiprocessing.Pool(NUM_CORES)
    ret = pool.map(_precomputeStart, its)
    pool.close()
    return ret
 


if __name__ == "__main__":
    '''
    Initialize data structures and create them if the file does not exist yet
    '''
    baraja = creaBaraja()
    try:
        f = open("precomputed_data",'rb')
        data = numpy.load(f)
        f.close()
    except:
        data = precomputeData()
        f = open("precomputed_data",'wb')
        numpy.save(f, data)
        f.close()
        
    import fileinput
    
    inp = fileinput.input()
    num_cases = int(inp.next())
    for _ in range(num_cases):
        desired_sequences = []
        for sub_sequence in inp.next()[:-1].split(","):
            for split_index in range(1, len(sub_sequence)):
                if sub_sequence[split_index] in ['S','C','H','D']:
                    break
            a1 = sub_sequence[:split_index]
            a2 = sub_sequence[split_index:]
            desired_sequences.append( get_new_codification((baraja.index(a1), baraja.index(a2))))
       
        '''
        Si la seed genera la cadena que vemos (cada vez con 120000 milisegundos 
        de delay), la seed es la buena... pero solo queremos una!
        
        Partimos el bucle en dos partes para evitar calcular el modulo cada vez 
        (incremento de la eficiencia del algoritmo brutal). El modulo es necesario
        porque en ningun sitio se especifica que la maquina no pueda reiniciarse
        mientras jugamos.
        '''
        
        num_candidate = 0
        exact_candidate = None
        for seed in range(0, 24*3600*1000-3*120000):
            if data[seed] == desired_sequences[0]:
                if data[seed+120000] == desired_sequences[1]:
                    if data[seed+120000*2] == desired_sequences[2]:
                        if data[seed+120000*3] == desired_sequences[3]:                
                            num_candidate += 1
                            exact_candidate = seed
                            if num_candidate > 1:
                                break
        if num_candidate <= 1:
            for seed in range(24*3600*1000-3*120000, 24*3600*1000):
                if data[seed] == desired_sequences[0]:
                    if data[numpy.mod(seed+120000, len(data))] == desired_sequences[1]:
                        if data[numpy.mod(seed+120000*2, len(data))] == desired_sequences[2]:
                            if data[numpy.mod(seed+120000*3, len(data))] == desired_sequences[3]:                
                                exact_candidate = seed
                                num_candidate += 1
                                if num_candidate > 1:
                                    break
    
        if  num_candidate == 1:
            f.write(baraja[data[numpy.mod(exact_candidate+120000*4,len(data))]%52] + baraja[data[numpy.mod(exact_candidate+120000*4,len(data))]/52] + "\n")
        else:
            print "WITHDRAW"
