
#필수 pip 패키지 설치
import subprocess, os, sys,shutil
def runpip(cmd): subprocess.run([sys.executable, "-m", "pip"] + cmd.split(), shell=False)
print("[ start ] Setting up e   nvironment for OpenFOAM automatic tasks...")
runpip("--version")
runpip("install -r requirements.txt")
if input('Press Enter to continue...')!=None:
    with open('foampy.py','w') as f:
        f.write('''
import os,subprocess,shutil,re;import numpy as np;import pandas as pd;import matplotlib.pyplot as plt



cases_p1=[];cases_p2=[];cases_check=[]
casesproc_p1=[];casesproc_p2=[]
process=[];results=[]; r_case=[];r_lift_mean=[];r_lift_std=[];r_drag_mean=[];r_drag_std=[]

def r_clear():
    for i in [results,r_case,r_lift_mean,r_lift_std,r_drag_mean,r_drag_std]: i.clear()

#케이스 공통 부모 클래스
class Case:
    def __init__(self,name):self.name=name
    def foamRun(self):
        try: 
            p = subprocess.Popen(["foamRun"], cwd = os.path.join('p1', self.name))
            return p
        except: print("[오류 발생: foamRun] 이 프로세스는 v11 이상의 OpenFOAM 환경에서 진행해야 합니다.")
    def decompose(self, num):
        with open (os.path.join('p1',self.name,"system","decomposeParDict"), "r") as f:
            lines = f.readlines()
        with open (os.path.join('p1',self.name,"system","decomposeParDict"), "w") as f:
            for line in lines:
                if "numberOfSubdomains" in line:
                    f.write(f"numberOfSubdomains  {num};\n")
                else:f.write(line)
                


#1번 파라메트릭 스윕 전용 클래스
class Case_p1(Case):
    def __init__(self,name):
        super().__init__(name)
        try:
            if self.name.startswith ("m-"):
                self.angle = float(self.name[1:-3])
            else:
                self.angle = float(self.name[:-3])
            if self.angle and self.angle:
                casesproc_p1.append(self)
                casesproc_p1.sort(key = lambda case:case.angle)
            cases_p1.append(self)
            cases_p1.sort(key = lambda case:case.angle)
        except: pass

    def delete(self, folder, file=None):
        base=os.path.join('p1',self.name)
        if folder is None and file:
            os.remove(os.path.join(base,file))
            print(f'Deleted {os.path.join(base,file)}')
        elif folder and file is None:
            shutil.rmtree(os.path.join(base,folder))
            print(f'Deleted {os.path.join(base,folder)}')
        elif folder and file:
            os.remove(os.path.join(base,folder,file))
            print(f'Deleted {os.path.join(base,folder,file)}')
        

    def update(self, folder, file=None):
        base=os.path.join('p1',self.name)
        source=os.path.join('p1','Casetemplate')
        if folder is None and file:
            shutil.copy2(os.path.join(source,file),os.path.join(base,file))
            print(f'Updated {os.path.join(base,file)}')
        elif folder and file is None:
            shutil.copytree(os.path.join(source,folder),os.path.join(base,folder),dirs_exist_ok=True)
            print(f'Updated {os.path.join(base,folder)}')
        elif folder and file:
            shutil.copy2(os.path.join(source,folder,file),os.path.join(base,folder,file))
            print(f'Updated {os.path.join(base,folder,file)}')


    def forces(self):
        global results
        timelines = []
        drag_list = []
        lift_list = []
        dat = os.path.join('p1', self.name, "postProcessing", "Forces", "0", "forces.dat")
        with open(dat, "r")as f:
            for line in f:
                if line.startswith("#") or line.strip() =="":
                    continue
                timeline = float(line[:10].strip())
                if timeline<1:continue
                vectors = re.findall(r"\(([^()]+)\)", line)
                f_a = vectors[0].strip().split()
                f_b = vectors[1].strip().split()
                lift = float(f_a[2]) + float(f_b[2])
                drag = float(f_a[1]) + float(f_b[1])
                drag_list.append(drag)
                lift_list.append(lift)
                timelines.append(timeline)
        drag_arr = np.array(drag_list)
        lift_arr = np.array(lift_list)
        drag_mean = np.mean(drag_arr)
        lift_mean = np.mean(lift_arr)
        drag_std = np.std(drag_arr)
        lift_std = np.std(lift_arr)
        timelines_arr = np.array(timelines)
        r_case.append(self.angle)
        r_lift_mean.append(lift_mean)
        r_lift_std.append(lift_std)
        r_drag_mean.append(drag_mean)
        r_drag_std.append(drag_std)
        results.append({
            "Case": self.angle,
            "Lift Mean": lift_mean,
            "Lift Std": lift_std,
            "Drag Mean": drag_mean,
            "Drag Std": drag_std,
        })
        df = pd.DataFrame({
            "Time": timelines_arr,
            "Drag": drag_arr,
            "Lift": lift_arr,
        })

        df.to_excel(f"single_forces_{self.name}.xlsx", index=False)

        plt.plot(timelines_arr, drag_arr, label = "Drag", color = (0.0, 0.0, 0.0, 0.5), linestyle="-", marker="")
        plt.axhline(y=float(686), label = "Gravity", color = (0.0, 0.0, 1.0, 0.7), linestyle=":")
        plt.plot(timelines_arr, lift_arr, label = "Lift", color = (1.0, 0.0, 0.0, 1.0), linestyle="-", marker="")

        plt.title(f"Lift and Drag of Human Body [ angle : {self.angle}deg ] [ Wind Velocity : 60m/s ]")
        plt.xticks([])
        plt.grid(axis='x', visible=False)
        plt.xlabel("Time         [   s   ]")
        plt.ylabel("Force        [   N   ]")
        plt.grid(True)
        plt.legend(
            loc       = "lower right",
            frameon   = True,
            edgecolor = "black",
            facecolor = "white",
            )

        plt.savefig(f"single_forces_{self.angle}.png", dpi=300, bbox_inches='tight')
        timelines.clear()
        lift_list.clear()
        drag_list.clear()
        plt.close()
    
    def foamRun(self):
        try: 
            p = subprocess.Popen(["foamRun"], cwd = os.path.join('p1', self.name))
            return p
        except: print("[오류 발생: foamRun] 이 프로세스는 v11 이상의 OpenFOAM 환경에서 진행해야 합니다.")
    def transformPoints(self):
        try:
            command = f"transformPoints 'Rx={self.angle}' "
            p = subprocess.Popen(command, cwd = os.path.join('p1', self.name), shell=True)
            return p
        except: print("[오류 발생: foamRun] 이 프로세스는 v11 이상의 OpenFOAM 환경에서 진행해야 합니다.")


#1번 파라메트릭 스윕 전용 함수들
def postProcessing_p1():
    r_clear()
    folders = sorted(cases_p1, key = lambda f:f.angle )
    for case in folders: case.forces()
    df = pd.DataFrame(results)
    df.to_excel("total_forces_10423.xlsx", index=False)
    plt.plot(r_case, r_drag_std, label = "Drag Std", color = (0.0, 0.0, 0.0, 0.3), linestyle=":", marker="")
    plt.plot(r_case, r_lift_std, label = "Lift Std", color = (1.0, 0.0, 0.0, 0.4), linestyle=":", marker="")
    plt.plot(r_case, r_drag_mean, label = "Drag", color = (0.0, 0.0, 0.0, 0.5), linestyle="-", marker="")
    plt.axhline(y=float(686), label = "Gravity", color = (0.0, 0.0, 1.0, 0.7), linestyle=":")
    plt.plot(r_case, r_lift_mean, label = "Lift", color = (1.0, 0.0, 0.0, 1.0), linestyle="-", marker="")
    plt.title(f"Lift and Drag of Human Body [ angle : [ Wind Velocity : 60m/s ]")
    plt.xlabel("Angle        [  deg  ]")
    plt.ylabel("Force        [   N   ]")
    plt.grid(True)
    plt.legend(
        loc       = "lower right",
        frameon   = True,
        edgecolor = "black",
        facecolor = "white",
        )

    plt.savefig(f"total_forces_10423.png", dpi=300, bbox_inches='tight')
    plt.close()

def launch_p1(): 
    cases_p1.clear()
    for case in os.listdir('p1'): case = Case_p1(case)

def update_p1():
    folder=input('Enter your FOLDER name: ')
    file=input('Enter your FILE name: ')
    for case in cases_p1:
        case.update(folder,file)
def delete_p1():
    folder=input('Enter your FOLDER name: ')
    file=input('Enter your FILE name: ')
    for case in cases_p1:
        case.delete(folder,file)

def parallelRun_p1():
        global process
        process = []
        num = int(input("Batch Size: "))
        sub = int(input("Number Of Subdomains: "))
        for i in range(0, len(casesproc_p1), num):
            batch = casesproc_p1[i : i+num]
            for case in batch:
                p = case.decompose(sub)
                if p: process.append(p)
            for p in process: p.wait()
            process.clear()

def batch_p1(func):
    def wrapper():
        global process
        process = []
        num = int(input("Concurrency level: "))
        for i in range(0, len(casesproc_p1), num):
            batch = casesproc_p1[i : i+num]
            for case in batch:
                p = func(case)
                if p: process.append(p)
            for p in process: p.wait()
            process.clear()
    return wrapper

@batch_p1
def foamRun_p1(case): return case.foamRun()
@batch_p1
def transformPoints_p1(case): return case.transformPoints()

#2번 파라메트릭 스윕 전용 클래스
class Case_p2:
    def __init__(self, name):
        try:
            super().__init__(name)
            self.velocity = float(self.name[:-3])
            if self.velocity:
                casesproc_p2.append(self)
                casesproc_p2.sort(key = lambda case:case.velocity)
            cases_p2.append(self)
            cases_p2.sort(key = lambda case:case.velocity)
        except: pass

    def delete(self, folder, file=None):
        base=os.path.join('p2',self.name)
        if folder is None and file:
            os.remove(os.path.join(base,file))
            print(f'Deleted {os.path.join(base,file)}')
        elif folder and file is None:
            shutil.rmtree(os.path.join(base,folder))
            print(f'Deleted {os.path.join(base,folder)}')
        elif folder and file:
            os.remove(os.path.join(base,folder,file))
            print(f'Deleted {os.path.join(base,folder,file)}')
        

    def update(self, folder, file=None):
        base=os.path.join('p2',self.name)
        source=os.path.join('p2','Casetemplate')
        if folder is None and file:
            shutil.copy2(os.path.join(source,file),os.path.join(base,file))
            print(f'Updated {os.path.join(base,file)}')
        elif folder and file is None:
            shutil.copytree(os.path.join(source,folder),os.path.join(base,folder),dirs_exist_ok=True)
            print(f'Updated {os.path.join(base,folder)}')
        elif folder and file:
            shutil.copy2(os.path.join(source,folder,file),os.path.join(base,folder,file))
            print(f'Updated {os.path.join(base,folder,file)}')
        
    def changeU(self):
        with open(os.path.join('p2',self.name,"0","U"), "r") as f:
            lines = f.readlines()
        with open(os.path.join('p2',self.name,"0","U"), "w") as f:
            for line in lines:
                if "internalField   uniform (0 60 0);" in line:
                    f.write(f"internalField   uniform (0 {self.velocity} 0);\n")
                elif "        value   uniform (0 60 0);" in line:
                    f.write(f"        value   uniform (0 {self.velocity} 0);\n")
                else: f.write(line)
    def forces(self):
        global results
        timelines = []
        drag_list = []
        lift_list = []
        dat = os.path.join('p2', self.name, "postProcessing", "Forces", "0", "forces.dat")
        with open(dat, "r")as f:
            for line in f:
                if line.startswith("#") or line.strip() =="":
                    continue
                timeline = float(line[:10].strip())
                if timeline<1:continue
                vectors = re.findall(r"\(([^()]+)\)", line)
                f_a = vectors[0].strip().split()
                f_b = vectors[1].strip().split()
                lift = float(f_a[2]) + float(f_b[2])
                drag = float(f_a[1]) + float(f_b[1])
                drag_list.append(drag)
                lift_list.append(lift)
                timelines.append(timeline)
        drag_arr = np.array(drag_list)
        lift_arr = np.array(lift_list)
        drag_mean = np.mean(drag_arr)
        lift_mean = np.mean(lift_arr)
        drag_std = np.std(drag_arr)
        lift_std = np.std(lift_arr)
        timelines_arr = np.array(timelines)
        r_case.append(self.velocity)
        r_lift_mean.append(lift_mean)
        r_lift_std.append(lift_std)
        r_drag_mean.append(drag_mean)
        r_drag_std.append(drag_std)
        results.append({
            "Case": self.velocity,
            "Lift Mean": lift_mean,
            "Lift Std": lift_std,
            "Drag Mean": drag_mean,
            "Drag Std": drag_std,
        })
        df = pd.DataFrame({
            "Time": timelines_arr,
            "Drag": drag_arr,
            "Lift": lift_arr,
        })

        df.to_excel(f"single_forces_{self.name}.xlsx", index=False)

        plt.plot(timelines_arr, drag_arr, label = "Drag", color = (0.0, 0.0, 0.0, 0.5), linestyle="-", marker="")
        plt.axhline(y=float(686), label = "Gravity", color = (0.0, 0.0, 1.0, 0.7), linestyle=":")
        plt.plot(timelines_arr, lift_arr, label = "Lift", color = (1.0, 0.0, 0.0, 1.0), linestyle="-", marker="")

        plt.title(f"Lift and Drag of Human Body [ angle : 50.00deg ] [ Wind Velocity : {self.name} ]")
        plt.xticks([])
        plt.grid(axis='x', visible=False)
        plt.xlabel("Time         [   s   ]")
        plt.ylabel("Force        [   N   ]")
        plt.grid(True)
        plt.legend(
            loc       = "lower right",
            frameon   = True,
            edgecolor = "black",
            facecolor = "white",
            )

        plt.savefig(f"single_forces_{self.name}.png", dpi=300, bbox_inches='tight')
        timelines.clear()
        lift_list.clear()
        drag_list.clear()
        plt.close()

#2번 파라메트릭 스윕 전용 함수들
def postProcessing_p2():
    r_clear()
    folders = sorted(cases_p2, key = lambda f:f.velocity )
    for case in folders: case.forces()
    df = pd.DataFrame(results)
    df.to_excel("total_forces_10423.xlsx", index=False)
    plt.plot(r_case, r_drag_std, label = "Drag Std", color = (0.0, 0.0, 0.0, 0.3), linestyle=":", marker="")
    plt.plot(r_case, r_lift_std, label = "Lift Std", color = (1.0, 0.0, 0.0, 0.4), linestyle=":", marker="")
    plt.plot(r_case, r_drag_mean, label = "Drag", color = (0.0, 0.0, 0.0, 0.5), linestyle="-", marker="")
    plt.axhline(y=float(686), label = "Gravity", color = (0.0, 0.0, 1.0, 0.7), linestyle=":")
    plt.plot(r_case, r_lift_mean, label = "Lift", color = (1.0, 0.0, 0.0, 1.0), linestyle="-", marker="")
    plt.title(f"Lift and Drag of Human Body [ angle : 50.00deg ]")
    plt.xlabel("velocity     [  m/s  ]")
    plt.ylabel("Force        [   N   ]")
    plt.grid(True)
    plt.legend(
        loc       = "lower right",
        frameon   = True,
        edgecolor = "black",
        facecolor = "white",
        )

    plt.savefig(f"total_forces_10423.png", dpi=300, bbox_inches='tight')
    plt.close()

def launch_p2(): 
    cases_p2.clear()
    for case in os.listdir('p2'): case = Case(case)

def update_p2():
    folder=input('Enter your FOLDER name: ')
    file=input('Enter your FILE name: ')
    for case in cases_p2:
        case.update(folder,file)
def delete_p2():
    folder=input('Enter your FOLDER name: ')
    file=input('Enter your FILE name: ')
    for case in cases_p2:
        case.delete(folder,file)

def foamRun_p2():
    global process
    process = []
    num = int(input("Batch Size: "))
    for i in range(0, len(casesproc_p2), num):
        batch = casesproc_p2[i : i+num]
        for case in batch:
            p = case.foamRun()
            if p: process.append(p)
        for p in process: p.wait()
        process.clear()

def parallelRun_p2():
        global process
        process = []
        num = int(input("Batch Size: "))
        sub = int(input("Number Of Subdomains: "))
        for i in range(0, len(casesproc_p2), num):
            batch = casesproc_p2[i : i+num]
            for case in batch:
                p = case.decompose(sub)
                if p: process.append(p)
            for p in process: p.wait()
            process.clear()

#1차 파라메트릭 스윕 결과 검증용 케이스 전용 함수들
def forces_check():
    global results
    timelines = []
    drag_list = []
    lift_list = []
    dat = os.path.join('check', "50deg", "postProcessing", "Forces", "0", "forces.dat")
    with open(dat, "r")as f:
        for line in f:
            if line.startswith("#") or line.strip() =="":
                continue
            timeline = float(line[:10].strip())
            if timeline<1.3:continue
            vectors = re.findall(r"\(([^()]+)\)", line)
            f_a = vectors[0].strip().split()
            f_b = vectors[1].strip().split()
            lift = float(f_a[2]) + float(f_b[2])
            drag = float(f_a[1]) + float(f_b[1])
            drag_list.append(drag)
            lift_list.append(lift)
            timelines.append(timeline)
    drag_arr = np.array(drag_list)
    lift_arr = np.array(lift_list)
    drag_mean = np.mean(drag_arr)
    lift_mean = np.mean(lift_arr)
    drag_std = np.std(drag_arr)
    lift_std = np.std(lift_arr)
    timelines_arr = np.array(timelines)
    r_case.append(50)
    r_lift_mean.append(lift_mean)
    r_lift_std.append(lift_std)
    r_drag_mean.append(drag_mean)
    r_drag_std.append(drag_std)
    df = pd.DataFrame({
        "Time": timelines_arr,
        "Drag": drag_arr,
        "Lift": lift_arr,
    })

    df.to_excel(f"single_forces_50deg.xlsx", index=False)

    plt.plot(timelines_arr, drag_arr, label = "Drag", color = (0.0, 0.0, 0.0, 0.5), linestyle="-", marker="")
    plt.axhline(y=float(686), label = "Gravity", color = (0.0, 0.0, 1.0, 0.7), linestyle=":")
    plt.plot(timelines_arr, lift_arr, label = "Lift", color = (1.0, 0.0, 0.0, 1.0), linestyle="-", marker="")

    plt.title(f"Lift and Drag of Human Body [ angle : 50deg ] [ Wind Velocity : 60m/s ]")
    plt.xticks([])
    plt.grid(axis='x', visible=False)
    plt.xlabel("Time         [   s   ]")
    plt.ylabel("Force        [   N   ]")
    plt.grid(True)
    plt.legend(
        loc       = "lower right",
        frameon   = True,
        edgecolor = "black",
        facecolor = "white",
        )

    plt.savefig(f"Checking_50deg_60mps.png", dpi=300, bbox_inches='tight')
    timelines.clear()
    lift_list.clear()
    drag_list.clear()
    plt.close()

def decompose_check(num):
    with open (os.path.join('check','50deg',"system","decomposeParDict"), "r") as f:
        lines = f.readlines()
    with open (os.path.join('check','50deg',"system","decomposeParDict"), "w") as f:
        for line in lines:
            if "numberOfSubdomains" in line:
                f.write(f"numberOfSubdomains  {num};\n")
            else:f.write(line)
    try: 
        subprocess.run(["decomposePar"], cwd = os.path.join('check', '50deg'))
    except: print("[오류 발생: foamRun] 이 프로세스는 v11 이상의 OpenFOAM 환경에서 진행해야 합니다.")
    subprocess.Popen(["mpirun","-np",str(num),"foamRun","-parallel"], cwd = os.path.join('check','50deg'))

def foamRun_check():
    try: 
        p = subprocess.Popen(["foamRun"], cwd = os.path.join('check', '50deg'))
        return p
    except: print("[오류 발생: foamRun] 이 프로세스는 v11 이상의 OpenFOAM 환경에서 진행해야 합니다.")

def transformPoints_check():
    try:
        command = f"transformPoints 'Rx={50}' "
        p = subprocess.Popen(command, cwd = os.path.join('check', '50deg'), shell=True)
        return p
    except: print("[오류 발생: foamRun] 이 프로세스는 v11 이상의 OpenFOAM 환경에서 진행해야 합니다.")
launch_p1()
launch_p2()
        ''')
    with open('make.py','w') as f:
        f.write('''
import os,shutil,foampy
def p1():
    root = os.path.join("..", "p1")
    for i in range(-175,181,5): 
        if i<0:os.makedirs(os.path.join(root, f"m{i}deg"), exist_ok = True)
        elif i>=0:os.makedirs(os.path.join(root, f"{i}deg"), exist_ok = True)
    foampy.launch_p1()
    shutil.copytree('CaseTemplate',os.path.join('p1','CaseTemplate'),dirs_exist_ok=True)
    for i in foampy.cases_p1:
        i.update('0')
        i.update('system')
        i.update('constant')
        i.update(None,'.foam')
        i.delete(os.path.join('constant','trisurface'),'HumanHQ0deg.stl')
        with open(os.path.join(root,i,'system','controlDict'), "r") as f:
            lines = f.readlines()
        with open(os.path.join(root,i,'system','controlDict'), "w") as f:
            for line in lines:
                        if 'writeIntervlal' in line and '//' in line:
                            f.write("writeInterval            1000;\n")
                        else:pass
        
def p2():
    root = os.path.join("..", "p2")
    for i in range(1,61,5): os.makedirs(os.path.join(root, f"{i}mps"), exist_ok = True)
    foampy.launch_p2()
    shutil.copytree('CaseTemplate',os.path.join('p2','CaseTemplate'),dirs_exist_ok=True)
    for i in foampy.cases_p2:
        i.update('0')
        i.update('system')
        i.update('constant')
        i.update(None,'.foam')
        i.changeU()
        i.delete(os.path.join('constant','trisurface'),'HumanHQ0deg.stl')
        with open(os.path.join(root,i,'system','controlDict'), "r") as f:
            lines = f.readlines()
        with open(os.path.join(root,i,'system','controlDict'), "w") as f:
            for line in lines:
                if "deltaT" in line:
                    f.write(f"deltaT                  0.05;\n")
                elif 'writeIntervlal' in line and '//' in line:
                    f.write("writeInterval            100;\n")
                else:pass

def check(): 
    shutil.copytree(os.path.join('..','CaseTemplate'), '50deg',dirs_exist_ok=True)
    os.remove(os.path.join('50deg0','constant','trisurface','HumanHQ0deg.stl'))
    with open(os.path.join(root,'50deg','system','controlDict'), "r") as f:
        lines = f.readlines()
    with open(os.path.join(root,'50deg','system','controlDict'), "w") as f:
        for line in lines:
            if "deltaT" in line:
                f.write(f"deltaT                  0.01;\n")
            elif 'endTime' in line:
                f.write(f'endtime                 50;\n')
            elif 'writeIntervlal' in line and '//' in line:
                f.write("writeInterval            5000;\n")
            else:pass
        ''')
    with open('menu.py','w') as f:
        f.write('''
def boxheader(title):
    padding = int((35-len(title))/2)
    print('┌'+'─'*padding+title+padding*'─'+'┐')
def boxcontent(string):
    print('│'+'  '+string+' '*(33-len(string))+'│')
def boxfooter():
    print("└───────────────────────────────────┘")
def box(title, contents):
    boxheader(title)
    for string in contents:
        boxcontent(string)
    boxfooter()
def answer():
    try: 
        choice=input("Enter NUMBER of task: ")
        if choice=='q': return 'quit'
        else:
            return int(choice)
    except ValueError:return None


def root():
    contents=['',
              '',
              '  [  1  ]  p1',
              '',
              '  [  2  ]  p2',
              '',
              '  [  3  ]  check',
              '',
              '',
              '  [  q  ]  quit'
              '',
              ''
              ]
    title = '[ Directories ]'
    box(title, contents)
    return answer()



def p(n):
    contents = [
        "",
        "",
        "I.   Case management",
        "",
        "  [  1  ]  Update File or Folder",
        "",
        "  [  2  ]  Delete File or Folder",
        '',
        '  [  3  ]  Initialize',
        "",
        "",
        "II.  OpenFOAM",
        "",
        "  [  4  ]  postProcessing",
        '',
        "  [  5  ]  foamRun",
        '',
        "  [  6  ]  PARALLEL foamRun",
        "",
        "",
        '',
        '',
        '  [  q  ]  quit'
        '',
        ''
        ]
    title = f'[ AUTO  PROCESSER: p{n} ]'
    box(title, contents)
    return answer()


def check():
    contents = [
        "",
        "",
        "I.   Case management",
        '',
        '  [  1  ]  Initialize',
        "",
        "",
        "II.  OpenFOAM",
        "",
        "  [  2  ]  postProcessing",
        '',
        "  [  3  ]  foamRun",
        '',
        "  [  4  ]  PARALLEL foamRun",
        "",
        "",
        '',
        '',
        '  [  q  ]  quit'
        '',
        ''
        ]
    title = '[ AUTO PROCESSER: check ]'
    box(title, contents)
    return answer()
    

    
        ''')

    with open('main.py','w') as f:
        f.write('''
import foampy,menu,make

while True:
    choice=menu.root()
    if choice==1:
        task=menu.p(1)
        if   task==1: foampy.update_p1()
        elif task==2: foampy.delete_p1()
        elif task==3: make.p1
        elif task==4: foampy.postProcessing_p1()
        elif task==5: foampy.foamRun_p1()
        elif task==6: foampy.parallelRun_p1()
        elif task=='quit':print('Process Exiting...');break
        

    elif choice==2:
        task=menu.p(2)
        if   task==1: foampy.update_p2()
        elif task==2: foampy.delete_p2()
        elif task==3: make.p2
        elif task==4: foampy.postProcessing_p2()
        elif task==5: foampy.foamRun_p2()
        elif task==6: foampy.parallelRun_p2()
        elif task=='quit':print('Process Exiting...');break

    elif choice==3:
        task=menu.check()
        if   task==1: make.check
        elif task==2: foampy.forces_check()
        elif task==3: foampy.foamRun_check()
        elif task==4: foampy.decompose_check()
        elif task=='quit':print('Process Exiting...');break

    elif choice is None:print('제대로 입력하세요 좀')
    elif choice=='quit':print('Process Exiting...');break
    else:print('[Fatal] Invalid Choice')
        ''')
    
    import make
    make.p1()
    make.p2()
    make.check()
