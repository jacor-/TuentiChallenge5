import fileinput
import os
import numpy

floatX = numpy.float128


def primes(n):
    '''
    We use this function to compute the firsts 25 integers (we can actually
    precompute it... but who cares!
    '''
    sieve = [True] * n
    for i in xrange(3,int(n**0.5)+1,2):
        if sieve[i]:
            sieve[i*i::2*i]=[False]*((n-i*i-1)/(2*i)+1)
    return [2] + [i for i in xrange(3,n,2) if sieve[i]]

def decompose(value, prime_numbers):
    '''
    We will decompose the given values (long types) in the given prime numbers.
    We will count in a vector in which each index represent the number of times
    that i-th prime number appears as a factor of value.
    '''
    vals = numpy.zeros(25, dtype=numpy.int32)
    for i in range(len(prime_numbers)):
        while value % prime_numbers[i] == 0:
            vals[i] += 1
            value = value // prime_numbers[i]
    return vals


def getMaximumRepetitions(decomposition):
    '''
    We get the maximum repetitions and the specific indexs in the input vector which
    have been repeated that maximum number of time.
    '''
    max_repetitions = max(decomposition)
    ordenat = sorted(zip(range(len(decomposition)), decomposition), key = lambda x: x[1], reverse = True)
    for i in range(1,len(decomposition)):
        if ordenat[i][1] != ordenat[i-1][1]:
            break
    max_repeated_values = sorted(zip(*ordenat[:i])[0])
    return max_repetitions, max_repeated_values

'''
Lets precompute the decomposition of each individual number in the train set. Once
this is done, computing the aggregation in a time interval will be trivial
'''
def precompute():
    f = open("numbers.txt")
    numbers = map(long, f.readlines())
    f.close()
        
    first_25_primes = primes(100)[:25]
    decompositions = numpy.zeros((len(numbers),25),dtype=numpy.int32)
    for i_number in range(len(numbers)):
        decompositions[i_number] = decompose(numbers[i_number], first_25_primes) 
    
    f = open("decomposed_numbers.txt", 'w')
    numpy.save(f, decompositions)
    f.close()

'''
Lets execute!
'''
if __name__ == "__main__":
    if not "decomposed_numbers.txt" in os.listdir("."):
        precompute()
    f = open("decomposed_numbers.txt")
    decompositions = numpy.load(f)
    f.close()

    first_25_primes = primes(100)[:25]
   
    inp = fileinput.input()
    cases = int(inp.next()[:-1])
    for case in range(cases):
        '''
        For each case we compute its prime decomposition and we aggregate it in
        the popularity vector. We write as output the maximum repetitions in this
        popularity vector.
        '''
        min_i, max_i = map(int,inp.next()[:-1].split(" "))
        popularity = decompositions[min_i:max_i].sum(axis=0)
        max_rep, values = getMaximumRepetitions(popularity)
        print str(max_rep) + " " + ' '.join(map(lambda val: str(first_25_primes[val]),values))
        
        
    
    