#!/usr/bin/env python

"""
A simple manager for running the nuclear reactions codes
wsaw > wsaw > fold > dwhi (in that order), to calculate angular 
distributions relevant for charge-exchange reactions.
"""

import argparse
import subprocess
import os
import sys
import shutil
import re
import time


ckz_bin = '/projects/ceclub/6Li6Li*/fold/working/ckz'
wsaw_bin = '/projects/ceclub/6Li6Li*/fold/working/wsaw'
fold_bin = '/projects/ceclub/6Li6Li*/fold/working/fold'
dwhi_bin = '/projects/ceclub/6Li6Li*/fold/working/dwhi'

is_64bits = sys.maxsize > 2**32


#def call_wsaw():

def deploy_payload(config_file,output_dir):    
    config_file[0] = os.path.abspath(config_file[0])
    config_file[1] = os.path.abspath(config_file[1])
    config_file[2] = os.path.abspath(config_file[2])
    config_file[3] = os.path.abspath(config_file[3])
    if is_64bits:
        wsaw_command_1 = \
            'cd {output} && {bin} < {input} > {save}'.format(
            bin=wsaw_bin,
            input=config_file[0],
            output=output_dir,
            save=config_file[0].replace('inp','out'))

        wsaw_command_2 = \
            'cd {output} && {bin} < {input} > {save}'.format(
            bin=wsaw_bin,
            input=config_file[1],
            output=output_dir,
            save=config_file[1].replace('inp','out'))

        fold_command = \
            'cp ./love_140 {output} && cd {output} && {bin} < {input} > {save}'.format(
            bin=fold_bin,
            input=config_file[2],
            output=output_dir,
            save=config_file[2].replace('inp','out'))

        dwhi_command = \
            'cd {output} && rm -f love_140 && {bin} < {input} > {save}'.format(
            bin=dwhi_bin,
            input=config_file[3],
            output=output_dir,
            save=config_file[3].replace('inp','out'))

    else:
        print "STOP: Executables were compiled in a 64-bit environment"
        exit()
    os.makedirs(output_dir)        
    subprocess.call(wsaw_command_1,shell=True)
    subprocess.call(wsaw_command_2,shell=True)
    subprocess.call(fold_command,shell=True)
    subprocess.call(dwhi_command,shell=True)

def main():
    p = argparse.ArgumentParser()
   
    p.add_argument('--wsaw1',dest='input_wsaw_1',
                   action='store',required=True,
                   help='The input file to be run through wsaw.')
    p.add_argument('--wsaw2',dest='input_wsaw_2',
                   action='store',required=True,
                   help='The input file to be run through wsaw.')
    p.add_argument('--fold',dest='input_fold',
                   action='store',required=True,
                   help='The input file to be run through fold.')
    p.add_argument('--dwhi',dest='input_dwhi',
                   action='store',required=True,
                   help='The input file to be run through dwhi.')
    p.add_argument('-o','--output',dest='output',
                   action='store',
                   help='The output directory')
    p.add_argument('-f','--force',dest='force',
                   action='store_true',default='',
                   help='If passed, will overwrite existing folders without confirmation')
    p.add_argument('-c','--clean',dest='clean',
                   action='store',
                   help='Analagous to make clean')
    p = p.parse_args()
    if p.clean != None:
        subprocess.call("rm -rf *.out && rm -f ./*~",shell=True)
        exit()

    #Pick a reasonable output folder if not given.
    if not p.output:
        if '.inp' in p.input_wsaw_1:
            p.output = p.input_wsaw_1.replace('.inp','.out')
        else:
            p.output = p.input_wsaw_1 + '.out'

    #Make sure I'm not clobbering the wrong thing.
    if os.path.exists(p.output):
        if not p.force:
            res = raw_input('{} exists.\nOkay to overwrite? (y/N)'.format(p.output))
            if res.lower() in ['y','1','yes']:
                p.force = True
        if p.force:
            shutil.rmtree(p.output)
        else:
            return

    inputs = [p.input_wsaw_1,p.input_wsaw_2,p.input_fold,p.input_dwhi]
    deploy_payload(inputs,p.output.replace('wsaw',''))

    

if __name__=='__main__':    
    main()
