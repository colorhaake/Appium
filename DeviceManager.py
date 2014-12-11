import subprocess
import re
import time
from AppiumEnv import AppiumEnv
from AppiumParameters import AppiumParameters

class Device:
    def __init__(self):
        self.platform = ''
        self.name = ''
        self.device = ''
        self.version = ''
        self.sdcard = ''
        self.uuid = ''
        
        self.launch = False
        self.used = False
        self.usedFrom = ''
        
class DeviceManager:
    def __init__(self):
        self.device_list = []
        self.list_AVD()
        self.list_iOS_emulators()
        
    def list_AVD(self):
        cmd = "android list avd"
        print "command: " + cmd

        output = subprocess.Popen(cmd, shell=True, env=AppiumEnv.appium_env, stdout=subprocess.PIPE)
        output, err = output.communicate()

        print "output : " + output
        
        
        # parse device info
        # divided into lines
        device = Device()
        port = 5554
        for line in output.splitlines():
            tokens = line.split(":")
            
            # find keyword
            if tokens[0].strip() == "Name":
                # add device
                device = Device()
                device.platform = AppiumParameters.PLATFORM_ANDROID
                device.uuid = "emulator-" + str(port)
                port += 2
                self.device_list.append(device)
                
                device.name = tokens[1].strip()
            elif tokens[0].strip() == "Device":
                device.device = tokens[1].strip()
                
            elif tokens[0].strip() == "Target":
                matchObj = re.match( r'(\d+(?:\.\d+)+)', tokens[1].strip())
                if matchObj:
                    device.version = matchObj.group()
            elif tokens[0].strip() == "Sdcard":
                device.sdcard = tokens[1].strip()
    def list_iOS_emulators(self):
        pass
    
               
    def get_target_devices(self, platformName, target_version, usedFrom):
        # get devices from current launch devices
        target_devices = self.get_target_devices_from_launch_devices(platformName, target_version)
        
        # check if is already in device list or not
        for i in target_devices:
            found = False
            for j in self.device_list:
                if i.uuid == j.uuid:
                    found = True
                    if j.used == False:
                        j.used = True
                        j.usedFrom = usedFrom
                        return j
            if found is False:
                i.used = True
                i.usedFrom = usedFrom
                self.device_list.append(i)
                return i
            
        # get devices from device list
        for i in self.device_list:
            if i.version == target_version and i.used == False:
                if i.launch == False:
                    self.launch_device(i)
                
                i.used = True
                i.usedFrom = usedFrom
                return i
        
        return None
    
    def launch_device(self, device):
        if device.platform == AppiumParameters.PLATFORM_ANDROID:
            self.launch_android_device(device)
        if device.platform == AppiumParameters.PLATFORM_IOS:
            pass
    
    def launch_android_device(self, device):
        # launch android emulator
        cmd = "emulator -avd " + device.name
        print "command: " + cmd

        output = subprocess.Popen(cmd, shell=True, env=AppiumEnv.appium_env, stdout=subprocess.PIPE)
        output, err = output.communicate()

        print "output : " + output
        
        
        # Wait for launching
        MAX_WAIT_TIME = 60
        wait_time = 0
        check_time = 5
        launch = None
        restart_adb_server = False
        
        while not launch and wait_time < MAX_WAIT_TIME: 
            launch = self.check_android_emulator_launch(device)
            # restart adb server (sometimes adb cannot get the new opening device)
            if launch is None and restart_adb_server == False and wait_time > MAX_WAIT_TIME/3:
                self.restart_adb_server()
                restart_adb_server = True
                
            wait_time += check_time
            time.sleep(check_time)
        
    def check_android_emulator_launch(self, device):
        cmd = "adb -s " + device.uuid + " shell getprop init.svc.bootanim"
        print "command: " + cmd

        output = subprocess.Popen(cmd, shell=True, env=AppiumEnv.appium_env, stdout=subprocess.PIPE)
        output, err = output.communicate()

        print "output : " + output
        
        if "stopped" in output:
            return True
        
        if "device not found" in output:
            return None
        
        # offline
        return False
    
    def restart_adb_server(self):
        
        # adb kill-server
        # adb start-server
    
        cmd = "adb kill-server"
        print "command: " + cmd

        output = subprocess.Popen(cmd, shell=True, env=AppiumEnv.appium_env, stdout=subprocess.PIPE)
        output, err = output.communicate()

        print "output : " + output
        
        cmd = "adb start-server"
        print "command: " + cmd

        output = subprocess.Popen(cmd, shell=True, env=AppiumEnv.appium_env, stdout=subprocess.PIPE)
        output, err = output.communicate()

        print "output : " + output       
        
    def get_target_devices_from_launch_devices(self, platformName, target_version):
        if platformName == AppiumParameters.PLATFORM_ANDROID:
            return self.get_target_devices_from_android_launch_devices(target_version)
        
        elif platformName == AppiumParameters.PLATFORM_IOS:
            return self.get_target_devices_from_ios_launch_devices(target_version)
        
        return None
    
    def get_target_devices_from_android_launch_devices(self, target_version):
        cmd = "adb devices"
        print "command: " + cmd

        output = subprocess.Popen(cmd, shell=True, env=AppiumEnv.appium_env, stdout=subprocess.PIPE)
        output, err = output.communicate()

        print "output : " + output
        
        
        target_device_list = []
        # get device info
        # e.g. : 
        # List of devices attached 
        # emulator-5554    device
        for line in output.splitlines()[1:]: # pass List of devices attached
            device = Device()
            device.launch = True
            
            # platform
            device.platform = AppiumParameters.PLATFORM_ANDROID
            
            # uuid
            tokens = line.split("\t")
            uuid = tokens[0]
            device.uuid = uuid
            
            # version
            cmd = "adb -s " + uuid + " shell getprop ro.build.version.release"
            print "command: " + cmd
    
            output = subprocess.Popen(cmd, shell=True, env=AppiumEnv.appium_env, stdout=subprocess.PIPE)
            output, err = output.communicate()
    
            print "output : " + output
            device.version = output.strip()   
            
            # check version match
            if device.version == target_version:
                target_device_list.append(device)
            else:
                continue
            
            # device name
            cmd = "adb -s " + uuid + " shell getprop ro.product.name"
            print "command: " + cmd
    
            output = subprocess.Popen(cmd, shell=True, env=AppiumEnv.appium_env, stdout=subprocess.PIPE)
            output, err = output.communicate()
    
            print "output : " + output
            device.name = output.strip()
            
            # model name
            cmd = "adb -s " + uuid + " shell getprop ro.product.model"
            print "command: " + cmd
    
            output = subprocess.Popen(cmd, shell=True, env=AppiumEnv.appium_env, stdout=subprocess.PIPE)
            output, err = output.communicate()
    
            print "output : " + output
            device.device = output.strip()        
            
            # sdcard: not implemented
        
        return target_device_list
    def get_target_devices_from_ios_launch_devices(self, target_version):
        return None