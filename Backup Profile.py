import tkinter as tk 
import multiprocessing as mp
import subprocess
import win32security, win32con #impersonation
import shutil, errno, os
import ctypes #Message Boxes
import time
import sys

class Impersonate:
    def __init__(self, login, password):
        self.domain = 'DOMAIN' 
        self.login = login
        self.password = password

    def logon(self):
        self.handle = win32security.LogonUser(self.login, self.domain,
            self.password, win32con.LOGON32_LOGON_INTERACTIVE,
            win32con.LOGON32_PROVIDER_DEFAULT)
        win32security.ImpersonateLoggedOnUser(self.handle)
            
    def logoff(self):
        win32security.RevertToSelf(  ) # Terminates impersonation
        self.handle.Close(  ) # Guarantees cleanup

def Copy(computer, newComputer, user, admin, password):
    
    adminSession = Impersonate(admin, password)
    userFolders = {'Desktop','Documents', 'Favorites', 'Links', 'Pictures', 'Videos', 'AppData/Roaming/Microsoft'}
    i = 0
    
    try:
        adminSession.logon() 
        if user is not 'Public':
            for folder in userFolders:
                src = r"//"+ computer + r'/c$/Users/'+ user + r"/" + folder
                if 'Microsoft' in folder:
                    folder = 'Microsoft'
                dest = r"//" + newComputer + r'/c$' + r"/" + computer + '-' + newComputer + r"/" + user + r"/" + folder
                try:
                    shutil.copytree(src, dest)
                except OSError as e:
                    if e.errno == errno.ENOTDIR: # If the error was caused because the source wasn't a directory
                        shutil.copy(src, dest)
                    elif e.winerror != None:
                        if e.winerror == 183:
                            #print(folder + ' already copied.')
                            pass
                        elif e.winerror == 3:
                            if 'Public' not in src: print(src + ' was not copied. Error: %s' % e.strerror)   
                        else:
                            print(src + ' was not copied. Error: %s' % e.strerror)
                finally:
                    i += 100/len(userFolders)
                    sys.stdout.write('\rTransferring '  + computer + '/' + user + ' to ' + newComputer + ':%d%%' % (i))
                    
                    if int(i) == 100:
                        sys.stdout.write('\n')
                    else:
                        sys.stdout.flush()
                        
                        
    finally:
        adminSession.logoff() # Ensure return-to-normal no matter what

class App(tk.Frame):
    def __init__(self, master = None):
        
        super().__init__(master)
        self.master = master
        master.title('Backup Profile')
        self.pack(fill='both', expand=True)
        self.Widgets()
        self.configure(background='alice blue')
        self.checkboxes =[]
        self.userList = dict()
        
    def Widgets(self):
        
        self.adminLabel=tk.Label(self, text='Admin Account', bg = 'alice blue')
        self.adminLabel.grid(row=0, column=0, sticky = 'W')
        self.adminEntry=tk.Entry(self)
        self.adminEntry.grid(row=0, column=1, sticky = 'W')

        self.passwordLabel=tk.Label(self, text='Admin Password', bg = 'alice blue')
        self.passwordLabel.grid(row=1, column=0, sticky = 'W')
        self.passwordEntry=tk.Entry(self, show = "*")
        self.passwordEntry.grid(row=1, column=1, sticky = 'W')

        self.computerLabel=tk.Label(self, text='Old Computer', bg = 'alice blue')
        self.computerLabel.grid(row=2, column=0, sticky = 'W')
        self.computerEntry=tk.Entry(self)
        self.computerEntry.grid(row=2, column=1, sticky = 'W')

        self.newComputerLabel=tk.Label(self, text='New Computer', bg = 'alice blue')
        self.newComputerLabel.grid(row=3, column=0, sticky = 'W')
        self.newComputerEntry=tk.Entry(self)
        self.newComputerEntry.grid(row=3, column=1, sticky = 'W')

        self.daysLabel=tk.Label(self, text='Check X days', bg = 'alice blue')
        self.daysLabel.grid(row=4, column=0, sticky = 'W')
        self.daysEntry=tk.Entry(self)
        self.daysEntry.grid(row=4, column=1, sticky = 'W')
        self.daysEntry.insert(0, '30')

        backupButton=tk.Button(self,text="Backup", width = 16, bg = 'SpringGreen2')
        backupButton['command']= lambda: self.StartTransfer(self.adminEntry.get(), self.passwordEntry.get(), self.computerEntry.get().strip(), self.newComputerEntry.get().strip())
        backupButton.grid(row=6,column=0, sticky = 'W')

        getUsersButton=tk.Button(self,text="Get Users", width = 16, bg = 'SkyBlue1')
        getUsersButton['command']= lambda: self.FilterUsers( self.adminEntry.get(), self.passwordEntry.get(), self.computerEntry.get().strip(), self.daysEntry.get())
        getUsersButton.grid(row=6,column=1, sticky = 'W')

    def FilterUsers(self, admin, password, computerName, days):
        
        adminSession = Impersonate(admin, password)
        pingTest = subprocess.call("ping -n 1 " + computerName, creationflags=8)
        allFolders = []
        
        defaultFilter = ['All Users', 'Default', 'Default User', 'defaultuser0']
        adminFilter = ['a-','a2-','A-','A2-']
        timeFilter = time.time() - (int(days)*86400) #Transform days to seconds

        if pingTest == 0:
            try:
                adminSession.logon()
                for (dirpath, dirnames, filenames) in os.walk(r"//"+ computerName + r"/c$/Users"):
                    allFolders.extend(dirnames)
                    break
                allFolders = [ x for x in allFolders if x not in defaultFilter ] #Filters folders out
                allFolders = [s for s in allFolders if not any(word in s for word in adminFilter)]
                
                for i in allFolders: 
                    if os.path.getmtime(r"//"+ computerName + r"/c$/Users/" + str(i)) < timeFilter:
                        allFolders.remove(i)
                allFolders.append('Public') #Probably there's a better way to do this
                self.CreateBoxes(allFolders)
                adminSession.logoff()
            except:
                ctypes.windll.user32.MessageBoxW(0, "Invalid credentials.", "ERROR", 0) 
        else:
            ctypes.windll.user32.MessageBoxW(0, computerName + " is offline.", "ERROR", 0)

    def CreateBoxes(self, folders):
        
        for chk in self.checkboxes:
            chk.destroy()
            
        self.checkboxes.clear()
        self.userList.clear()
        xAxis=0
        yAxis=0
        
        for i in folders:
            self.userList[i] = tk.IntVar()
            chk = tk.Checkbutton(self, text=str(i), variable=self.userList[i], bg = 'alice blue')
            self.checkboxes.append(chk)
            if xAxis % 10 == 0 and xAxis != 0:
                xAxis -= 10
                yAxis += 1
            chk.grid(row = 7 + xAxis, column = 0 + yAxis, sticky = 'W')
            xAxis += 1

    def StartTransfer(self, admin, password, computer, newComputer):

        pingTest = subprocess.call("ping -n 1 " + newComputer, creationflags=8)
        processes = []
        
        if pingTest == 0:
            for user in self.userList:
                if (self.userList.get(user)).get() == 1:
                    processes.append(mp.Process(target = Copy, args = [computer, newComputer, user, admin, password]))
            [proc.start() for proc in processes]
        else:
            ctypes.windll.user32.MessageBoxW(0, "New computer is offline", "ERROR", 0)

if __name__ == '__main__':
    root = tk.Tk()
    app = App(master = root)
    root.mainloop()
