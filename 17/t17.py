#! python3

import sys
from pprint import pprint
import numpy as np
from itertools import permutations
import csv
from collections import deque,defaultdict
import networkx as nx

# keep grid state in grid
# x,y for robot
# deque for steps taken
# look around, can find uknown field => try to move to it
# if oxygen found, ... ?
# if no uknown field, remove from deque and go back

processor = {}
program_param = {}
grid = defaultdict(str)
robot_x = 0
robot_y =0
score =0

back_step_adj = { 1:(-1,0), 2:(1,0), 3:(0,1), 4:(0,-1) }

def get_input(cur_proc) :
    print('asking input')
    instr = ''
    inp =  processor[cur_proc]['io'].popleft()
    print("inp",inp)
    while inp != 10:
       instr = instr+str(inp)
       print("building instr",instr)
       inp =  processor[cur_proc]['io'].popleft()
    instr = instr + str('10')
    print("providing ",instr)
    return int(instr)


  

def process_output(cur_proc) :
    global grid
    global robot_x
    global robot_y

    response = processor[cur_proc]['io'].pop()
#    print(chr(response),end='')
    if response == 10 :
        robot_y += 1
        robot_x = 0
    else:
        if chr(response) == "^": response = 35
        grid[(robot_x,robot_y)] = chr(response)
        robot_x += 1

    return 1

def run_intcode(cur_proc) :

    params = { 1 : 3, 2 : 3, 3 : 1,    4 : 1,    5 : 2,    6 : 2,    7 : 3,    8 : 3, 9 : 1, 99:0 }

    pos = processor[cur_proc]['position']

    while 1:
        instr = processor[cur_proc]['program'][pos]

        op = instr % 100;

        mode1 = int( instr / 100 ) % 10;
        mode2 = int( instr / 1000 ) % 10;
        mode3 = int( instr / 10000 ) % 10;

        reg1 = processor[cur_proc]['program'].get(pos+1,0)
        reg2 = processor[cur_proc]['program'].get(pos+2,0)
        reg3 = processor[cur_proc]['program'].get(pos+3,0)

        v1 = reg1

        if (op != 3) :
            if mode1 == 0:  v1 = processor[cur_proc]['program'].get(reg1,0)
            if mode1 == 2:  v1 = processor[cur_proc]['program'].get(reg1 + processor[cur_proc]['relative_base'],0)
        else:
            if mode1 == 2:  v1 += processor[cur_proc]['relative_base']

        v2 = reg2
        if mode2 == 0:  v2 = processor[cur_proc]['program'].get(reg2,0)
        if mode2 == 2:  v2 = processor[cur_proc]['program'].get(reg2 + processor[cur_proc]['relative_base'],0)

        v3 = reg3
        if mode3 == 2:  v3 += processor[cur_proc]['relative_base']

        if op == 1 : processor[cur_proc]['program'][ v3 ] = v1 + v2

        # Process the opcodes
        elif op == 2 : processor[cur_proc]['program'][ v3 ] = v1 * v2

        elif op == 3 :
 #           processor[cur_proc]['io'].append(get_input(cur_proc))
#            processor[cur_proc]['program'][ v1 ] = processor[cur_proc]['io'].popleft()
             processor[cur_proc]['program'][ v1 ] = get_input(cur_proc)

        elif op == 4 :
             processor[cur_proc]['io'].append(v1)
             process_output(cur_proc)
        
        elif (op == 5) :
            if v1 > 0: pos = v2; continue
        
        elif op == 6 :
            if v1 == 0 : pos = v2; continue

        elif op == 7 :
            if int(v1) < int(v2) :
                processor[cur_proc]['program'][ v3 ] = 1
            else :
                processor[cur_proc]['program'][ v3 ] = 0
        
        elif op == 8 :
            if v1 == v2 :
                processor[cur_proc]['program'][ v3 ] = 1
            else :
                processor[cur_proc]['program'][ v3 ] = 0
       
        elif op == 9 :
            processor[cur_proc]['relative_base'] += v1;

        elif op == 99 :
            return processor[cur_proc]['io']
        
        else :
            sys.exit("Unknown argument found")

        shift = params[ op ] + 1;
        pos = pos + shift;



# ------- MAIN ----------

def run_program(data,mode,inp=[]):



    program_param['mode'] = 'normal';
    program_param['program_end'] = 0;

    phase_list = ''
    if program_param['mode'] == 'normal':
        phase_list='0'

    if program_param['mode'] == 'feedback':
        phase_list = '56789'


    max = 0

    for combo in permutations(phase_list,len(phase_list)):
        program_param['program_end'] = 0;

        amp = ['A']

        # initialize the processors

        for phase in combo :
            cur_proc = amp.pop(0)
            processor[cur_proc] = {}
            processor[cur_proc]['phase']  = phase
            processor[cur_proc]['position'] = 0
            processor[cur_proc]['output']   = 0
            processor[cur_proc]['phase_set']   = 0
            processor[cur_proc]['program']   = {}
            processor[cur_proc]['io'] = deque(inp)
            print("initial io ",  processor[cur_proc]['io'])
            #processor[cur_proc]['io'].append(mode)
            processor[cur_proc]['relative_base']   = 0
            processor[cur_proc]['x']   = 50
            processor[cur_proc]['y']   = 50
            processor[cur_proc]['direction']   = '^'

            i = 0
            for instr in data:
                processor[cur_proc]['program'][i]   = instr
                i+=1

        end = 0

    
        while (end == 0) :
            proc = ['A']
            
            # loop through the processors
            for procs in range(len(proc)) :
                cur_proc = proc[procs]
                next_proc = proc[(procs +1) % len(proc)]

                processor[next_proc]['input'] = run_intcode( cur_proc )

#                if (cur_proc == 'A') and (processor[next_amp,'input'] > max) :
 #                   max = processor[next_amp,'input']

                if ( procs == len(proc) - 1 ) : return processor[next_proc]['input']

                if (program_param['program_end'] ==1 ) :
                    end = 1;
                    break

                if program_param['mode'] == 'normal' : end =1


# -------------- START -------------
assert len(sys.argv) == 2

inp = open(sys.argv[1]).read().strip().split(',')
data = list(map(int, inp))

run_program(data,1)

# convert the grid to graph
g = nx.DiGraph()

max_path = 0

for x, y in grid.keys() :
    if grid.get((x,y)) != "#": continue

    if grid.get((x-1,y),0) == '#' : g.add_edge((x,y), (x-1,y))
    if grid.get((x+1,y),0) == '#' : g.add_edge((x,y), (x+1,y))
    if grid.get((x,y-1),0) == '#' : g.add_edge((x,y), (x,y-1))
    if grid.get((x,y+1),0) == '#' : g.add_edge((x,y), (x,y+1))

sum =0
for n in  g:
    if len(g.edges(n)) > 2:
        sum += n[0]*n[1]

print("Part 1: ",sum)


#for x, y in grid.keys() :
#    if grid.get((x,y)) == "#": continue
#    path_l =  len(nx.dijkstra_path(g,(14,16),(x,y)))
#    if path_l > max_path :  max_path = path_l

#arr = np.flip(arr,0)

