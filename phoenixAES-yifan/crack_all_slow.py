#!/usr/bin/env python3
import phoenixAES
import binascii
import sys

# THIS SCRIPT MIGHT GIVE YOU WRONG RESULTS!!!
# It brute forces all possible 'expected' results and this may lead to 
# a corrupted key. Only use for debugging or if you are okay with a 
# corrupted key (only a few bits might be off or it's unlikely to be 
# solved.

def main(flavour, last_round_file, second_round_file=None, known=None):
    encrypt = flavour[0] == 'E'
    candidates = []
    with open(last_round_file, "r") as fp:
        for line in fp:
            candidates.append(bytearray.fromhex(line.strip()))
    if not known:
        last_round = None
        for k in range(0, len(candidates)):
            for i in range(0, len(candidates)):
                for j in range(i+1, len(candidates)):
                    if k == i or k == j:
                        continue
                    r9faults = phoenixAES.convert_r8faults_bytes((candidates[i], candidates[j]), candidates[k], encrypt=encrypt)
                    res = phoenixAES.crack_bytes(r9faults, candidates[k], encrypt=encrypt, verbose=0)
                    if res is not None:
                        last_round = bytearray.fromhex(res)
                        break
                if last_round is not None:
                    break
            if last_round is not None:
                break
        if int(flavour[1:], 10) == 128 or last_round is None:
            return last_round
    else:
        last_round = known
    # get second to last round
    if second_round_file is not None:
        candidates = []
        with open(second_round_file, "r") as fp:
            for line in fp:
                candidates.append(bytearray.fromhex(line.strip()))
    candidates = [phoenixAES.rewind(c, [last_round], encrypt=encrypt, mimiclastround=True) for c in candidates]
    second_round = None
    for k in range(0, len(candidates)):
        for i in range(0, len(candidates)):
            for j in range(i+1, len(candidates)):
                if k == i or k == j:
                    continue
                r9faults = phoenixAES.convert_r8faults_bytes((candidates[i], candidates[j]), candidates[k], encrypt=encrypt)
                res = phoenixAES.crack_bytes(r9faults, candidates[k], encrypt=encrypt, verbose=0)
                if res is not None:
                    second_round = bytearray.fromhex(res)
                    break
            if second_round is not None:
                break
        if second_round is not None:
            break
    if second_round is None:
        return last_round
    else:
        return last_round + second_round

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('usage: python3 crack_all_slot.py E256|E128|D256|D128 round_n_minus_3.txt [round_n_minus_4.txt|round N key]')
        sys.exit()
    second_round_file = None
    known = None
    if len(sys.argv) > 3:
        try:
            known = bytearray.fromhex(sys.argv[3])
        except ValueError:
            second_round_file = sys.argv[3]
    r = main(sys.argv[1], sys.argv[2], second_round_file, known)
    if r is not None:
        print(''.join(['{:02X}'.format(c) for c in r]))
    else:
        print('unknown')


