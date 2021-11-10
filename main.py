# A recursive method to simplify BGT-CellML equations

import time

def find_exp(txt, var):
    print(var)
    match = []
    if var == 'v_Ke': # # v_Nae f_3
        j = 10
    try:
        match = [s for s in txt if '%s = '%var in s][0]
    except:
        match = [s for s in txt if '%s = '%var in s]
    if not match:
        match = var
    if match == 'sel': # or 'Af' in match or 'Ar' in match:
        return match

    allowedRHS = ['z','Ar','sel','0{fmol','V_mem','v_','I_stim'] #'z' not in rhs and 'Ar' not in rhs and 'sel' not in rhs and '0{fmol' not in rhs and 'V_mem' not in rhs
    if ('e_' not in match and 'f_' not in match) or 'z' in match and '*f' not in match: # or 'Af' in match or 'Ar' in match
        return match
    elif not match:
        return 0
    elif len(match)>0:
        if '=' in match:
            lhs = match.split(' = ')[0]
            rhs = match.split(' = ')[-1]
        else:
            rhs = match
        while ((('e_' in rhs and 'e_N' not in rhs) or ('f_' in rhs and 'Af' not in rhs)) or([k not in rhs for k in allowedRHS]==[True]*len(allowedRHS))):
            if match[0] == '_':
                return 0
            if '= -' in match and match.count('-') == 1 and '+' not in match:
                if 'Af' in match or 'Ar' in match:
                    return match
                # sign = -1
                if '= -f' in match:
                    match = find_exp(txt, rhs[1:]) # if negative sign in front of f
                    rhs = match.split(' = ')[-1]
                    match = lhs + ' = -' + rhs
            elif '+' not in match and '*' not in match and '/' not in match and '-' not in match:
                match = find_exp(txt, match.split('= ')[-1])
                rhs = match.split(' = ')[-1]
                # do not overwrite lhs with a middle variable
                match = lhs + ' = ' + rhs
            elif True:
                if '*' in rhs and '+' not in rhs and '-' not in rhs:
                    terms = rhs.split('*')
                    for it, term in enumerate(terms):
                        if ('e_' in term or 'f_' in term) and 'z' not in term and '*f' not in term and 'Af' not in term and 'Ar' not in term and 'e_N' not in term:
                            term=find_exp(txt,term)
                            terms[it] = '('+term.split(' = ')[-1]+')'
                        else:
                            terms[it] = term
                    match = match.split(' = ')[0] + ' = ' + '*'.join(terms)
                else:
                    if '+' not in rhs:
                        # subtraction only
                        terms = rhs.split('-')
                        terms = [t for t in terms if t != '']
                        for it, term in enumerate(terms):
                            term=find_exp(txt,term)
                            terms[it] = term.split(' = ')[-1]
                        if rhs[0] == '-':
                            match = match.split(' = ')[0]+' = -'+'-'.join(terms)
                        else:
                            match = match.split(' = ')[0]+' = '+'-'.join(terms)
                    else:
                        # addition only
                        terms = rhs.split('+')
                        for it, term in enumerate(terms):
                            if '*' in term:
                                terms2 = term.split('*')
                                for it2, term2 in enumerate(terms2):
                                    term2 = find_exp(txt, term2)
                                    terms2[it2] = term2.split(' = ')[-1]
                                term = '*'.join(terms2)
                            term=find_exp(txt,term)
                            terms[it] = term.split(' = ')[-1]
                        match = match.split(' = ')[0]+' = '+'+'.join(terms)
                return match
            else:
                break
        return match

if __name__ == '__main__':
    tstart = time.time()

    path = 'examples\\'
    inputname = 'cardiac_AP_dynamic_ions.txt'
    cfname = path + inputname

    with open(cfname,'r') as cf:
        txt = cf.readlines()

    txt = [t[:-1].replace(';', '') for t in txt]
    txt = [t for t in txt if t]

    vs = [] # list of variables that do no have init. So v does not contain constants nor state variables
    vode = [] # list for ODEs
    for line in txt:
        if ' var ' in line and 'init' not in line and 'e_' not in line and 'f_' not in line and 'sel' not in line:
            vs.append(line.split('var ')[-1].split(':')[0])
        if 'ode(' in line:
            vode.append(line + ';')

    simpEqns = []
    sign = 1
    for v in vs:
        if '-' in v:
            sign = -1
        simpEqns.append(sign*find_exp(txt, v))

    simpEqns.sort()
    # change '--' to '+'
    simpEqns = [line.replace('--','+')+';' for line in simpEqns]
    simpEqns += vode

    outputFile = path + 'simplified_' + inputname
    with open (outputFile, 'w') as fo:
        for line in simpEqns:
            fo.write(line + '\n')
        print('Written output file: ', outputFile)

    print('elapsed = ', round(time.time() - tstart,3), ' s')



