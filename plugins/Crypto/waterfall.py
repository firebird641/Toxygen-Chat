#!/usr/bin/python3
# -*- coding: utf-8 -*-

import random
import bitarray
import base64
import time

def xor_chain(iv, key):
    XOR = 0
    for i in range(len(iv)):
        value = iv[i]
        switch = key[i]
        XOR += value*switch
    XOR = XOR % 2
    return XOR

def xor_list(a,b):
    c = []
    for i in range(len(a)):
        c.append(a[i] ^ b[i])
    return c

def shift_chain(iv, feedback):
    shifted = [feedback]
    for x in iv[:-1]:
        shifted.append(x)
    return shifted

def bits2readable(b):
  b = bitarray.bitarray(b).tobytes()
  readable = base64.b64encode(b).decode()
  return readable

def readable2bits(readable):
  b = base64.b64decode(readable.encode())
  c = bitarray.bitarray()
  c.frombytes(b)
  c = c.tolist()
  output = ""
  for x in c:
    if x==False: output+='0'
    if x==True: output+='1'
  return output

def string2bits(string):
    c = bitarray.bitarray()
    c.frombytes(string.encode())
    bits = c.tolist()
    bits = ''.join(map(str,list(map(int,bits))))
    return bits

def bits2string(bits):
    string = ""
    c = bitarray.bitarray(bits)
    string = c.tobytes().decode()
    return string

def random_key():
    out = ""
    for _ in range(128):
        out += str(random.randint(0,1))
    out = bits2readable(out)
    return out

def bits2list(bits):
    l = []
    for bit in bits:
        l.append(int(bit))
    return l

def list2bits(l):
    bits = ""
    for bit in l:
        bits += str(bit)
    return bits

def open_file(filename):
  try:
    f = open(filename,"rb")
    data = f.read()
    f.close()
    ba = bitarray.bitarray()
    ba.frombytes(data)
    boolarray = ba.tolist()
    output = ""
    for bit in boolarray:
      if bit==False: output+="0"
      if bit==True: output+="1"
    return output
  except:
    print("File '"+filename+"' not found.")
    exit(1)

def save_file(filename, bits):
  try:
    f = open(filename,"wb")
    ba = bitarray.bitarray(bits)
    ba.tobytes()
    f.write(ba)
    f.close()
  except:
    print("File '"+filename+"' could not be written.")
    exit(1)

class LFSR(object):
    def __init__(self, iv, feedback, forward, and0, and1):
        self.registers = iv
        self.feedback = feedback
        self.forward = forward
        self.andgate = [and0,and1]
    def shift(self, inputbit):
        self.registers = shift_chain(self.registers, inputbit)
    def state(self):
        feedbackbit = self.registers[self.feedback]
        forwardbit = self.registers[self.forward]
        andgate = self.registers[self.andgate[0]] & self.registers[self.andgate[1]]
        outputbit = self.registers[-1]
        return {"Feedback": feedbackbit, "Forward": forwardbit, "AND": andgate, "Output": outputbit}

class Waterfall(object):
    def __init__(self, key, iv):
        key = bits2list(readable2bits(key))
        iv = bits2list(readable2bits(iv))
        a_reg = key[:64]+[1]*39
        b_reg = [1]*113+iv
        c_reg = key[64:128]+[0]*58
        self.A = LFSR(a_reg, 86, 32, 2, 100)
        self.B = LFSR(b_reg, 64, 77, 222, 240)
        self.C = LFSR(c_reg, 121, 19, 33, 66)
    def warmup(self):
        for _ in range(4096):
            A_in = (self.A.state()["Feedback"]+self.C.state()["AND"]+self.C.state()["Output"]+self.B.state()["Forward"]) % 2
            B_in = (self.B.state()["AND"]+self.B.state()["Feedback"]+self.C.state()["Forward"]+self.A.state()["Output"]) % 2
            C_in = (self.A.state()["Forward"]+self.B.state()["Feedback"]+self.A.state()["AND"]+self.C.state()["Output"]) % 2
            self.A.shift(A_in)
            self.B.shift(B_in)
            self.C.shift(C_in)
    def stream(self, l):
        stream = []
        for _ in range(l):
            A_in = (self.A.state()["Feedback"]+self.C.state()["AND"]+self.C.state()["Output"]+self.B.state()["Forward"]) % 2
            B_in = (self.B.state()["AND"]+self.B.state()["Feedback"]+self.C.state()["Forward"]+self.A.state()["Output"]) % 2
            C_in = (self.A.state()["Forward"]+self.B.state()["Feedback"]+self.A.state()["AND"]+self.C.state()["Output"]) % 2
            stream.append((self.A.state()["Forward"]+self.A.state()["Feedback"]+self.A.state()["Output"]+self.B.state()["AND"]+self.B.state()["Feedback"]+self.B.state()["Output"]+self.C.state()["Forward"]+self.C.state()["AND"]+self.C.state()["Output"])%2)
            self.A.shift(A_in)
            self.B.shift(B_in)
            self.C.shift(C_in)
        return stream

def encrypt_text(message, key):
    iv = random_key()
    waterfall = Waterfall(key, iv)
    waterfall.warmup()
    message = bits2list(string2bits(message))
    stream = waterfall.stream(len(message))
    iv_bits = readable2bits(iv)
    ciphertext = bits2readable(iv_bits+list2bits(xor_list(message, stream)))
    return ciphertext

def decrypt_text(ciphertext, key):
    cipherbits = readable2bits(ciphertext)
    iv = bits2readable(cipherbits[:128])
    encrypted = cipherbits[128:]
    waterfall = Waterfall(key, iv)
    waterfall.warmup()
    stream = waterfall.stream(len(encrypted))
    message = bits2string(xor_list(bits2list(encrypted), stream))
    return message

def password2key(password):
    if len(string2bits(password))>=128:
        key = bits2readable(string2bits(password)[:128])
        return key
    else:
        print("Password is too short.")
        exit(1)
