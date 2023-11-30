# original: https://github.com/Seconb/Arsenal-Colorbot

from cv2 import findContours, threshold, dilate, inRange, cvtColor, COLOR_BGR2HSV, THRESH_BINARY, RETR_EXTERNAL, CHAIN_APPROX_NONE, contourArea
from numpy import array, ones, uint8
from os import path, system
from math import sqrt
from mss import mss
from keyboard import is_pressed
from configparser import ConfigParser
from win32api import GetAsyncKeyState
from colorama import Fore, Style
from ctypes import windll
from time import sleep
from threading import Thread
from urllib.request import urlopen

range=range
len=len
print=print
tuple=tuple
int=int
max=max

user32 = windll.user32

CURRENT_VERSION = "v1.5" # IMPORTANT !!!!!! CHANGE lmfao

system("title Colorbot")

if urlopen("https://raw.githubusercontent.com/AndrewDarkyy/Colorbot-Modded/main/version.txt").read().decode("utf-8")!=CURRENT_VERSION+"\n":
    print(Style.BRIGHT + Fore.CYAN + "This version is outdated, please get the latest one at " + Fore.YELLOW + "https://github.com/AndrewDarkyy/Colorbot-Modded/releases" + Style.RESET_ALL)
    while True:
        pass

switchmodes = ("Hold", "Toggle")

sdir = path.dirname(path.abspath(__file__))

config = ConfigParser()
config.optionxform = str
config.read(path.join(sdir, "config.ini"))

def check_key(string, key):
    if string == "LeftClick" or string == "win32con.VK_XBUTTON1" or string == "VK_XBUTTON1":
        return 0x01
    elif string == "RightClick" or string == "win32con.VK_XBUTTON2" or string == "VK_XBUTTON2":
        return 0x02
    elif string == "MiddleClick" or string == "win32con.VK_XBUTTON3" or string == "VK_XBUTTON3":
        return 0x04
    elif string == "SideButton1" or string == "win32con.VK_XBUTTON4" or string == "VK_XBUTTON4":
        return 0x05
    elif string == "SideButton2" or string == "win32con.VK_XBUTTON5" or string == "VK_XBUTTON5":
        return 0x06
    elif string == "Disabled":
        return "Disabled"
    else:
        try:
            is_pressed(string)
        except:
            print(f"Please change {key} to an existing key.")
            while True:
                sleep(0.1) # omggg check if key exists so just, just amazing
                try:
                    new_config = ConfigParser()
                    new_config.optionxform = str
                    new_config.read(path.join(sdir, "config.ini"))
                    is_pressed(new_config.get("Config", key))
                    string = new_config.get("Config", key)
                    break
                except:
                    pass
        return string

def print_banner_stuffz(key):
    if key == 0x01:
        return "LeftClick"
    elif key == 0x02:
        return "RightClick"
    elif key == 0x04:
        return "MiddleClick"
    elif key == 0x05:
        return "SideButton1"
    elif key == 0x06:
        return "SideButton2"
    elif key == "Disabled":
        return "Disabled"
    else:
        return str(key)

def is_roblox_focused():
    return True

try:
    global A1M_KEY, SWITCH_MODE_KEY
    global CAM_FOV, A1M_FOV, TRIGGERBOT_DELAY
    global A1M_OFFSET_Y, A1M_OFFSET_X, A1M_SPEED_X, A1M_SPEED_Y
    global upper, lower
    A1M_KEY = check_key(config.get("Config", "A1M_KEY"), "A1M_KEY")
    SWITCH_MODE_KEY = check_key(config.get("Config", "SWITCH_MODE_KEY"), "SWITCH_MODE_KEY")
    CAM_FOV = int(config.get("Config", "CAM_FOV"))
    A1M_FOV = int(config.get("Config", "A1M_FOV"))
    TRIGGERBOT_DELAY = float(config.get("Config", "TRIGGERBOT_DELAY"))
    A1M_OFFSET_Y = int(config.get("Config", "A1M_OFFSET_Y"))
    A1M_OFFSET_X = int(config.get("Config", "A1M_OFFSET_X"))
    A1M_SPEED_X = float(config.get("Config", "A1M_SPEED_X"))
    A1M_SPEED_Y = float(config.get("Config", "A1M_SPEED_Y"))
    upper = array((123, 255, 217), dtype="uint8")
    lower = array((113, 206, 189), dtype="uint8")

    if A1M_SPEED_X <= 0:
        A1M_SPEED_X = 0.001 # everything multiplied by 0 is 0 (except infinity) so no use
    if A1M_SPEED_X > 1:
        A1M_SPEED_X = 1 # more than one prob useless

    if 0 > TRIGGERBOT_DELAY:
        TRIGGERBOT_DELAY = 0

    if A1M_SPEED_Y <= 0:
        A1M_SPEED_Y = 0.001
    if A1M_SPEED_Y > 1:
        A1M_SPEED_Y = 1
except Exception as e:
    print("Error loading settings:", e)

sct = mss()

center = CAM_FOV / 2

screenshot = sct.monitors[1]
screenshot["left"] = int((screenshot["width"] / 2) - center)
screenshot["top"] = int((screenshot["height"] / 2) - center)
screenshot["width"] = CAM_FOV
screenshot["height"] = CAM_FOV

ones_uint = ones((3, 3), uint8)
sct_grab=sct.grab
m_event=user32.mouse_event

class colorbot:
    def __init__(self):
        self.aimtoggled = False
        self.switchmode = 0
        self.__clicks = 0
        self.__shooting = False

    def __stop(self):
        oldclicks = self.__clicks
        sleep(.05)
        if self.__clicks == oldclicks:
            m_event(0x0004)

    def __delayedaim(self):
        self.__shooting=True
        sleep(TRIGGERBOT_DELAY)
        m_event(0x0002)
        self.__clicks += 1
        Thread(target = self.__stop).start()
        self.__shooting = False

    def process(self):
        if is_roblox_focused():
            (contours, hierarchy) = findContours(threshold(dilate(inRange(cvtColor(array(sct_grab(screenshot)), COLOR_BGR2HSV), lower, upper), ones_uint, iterations=5), 60, 255, THRESH_BINARY)[1], RETR_EXTERNAL, CHAIN_APPROX_NONE)
            if len(contours) != 0:
                contour = max(contours, key=contourArea)
                topmost = tuple(contour[contour[:, :, 1].argmin()][0])
                x = topmost[0] - center + A1M_OFFSET_X
                y = topmost[1] - center + A1M_OFFSET_Y
                distance = sqrt(x*x + y*y)
                if distance <= A1M_FOV:
                    m_event(0x0001, int(x * A1M_SPEED_X), int(y * A1M_SPEED_Y), 0, 0)
                if distance<=8:
                    if TRIGGERBOT_DELAY!=0:
                        if self.__shooting == False:
                            Thread(target = self.__delayedaim).start()
                    else:
                        m_event(0x0002)
                        self.__clicks += 1
                        Thread(target = self.__stop).start()
                elif distance<=50:
                    for index in range(len(contour)):
                        topmost = tuple(contour[index][0])
                        x = topmost[0] - center + A1M_OFFSET_X
                        y = topmost[1] - center + A1M_OFFSET_Y
                        distance = sqrt(x*x + y*y)
                        if distance<=7:
                            if TRIGGERBOT_DELAY!=0:
                                if self.__shooting == False:
                                    Thread(target = self.__delayedaim).start()
                            else:
                                m_event(0x0002)
                                self.__clicks += 1
                                Thread(target = self.__stop).start()
                            break

    def a1mtoggle(self):
        self.aimtoggled = not self.aimtoggled
        sleep(.08)

    def modeswitch(self):
        if self.switchmode == 0:
            self.switchmode = 1
        elif self.switchmode == 1:
            self.switchmode = 0
        sleep(.08)

def print_banner(bot: colorbot):
    system("cls")
    print(Style.BRIGHT + Fore.LIGHTMAGENTA_EX + "Lunar's Arsenal Colorbot" + Style.RESET_ALL)
    print("====== Controls ======")
    print("Aimbot Keybind      :", Fore.YELLOW + print_banner_stuffz(A1M_KEY) + Style.RESET_ALL)
    print("Change Mode         :", Fore.YELLOW + print_banner_stuffz(SWITCH_MODE_KEY) + Style.RESET_ALL)
    print("==== Information =====")
    print("Aimbot Mode         :", Fore.CYAN + switchmodes[bot.switchmode] + Style.RESET_ALL)
    print("Aimbot FOV          :", Fore.CYAN + str(A1M_FOV) + Style.RESET_ALL)
    print("Camera FOV          :", Fore.CYAN + str(CAM_FOV) + Style.RESET_ALL)
    print("Shoot Delay         :", Fore.CYAN + str(TRIGGERBOT_DELAY) + Style.RESET_ALL)
    print("Sensitivity         :", Fore.CYAN + "X: " + str(A1M_SPEED_X) + " Y: " + str(A1M_SPEED_Y) + Style.RESET_ALL)
    print("Offset              :", Fore.CYAN + "X: " + str(A1M_OFFSET_X) + " Y: " + str(A1M_OFFSET_Y) + Style.RESET_ALL)
    print("Aiming              :", (Fore.GREEN if bot.aimtoggled else Fore.RED) + str(bot.aimtoggled))

del CURRENT_VERSION
del config
del sdir
del check_key
del urlopen
del mss
del ConfigParser

if __name__ == "__main__":
    bot = colorbot()
    del colorbot
    print_banner(bot)
    while True:
        if SWITCH_MODE_KEY != "Disabled":
            if SWITCH_MODE_KEY == 0x01 or SWITCH_MODE_KEY == 0x02 or SWITCH_MODE_KEY == 0x04:
                if GetAsyncKeyState(SWITCH_MODE_KEY) < 0:
                    bot.modeswitch()
                    print_banner(bot)
            elif SWITCH_MODE_KEY == 0x05 or SWITCH_MODE_KEY == 0x06:
                if bool(user32.GetKeyState(SWITCH_MODE_KEY) & 0x80):
                    bot.modeswitch()
                    print_banner(bot)
            elif is_pressed(SWITCH_MODE_KEY):
                bot.modeswitch()
                print_banner(bot)

        sleep(0.1)

        if A1M_KEY != "Disabled":
            if A1M_KEY == 0x02 or A1M_KEY == 0x01 or A1M_KEY == 0x04:
                if GetAsyncKeyState(A1M_KEY) < 0:
                    if bot.switchmode == 0:
                        while GetAsyncKeyState(A1M_KEY) < 0:
                            if not bot.aimtoggled:
                                bot.a1mtoggle()
                                print_banner(bot)
                                while bot.aimtoggled:
                                    bot.process()
                                    if not GetAsyncKeyState(A1M_KEY) < 0:
                                        bot.a1mtoggle()
                                        print_banner(bot)
                    else:
                        bot.a1mtoggle()
                        print_banner(bot)
                        while bot.aimtoggled:
                            bot.process()
                            if GetAsyncKeyState(A1M_KEY) < 0:
                                bot.a1mtoggle()
                                print_banner(bot)
            elif A1M_KEY == 0x05 or A1M_KEY == 0x06:
                if bool(user32.GetKeyState(A1M_KEY) & 0x80):
                    if bot.switchmode == 0:
                        while bool(user32.GetKeyState(A1M_KEY) & 0x80):
                            if not bot.aimtoggled:
                                bot.a1mtoggle()
                                print_banner(bot)
                                while bot.aimtoggled:
                                    bot.process()
                                    if not bool(user32.GetKeyState(A1M_KEY) & 0x80):
                                        bot.a1mtoggle()
                                        print_banner(bot)
                    else:
                        bot.a1mtoggle()
                        print_banner(bot)
                        while bot.aimtoggled:
                            bot.process()
                            if bool(user32.GetKeyState(A1M_KEY) & 0x80):
                                bot.a1mtoggle()
                                print_banner(bot)
            elif is_pressed(A1M_KEY):
                if bot.switchmode == 0:
                    while is_pressed(A1M_KEY):
                        if not bot.aimtoggled:
                            bot.a1mtoggle()
                            print_banner(bot)
                            while bot.aimtoggled:
                                bot.process()
                                if not is_pressed(A1M_KEY):
                                    bot.a1mtoggle()
                                    print_banner(bot)
                else:
                    bot.a1mtoggle()
                    print_banner(bot)
                    while bot.aimtoggled:
                        bot.process()
                        if is_pressed(A1M_KEY):
                            bot.a1mtoggle()
                            print_banner(bot)
