#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 27 May 2015

###########################################################################
# Copyright (c) 2015 iRobot Corporation
# http://www.irobot.com/
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#   Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
#
#   Neither the name of iRobot Corporation nor the names
#   of its contributors may be used to endorse or promote products
#   derived from this software without specific prior written
#   permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
###########################################################################

from flask import Flask, render_template
import struct
import sys, glob # for listing serial ports
import serial

connection = None

TEXTWIDTH = 40 # window width, in characters
TEXTHEIGHT = 16 # window height, in lines

VELOCITYCHANGE = 200
ROTATIONCHANGE = 300

# # # # #

class TetheredDriveApp():
    # static variables for keyboard callback -- I know, this is icky
    callbackKeyUp = False
    callbackKeyDown = False
    callbackKeyLeft = False
    callbackKeyRight = False
    callbackKeyLastDriveCommand = ''

    def __init__(self):
      print 'HELLO ROMMBA'

    # sendCommandASCII takes a string of whitespace-separated, ASCII-encoded base 10 values to send
    def sendCommandASCII(self, command):
        cmd = ""
        for v in command.split():
            cmd += chr(int(v))

        self.sendCommandRaw(cmd)

    # sendCommandRaw takes a string interpreted as a byte array
    def sendCommandRaw(self, command):
        global connection
        print 'SEND COMMAND RAW'

        try:
            if connection is not None:
                print "HAS CONNECTION"

                connection.write(command)
            else:
                # tkMessageBox.showerror('Not connected!', 'Not connected to a robot!')
                print "Not connected."
        except serial.SerialException:
            print "Lost connection"
            # tkMessageBox.showinfo('Uh-oh', "Lost connection to the robot!")
            connection = None

        print ' '.join([ str(ord(c)) for c in command ])
        # self.text.insert(END, ' '.join([ str(ord(c)) for c in command ]))
        # self.text.insert(END, '\n')
        # self.text.see(END)

    # getDecodedBytes returns a n-byte value decoded using a format string.
    # Whether it blocks is based on how the connection was set up.
    def getDecodedBytes(self, n, fmt):
        global connection

        try:
            return struct.unpack(fmt, connection.read(n))[0]
        except serial.SerialException:
            # print "Lost connection"
            # tkMessageBox.showinfo('Uh-oh', "Lost connection to the robot!")
            print "Lost connection to the robot!"
            connection = None
            return None
        except struct.error:
            print "Got unexpected data from serial port."
            return None

    # get8Unsigned returns an 8-bit unsigned value.
    def get8Unsigned(self):
        return getDecodedBytes(1, "B")

    # get8Signed returns an 8-bit signed value.
    def get8Signed(self):
        return getDecodedBytes(1, "b")

    # get16Unsigned returns a 16-bit unsigned value.
    def get16Unsigned(self):
        return getDecodedBytes(2, ">H")

    # get16Signed returns a 16-bit signed value.
    def get16Signed(self):
        return getDecodedBytes(2, ">h")

    # A handler for keyboard events. Feel free to add more!
    # def callbackKey(self, event):
    #     k = event.keysym.upper()
    #     motionChange = False

    #     if event.type == '2': # KeyPress; need to figure out how to get constant
    #         if k == 'P':   # Passive
    #             self.sendCommandASCII('128')
    #         elif k == 'S': # Safe
    #             self.sendCommandASCII('131')
    #         elif k == 'F': # Full
    #             self.sendCommandASCII('132')
    #         elif k == 'C': # Clean
    #             self.sendCommandASCII('135')
    #         elif k == 'D': # Dock
    #             self.sendCommandASCII('143')
    #         elif k == 'SPACE': # Beep
    #             self.sendCommandASCII('140 3 1 64 16 141 3')
    #         elif k == 'R': # Reset
    #             self.sendCommandASCII('7')
    #         elif k == 'UP':
    #             self.callbackKeyUp = True
    #             motionChange = True
    #         elif k == 'DOWN':
    #             self.callbackKeyDown = True
    #             motionChange = True
    #         elif k == 'LEFT':
    #             self.callbackKeyLeft = True
    #             motionChange = True
    #         elif k == 'RIGHT':
    #             self.callbackKeyRight = True
    #             motionChange = True
    #         else:
    #             print repr(k), "not handled"
    #     elif event.type == '3': # KeyRelease; need to figure out how to get constant
    #         if k == 'UP':
    #             self.callbackKeyUp = False
    #             motionChange = True
    #         elif k == 'DOWN':
    #             self.callbackKeyDown = False
    #             motionChange = True
    #         elif k == 'LEFT':
    #             self.callbackKeyLeft = False
    #             motionChange = True
    #         elif k == 'RIGHT':
    #             self.callbackKeyRight = False
    #             motionChange = True

    #     if motionChange == True:
    #         velocity = 0
    #         velocity += VELOCITYCHANGE if self.callbackKeyUp is True else 0
    #         velocity -= VELOCITYCHANGE if self.callbackKeyDown is True else 0
    #         rotation = 0
    #         rotation += ROTATIONCHANGE if self.callbackKeyLeft is True else 0
    #         rotation -= ROTATIONCHANGE if self.callbackKeyRight is True else 0

    #         # compute left and right wheel velocities
    #         vr = velocity + (rotation/2)
    #         vl = velocity - (rotation/2)

    #         # create drive command
    #         cmd = struct.pack(">Bhh", 145, vr, vl)
    #         if cmd != self.callbackKeyLastDriveCommand:
    #             self.sendCommandRaw(cmd)
    #             self.callbackKeyLastDriveCommand = cmd

    def onConnect(self):
        global connection

        if connection is not None:
            print 'Already connected.'
            # tkMessageBox.showinfo('Oops', "You're already connected!")
            return

        try:
            ports = self.getSerialPorts()
            # port = tkSimpleDialog.askstring('Port?', 'Enter COM port to open.\nAvailable options:\n' + '\n'.join(ports))
            port = ports[1]
            print "GOT PORT"
            print port
        except EnvironmentError:
            print 'ENV ERROR!'
            # port = tkSimpleDialog.askstring('Port?', 'Enter COM port to open.')

        if port is not None:
            print "Trying " + str(port) + "... "
            try:
                connection = serial.Serial(port, baudrate=115200, timeout=1)
                print "Connected!"
                # tkMessageBox.showinfo('Connected', "Connection succeeded!")
            except:
                print "Failed."
                # tkMessageBox.showinfo('Failed', "Sorry, couldn't connect to " + str(port))

    def getSerialPorts(self):
        """Lists serial ports
        From http://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of available serial ports
        """
        if sys.platform.startswith('win'):
            ports = ['COM' + str(i + 1) for i in range(256)]

        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this is to exclude your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')

        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')

        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def ensureSafe(self):
      # Passive
      self.sendCommandASCII('128')
      # Safe
      self.sendCommandASCII('131')

    def clean(self):
      self.ensureSafe()
      self.sendCommandASCII('135') # Clean

# # # # # # # # # # # # # # # # # # # #

app     = Flask(__name__)
roomba  = TetheredDriveApp()

# Connect route
@app.route('/')
def index():
  return render_template('index.html')
  # ports = roomba.getSerialPorts()
  # return 'Hello world'

# Clean route
@app.route('/clean')
def clean():
  # ports = roomba.getSerialPorts()
  # roomba.onConnect()
  roomba.onConnect()
  roomba.clean()
  return 'Clean!'

# Start
if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')


# # # # # # # # # # # # # # # # # # # #


