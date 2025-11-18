@echo off
winget install -e --id Python.Python.3.14
winget install -e --id Git.Git
winget install -e --id Microsoft.VisualStudioCode
winget install -e --id bluecfd.bluecfd
start "" py ".\PATH.py"
pause