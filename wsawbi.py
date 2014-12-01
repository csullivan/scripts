import readline, glob
import fortranformat as form
import numpy as np
import math

def get(prompt, default):
    return raw_input("%s [%s] " % (prompt, default)) or default

def complete(text, state):
    return (glob.glob(text+'*')+[None])[state]

def init_tab_complete():
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete)

class Nucleus():
    def __init__(self,A,Z,J,Pi,T):
        self.A = A
        self.Z = Z
        self.J = J
        self.Parity = Pi
        self.T = T
        self.Tz = (A-2.0*Z)/2.0

class FOLDInstance():
    def __init__(self):
        #self.Projectile = Nucleus(A,Z,J,Pi,T,Tz)
        self.temp = 0
    def SetProjectile(self,A,Z,J,Pi,T):
        self.Projectile = Nucleus(A,Z,J,Pi,T)
    def SetTarget(self,A,Z,J,Pi,T):
        self.Target = Nucleus(A,Z,J,Pi,T)
    def SetEjectile(self,A,Z,J,Pi,T):
        self.Ejectile = Nucleus(A,Z,J,Pi,T)
    def SetResidual(self,A,Z,J,Pi,T):
        self.Residual = Nucleus(A,Z,J,Pi,T)





def parse_obtd(obtd_filename):
    try:
        obtd_file = open(obtd_filename,"rb")
    except IOError:
        print "Error, file does not exist"; exit()
    obtd_list = []
    for i,line in enumerate(obtd_file):        
        if 'ai <-> af' in line:
            line = line.split()
            print int(line[6]),int(line[8])
        if 'ji <-> jf' in line:
            line = line.split()
            print line[6],line[8]
        if 'ti <-> tf' in line:
            line = line.split()
            print line[6],line[8]
        if 'pi <-> pf' in line:
            line = line.split()
            print line[6],line[8]

def parse_dens(initialdens,finaldens):
    try:
        initial_dens_file = open(initialdens,"rb")
        final_dens_file = open(finaldens,"rb")
    except IOError:
        print "Error, file does not exist"; exit()

    for line in initial_dens_file:
        if '* ia,iz' in line:
            line = line.split()
            ai = int(line[3])
            zi = int(line[4])
            break
    for line in final_dens_file:
        if '* ia,iz' in line:
            line = line.split()
            af = int(line[3])
            zf = int(line[4])
            break
    print ai,zi," ",af,zf
    assert(ai==af)
    # determine which nucleon is valence in system
    if zi>zf:
        initial_nucleon = 'proton'
        final_nucleon = 'neutron'
    if zi<zf:
        initial_nucleon = 'neutron'
        final_nucleon = 'proton'
    if zi==zf:
        initial_nucleon = 'proton'
        final_nucleon = 'neutron'
        # doesn't matter initial == final
    valence_nucleon_initial = []
    sp_lines = False
    for i,line in enumerate(initial_dens_file):
        if sp_lines:
            if '-----' in line:
                sp_lines = False
                break
            valence_nucleon_initial.append(line.split())
        if initial_nucleon+' bound state results' in line:
            sp_lines = True
    valence_nucleon_final = []
    for i,line in enumerate(final_dens_file):
        if sp_lines:
            if '-----' in line:
                sp_lines = False
                break
            valence_nucleon_final.append(line.split())
        if final_nucleon+' bound state results' in line:
            sp_lines = True
    print valence_nucleon_final

if __name__=="__main__":
    init_tab_complete()
    #parse_obtd('t331dp150.obd')

    #FOLD = FOLDInstance()
    #FOLD.SetProjectile(13,5,1.5,-1,1.5)
    #FOLD.SetEjectile(13,4,0.5,+1,2.5)
    #FOLD.SetTarget(9,4,1.5,-1,0.5)
    #FOLD.SetResidual(9,5,1.5,-1,0.5)

    
    projdens = get("Enter path for dens projectile file from oxbash/nushell","13b-dens.dao")
    finaldens = get("Enter path for dens projectile file from oxbash/nushell","13be-dens.dao")
    data = parse_dens(projdens,finaldens)
    exit()

    filename = get("Enter a name for the WSAW input file to be generated","wsaw.inp")
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


    
