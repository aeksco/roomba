def callbackKey(self, event):
    k = event.keysym.upper()
    motionChange = False

    if event.type == '2': # KeyPress; need to figure out how to get constant
        self.sendCommandASCII('132') # Full
        self.sendCommandASCII('7') # Reset

        elif k == 'UP':
            self.callbackKeyUp = True
            motionChange = True
        elif k == 'DOWN':
            self.callbackKeyDown = True
            motionChange = True
        elif k == 'LEFT':
            self.callbackKeyLeft = True
            motionChange = True
        elif k == 'RIGHT':
            self.callbackKeyRight = True
            motionChange = True
        else:
            print repr(k), "not handled"

    elif event.type == '3': # KeyRelease; need to figure out how to get constant
        if k == 'UP':
            self.callbackKeyUp = False
            motionChange = True
        elif k == 'DOWN':
            self.callbackKeyDown = False
            motionChange = True
        elif k == 'LEFT':
            self.callbackKeyLeft = False
            motionChange = True
        elif k == 'RIGHT':
            self.callbackKeyRight = False
            motionChange = True

    if motionChange == True:
        velocity = 0
        velocity += VELOCITYCHANGE if self.callbackKeyUp is True else 0
        velocity -= VELOCITYCHANGE if self.callbackKeyDown is True else 0
        rotation = 0
        rotation += ROTATIONCHANGE if self.callbackKeyLeft is True else 0
        rotation -= ROTATIONCHANGE if self.callbackKeyRight is True else 0

        # compute left and right wheel velocities
        vr = velocity + (rotation/2)
        vl = velocity - (rotation/2)

        # create drive command
        cmd = struct.pack(">Bhh", 145, vr, vl)
        if cmd != self.callbackKeyLastDriveCommand:
            self.sendCommandRaw(cmd)
            self.callbackKeyLastDriveCommand = cmd
