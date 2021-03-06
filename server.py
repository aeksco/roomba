#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

# # # # #

class TetheredRoomba():

    def __init__(self):
      print 'Roomba Initializing...'

    # # # # #

    # sendCommandASCII takes a string of whitespace-separated, ASCII-encoded base 10 values to send
    def sendCommandASCII(self, command):
        print 'Sending ASCII...'
        print command
        cmd = ""
        for v in command.split():
            cmd += chr(int(v))

        self.sendCommandRaw(cmd)

    # # # # #

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

    # # # # #

    def onConnect(self):
        global connection

        if connection is not None:
            print 'Already connected.'
            return

        try:
            ports = self.getSerialPorts()

            # TODO - Lazily grabs first available port
            # Add connectionManager to handle listing
            port = ports[1]
            # port = tkSimpleDialog.askstring('Port?', 'Enter COM port to open.\nAvailable options:\n' + '\n'.join(ports))

        except EnvironmentError:
            print 'ENV ERROR!'
            # port = tkSimpleDialog.askstring('Port?', 'Enter COM port to open.')

        if port is not None:
            print "Trying " + str(port) + "... "
            try:
                connection = serial.Serial(port, baudrate=115200, timeout=1)
                print "Connection successful!"

            except:
                print "Failed connecting on " + str(port)

    # # # # #

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
                result.append({ 'name': port })
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
      actions = {
        'clean':  '135',
        'dock':   '143',
        'reset':  '7',
        'full':   '132'
      }

      return actions[action]

    # # # # #

    def sendAction(self, action):
      self.ensureConnection()
      self.ensureSafe()

      command = self.getActionAscii(action)
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

@app.route('/roomba')
def invokeAction():
  if 'action' in request.args:
    return sendResponse(roomba.sendAction(request.args['action']))

  return sendResponse({ 'error': 'no state' }, 400)

@app.route('/serial_ports')
def getSerialPorts():
  return sendResponse(roomba.getSerialPorts(), 200)

# # # # #

# Start
if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')

# # # # # # # # # # # # # # # # # # # #


