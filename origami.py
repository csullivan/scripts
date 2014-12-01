import readline, glob
import fortranformat as form
import numpy as np
import math
from sympy.physics.quantum.cg import CG
from sympy import S

def get(prompt, default):
    return raw_input("%s [%s] " % (prompt, default)) or default

def complete(text, state):
    return (glob.glob(text+'*')+[None])[state]

def init_tab_complete():
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete)

def init_obtd_key_map():
    """ lookup[oxbash_key] = fold_key"""
    lookup = np.zeros(45)
    lookup[1] = 1
    lookup[2] = 3
    lookup[3] = 2
    lookup[4] = 6
    lookup[5] = 5
    lookup[6] = 4
    lookup[7] = 10
    lookup[8] = 9
    lookup[9] = 8
    lookup[10] = 7
    # more needed....
    lookup = [int(x) for x in lookup]
    return lookup

def get_zT_prefactor(Ji,Ti,Tiz,dT,dTz,Tf,Tfz):
    cg = CG(Ti,Tiz,dT,dTz,Tf,Tfz)
    return ((math.sqrt(2*dT+1))/(math.sqrt(2*Ji+1)*math.sqrt(2*Tf+1)))*float(cg.doit())


def get_obtd(obtd_filename,dj):
    oxbash_to_fold_key_map = init_obtd_key_map()
    try:
        obtd_file = open(obtd_filename,"rb")
    except IOError:
        print "Error, file does not exist"; exit()

    obtd_list = []
    for i,line in enumerate(obtd_file):
        if '!' == line[1] or i == 0:
            continue
        line = line.split()
        obtd_list.append(line)
    mark = 0
    for i,line in enumerate(obtd_list):
        if len(line) == 7 and float(line[0][:-1]) == dj:
            mark = i
    obtds = []
    fold_obtds = []
    for i in range(mark+1,len(obtd_list)):
        if len(obtd_list[i])==7:
            break
        if len(obtd_list[i])>3:
            obtds.append([int(obtd_list[i][0][:-1]),int(obtd_list[i][1][:-1]),float(obtd_list[i][3][:-1])])
            fold_obtds.append([oxbash_to_fold_key_map[int(obtd_list[i][0][:-1])],oxbash_to_fold_key_map[int(obtd_list[i][1][:-1])],float(obtd_list[i][3][:-1])])
    return fold_obtds
        
if __name__=="__main__":

    """ A tool for building fold input files """    
    init_tab_complete()
    print "Welcome to oragami, the FOLD inputfile generator. \nFor each question, pay careful attention to the example answer and format all answers in the way specified. For example, if the default answer is [12] then the following input should be an integer. But if it is [12.], then a float should be entered.\n\n"
    filename = get("Enter a name for the FOLD input file to be generated","fold.inp")
    file = open(filename,"wb")    
    djr = 0.0 # Change of relative spin
    djp = 0.0 # Change of spin in projectile
    djt = 0.0 # Change of spin in target

    ################### Line 1 ###################

    output_file = \
        get("Enter a filename for the FOLD output file.\nNote that this filename is restricted to 8 characters or less","FOLDOUT")    
    line = form.FortranRecordWriter('(I5,I5,A7)')
    line = line.write([1,1,output_file[0:8]])
    file.write(line+'\n')

    ################### Line 2 ###################

    nr = int(get("Number of integration steps:\n",600))
    ns = float(get("Step size (fm):\n",0.03))
    beam_energy_lab = float(get("Bombarding energy (MeV):\n",1000.))
    a = float(get("Projectile mass number (A):\n",12))
    line = form.FortranRecordWriter('(I5,F5.2,F10.0,F10.0,I10,I4,I4)')
    line = line.write([nr,ns,beam_energy_lab,a,1,1,1])
    file.write(line+'\n')

    ################### Line 3 ###################

    jf = float(get("Spin of the projectile final state:\n",1.0))
    pf = str(get("Parity of the projectile final state:\n","+"))
    ji = float(get("Spin of the projectile initial state:\n",0.0))
    pi = str(get("Parity of the projectile initial state:\n","+"))
    line = form.FortranRecordWriter('(F10.1,A1,F9.1,A1)')
    line = line.write([jf,pf,ji,pi])
    file.write(line+'\n')
    djp = abs(jf - ji)

    ################### Line 4 ###################

    tf = float(get("Isospin of the projectile final state:\n",0.0))
    tzf = str(get("Isospin projection of the projectile final state:\n","+0.0"))
    ti = float(get("Isospin of the projectile initial state:\n",0.0))
    tzi = str(get("Isospin projection of the projectile initial state:\n","+0.0"))
    line = form.FortranRecordWriter('(F5.1,A10,F10.1,A11)')
    line = line.write([tf,tzf,ti,tzi])
    file.write(line+'\n')

    ################### Line 5 ###################
    
    ntypf = int(get("NTYPF (=1 static, =2 inelastic, =3 charge exchange):\n",3))
    koptn = int(get("Transition amplitude type: 1 (S[T]), 2 (S[pn]), 3 (Z[T] - OXBASH OBTD), 4 (Z[pn]), 5 (Wildenthal):\n",3))
    alpha = float(get("Alpha (=0.000 to use WSAW radial wave functions):\n",0.000))
    line = form.FortranRecordWriter('(I5,I5,F7.3)')
    line = line.write([ntypf,koptn,alpha])
    file.write(line+'\n')

    ################### Line 6 ###################
     ################## OBTDs ###################
    
    djp = float(get("Change in spin of projectile:\n",djp))
    dtp = float(get("Change in isospin of projectile:\n",1.0))
    obtd_filename = str(get("Enter filename/path to OXBASH obtd file","t331dp150.obd"))
    fold_obtds = get_obtd(obtd_filename,djp) # STILL NEED CG COEFs
    prefactor = get_zT_prefactor(ji,ti,float(tzi),dtp,float(tzf)-float(tzi),tf,float(tzf))   
    print "Projectile prefactor = ",prefactor
    for obtd in fold_obtds:
        line = form.FortranRecordWriter('(I5,I5,I5,F5.1,F17.6)')
        obtd[2] *= prefactor
        line = line.write([obtd[0],obtd[1],1,0.0,obtd[2]])
        file.write(line+'\n')
    line = form.FortranRecordWriter('(I5,I5)')
    line = line.write([-1,-1])
    file.write(line+'\n')
    wsaw_proj = str(get("Enter filename of projectile WSAW radial wavefunction file:\n","6LI6LI"))
    line = form.FortranRecordWriter('(A7)')
    line = line.write([wsaw_proj])
    file.write(line+'\n')

    ################### Target ###################
    ################### Line 3 ###################

    jf = float(get("Spin of the target final state:\n",1.0))
    pf = str(get("Parity of the target final state:\n","+"))
    ji = float(get("Spin of the target initial state:\n",0.0))
    pi = str(get("Parity of the target initial state:\n","+"))
    line = form.FortranRecordWriter('(F10.1,A1,F9.1,A1)')
    line = line.write([jf,pf,ji,pi])
    file.write(line+'\n')
    djt = abs(jf - ji)

    ################### Line 4 ###################

    tf = float(get("Isospin of the target final state:\n",0.0))
    tzf = str(get("Isospin projection of the target final state:\n","+0.0"))
    ti = float(get("Isospin of the target initial state:\n",0.0))
    tzi = str(get("Isospin projection of the target initial state:\n","+0.0"))
    line = form.FortranRecordWriter('(F5.1,A10,F10.1,A11)')
    line = line.write([tf,tzf,ti,tzi])
    file.write(line+'\n')

    ################### Line 5 ###################
    
    ntypf = int(get("NTYPF (=1 static, =2 inelastic, =3 charge exchange):\n",3))
    koptn = int(get("Transition amplitude type: 1 (S[T]), 2 (S[pn]), 3 (Z[T] - OXBASH OBTD), 4 (Z[pn]), 5 (Wildenthal):\n",3))
    alpha = float(get("Alpha (=0.000 to use WSAW radial wave functions):\n",0.000))
    line = form.FortranRecordWriter('(I5,I5,F7.3)')
    line = line.write([ntypf,koptn,alpha])
    file.write(line+'\n')

    ################### Line 6 ###################
     ################## OBTDs ###################
    
    djt = float(get("Change in spin of target:\n",djt))
    dtt = float(get("Change in isospin of target:\n",1.0))
    obtd_filename = str(get("Enter filename/path to OXBASH obtd file","t331dp150.obd"))
    prefactor = get_zT_prefactor(ji,ti,float(tzi),dtt,float(tzf)-float(tzi),tf,float(tzf))   
    print "Target prefactor = ",prefactor
    fold_obtds = get_obtd(obtd_filename,djt) # STILL NEED CG COEFs
    for obtd in fold_obtds:
        line = form.FortranRecordWriter('(I5,I5,I5,F5.1,F17.6)')
        line = line.write([obtd[0],obtd[1],1,0.0,obtd[2]])
        file.write(line+'\n')
    line = form.FortranRecordWriter('(I5,I5)')
    line = line.write([-1,-1])
    file.write(line+'\n')
    wsaw_proj = str(get("Enter filename of target WSAW radial wavefunction file:\n","6LI6LI"))
    line = form.FortranRecordWriter('(A7)')
    line = line.write([wsaw_proj])
    file.write(line+'\n')

    ################### Line 6 ###################
    fnrm1 = float(get("Normalization of SNKE Yukawas (all ranges) for transformation from tNN to tNA:\n",0.954))
    fnrm2 = float(get("kA (momentum of projectile in NA frame) instead of lab -- of particular importance for very light (A<10) target nuclei:\n",2.46))
    line = form.FortranRecordWriter('(F6.3,F9.2,F11.3,A12)')
    line = line.write([fnrm1,fnrm2,1.000,'love_140'])
    file.write(line+'\n')
    nform = int(get("The number of (jr,jp,jt) that will be entered",2))
    line = form.FortranRecordWriter('(I5)')
    line = line.write([nform])
    file.write(line+'\n')
    for i in range(0,nform):
        jrjpjt = str(get("(jr,jp,jt)","011"))
        line = form.FortranRecordWriter('(I5,I5,I5,I5)')
        line = line.write([jrjpjt[0],jrjpjt[1],jrjpjt[2],-1])
        file.write(line+'\n')
        line = form.FortranRecordWriter('(F5.2,F10.2,F10.2,F10.2,F10.2,F10.2,F10.2)')
        line = line.write([1.0,1.0,1.0,1.0,1.0,1.0,1.0,])
        file.write(line+'\n')
        line = form.FortranRecordWriter('(F5.2,F10.2,F10.2,F10.2,F10.2,F10.2,F10.2)')
        line = line.write([1.0,1.0,1.0,1.0,1.0,1.0,1.0,])
        file.write(line+'\n')

    
    




    file.close()
