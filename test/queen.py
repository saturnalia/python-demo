#!/usr/bin/python

import os, sys
import math


global pos, col, row, i , j

def mark_position(array, ):
    pass
    

def print_matrix(array, num):
    #
    # array[num][num]
    #
    print "--------------------------"
    for row in range(0, num):
        for col in range(0, num):
            if array[row][col] == 1:
                print " X ",
            elif array[row][col] == 0:
                print ' * ',
            elif array[row][col] == 2:
                print ' ? ',
        print "\n",
    print "--------------------------"

#
# For given array[num][num], to check if one queen can be placed
# at array[row][col]
# return True if it has no conflict.
# or else return False
#
def try_place_queen(array, num, row, col):
    result = True
    # validate array[row][col]
    for r in range(0, row):
        if array[r][col] == 1:
            result = False
    # actually we do not need to check row
    for c in range(0, num):
        if array[row][c] == 1:
            # this should not happen
            # this row is firstly to be placed element
            assert 0
        else:
            pass
    return result


def queen_iterator(array, num):
    # iterate each row of the num rows
    #
    # place the first row
    #
    row = 0
    for col in range(0,num):
        array[row][col] = 1
        #
        # place the second row
        #
        for i in range(0, num):
            res = try_place_queen(array, num, 1, i)
            if res == True:
                #
                # place the third row
                for r3 in range(0, num):
                    res3 = try_place_queen(array, num, 2, i )
                    if res3 == True:
                        #
                        # placethe forth row
                        #
                        print_matrix(array, num)
                    else:
                        continue
                
            else:
                continue


def prettyprint(solution):
    def line(pos, length=len(solution)):
        return '. ' * (pos) + 'X ' + '. ' * (length-pos-1)
    
    for pos in solution:
        print line(pos)

def conflict(state, nextX):
    nextY = len(state)
    for i in range(nextY):
        if abs(state[i]-nextX) in (0, nextY-i):
            return True
    return False


def queens(num, state=()):
    if len(state) == num-1:
        for pos in range(num):
            if not conflict(state, pos):
                yield pos
    else:
        for pos in range(num):
            if not conflict(state, pos):
                for result in queens(num, state + (pos,)):
                    yield (pos,) + result

def main():
    cols = raw_input("Please input the num of queens:")
    if int(cols) <= 0:
        print "Please input positive number!\n"
        sys.exit(1)
    num = int(cols)
    #
    # In this method, set array[0][0]=1 will make array[0][0], array[1][0],array[2][0],...array[num-1][0] as 1
    # Those share the same reference address??
    #
    #subarray = [0] * num
    #array = [subarray] * num
    #
    #subarray = [ 0 for x in range(0, num) ]
    #array = [subarray] * num
    #
    array = [[ 0 for x in range(0,num)] for y in range(0,num)]
    
    queen_iterator(array, num)


if __name__ == "__main__":
    main()

