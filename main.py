from threading import Thread  # Required to constantly read values from arduino serial port in separate thread
import serial  # To communicate with arduino and track ball
from psychopy import visual, core, event  # import PsychoPy libraries that use c++ make files to generate stimulus


def receiving(ser):
    """Function that receives serial information from trackball - designed to be run in a separate thread"""
    ser.flushInput()
    global last_received

    while True:  # Constantly updates most recently received value to avoid issue with buffered input
        data_packet = ser.readline()
        temp = data_packet.decode('cp1252')
        last_received = float(temp.strip() + '0')


# Initialise variables
mouse_or_trackball = 0  # 0 for mouse and 1 for trackball
last_received = 0

# create a window to draw in
myWin = visual.Window((1500.0, 1000.0), allowGUI=True)

# initialise the stimulus (change size and colours of the window)
fixSpot = visual.PatchStim(myWin,
                           tex="none", mask=None,
                           pos=(0, 0), size=(1, 1),  # size and location as fraction of window
                           rgb=[0, -1, 0])  # the colour of the fixation (black)
grating = visual.PatchStim(myWin, pos=(0, 0),
                           tex="sin", mask=None,
                           rgb=[-1, -1, 0],
                           size=(1.0, 1.0), sf=(3, 0))  # set the size and the grating cycles

# If using trackball: initialise arduino input and start reading serial in one thread
if mouse_or_trackball:
    arduino = serial.Serial(port='COM8', baudrate=115200)
    Thread(target=receiving, args=(arduino,)).start()

# Initialise mouse object
myMouse = event.Mouse(visible=False, win=myWin)

# Set angular gains for input to screen angle ratio
if mouse_or_trackball:
    gain = 1 / 60  # Gain parameter for ball movement vs screen movement
else:
    gain = 2.5

# For a time of 20,000 frames update the angular position of the window based on the input
for frameN in range(20000):

    # handle key presses each frame
    for key in event.getKeys():  # returns keys pressed this frame
        if key in ['escape', 'q']:
            core.quit()  # close window and stop operation if q or esc are pressed

    # get mouse events
    mouse_dx, mouse_dy = myMouse.getRel()  # get position relative to previous

    # Handle the mouse wheel to change orientation of the stimulus
    wheel_dx, wheel_dy = myMouse.getWheelRel()

    # change the grating orientation according to the wheel
    grating.setOri(wheel_dy * 5, '+')  # 2 clicks will give 10deg rotation
    event.clearEvents()  # get rid of other, unprocessed events

    # draw our stimuli (every frame)
    if mouse_or_trackball == 0:  # If using mouse
        grating.setPhase(mouse_dx * gain, '+')  # advance grating by gain multiplied by dx
    if mouse_or_trackball == 1:  # If using trackball
        grating.setPhase(last_received * gain)  # set grating angle
    grating.draw()
    myWin.flip()  # update the window

core.quit()  # end
