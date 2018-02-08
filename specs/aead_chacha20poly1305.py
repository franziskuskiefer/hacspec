#!/usr/bin/python3

from speclib import *
from typing import Tuple
from chacha20 import chacha20_block, chacha20_encrypt, chacha20_decrypt
from poly1305 import poly1305_mac

def padded_aad_msg(aad:bytes,msg:bytes) -> Tuple[int,bytes]:
    laad = len(aad)
    lmsg = len(msg)
    pad_aad = laad if laad % 16 == 0 else 16 * (laad // 16 + 1)
    pad_msg = lmsg if lmsg % 16 == 0 else 16 * (lmsg // 16 + 1)
    to_mac = array.create(0,pad_aad + pad_msg + 16);
    to_mac[0:laad] = aad
    to_mac[pad_aad:pad_aad+lmsg] = msg
    to_mac[pad_aad+pad_msg:pad_aad+pad_msg+8] = uint64.to_bytes_le(uint64(laad))
    to_mac[pad_aad+pad_msg+8:pad_aad+pad_msg+16] = uint64.to_bytes_le(uint64(lmsg))
    return pad_aad+pad_msg+16, bytes(to_mac)

def aead_chacha20poly1305_encrypt(key:bytes,nonce:bytes,aad:bytes,msg:bytes) -> Tuple[bytes,bytes]:
    keyblock0 = chacha20_block(key,0,nonce)
    mac_key = keyblock0[0:32]
    ciphertext = chacha20_encrypt(key,1,nonce,msg)
    len, to_mac = padded_aad_msg(aad,ciphertext)
    mac = poly1305_mac(to_mac,mac_key)
    return ciphertext, mac

def aead_chacha20poly1305_decrypt(key:bytes,nonce:bytes,
                                  aad:bytes,
                                  ciphertext:bytes,
                                  tag:bytes) -> bytes:
    keyblock0 = chacha20_block(key,0,nonce)
    mac_key = keyblock0[0:32]
    len, to_mac = padded_aad_msg(aad,ciphertext)
    mac = poly1305_mac(to_mac,mac_key)
    if mac == tag:
        msg = chacha20_decrypt(key,1,nonce,ciphertext)
        return msg
    else:
        raise Exception("mac failed")

from test_vectors.aead_chacha20poly1305_test_vectors import *

def main(x: int) -> None :
    k = bytes([0x80,0x81,0x82,0x83,0x84,0x85,0x86,0x87,
               0x88,0x89,0x8a,0x8b,0x8c,0x8d,0x8e,0x8f,
	       0x90,0x91,0x92,0x93,0x94,0x95,0x96,0x97,
               0x98,0x99,0x9a,0x9b,0x9c,0x9d,0x9e,0x9f])
    n = bytes([0x07,0x00,0x00,0x00,0x40,0x41,0x42,0x43,
               0x44,0x45,0x46,0x47])
    p = bytes([0x4c, 0x61, 0x64, 0x69, 0x65, 0x73, 0x20, 0x61,
    	       0x6e, 0x64, 0x20, 0x47, 0x65, 0x6e, 0x74, 0x6c,
    	       0x65, 0x6d, 0x65, 0x6e, 0x20, 0x6f, 0x66, 0x20,
    	       0x74, 0x68, 0x65, 0x20, 0x63, 0x6c, 0x61, 0x73,
    	       0x73, 0x20, 0x6f, 0x66, 0x20, 0x27, 0x39, 0x39,
    	       0x3a, 0x20, 0x49, 0x66, 0x20, 0x49, 0x20, 0x63,
   	       0x6f, 0x75, 0x6c, 0x64, 0x20, 0x6f, 0x66, 0x66,
    	       0x65, 0x72, 0x20, 0x79, 0x6f, 0x75, 0x20, 0x6f,
    	       0x6e, 0x6c, 0x79, 0x20, 0x6f, 0x6e, 0x65, 0x20,
    	       0x74, 0x69, 0x70, 0x20, 0x66, 0x6f, 0x72, 0x20,
    	       0x74, 0x68, 0x65, 0x20, 0x66, 0x75, 0x74, 0x75,
    	       0x72, 0x65, 0x2c, 0x20, 0x73, 0x75, 0x6e, 0x73,
    	       0x63, 0x72, 0x65, 0x65, 0x6e, 0x20, 0x77, 0x6f,
    	       0x75, 0x6c, 0x64, 0x20, 0x62, 0x65, 0x20, 0x69,
    	       0x74, 0x2e])
    aad = bytes([0x50,0x51,0x52,0x53,0xc0,0xc1,0xc2,0xc3,
           0xc4,0xc5,0xc6,0xc7])
    exp_cipher = bytes([0xd3,0x1a,0x8d,0x34,0x64,0x8e,0x60,0xdb,
               0x7b,0x86,0xaf,0xbc,0x53,0xef,0x7e,0xc2,
	       0xa4,0xad,0xed,0x51,0x29,0x6e,0x08,0xfe,
               0xa9,0xe2,0xb5,0xa7,0x36,0xee,0x62,0xd6,
	       0x3d,0xbe,0xa4,0x5e,0x8c,0xa9,0x67,0x12,
               0x82,0xfa,0xfb,0x69,0xda,0x92,0x72,0x8b,
	       0x1a,0x71,0xde,0x0a,0x9e,0x06,0x0b,0x29,
               0x05,0xd6,0xa5,0xb6,0x7e,0xcd,0x3b,0x36,
	       0x92,0xdd,0xbd,0x7f,0x2d,0x77,0x8b,0x8c,
               0x98,0x03,0xae,0xe3,0x28,0x09,0x1b,0x58,
	       0xfa,0xb3,0x24,0xe4,0xfa,0xd6,0x75,0x94,
               0x55,0x85,0x80,0x8b,0x48,0x31,0xd7,0xbc,
	       0x3f,0xf4,0xde,0xf0,0x8e,0x4b,0x7a,0x9d,
               0xe5,0x76,0xd2,0x65,0x86,0xce,0xc6,0x4b,
	       0x61,0x16])
    exp_mac = bytes([0x1a,0xe1,0x0b,0x59,0x4f,0x09,0xe2,0x6a,
            0x7e,0x90,0x2e,0xcb,0xd0,0x60,0x06,0x91])
    cipher, mac = aead_chacha20poly1305_encrypt(k,n,aad,p)
    if (exp_cipher == cipher and exp_mac == mac):
        print("Test  0 passed.")
    else:
        print("expected cipher: ", exp_cipher)
        print("computed cipher: ", cipher)
        print("expected mac: ", exp_mac)
        print("computed mac: ", mac)
    for i in range(len(aead_chacha20poly1305_test_vectors)):
        msg = aead_chacha20poly1305_test_vectors[i]['input']
        k   = aead_chacha20poly1305_test_vectors[i]['key']
        n = aead_chacha20poly1305_test_vectors[i]['nonce']
        aad  = aead_chacha20poly1305_test_vectors[i]['aad']
        expected = aead_chacha20poly1305_test_vectors[i]['output']
        exp_mac = expected[len(msg):len(expected)]
        exp_cipher = expected[0:len(msg)]
        cipher,mac = aead_chacha20poly1305_encrypt(k,n,aad,msg)
        if (exp_cipher == cipher and exp_mac == mac):
            print("Test ",i+1," passed.")
        else:
            print("Test ",i+1," failed:")
            print("expected cipher: ", exp_cipher)
            print("computed cipher: ", cipher)
            print("expected mac: ", exp_mac)
            print("computed mac: ", mac)

if __name__ == "__main__":
    main(0)
