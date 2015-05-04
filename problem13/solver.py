'''

Reading the code we see two parts. The first one, we have to generate a sequence
starting by the given proposed sequence of 16 bytes and the hash of which must
finish with 0xff.

Once we have this hash, we have to find the raw input sentence which generates
the sentence given by the input. 

The algorithm used is AES (CFB mode). This algorithms codifies the sequence as 
a chain, so each character deppends on the previous ones. We will just try all
the possible characters as inputs and we will se which one generates the same
codification than the proposed output. 

Once we find the first character, we try all the possible second characters until we 
generate the two firsts characters of the codified sequence. We do this until the
end of the sequence.

'''


import hashlib
import pycurl
import socket
import base64
import string

def get_Proof(base_proof):
    inp_chain = [i for i in (base_proof + chr(0)*8)]
    stop = False
    for i in range(8):
        if stop == True:
            break
        for j in range(255,-1,-1):
            inp_chain[-i-1] = chr(j)
            h = hashlib.new('sha1')
            h.update(''.join(inp_chain))
            output = ord(h.digest()[-1])
            if output == 255:
                stop = True
                break
    return ''.join( inp_chain )

if __name__ == "__main__":
    HOST, PORT = "54.83.207.93", 12345
    message_to_decodify = base64.b64decode("ilVi0dCr/bUToynwgX6oYJeyX3CPy3pjy0H7eNdQsJGauD0MHBCMvyDhsuHQWkszcB2jo8jDaFMK5I0/WJcPD1Y/Iw2FxcETRjxQvUi69+Q5UQ==")

    decoded_until_now = []
    
    starting_sentence = string.ascii_uppercase + string.ascii_lowercase + ' ' + string.digits + "."
    middle_sentence = ' '  + string.ascii_lowercase + string.ascii_uppercase + string.digits + "."
    
    while len(decoded_until_now) < 82:
        if len(decoded_until_now) == 0:
            test_list = starting_sentence
        else:
            test_list = middle_sentence
        for code_now in test_list:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((HOST, PORT))
        
            proof = sock.recv(114).split("with ")[1].split(" of")[0]
            sock.sendall(get_Proof(proof))
            _ = sock.recv(33)
                
            sent_code = ''.join(decoded_until_now) + code_now
            sock.sendall(sent_code)
            received = sock.recv(2000)
            received_message = base64.b64decode(received)
            
            if message_to_decodify[len(decoded_until_now)] == received_message[-1]:
                decoded_until_now.append(code_now)
                #print ''.join(decoded_until_now)
                sock.close()
                break
            
    #print "Te sentence we have decodified is:"
    print ''.join(decoded_until_now)
