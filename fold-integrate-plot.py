import math
import pylab
import numpy as np
import code
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

def setfont(font='helvetica',unicode=True): 
    r""" 
    Set Matplotlibs rcParams to use LaTeX for font rendering. 
    Revert all changes by calling rcdefault() from matplotlib. 
    
    Parameters: 
    ----------- 
    font: string 
        "Helvetica" 
        "Times" 
        "Computer Modern" 
    
    usetex: Boolean 
        Use unicode. Default: False.     
    """ 
    
    # Use TeX for all figure text! 
    pylab.rc('text', usetex=True) 

    font = font.lower().replace(" ","") 
    if font == 'times': 
        # Times 
        font = {'family':'serif', 'serif':['Times']} 
        preamble  = r""" 
                       \usepackage{color} 
                       \usepackage{mathptmx} 
                    """ 
    elif font == 'helvetica': 
        # Helvetica 
        # set serif, too. Otherwise setting to times and then 
        # Helvetica causes an error. 
        font = {'family':'sans-serif','sans-serif':['Helvetica'], 
                'serif':['cm10']} 
        preamble  = r""" 
                       \usepackage{color} 
                       \usepackage[tx]{sfmath} 
                       \usepackage{helvet} 
                    """ 
    else: 
        # Computer modern serif 
        font = {'family':'serif', 'serif':['cm10']} 
        preamble  = r""" 
                       \usepackage{color} 
                    """ 
    
    if unicode: 
        # Unicode for Tex 
        #preamble =  r"""\usepackage[utf8]{inputenc}""" + preamble 
        # inputenc should be set automatically 
        pylab.rcParams['text.latex.unicode']=True 
    
    #print font, preamble 
    pylab.rc('font',**font) 
    pylab.rcParams['text.latex.preamble'] = preamble 


def read_xs_file(filename):
    file = open(filename)
    data = [map(float,line.split()) for line in file]
    dataset = [] 
    datasets = [] 
    for i,line in enumerate(data):        
        if line[0]==0.0 and i!=0: 
            # this will skip the last column because it is usually the sum of the other three columns
            datasets.append(dataset)
            dataset = []
        dataset.append(line)
    datasets = np.asarray(datasets)    
    return datasets

def integrate_xs(dataset):
    integral = 0.0
    for pt in dataset:
        if pt[0] > 50.0:
            break
        theta = pt[0]*math.pi/180.0
        dSigmadOmega = pt[1]
        dtheta = (dataset[1][0]-dataset[0][0])*math.pi/180
        integral += math.sin(theta)*dSigmadOmega*dtheta
    return 2*math.pi*integral


def plot_xs(path,Max=None,labels=None,summed=False,title=""):
    datasets = read_xs_file(path)
    if (labels != None and Max != None):
        assert(len(labels)==int(Max))
    elif (labels != None):
        assert(len(labels)==len(datasets))
    
    datasum = np.zeros(180)
    for i,data in enumerate(datasets):
        #print i
        if i > Max-1:
            break
        if sum(data[:,1]) == 0:
            pass
            #canvas.set_yscale('linear')
            #pylab.plot(data[:,0],data[:,1])
            #print "linear scale"
        else:
            #y = [math.log10(x) for x in [float(x) for x in data[:,1]]]
            canvas.set_yscale('log')
            #pylab.plot(data[:,0],y)
            if labels != None:
                pylab.plot(data[:,0],data[:,1],label="("+labels[i]+")")
            else:
                pylab.plot(data[:,0],data[:,1])
        datasum+=data[:,1] 
    if summed:
        pylab.plot(data[:,0],datasum)

    if labels != None:
        pylab.legend(loc=1,prop={'size':14})
    pylab.ylabel(r"$\frac{d\sigma}{d\Omega}$ (mb/sr)")
    pylab.xlabel(r"$\theta_{cm}$ (deg)")
    pylab.title(title)


def plot_wvfunc(path):
    file = open(path)
    data = [map(float,line.split()) for line in file]
    datasets = [[],[],[],[]]
    counter = -1
    for line in data:                
        if len(line)==4:
            counter += 1
            #print counter
            continue
        if len(line)!=5:
            continue
        datasets[counter].append(line)
    datasets = np.asarray(datasets)
    wfset = []
    for i in range(0,len(datasets)):
        temp = np.asarray(datasets[i])
        wf = []    
        for j in range(0,len(temp[0])):
            for el in temp[:,j]:
                wf.append(el)
        wfset.append(wf)

    radius = np.arange(0.1,15.1,0.1)
    wfset = np.asarray(wfset)    
    fig = pylab.figure(figsize=(5.5,2))
    canvas = pylab.subplot(1,1,1)
    #print len(radius),len(wfset[0])
    pylab.plot(radius,wfset[0],label="0")    
    pylab.plot(radius,wfset[1],label="1")    
    pylab.plot(radius,wfset[2],label="2")    
    pylab.plot(radius,wfset[3],label="3")    
    pylab.legend()
    pylab.xlim(0.1,2.2)
    pylab.savefig('/user/sullivan/public_html/research/wvfunc2.pdf')
    #pylab.show()
    code.interact(local=locals())

def wood_saxon(V,r,a,Ap,At):
    domain = np.arange(0.0,10.1,0.1)
    mass = np.power(Ap,1.0/3.0)+np.power(At,1.0/3.0)
    exp = np.exp((domain-r*mass)/a)
    output = -np.abs(V)/(1+exp)
    return [domain,output]
    
def plot_pot(V,r,a,Ap,At):
    radius, pot = wood_saxon(V,r,a,Ap,At)
    pylab.plot(radius,pot)    

def plot_pot(filename,label,color=None):
    radius = []
    real = []
    imag = []
    for line in open(filename):
        line = line.split()
        radius.append(float(line[0]))
        real.append(float(line[1]))
        imag.append(float(line[2]))
    if color == None:        
        pylab.plot(radius,real,label=label)    
        pylab.plot(radius,imag,'--',)    
    else:
        pylab.plot(radius,real,label=label,color=color)    
        pylab.plot(radius,imag,'--',color=color)            
        pylab.legend(loc='lower right', bbox_to_anchor=(0.98, 0.65),prop={'size':10})
    

if __name__=='__main__':
    setfont()
    fig = pylab.figure(figsize=(5.5,7.5))
    canvas = pylab.subplot(1,1,1)
    plot_xs("./dwhi_jf0.5/8deg/b13be9_jp1.plot",3,labels=['011','111','211'])
    plot_xs("./dwhi_jf0.5/8deg/b13be9_jp2.plot",3,labels=['121','221','321'],title=r"$^{13}$Be[1/2+]")
    pylab.savefig('/user/sullivan/public_html/csxn-13Be_0.5+.pdf',bbox_inches='tight')
    pylab.clf()

    data_jp1 = read_xs_file("./dwhi_jf0.5/54deg/b13be9_jp1.plot")
    int011 = integrate_xs(data_jp1[0])
    int111 = integrate_xs(data_jp1[1])
    int211 = integrate_xs(data_jp1[2])
    data_jp2 = read_xs_file("./dwhi_jf0.5/54deg/b13be9_jp2.plot")
    int121 = integrate_xs(data_jp2[0])
    int221 = integrate_xs(data_jp2[1])
    int321 = integrate_xs(data_jp2[2])
    print int011,int111,int211,int121,int221,int321
    csxn1 = sum([int011,int111,int211,int121,int221,int321])
    print "Integrated cross section (50 degrees) 13Be[1/2+] = ", csxn1
    print "Per unit B(GT): ", csxn1/1.10856
    print "Scaled for unaccounted GT in 9B: ",(csxn1/1.10856)*2.07
    print "Further scaled for unaccounted multipole in 9B: ",((csxn1/1.10856)*2.07)*10
    
    #######    #######    #######    #######    #######    #######

    fig = pylab.figure(figsize=(5.5,7.5))
    canvas = pylab.subplot(1,1,1)
    plot_xs("./dwhi_jf2.5/8deg/b13be9_jp1.plot",3,labels=['011','111','211'])
    plot_xs("./dwhi_jf2.5/8deg/b13be9_jp2.plot",3,labels=['121','221','321'])
    plot_xs("./dwhi_jf2.5/8deg/b13be9_jp3.plot",3,labels=['231','331','431'])
    plot_xs("./dwhi_jf2.5/8deg/b13be9_jp4.plot",3,labels=['341','441','541'],title=r"$^{13}$Be[5/2+]")
    pylab.savefig('/user/sullivan/public_html/csxn-13Be_2.5+.pdf',bbox_inches='tight')

    data_jpf5_djp1 = read_xs_file("./dwhi_jf2.5/54deg/b13be9_jp1.plot")
    int011 = integrate_xs(data_jpf5_djp1[0])
    int111 = integrate_xs(data_jpf5_djp1[1])
    int211 = integrate_xs(data_jpf5_djp1[2])
    data_jpf5_djp2 = read_xs_file("./dwhi_jf2.5/54deg/b13be9_jp2.plot")
    int121 = integrate_xs(data_jpf5_djp2[0])
    int221 = integrate_xs(data_jpf5_djp2[1])
    int321 = integrate_xs(data_jpf5_djp2[2])
    data_jpf5_djp3 = read_xs_file("./dwhi_jf2.5/54deg/b13be9_jp3.plot")
    int231 = integrate_xs(data_jpf5_djp3[0])
    int331 = integrate_xs(data_jpf5_djp3[1])
    int431 = integrate_xs(data_jpf5_djp3[2])
    data_jpf5_djp4 = read_xs_file("./dwhi_jf2.5/54deg/b13be9_jp4.plot")
    int341 = integrate_xs(data_jpf5_djp4[0])
    int441 = integrate_xs(data_jpf5_djp4[1])
    int541 = integrate_xs(data_jpf5_djp4[2])
    print int011,int111,int211,int121,int221,int321,int231,int331,int431,int341,int441,int541
    csxn5 = sum([int011,int111,int211,int121,int221,int321,int231,int331,int431,int341,int441,int541])
    print "Integrated cross section (50 degrees) 13Be[5/2+] = ", csxn5
    print "Per unit B(GT): ", csxn5/1.10856
    print "Scaled for unaccounted GT in 9B: ",(csxn5/1.10856)*2.07
    print "Further scaled for unaccounted multipole in 9B: ",((csxn5/1.10856)*2.07)*10

   # plot_wvfunc("/projects/ceclub/6Li6Li*/rxns_codes/working/results_6li.out/C12C12")#LI6LI6

   # fig = pylab.figure(figsize=(5.5,2.75))
   # canvas = pylab.subplot(1,1,1)
   # plot_pot("omp/13b9be_potl.out",r"13B-9Be",'red')
   # plot_pot("omp/13be9b_potl.out",r"13Be-9B",'black')
   # pylab.xlim(0,8)
   # pylab.ylim(-300,10)
   # extraticks = [4.5]
   # pylab.xticks(np.arange(0,8.25.5,0.25))
   # pylab.savefig('/user/sullivan/public_html/pots.pdf')

