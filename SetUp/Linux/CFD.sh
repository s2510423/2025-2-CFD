sudo apt update
sudo apt install python3 git wget gpg

wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
rm -f packages.microsoft.gpg

sudo apt install -y openfoam
sudo apt install -y code
source /opt/openfoam*/etc/bashrc
echo "source /opt/openfoam*/etc/bashrc" >> ~/.bashrc
