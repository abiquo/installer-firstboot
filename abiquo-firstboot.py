#!/usr/bin/python

from snack import *
import sys,os
import socket
import signal
import commands
import fileinput
import ConfigParser


def signal_handler(signal, frame):
  print 'You pressed Ctrl+C!'
  sys.exit(0)

def check_api_url(url):
    if "http://" in url:
      try:
        s = socket.inet_aton(url.split("http://")[1].split("/")[0])
        return True
      except socket.error:
        pass
    return False

def check_nfs_url(url):
    if ":/" in url:
      try:
        s = socket.inet_aton(url.split(":/")[0])
        return True
      except socket.error:
        pass
    return False

def mount_nfs_url(url):
    pass

def set_nfs_url(url):
  fstab_path = "/etc/fstab"
  if os.path.exists(fstab_path):
    # Check this before
    with open(fstab_path,"r+a") as f:
      for line in f:
        if '/opt/vm_repository' in line:
          return
      f.write(url+'  /opt/vm_repository nfs    defaults        0 0\n')

def set_api_url(url):
  conf_path = '/var/www/html/ui/config/client-config.json'
  if os.path.exists(conf_path):
    f = fileinput.FileInput(conf_path,inplace=1)
    for line in f:
        line = line.replace("http://localhost/api",url)
        print line.rstrip()
    f.close()

def set_dc_id(dcid):
  config = ConfigParser.ConfigParser()
  conf_path = '/opt/abiquo/config/abiquo.properties'
  if os.path.exists(conf_path):
    config.readfp(open(conf_path))
    config.set('remote-services', 'abiquo.datacenter.id', dcid)
    config.write(open(conf_path,'wb'))

def set_https():
    passres

def detect_public_ip():
  try:
    # Warning: Not working in all linuxes.
    ip = commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:]
    s = socket.inet_aton(ip)
    return ip
  except socket.error:
    return False


class NfsWindow:
    def __init__(self,screen):
        self.defaulturl = "<nfs-ip>:/opt/vm_repository"
        self.screen = screen
        self.label = Label('NFS repository:')
        self.entry = Entry(33,self.defaulturl)
        self.text = TextboxReflowed(50,"Some helper text.\n Enter your NFS repository URL.\n")
        self.topgrid = GridForm(self.screen, "NFS Repository", 1, 3)
        self.topgrid.add(self.text,0,0,(0, 0, 0, 1))
        self.grid = Grid(2, 1)
        self.grid.setField (self.label, 0, 0, (0, 0, 1, 0), anchorLeft = 1)
        self.grid.setField (self.entry, 1, 0)
        self.topgrid.add (self.grid, 0, 1, (0, 0, 0, 1))
        self.bb = ButtonBar (self.screen, ["OK","Cancel"],compact=1)
        self.topgrid.add (self.bb, 0, 2, growx = 1)

    def run(self):
        self.topgrid.setCurrent(self.entry)
        result = self.topgrid.run()
        rc = self.bb.buttonPressed(result)
        if rc == "cancel":
            return -1
        if not check_nfs_url(self.entry.value()):
            self.defaulturl = self.entry.value()
            ButtonChoiceWindow(self.screen,"URL incorrect","Please enter a URL with the form:\n <ip>:<mountpoint>",buttons = ["OK"], width = 50)
        else:
            self.defaulturl = self.entry.value()
            set_nfs_url(self.defaulturl)
            return 0

class ApiWindow:
    def __init__(self,screen):
        ip = detect_public_ip()
        if ip:
          self.defaulturl = 'http://'+ip+'/api'
        else:
          self.defaulturl = "http://<endpoint-ip>/api"
        self.screen = screen
        self.label = Label('API endpoint:')
        self.entry = Entry(33,self.defaulturl)
        self.text = TextboxReflowed(50,"Enter API endpoint.\nThis URL should be reachable by the client browser.\n")
        self.topgrid = GridForm(self.screen, "API endpoint", 1, 3)
        self.topgrid.add(self.text,0,0,(0, 0, 0, 1))
        self.grid = Grid(2, 1)
        self.grid.setField (self.label, 0, 0, (0, 0, 1, 0), anchorLeft = 1)
        self.grid.setField (self.entry, 1, 0)
        self.topgrid.add (self.grid, 0, 1, (0, 0, 0, 1))
        self.bb = ButtonBar (self.screen, ["OK","Cancel"],compact=1)
        self.topgrid.add (self.bb, 0, 2, growx = 1)

    def run(self):
        self.topgrid.setCurrent(self.entry)
        result = self.topgrid.run()
        rc = self.bb.buttonPressed(result)
        if rc == "cancel":
            return -1
        if not check_api_url(self.entry.value()):
            ButtonChoiceWindow(self.screen,"URL incorrect","Please enter a URL with the form:\n http://<endpoint-ip>/api",buttons = ["OK"], width = 50)
            self.screen.popWindow()
        else:
            self.defaulturl = self.entry.value()
            set_api_url(self.entry.value())
            return 0

class DCWindow:
    def __init__(self,screen):
        self.defaultdc = "Abiquo"
        self.screen = screen
        self.label = Label('Datacenter name:')
        self.entry = Entry(33,self.defaultdc)
        self.text = TextboxReflowed(50,"Enter Datacenter ID for your set of remote services.\n")
        self.topgrid = GridForm(self.screen, "Datacenter name", 1, 3)
        self.topgrid.add(self.text,0,0,(0, 0, 0, 1))
        self.grid = Grid(2, 1)
        self.grid.setField (self.label, 0, 0, (0, 0, 1, 0), anchorLeft = 1)
        self.grid.setField (self.entry, 1, 0)
        self.topgrid.add (self.grid, 0, 1, (0, 0, 0, 1))
        self.bb = ButtonBar (self.screen, ["OK","Cancel"],compact=1)
        self.topgrid.add (self.bb, 0, 2, growx = 1)

    def run(self):
        self.topgrid.setCurrent(self.entry)
        result = self.topgrid.run()
        rc = self.bb.buttonPressed(result)
        if rc == "cancel":
            return -1
        else:
            self.defaultdc = self.entry.value()
            set_dc_id(self.entry.value())
            return 0

class HTTPSWindow:
    def __init__(self,screen):
        self.screen = screen
        self.bc = ButtonChoiceWindow(self.screen,"HTTPS ","Do you want to enable secure SSL front-end?",buttons = ["No","Yes"], width = 50)

    def run(self):
        self.bc.setCurrent(self.entry)
        result = self.bc.run()
        rc = self.bb.buttonPressed(result)
        if rc == "No":
            return 
        else:
            set_https()
            # Generate certs and set HTTPS
            return 0

# Password is set in anaconda, not needed at firstboot.
class AdminPasswordWindow:
    def __init__(self,screen):
        self.defaultpw = "xabiquo"
        self.screen = screen
        self.passlabel1 = Label('Enter Password:')
        self.passlabel2 = Label('Repeat Password:')
        self.passfield = Entry(15,self.defaultpw, password = 1)
        self.passconfirm = Entry(15,self.defaultpw, password = 1)
        self.text = TextboxReflowed(50,"Some helper text.\n Enter your abiquo cloud admin password.\n Default: xabiquo")
        self.topgrid = GridForm(self.screen, "Enter Admin password", 1, 3)
        self.topgrid.add(self.text,0,0,(0, 0, 0, 1))
        self.passgrid = Grid(2, 2)
        self.passgrid.setField (self.passlabel1, 0, 0, (0, 0, 1, 0), anchorLeft = 1)
        self.passgrid.setField (self.passlabel2, 0, 1, (0, 0, 1, 0), anchorLeft = 1)
        self.passgrid.setField (self.passfield, 1, 0)
        self.passgrid.setField (self.passconfirm, 1, 1)
        self.topgrid.add (self.passgrid, 0, 1, (0, 0, 0, 1))
        self.bb = ButtonBar (self.screen, ["OK","Cancel"], compact=1)
        self.topgrid.add (self.bb, 0, 2, growx = 1)

    def run(self):
        self.topgrid.setCurrent(self.passfield)
        result = self.topgrid.run()
        rc = self.bb.buttonPressed(result)
        if rc == "cancel":
            return -1
        if len(self.passfield.value ()) < 6:
            ButtonChoiceWindow(self.screen,"Password Length","The root password must be at least 6 characters long.",buttons = ["OK"], width = 50)
        elif self.passfield.value () != self.passconfirm.value():
                ButtonChoiceWindow(self.screen, "Password Mismatch","The passwords you entered were different. Please try again.", buttons = ["OK"], width = 50)
        else:
            self.defaultpw = self.passfield.value()
            # Replace password in schema (TODO, not needed in postinstall)
            return 0

class mainWindow:
    def __init__(self):

        # fetch profiles from /etc/abiquo-installer
        profiles = ""
        if os.path.os.path.exists("/etc/abiquo-installer"):
          try:
            profiles = eval(open("/etc/abiquo-installer", "r").readline().split(": ")[1])
          except:
            print "Error: Cannot read profiles."
            exit(1)
        else:
          screen.finish()
          print "Error: No abiquo profiles detected."
          exit(1)

        screen = SnackScreen()
        # Attempt to handle signal for Control+C
        signal.signal(signal.SIGINT, signal_handler)       

        #  Abiquo colors theme
        screen.setColor('ROOT','yellow','black')
        screen.setColor('SHADOW','black','black')
        screen.setColor('TITLE','black','white')
        screen.setColor('ENTRY','black','yellow')
        screen.setColor('LABEL','black','white')
        screen.setColor('WINDOW','black','white')
        screen.setColor('BUTTON','yellow','black')
        screen.setColor('ACTBUTTON','yellow','black')
        screen.setColor('HELPLINE','yellow','black')
        screen.setColor('ROOTTEXT','yellow','black')
        """ Reference:
        colorsets = { "ROOT" : _snack.COLORSET_ROOT,
              "BORDER" : _snack.COLORSET_BORDER,
              "WINDOW" : _snack.COLORSET_WINDOW,
              "SHADOW" : _snack.COLORSET_SHADOW,
              "TITLE" : _snack.COLORSET_TITLE,
              "BUTTON" : _snack.COLORSET_BUTTON,
              "ACTBUTTON" : _snack.COLORSET_ACTBUTTON,
              "CHECKBOX" : _snack.COLORSET_CHECKBOX,
              "ACTCHECKBOX" : _snack.COLORSET_ACTCHECKBOX,
              "ENTRY" : _snack.COLORSET_ENTRY,
              "LABEL" : _snack.COLORSET_LABEL,
              "LISTBOX" : _snack.COLORSET_LISTBOX,
              "ACTLISTBOX" : _snack.COLORSET_ACTLISTBOX,
              "TEXTBOX" : _snack.COLORSET_TEXTBOX,
              "ACTTEXTBOX" : _snack.COLORSET_ACTTEXTBOX,
              "HELPLINE" : _snack.COLORSET_HELPLINE,
              "ROOTTEXT" : _snack.COLORSET_ROOTTEXT,
              "EMPTYSCALE" : _snack.COLORSET_EMPTYSCALE,
              "FULLSCALE" : _snack.COLORSET_FULLSCALE,
              "DISENTRY" : _snack.COLORSET_DISENTRY,
              "COMPACTBUTTON" : _snack.COLORSET_COMPACTBUTTON,
              "ACTSELLISTBOX" : _snack.COLORSET_ACTSELLISTBOX,
              "SELLISTBOX" : _snack.COLORSET_SELLISTBOX }  """
        

        # Title
        if os.path.exists("/etc/system-release"):
          release = open("/etc/system-release", "r").readline()
          screen.drawRootText(0, 0, release)

        # NFS Repository window
        DONE = 0
        if ('abiquo-monolithic' or 'abiquo-kvm' or 'abiquo-remote-services' in profiles) \
            and not ('abiquo-nfs-repository' in profiles):
          while not DONE:
            self.win = NfsWindow(screen)
            rc = self.win.run()
            if rc == -1:
              screen.popWindow()
              DONE = 1
            elif rc == 0:
              screen.popWindow()
              DONE = 1
            
        # API endpoint 
        DONE = 0
        if ('abiquo-ui-standalone' or 'abiquo-monolithic' or 'abiquo-server' in profiles):
          # Loop until NFS steps done.
          while not DONE:
            self.win = ApiWindow(screen)
            rc = self.win.run()
            if rc == -1:
              screen.popWindow()
              DONE = 1
            elif rc == 0:
              screen.popWindow()
              DONE = 1

        # Datacenter ID (Server, V2V, Public Cloud, )
        DONE = 0
        if ('abiquo-v2v' or 'abiquo-server' or 'abiquo-remote-services' or 'abiquo-public-services' in profiles):
          # Loop until NFS steps done.
          while not DONE:
            self.win = DCWindow(screen)
            rc = self.win.run()
            if rc == -1:
              screen.popWindow()
              DONE = 1
            elif rc == 0:
              screen.popWindow()
              DONE = 1
     
        # RS IP (KVM)
        # SSL Selection
        # DHCP relay (?)
        # NFS + Monolithic -> abiquo.appliancemanager.checkMountedRepository = false
        screen.popWindow()
        screen.finish()
        # Also clean terminal


if __name__ == "__main__":

    ret = mainWindow()
