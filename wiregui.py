import os
import subprocess
from tkinter import *
from tkinter import filedialog

class Application():
    def __init__(self):
        self.root = Tk()
        self.wireguardDirectory = "/etc/wireguard"
        self.screen()
        self.frame()
        self.root.mainloop()
    
    def screen(self):
        self.root.title("wiregui")
        self.root.configure(background="#B71C1C")
        self.root.geometry("500x350")
        self.root.resizable(False, False)

    def frame(self):
        self.frameBackgroundColor = "#FFCDD2"
        self.frame1 = Frame(self.root, bd=4, bg=self.frameBackgroundColor, highlightbackground="#F44336", highlightthickness=3)
        self.frame1.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)

        self.password = None
        self.vpnName = "Selecione uma VPN"

        self.checkLogin()
        

    def checkLogin(self):
        if not self.isSudo():
            if not self.password and not hasattr(self, 'passwordLabel'):
                self.passwordLabel = Label(self.root, text="Senha do Sudo", bg=self.frameBackgroundColor)
                self.passwordLabel.pack(pady=(20,0))

                self.passwordInput = Entry(self.root, show="*", bg="white")
                self.passwordInput.pack(pady=(5,0))

                self.accessButton = Button(self.frame1, text="Acessar", command=self.definePassword, bg="#81C784")
                self.accessButton.pack(pady=(60,0))

            if not self.password:
                self.root.after(100, self.checkLogin)
            elif not self.validateSudoPassword():
                self.root.after(100, self.checkLogin)
                self.password = None
            else:
                self.passwordLabel.pack_forget()
                self.passwordInput.pack_forget()
                self.accessButton.pack_forget()
                self.vpnSelector()
        else:
            self.password = ""
            self.vpnSelector()
    
    def vpnSelector(self):
        self.defineVpnList()

        self.createUploadFileButton()

        self.createSelectVpnDropdown()

        self.createActivateButton()

        self.createDeactivateButton()

        self.createVpnStatusViewer()        

        self.vpnStatus()

    def createUploadFileButton(self):
        self.uploadFileButton = Button(self.frame1, text="Adicionar configuração", command=self.uploadFile, bg="#64B5F6")
        self.uploadFileButton.pack(pady=(5,0))

    def createSelectVpnDropdown(self):
        self.selectVpnLabel = StringVar()
        self.selectVpnLabel.set(self.vpnName)
        self.selectVpnDropdown = OptionMenu(self.frame1, self.selectVpnLabel, *self.listOfVpns, command=self.selectVpn)
        self.selectVpnDropdown.pack(pady=(5,0))
        self.selectVpnDropdownIsCreated = True

    def createActivateButton(self):
        self.activateButton = Button(self.frame1, text="Ativar", command=self.activateVpn, bg="#81C784")
        self.activateButton.pack(pady=(5,0))
        self.activateButtonIsCreated = True

    def createDeactivateButton(self):
        self.deactivateButton = Button(self.frame1, text="Desativar", command=self.deactivateVpn, bg="#E57373")
        self.deactivateButton.pack(pady=(5,0))
        self.deactivateButtonIsCreated = True

    def createVpnStatusViewer(self):
        self.vpnStatusBody = StringVar()

        self.vpnStatusViewer = Label(self.root, textvariable=self.vpnStatusBody, bg=self.frameBackgroundColor)
        self.vpnStatusViewer.pack(pady=(100,0))
        self.vpnStatusViewerIsCreated = True

    def uploadFile(self):
        path = filedialog.askopenfilename()
        fileName = os.path.basename(path)
        if fileName.endswith(".conf") and fileName not in self.listOfVpns:
            self.copyFileWithSudo(path, self.wireguardDirectory)
            self.defineVpnList()
            self.selectVpnDropdown.pack_forget()
            self.activateButton.pack_forget()
            self.createSelectVpnDropdown()
            self.createActivateButton()

        

    def defineVpnList(self):
        self.listOfVpns = ["Selecione uma VPN"]

        if self.pathExistsWithSudo(self.wireguardDirectory):
            itens = self.listDirWithSudo(self.wireguardDirectory)
            
            if itens:
                for item in itens:
                    if item.endswith(".conf"):
                        name = item.replace(".conf", "")
                        self.listOfVpns.append(name)


    def definePassword(self):
        self.password = self.passwordInput.get()

    def selectVpn(self, event):
        self.vpnName = self.selectVpnLabel.get()

    def vpnStatus(self):
        cmd = f"sudo wg show"
        p = subprocess.Popen(['sudo', '-S', *cmd.split()], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        body = p.communicate(input=(self.password + '\n'))[0]

        if body:
            if not self.deactivateButtonIsCreated:
                self.createDeactivateButton()
                self.createVpnStatusViewer()
            self.selectVpnDropdown.pack_forget()
            self.selectVpnDropdownIsCreated = False
            self.activateButton.pack_forget()
            self.activateButtonIsCreated = False
        elif not self.activateButtonIsCreated:
            self.createSelectVpnDropdown()
            self.createActivateButton()
            
        if not body:
            if not self.activateButtonIsCreated:
                self.createSelectVpnDropdown()
                self.createActivateButton()
            self.deactivateButton.pack_forget()
            self.deactivateButtonIsCreated = False
            self.vpnStatusViewer.pack_forget()
            self.vpnStatusViewerIsCreated = False

        self.vpnStatusBody.set(body)
        self.root.after(100, self.vpnStatus)

    def activateVpn(self):
        if self.vpnName != "Selecione uma VPN":
            cmd = f"sudo wg-quick up {self.vpnName}"
            if self.isSudo():
                os.system(cmd)
            else:
                p = subprocess.Popen(['sudo', '-S', *cmd.split()], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                p.communicate(self.password + '\n')

    def deactivateVpn(self):
        for vpnName in self.listOfVpns:
            if vpnName != "Selecione uma VPN":
                cmd = f"sudo wg-quick down {vpnName}"
                if self.isSudo():
                    os.system(cmd)
                else:
                    p = subprocess.Popen(['sudo', '-S', *cmd.split()], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    p.communicate(self.password + '\n')

    def copyFileWithSudo(self, sourcePath, destinationPath):
        command = f"sudo cp {sourcePath} {destinationPath}"
        p = subprocess.Popen(command, stdin=subprocess.PIPE, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        p.communicate(input=self.password + '\n', timeout=5)

    def listDirWithSudo(self, path):
        try:
            command = ['sudo', 'ls', path]
            p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            output, error = p.communicate(input=self.password + '\n', timeout=5)

            if p.returncode == 0:
                contents = output.splitlines()
                return contents
            else:
                return None
        except subprocess.CalledProcessError as e:
            return None

    def pathExistsWithSudo(self, path):
        try:
            command = ['sudo', 'test', '-d', path]
            p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            p.communicate(input=self.password + '\n', timeout=5)

            return p.returncode == 0
        except subprocess.CalledProcessError:
            return False

    def validateSudoPassword(self):
        try:
            command = ['sudo', '-S', 'echo', 'Success']
            p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            output, error = p.communicate(input=self.password + '\n', timeout=5)

            return p.returncode == 0 and 'Success' in output
        except subprocess.TimeoutExpired:
            return False

    def isSudo(self):
        return os.geteuid() == 0


Application()