import json
from DeviceManager import DeviceManager
from AppiumServerManager import AppiumServerManager

class AppiumServerLauncher:
    def __init__(self):
        self.device_manager = DeviceManager()
        self.appium_server_manager = AppiumServerManager()
        
    def execute_server(self, server_info):
        
        # decoded command
        decoded_info = json.loads(server_info)
        cmd = decoded_info['command']
        print "Execute server command : " + cmd
        
        # execute command
        if cmd == 'launch':
            return self.launch_server(server_info)
        elif cmd == 'close':
            return self.close_server(server_info)
        
        return "Error : wrong command for executing server"

    def launch_server(self, server_info):
        
        # decoded server info
        if self.decoded_server_info(server_info) is False:
            return "Decoded server info error"
        
        # get suitable devices
        target_device = self.device_manager.get_target_devices(self.platform_verion, self.appium_server + ":" + self.appium_port)
        if not target_device:
            return "Can not find suitable devices"
        
        # launch appium server
        self.appium_server_manager.launch_server(self.appium_server, self.appium_port, target_device)
    
    def decoded_server_info(self, server_info):
        
        try:
            decoded_info = json.loads(server_info)
            
            # appium server info
            self.appium_server = decoded_info['server']
            self.appium_port = decoded_info['port']
            
            # platform info
            self.platform_name = decoded_info['platformName']
            self.platform_verion = decoded_info['platformVersion']
            self.device_name = decoded_info['deviceName']
        except ValueError:
            return False
        
        return True
    
    def close_server(self, server_info):
        self.appium_server_manager.close_server(self.appium_server, self.appium_port)
        