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

from flask import Flask, request, redirect, url_for, send_from_directory, json, Response
import struct
import sys, glob # for listing serial ports
import serial

connection = None

TEXTWIDTH = 40 # window width, in characters
TEXTHEIGHT = 16 # window height, in lines

VELOCITYCHANGE = 200
ROTATIONCHANGE = 300

# # # # #

class TetheredRoomba():
    # static variables for keyboard callback -- I know, this is icky
    callbackKeyUp = False
    callbackKeyDown = False
    callbackKeyLeft = False
    callbackKeyRight = False
    callbackKeyLastDriveCommand = ''

    def __init__(self):
      print 'HELLO ROOMBA'

    # sendCommandASCII takes a string of whitespace-separated, ASCII-encoded base 10 values to send
    def sendCommandASCII(self, command):
        print 'Sending ASCII...'
        print command
        cmd = ""
        for v in command.split():
            cmd += chr(int(v))

        self.sendCommandRaw(cmd)

    # sendCommandRaw takes a string interpreted as a byte array
    def sendCommandRaw(self, command):
        global connection
        print 'Sending raw command...'

        try:
            if connection is not None:
                connection.write(command)
            else:
                print "Not connected."
        except serial.SerialException:
            print "Lost connection"
            connection = None

        # print ' '.join([ str(ord(c)) for c in command ])
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

    def onConnect(self):
        global connection

        if connection is not None:
            print 'Already connected.'
            # tkMessageBox.showinfo('Oops', "You're already connected!")
            return

        try:
            ports = self.getSerialPorts()
            print ports
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

    # # # # #

    def ensureConnection(self):
      self.onConnect()

    def ensureSafe(self):
      self.sendCommandASCII('128') # Passive
      self.sendCommandASCII('131') # Safe

    # # # # #

    def getActionAscii(self, action):
      actions = { # TODO - make this global.
        'clean':  '135',
        'dock':   '143',
        'reset':  '7',
        'full':   '132'
      }

      # NOTE - beep doesn't work
      # 'beep':   '140 3 64 16 141 3',

      return actions[action]

    # # # # #

    def sendAction(self, action):
      command = self.getActionAscii(action)

      self.ensureConnection()
      # self.ensureSafe()
      self.sendCommandASCII('128') # Passive
      self.sendCommandASCII('131') # Safe
      # self.sendCommandASCII('135')
      self.sendCommandASCII(command)
      return { 'sent': 'true' }

# # # # # # # # # # # # # # # # # # # #

# Init server & Roomba instance
app     = Flask(__name__, static_folder='build')
roomba  = TetheredRoomba()

# Static asset routes
@app.route('/')
def root():
  return send_from_directory('build', 'index.html')

@app.route('/js/<path:path>')
def sendJS(path):
  return send_from_directory('build/js/', path)

@app.route('/css/<path:path>')
def sendCss(path):
  return send_from_directory('build/css/', path)

# # # # #

# Response handler
def sendResponse(state, status=200):
  return Response(json.dumps(state), status=status, mimetype='application/json')

# Roomba API
@app.route('/roomba')
def invokeAction():
  if 'action' in request.args:
    return sendResponse(roomba.sendAction(request.args['action']))

  return sendResponse({ 'error': 'no state' }, 400)

# # # # #

# Start
if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')


# # # # # # # # # # # # # # # # # # # #


