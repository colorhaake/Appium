import os

class AppiumEnv:
    # Environment settings
    SDK_PATH = "/Users/minibarque/android/sdk:/Users/minibarque/android/sdk/tools:/Users/minibarque/android/sdk/platform-tools:"
    APPIUM_PATH = "/usr/local/bin:"
    appium_env = os.environ
    appium_env["PATH"] =  SDK_PATH + APPIUM_PATH + appium_env.get("PATH", '')