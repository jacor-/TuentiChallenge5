import numpy
import fileinput
import os
from multiprocessing import Pool
from itertools import repeat

'''
Here we precompute all the possible values for the stated input.
First, we will compute all the prime numbers in the interval from 0 to the 
maximum allowed input (B value).
Then, we use these prime numbers to factorize all the numbers in this interval.

We save in a list all these values in order to be used as a precomputed values
in future executions of the program.

'''

def primes(n):
    """ Returns  a list of primes < n """
    sieve = [True] * n
    for i in xrange(3,int(n**0.5)+1,2):
        if sieve[i]:
            sieve[i*i::2*i]=[False]*((n-i*i-1)/(2*i)+1)
    return [2] + [i for i in xrange(3,n,2) if sieve[i]]

def descompositionOfN(n, list_primes):
    factors = 0
    finish = False
    for d in list_primes:
        if not finish and d*d <= n:
            while (n % d) == 0:
                factors += 1
                if factors > 2:
                    finish = True
                    break
                n //= d
        else:
            break
    if n != 1:
        factors += 1
    return factors == 2

def descomposeSetOfValues(arguments):
    index, list_primes, range_size = arguments
    results = []
    for i in range(range_size):
        n = range_size*index + i + 1
        if descompositionOfN(n, list_primes):
            results.append(n)
    return results

def precompute():
    MAX_VALUE = 100000000
    splits = 1000000
    tots_els_primers_imaginables = numpy.array(primes(MAX_VALUE+1))
    p = Pool(4)
    results = p.map(descomposeSetOfValues, zip(range((MAX_VALUE+1)/splits), repeat(tots_els_primers_imaginables), repeat(splits)))
    p.close()
    results = numpy.concatenate(results)
    f = open("precomputed_almost_prime_numbers", 'w')
    numpy.save(f, results)
    f.close()
    
    

'''
This code just loads the precomputed file and gives the answer by counting the 
values which has been found in the precomputing stage.
'''    
def solve(A,B, almost_prime_numbers):        
    return numpy.sum((almost_prime_numbers >= A) * (almost_prime_numbers <= B))

'''
Lets execute!
'''
if __name__ == "__main__":
    if not "precomputed_almost_prime_numbers" in os.listdir("."):
        precompute()
    f = open("precomputed_almost_prime_numbers")
    almost_prime_numbers = numpy.load(f)
    f.close()
    inp = fileinput.input()
    cases = int(inp.next()[:-1])
    for case in range(cases):
        A,B = map(int,inp.next().split(" "))
        print solve(A,B, almost_prime_numbers)
