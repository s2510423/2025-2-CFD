# **인간의 맨몸 비행 가능성에 대한 <br> CFD 시뮬레이션 기반 유체역학적 검증**

<br>

> 2025 시흥고등학교 창의융합눈꽃학술제 - 10423 정승환

<br><br>

## 시뮬레이션 파이프라인

<br>

이것은 제가 실제로 학술제 연구에 사용한 코드들을 일부 수정하여 압축해둔 레포지토리입니다. OpenFOAM을 활용한 파라메트릭 스윕 과정에서의 불가피한 반복작업을 자동화하여 효율성을 높이기 위하여 설계한 코드입니다. 파이썬 스크립트를 모듈화하여 확장과 유지보수성을 증대하였으며, 배포 시 파일 관리를 용이하게 하기 위하여 단일 셋업 스크립트에 모든 스크립트와 케이스 분산 정보를 담았습니다. 폴더 및 파일의 업데이트, 제거의 자동화 뿐만 아니라 OpenFOAM을 이용한 시뮬레이션 실행 자동화, 병렬처리, 후처리 자동화를 구현하였습니다.

<br><br>

## 포함된 프로그램


| 프로그램명 | 한줄 설명 |
| - | - |
| [blueCFD-Core 2024](https://github.com/blueCFD/Core/releases/download/blueCFD-Core-2024-1/blueCFD-Core-2024-1-win64-setup.exe) | Windows용 OpenFOAM(<span title='Computational Fluid Dynamics, 전산유체역학'>CFD 소프트웨어</span>) |
| [Python 3.14.0](https://www.python.org/ftp/python/3.14.0/python-3.14.0-amd64.exe)                                              | 스크립트 작동에 필수적인 프로그래밍 언어 |
| [Visual Studio Code](https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user)                                | 코드 편집기 |
| [Git for Windows](https://github.com/git-for-windows/git/releases/download/v2.51.2.windows.1/Git-2.51.2-64-bit.exe)            | 버전 관리 프로그램 |

<br><br>

## 사용 가이드 목차

1. [프로그램 세팅](#1-프로그램-세팅)
   * Windows용
   * Linux용

2. [시작](#2-시작)
   * 폴더 구조 불러오기

3. [파일 관리](#3-파일-관리)
   * [Update](#update)
   * [Delete](#delete)
   * [Initialize](#initialize)

4. [OpenFOAM](#4-openfoam)
   * [FoamRun](#foamrun)
   * [Parallel FoamRun](#parallel-foamrun)
   * [PostProcessing](#postprocessing)

<br><br><br><br><br>

## 1. 프로그램 세팅

<br>

### **Windows**

>\[OS 버전] 실험자는 **Windows 11** 환경에서 진행하였습니다.

<br>

레포지토리 내 최신 릴리스에서 소스 코드 압축 파일을 다운로드하여 압축해제합니다.

<br>

레포지토리 내 다음 위치의 파일을 실행합니다: ```SetUp\Windows\CFD.bat```

<br>

### **Linux**

>\[OS 버전] 실험자는 Ubuntu 22.04 LTS 환경에서 진행하였습니다.

<br>

레포지토리의 최신 릴리스에서 소스 코드 압축 파일을 다운로드하여 압축해제합니다.

<br>

레포지토리 내 다음 위치의 파일을 실행합니다: ```SetUp\Linux\CFD.sh```

<br><br><br><br><br>

## 2. 시작

<br>

#### 1. <span title='CMD, PowerShell, Linux용 터미널 등'>터미널</span>에서 'CFD' 폴더에 접근합니다. 

'cd' 뒤에 원하는 폴더의 상대경로 또는 절대경로를 붙여 ```cd user``` 등의 형태로 명령어를 사용하여 원하는 폴더에 접근할 수 있습니다.

또는 파일 탐색기에서 'CFD' 폴더에서 우클릭 후 '터미널에서 열기'를 마우스로 선택합니다.

<br>

#### 2. 다음의 명령어를 입력합니다.

이때, Linux 혹은 Mac OS 운영체제의 경우 'python'명령어 대신 'python3' 명령어를 사용합니다.

```terminal

python start.py 

```

실행 직후 'p1','p2','check' 등의 폴더들이 생성될 것입니다. 이것들은 각각 학술제 연구 보고서에 명시된 것과 같은 시뮬레이션 절차를 위한 케이스 디렉토리들입니다. p1은 **P**arametric sweep **1**(1차 파라메트릭 스윕), p2는 2차를 의미하며, 'check'는 1차 파라메트릭 스윕 결과 검증 시뮬레이션 디렉토리입니다.

이 'start.py' 스크립트는 시뮬레이션 환경을 구축하는 셋업 스크립트로, 이를 통해 여러개의 스크립트와 3D 모델의 용량 크기로 인한 디스크 사용 공간을 절약하는 일종의 압축 효과를 얻을 수 있으며, 초기 파일 수를 줄여 사용 편의성을 증대하였습니다.

#### 3. 다음의 명령어로 중앙 제어 스크립트를 실행합니다.

```terminal

python main.py

```

출력되는 메뉴의 입력창에 원하는 작업 또는 디렉토리의 번호를 입력합니다.

<br><br><br><br><br>

## 3. 파일 관리

<br>

#### Update

이 스크립트의 파일 관리 시스템에서 ```update``` 기능은 기본적으로 ```CaseTemplate```디렉토리의 파일들을 기준으로 합니다. 원하는 파일 또는 폴더를 ```CaseTemplate```에 복사한 후 이 ```update``` 기능을 실행하면 모든 케이스 폴더들로 자동 복사/덮어쓰기 됩니다. 케이스의 루트 디렉토리에 있는 파일을 업데이트할 경우 file name을 입력하지 않으며, 케이스의 루트 디렉토리에 있는 폴더를 업데이트할 경우 file을 입력하지 않으면 됩니다.

#### Delete

```delete``` 기능 또한 ```update```와 같은 방식이되, ```CaseTemplate```에 없는 항목이라도 각각의 케이스 디렉토리에서 발견되는 입력 항목들을 모두 제거합니다. 

#### Initialize

```Initialize``` 기능은 각 케이스 폴더의 내용을 모두 초기화하는 기능입니다. ```Ctrl```+```z``` 단축키로 실행 취소 가능한지 확인되지 않았습니다. 신중히 사용하시기 바랍니다.

<br><br><br><br><br>

## 4. OpenFOAM

<br>

여기서부터는 ``` check``` 디렉토리에서도 사용이 가능합니다.

<br>

#### 1. 마찬가지로 터미널을 이용하여 원하는 폴더에 접근 후 ```auto.py``` 스크립트를 실행합니다.

여기서도 원하는 작업의 번호를 입력합니다.

#### 2. ```FoamRun```

이 기능은 기본적인 OpenFOAM 시뮬레이션 실행 자동화 함수입니다. 이 기능을 선택하면 ```Batch Size```를 묻는 입력창이 출력됩니다. 이때 '배치 사이즈'란 동시에 실행할 시뮬레이션 수를 뜻합니다. 이때 다른 작업으로 CPU 자원을 점유하고 있지 않다면 ```기기의 스레드 수 -1``` 또는 ```기기의 스레드 수 -2```를 입력하는 것을 권장합니다.

기기의 스레드 수보다 과하게 많은 수를 선택할 경우 병렬처리 효율이 급감할 수 있을 뿐더러 심각한 경우 시스템 속도가 순간적으로 느려지거나 시스템에 일시적 문제가 생기는 등의 증상이 있을 수 있습니다.

'스레드'란 CPU가 동시에 처리할 수 있는 작업의 수를 뜻합니다. 하이퍼스레딩 기술이 적용된 CPU의 경우 물리 코어 수보다 스레드 수가 많을 수 있습니다. 코어 수와 스레드 수는 Windows에서는 작업 관리자, Linux에서는 system monitor 등을 통하여 확인하실 수 있습니다.

#### 3. ```Parallel FoamRun```

이 기능은 각각의 단일 케이스를 병렬처리하여 작업 효율을 향상하기 위하여 ```FoamRun```을 고급화한 기능입니다. 이 기능을 선택하면 ```Number of Subdomains```와 ```Batch Size```를 묻는 입력창이 출력됩니다. ```Number of Subdomains```는 각각의 단일 케이스를 몇 갈래로 나누어 병렬처리할지를 묻는 입력창입니다. 이때도 두 입력창의 입력값의 곱이 기기의 스레드 수보다 1~2개 적은 값을 권장합니다. 

#### 4. ```PostProcessing```

이 기능을 통하여 FoamRun 계통의 기능들의 결과로 얻어진 ```forces.dat``` 파일을 파싱하여 엑셀, 그래프로 변환할 수 있습니다. 파이썬으로 만들어서 아무래도 느립니다. 생성된 그래프와 엑셀파일들은 ```CFD```폴더 루트에 저장되며, 이후의 정리는 사용자의 몫입니다. 

<br><br><br><br><br>
## **라이선스**

***License***

<br>

이 프로젝트는 GNU 일반 공중 사용 허가서 버전 3(GPL v3.0)에 따라 배포됩니다. <br>자세한 내용은 [LICENSE](./LICENSE) 파일을 참고하세요.

This project is licensed under the GNU General Public License v3.0 <br> see the [LICENSE](./LICENSE) file for details.

<br><br><br><br><br>
