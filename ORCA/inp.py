import os
import re

cmd = "wB97X-D3 def2-QZVP Opt Freq"
dir = input('Directory: ')
os.chdir(dir)
jobs = [fn.replace('.gjf', '') for fn in os.listdir() if fn.endswith('.gjf')]

for job in jobs:
    # Input charge and spin multiplicity
    chrg_spin = input(f"{job} - specify charge and spin (e.g. 0 1): ")

    # Read coords from gjf
    with open(job + '.gjf') as gjf_file: lines = gjf_file.readlines()
    coords = [l for l in lines if re.match(' [A-Z][a-z]? ', l) != None]
    natoms = len(coords)

    # Write xyz file
    with open(job + '.xyz', 'w', newline='\n') as xyz_file:
        xyz_file.write(f"{natoms}\n")
        xyz_file.write(f"\n")
        xyz_file.write("".join(coords))

    # Write orca input file
    with open(job + '.inp', 'w', newline='\n') as orca_inp_file:
        orca_inp_file.write(f"! {cmd}\n")
        orca_inp_file.write("%maxcore 11500\n")
        orca_inp_file.write("%pal nprocs 16 end\n")
        orca_inp_file.write(f"* xyzfile {chrg_spin} {job}.xyz\n")

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
