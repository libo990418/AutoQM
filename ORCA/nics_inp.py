""" generate orca .inp files from all .gjf files in a given folder for NICS calculations (single ring) """

import numpy as np
import os
import re

cmd = "NMR PBE0 D4 def2-TZVP(-f)"

print("This program generates orca .inp files from all .gjf files in a given folder for NICS calculations")
folder = input(' Folder: ')
os.chdir(folder)
jobs = [fn.replace('.gjf', '') for fn in os.listdir() if fn.endswith('.gjf')]

for job in jobs:
    # Input charge and spin multiplicity
    chrg_spin = input(f"{job} - specify charge and spin (e.g. 0 1): ")
    ring = input(f"{' ' * len(job)} - specify atoms in the ring of interest (1-indexed, comma-separated): ")

    # Read coords from gjf
    with open(job + '.gjf') as gjf_file: lines = gjf_file.readlines()
    coords = [l for l in lines if re.search(' [A-Z][a-z]? ', l) != None]

    # Generate NICS ghost atom
    ring_idx = [int(eval(i)) - 1 for i in ring.split(',')]
    ring_coords = [coords[i] for i in ring_idx]
    ring_coords = np.array([[eval(x) for x in l.strip().split()[1:4]] for l in ring_coords])
    center = np.average(ring_coords, axis=0)
    center_str = '  H :  {}  {}  {} NewGTO S 1 1 1e6 1 end NewAuxJGTO S 1 1 2e6 1 end\n'.format(center[0], center[1], center[2])

    # Write orca input file
    with open(job + '.inp', 'w', newline='\n') as orca_inp_file:
        orca_inp_file.write(f"! {cmd}\n")
        orca_inp_file.write("%maxcore 11500\n")
        orca_inp_file.write("%pal nprocs 16 end\n")
        orca_inp_file.write(f"* xyz {chrg_spin}\n")
        orca_inp_file.write("".join(coords))
        orca_inp_file.write(center_str)

    # Write submission script
    with open(job + '.sub', 'w', newline='\n') as sub_file:
        sub_file.write('#!/bin/bash -l\n')
        sub_file.write(f'#SBATCH --job-name={job}\n')
        sub_file.write('#SBATCH --nodes=1\n')
        sub_file.write('#SBATCH --ntasks-per-node=16\n')
        sub_file.write('#SBATCH --mem=190000\n')
        sub_file.write('#SBATCH -t 3-00:00:00\n')
        sub_file.write('#SBATCH -p any\n')
        sub_file.write('#SBATCH -o joblog.%j\n')
        sub_file.write('#SBATCH -e joblog.%j\n')
        sub_file.write('#\n')
        sub_file.write('\n')
        sub_file.write('module load openmpi/4.1.1\n')
        sub_file.write('module load orca/5.0.2\n')
        sub_file.write('\n')
        sub_file.write(f"/software/orca/orca_5_0_2_linux_x86-64_shared_openmpi411/orca {job}.inp > {job}.out\n")
        sub_file.write(f"orca_2mkl {job} -molden")
        sub_file.write('\n')
