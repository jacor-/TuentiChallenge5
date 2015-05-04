from base64 import *
import fileinput
import numpy


def getBits(ini_seq, end_seq, big_end, twist, input_sequence):    
    subseq = input_sequence[ini_seq:end_seq]
        
    if big_end == "L":
        subseq = ''.join([subseq[i*8:(i+1)*8] for i in range(len(subseq)/8+1)][::-1])

    if twist == "R":
        subseq = subseq[::-1]
    
    acum = 0
    for i in range(len(subseq)):
        acum *= 2
        if subseq[i] == "1":
            acum += 1
    return acum
        


if __name__ == "__main__":
    inp = fileinput.input()
    cumuled_bits = 0

    bit_sequence = ''.join(map(lambda x: bin(x)[2:].rjust(8,'0'), map(ord, b64decode( inp.next()[:-1] )))) 
    cpuses = int(inp.next()[:-1])
    for cpu in range(cpuses):
        cpu_config = inp.next()[:-1]
        reverse = ""
        big_endian = cpu_config[-1]
        if big_endian not in ["L", "B"]:
            reverse = cpu_config[-1]
            big_endian = cpu_config[-2]
            bits_to_eat = int(cpu_config[:-2])
        else:
            bits_to_eat = int(cpu_config[:-1])
        
        print getBits(cumuled_bits, cumuled_bits+bits_to_eat, big_endian, reverse, bit_sequence)
        cumuled_bits = cumuled_bits + bits_to_eat
        #print str(bits_to_eat) + "    " + str(cumuled_bits)
