# A recursive method to simplify BGT-CellML equations

# TODO: add var declarations (decs) of all ODE variables

import time

def find_exp(txt, var):
    # global lhs
    mathSymbols = ['+','-','*','/']
    print(var)
    match = []
    if var == 'Af_r5': # # I_mem
        j = 10
    try:
        match = [s for s in txt if '%s = '%var in s][0]
    except:
        match = [s for s in txt if '%s = '%var in s]
    if not match:
        match = var
    if '= sel' in match: # or 'Af' in match or 'Ar' in match:
        return var

    allowedRHS = ['z','Af','Ar','mu','0{fmol','V_mem','v_','I_stim'] # 'sel'
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
                    lhs = var
                    match = lhs + ' = -' + rhs
            elif '+' not in match and '*' not in match and '/' not in match and '-' not in match:
                match = find_exp(txt, match.split('= ')[-1])
                rhs = match.split(' = ')[-1]
                # do not overwrite lhs with a middle variable
                lhs = var
                match = lhs + ' = ' + rhs
            elif True:
                if '*' in rhs and '+' not in rhs and '-' not in rhs:
                    terms = rhs.split('*')
                    for it, term in enumerate(terms):
                        if ('e_' in term or 'f_' in term) and 'z' not in term and '*f' not in term and 'Af' not in term and 'Ar' not in term and 'e_N' not in term:
                            term=find_exp(txt,term)
                            newRHS = term.split(' = ')[-1]
                            if any([m in newRHS for m in mathSymbols]):
                                terms[it] = '('+newRHS+')'
                            else:
                                terms[it] = newRHS
                        else:
                            terms[it] = term
                    if rhs[0] != '(' and rhs[-1] != ')':
                        match = match.split(' = ')[0] + ' = (' + '*'.join(terms) + ')' # but don't bracket if there are already brackets
                    else:
                        match = match.split(' = ')[0] + ' = ' + '*'.join(terms) # but don't bracket if there are already brackets
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

    path = 'G:\\My Drive\\SPARC_work\\BOND_GRAPHS_sparc\\MODELS\\pan_SERCA_shelleymod\\cellml_to_txt\\'
    path = 'examples\\'
    inputname = 'SERCA_bg.cellml.txt'
    inputname = 'cardiac_AP_dynamic_ions.txt'
    cfname = path + inputname

    with open(cfname,'r') as cf:
        txt = cf.readlines()

    txt = [t[:-1].replace(';', '') for t in txt]
    txt = [t for t in txt if t]

    v_names = ['I_stim','Na','K','K1','Kp','LCC_Ca1','LCC_Ca2','LCC_K1','LCC_K2'] #,'NaK','NCX'
    v_names = ['v_'+n if 'I_stim' not in n else n for n in v_names]
    vs = [] # list of variables that do no have init. So v does not contain constants nor state variables
    vode = [] # list for ODEs
    decs = [] # list of declarations of variables
    vrates = []
    vdict = {c:[] for c in v_names}
    vstart = False
    for ii, line in enumerate(txt):
        if 'var Af_R1: J_per_mol' in line:
            j = 10
        if ' var ' in line and 'var e_' not in line and 'var f_' not in line: # and 'init:' not in line:
            if 'sel' not in line and 'init' not in line:
                vs.append(line.split('var ')[-1].split(':')[0])
                # copy over rate equations for each channel - happens over several lines
            decs.append(line+';')
        elif 'ode(' in line:
            vode.append(line + ';')
        elif '= sel' in line:
            vstart = True
            fluxname = line.split(' =')[0].replace(' ','')
        elif 'endsel' in line:
            vstart = False
            vrates.append(line+';')
            vdict[fluxname].append(line+';')
        if vstart:
            if '= sel' not in line and 'otherwise' not in line and 'case' not in line:
                line += ';'
            vrates.append(line)
            vdict[fluxname].append(line)

    simpEqns = []
    for v in vs:
        newLine = find_exp(txt, v)
        if '= sel' not in newLine and newLine != v:
            simpEqns.append(newLine)

    simpEqns.sort()
    simpEqns = [line.replace('--','+').replace('+-','-').replace('+0{fmol_per_sec}','').replace('-0{fmol_per_sec}','')+';' for line in simpEqns]
    simpEqns += vode #+ vrates
    decs += simpEqns

    outputFile = path + 'simplified_' + inputname
    with open (outputFile, 'w') as fo:
        for line in decs+vrates:
            fo.write(line + '\n')
        print('Written output file: ', outputFile)

    if True:

        # write out equations pertaining to a specific channel/component in its own file

        unitWords = ['fmol','per_fmol','fmol_per_sec','fA','fC','J_per_mol','mM']

        channels = ['Na','K1','Kp','NaK','LCC','NCX']
        special_channels = ['NaK','LCC','NCX']
        chd = {c:{'keywords':[],'nonkeywords':[],'fluxname':[]} for c in channels}

        chd['Na']['keywords'] = ['Na','_m', '_h', '_j']
        chd['Na']['nonkeywords'] = ['NaK','NCX']
        chd['K1']['keywords'] = ['Ki','Ke','K1']
        chd['K1']['nonkeywords'] = ['LCC']
        chd['Kp']['keywords'] = ['Ki','Ke','Kp']
        chd['Kp']['nonkeywords'] = []
        chd['NaK']['keywords'] = ['NaK','_R','Nai','Nae','Ki','Ke']
        chd['NaK']['nonkeywords'] = []
        chd['LCC']['keywords'] = ['LCC','_fCa','_f1','_f2','_f3','d0']
        chd['LCC']['nonkeywords'] = []
        chd['NCX']['keywords'] = ['NCX']
        chd['NCX']['nonkeywords'] = []

        for key in chd.keys():
            chd[key]['keywords'].append('t: second')
            chd[key]['keywords'].append('mem')
            if key not in special_channels:
                chd[key]['fluxname'] = ['v_'+key]
            elif key == 'LCC':
                chd[key]['fluxname'] = ['v_LCC_Ca1','v_LCC_Ca2','v_LCC_K1','v_LCC_K2']
            else:
                chd[key]['fluxname'] = []

        for n in channels:
            channel_outputFile = path + n+'ChannelOnly_' + inputname
            with open(channel_outputFile, 'w') as co:
                for line in decs:
                    if n == 'LCC' and 'fCa' in line and 'var' not in line:
                        j = 10
                    lhs = line.split('=')[0]
                    # for u in unitWords:
                    #     lhs = lhs.replace(u,'')
                    if any([k in lhs for k in chd[n]['keywords']]) and not any([k in lhs for k in chd[n]['nonkeywords']]):
                        co.write(line + '\n')
                for flux in chd[n]['fluxname']:
                    for line in vdict[flux]:
                        co.write(line + '\n')
                # try:
                #     for line in vdict['v_'+n]:
                #         co.write(line + '\n')
                # except:
                #     for flux in chd[key]['fluxname']:
                #         for line in vdict[flux]:
                #             co.write(line + '\n')

            print('Written output file: ', channel_outputFile)

    print('elapsed = ', round(time.time() - tstart,3), ' s')



