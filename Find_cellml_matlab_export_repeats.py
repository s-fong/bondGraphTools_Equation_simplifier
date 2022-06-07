import os

path = 'C:\\Users\\sfon036\\OneDrive - The University of Auckland\\physiome_curation_work\\BG_models\\FCU_EC_coupling\\'
filename = 'FCU_EC_coupling_new.m'

file = path + filename

with open(file,'r') as fr:
    txt = fr.readlines()
    
start = False
end = False
LHS = []
repeatLHS = []
for line in txt:
    if 'function [STATES, CONSTANTS] = initConsts()' in line:
        start = True
    if 'if (isempty(STATES))' in line:
        end = True
    if start and not end:
        this_LHS = line.split(' = ')[0]
        id = this_LHS.split(',')[-1].replace(')','')
        if this_LHS not in LHS:
            LHS.append(this_LHS)
        else:
            repeatLHS.append(this_LHS)
LHS.sort()
repeatLHS.sort()
print('repeat LHS init terms')
print(repeatLHS)