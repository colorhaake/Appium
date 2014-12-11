import subprocess
from AppiumEnv import AppiumEnv

class AppiumServer:
    def __init__(self):
        self.server = ''
        self.port = ''
        self.window_id = ''
        self.device = ''
        
class AppiumServerManager:
    def __init__(self):
        self.appium_server_list = []
    
    def launch_server(self, address, port, device):
        
        # Open Terminal and launch appium server ( appium -p 4723 -U emulator-5562 )        
        cmd = """osascript -e 'tell application "Terminal"
            activate
            do script "appium -p """ + port + """ -U """ + device.uuid + """ 
        end tell'"""
        print "command: " + cmd
        
        output = subprocess.Popen(cmd, shell=True, env=AppiumEnv.appium_env, stdout=subprocess.PIPE)
        output, err = output.communicate()
        
        print "output : " + output
        
        # get window id
        # e.g.: tab 1 of window id 4564
        key = "window id"
        key_loc = output.find(key)
        window_id = output[key_loc+len(key)+1:].strip()
        
        print "window id : " + window_id 
        
        appium_server = AppiumServer()
        appium_server.server = address
        appium_server.port = port
        appium_server.device = device
        appium_server.window_id = window_id
        
        self.appium_server_list.append(appium_server)
        
    def close_server(self, address, port):
        appium_server = ''
        # find server from appium server list
        for i in self.appium_server_list:
            usedFrom = address + ":" + port
            
            if i.device.usedFrom == usedFrom:
                appium_server = i
                break
        
        if not appium_server:
            return "Cannot find the appium server"
        
        # Close Terminal
        cmd = """osascript -e 'tell application "Terminal"
            close (every window whose id is """ + appium_server.device.window_id + """)
            tell application "System Events" to tell process "Terminal" to keystroke return
            end tell'"""
        print "command: " + cmd
        
        output = subprocess.Popen(cmd, shell=True, env=AppiumEnv.appium_env, stdout=subprocess.PIPE)
        output, err = output.communicate()
        
        print "output : " + output
        
        appium_server.device.used = False
        self.appium_server_list.remove(appium_server)