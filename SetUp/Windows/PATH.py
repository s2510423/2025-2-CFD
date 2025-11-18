import subprocess,os
bin=os.path.join(r'C:\\','Program Files','blueCFD-Core-2024','OpenFOAM-12','bin')
platformbin=os.path.join(r'C:\\','Program Files','blueCFD-Core-2024','OpenFOAM-12','platforms','mingw_w64Gcc122DPInt32Opt','bin')
subprocess.run(['setx','PATH',f'{bin};{platformbin};{os.environ["PATH"]}'],shell=True)
if input('press Enter to continue...'): pass