### SJSU ME106 Project Spring 2021
### Zach Abdallah, Trevin Aguilar, Tan Nguyen

## Program to run a two axis solar panel that adjusts its position
## with respect to the Sun based on the time

### Devices used ###
# INA169 Current Sensor
# PCF8523 Real Time Clock Sensor
# Adafruit Feather nRF52840 Sense
# Sparkfun Bipolar Stepper Motors https://www.sparkfun.com/products/9238
# Pololu A4988 Stepper Motor Drivers


import board, digitalio, time, adafruit_pcf8523, busio, analogio, math

## Top Stepper Motor Config ## Y - axis rotation
directionTop = digitalio.DigitalInOut(board.D9)
stepTop = digitalio.DigitalInOut(board.D10)

directionTop.direction = digitalio.Direction.OUTPUT
directionTop.value = False                           # True = CW, False = CCW
stepTop.direction = digitalio.Direction.OUTPUT


## Bottom Stepper Motor ## X - axis rotation
directionBot = digitalio.DigitalInOut(board.D11)
stepBot = digitalio.DigitalInOut(board.D12)

directionBot.direction = digitalio.Direction.OUTPUT
directionBot.value = True                           # True = CW, False = CCW
stepBot.direction = digitalio.Direction.OUTPUT



## Test Code for Stepper Motor ##
# Checks cw and ccw movement for stepper motor
def testStepper(direction,step):
    
    while True:
            
            userInput = int(input("Type 1(CW) or 2(CCW): "))
            
            if userInput == 1:
                #print('Hello')                 # For Testing
                for i in range(10):             # moves cw
                    direction.value = True
                    time.sleep(0.05)
                    step.value = True
                    time.sleep(0.05)
                    step.value = False
                    time.sleep(0.05)
                    #print('clockwise')         # For Testing
            
            if userInput == 2 :                 # Moves ccw
                for i in range(10):
                    direction.value = False
                    time.sleep(0.05)
                    step.value = True
                    time.sleep(0.05)
                    step.value = False
                    time.sleep(0.05)
                    #print('Counter-Clockwise') # For Testing
            
            if userInput == 3: # breaks loop
                print('Ok bye')
                break

            if userInput == 4:                  # Moves 75 steps cw and ccw, for demo footage
                for i in range(75):
                    direction.value = True
                    time.sleep(0.05)
                    step.value = True
                    time.sleep(0.05)
                    step.value = False
                    time.sleep(0.05)
                for i in range(75):
                    direction.value = False
                    time.sleep(0.05)
                    step.value = True
                    time.sleep(0.05)
                    step.value = False
                    time.sleep(0.05)
            
            else:
                continue

#testStepper(directionBot,stepBot)              # For Testing
#testStepper(directionTop,stepTop)              # For Testing

def stepOnce(direction, step):
    # Given Stepper motor steps once, directionpin no longer used
    step.value = True
    time.sleep(0.05)
    step.value = False
    time.sleep(0.05)

#while True:                                    # Test stepOnce function
#    userInput = int(input('1: '))
#    if userInput == 1:
#        stepOnce(directionBot,stepBot,1)
#    else:
#        continue





### PCF8523 Real Time Clock (RTC) Sensor Config ###
myI2C = busio.I2C(board.SCL, board.SDA)
rtc = adafruit_pcf8523.PCF8523(myI2C)
t = rtc.datetime
days = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")

## Set RTC Time ##
# Pulled from Adafruit PCF8523 guide: https://learn.adafruit.com/adafruit-pcf8523-real-time-clock/rtc-with-circuitpython
if False:       # change to True if you want to write the time!
    #                     year, mon, date, hour, min, sec, wday, yday, isdst
    t = time.struct_time((2021,  4,   18,   00,  12,  00,    0,   -1,    -1))
    # you must set year, mon, date, hour, min, sec and weekday
    # yearday is not supported, isdst can be set but we don't do anything with it at this time

    print("Setting time to:", t)     # uncomment for debugging
    rtc.datetime = t
    print()



### INA 169 Current Sensor ###
currentPin = analogio.AnalogIn(board.A5)

def readCurrent(pin):
    # Reads current measured from INA169 sensor
    return ((pin.value * 3.3) / 65536) #*100<- to scale for plotter #65536 is max analog reading

#readCurrent(currentPin)        # For Testing



## Recording Current + Time ##
currentList = []
def recordCurrent():
    # Measures current and time at a given instance and prints out a list of every current recording so far
    t = rtc.datetime # Updates RTC
    currentTime = ("%s %d/%d/%d %d:%02d:%02d" % (days[t.tm_wday], t.tm_mon, t.tm_mday, t.tm_year,t.tm_hour, t.tm_min, t.tm_sec))
    current = (str(readCurrent(currentPin)) + ' A')
    c = (( currentTime,current ))
    currentList.append(c)

    #print(currentList) # For Testing
    for i in range(len(currentList)):
        print(currentList[i])

#recordCurrent()        # For Testing



### Main Code ###

def runProject():
    
    ## Assume start at 8am, facing North
    for i in range(13):                 # Moves to starting 8am position
        stepOnce(directionTop, stepTop)
    for i in range(50):                 # Moves to starting 8am position
        stepOnce(directionBot,stepBot)

    h = 8  # Hour
    #h = t.tm_hour
    print(h) # troubleshooting
    n = 117 # Year Day, can use a RTC that has yearday supported,

    # Calculate initial position before while loop
    delta = 23.45 *(math.pi / 180) * math.sin(math.radians( 2 * math.pi * ( ( 284 + n ) / 36.25 )) )
    phi = 37.3382
    w = 15 * h
    alpha_1 = math.sin(math.radians(delta))
    alpha_2 = math.sin(math.radians(phi))
    alpha_sin = (alpha_1) * (alpha_2)
    alpha_3 = math.cos(math.radians(delta))
    alpha_4 = math.cos(math.radians(w))
    alpha_5 = math.cos(math.radians(phi))
    alpha_cos = (alpha_3) * (alpha_4) * (alpha_5)
    alpha_arc = math.asin((alpha_sin) + (alpha_cos))
    alpha_actual = (alpha_arc) * (180 / (math.pi))
    theta_top = ((math.sin(math.radians(w))) * (math.cos(delta))) / (math.cos(math.radians(alpha_actual)))
    theta_actual = (math.asin(theta_top)) * (180 / math.pi)

    # Initial Altitude and Azimuth values  before while loop
    atu = (abs(alpha_actual))   # set default, y-axis
    azo = (90 + (h - 8 ) * 10)  # set default, x-axis



    while True:
        
        t=rtc.datetime # Updates RTC
        #userHour = float(input('Input Hour Number: '))  # For Testing
        #h = userHour                                    # For Testing

        # Sets current atu and azo as previous for future calcs
        prevAtu = atu                                    # y axis top motor
        prevAzo = azo                                    # x axis bottom motor

        # Converts current time into a hour float value
        h = t.tm_hour
        m = t.tm_min / 60
        h = h + m
        print(h) # For troubleshooting

        # Current day - requires manual input
        n = 117 # Year Day, another RTC might have yearday functionality supported


        ## Calculate current sun position based on time
        delta = 23.45 *(math.pi / 180) * math.sin(math.radians( 2 * math.pi * ( ( 284 + n ) / 36.25 )) )
        phi = 37.3382
        w = 15 * h
        alpha_1 = math.sin(math.radians(delta))
        alpha_2 = math.sin(math.radians(phi))
        alpha_sin = (alpha_1) * (alpha_2)
        alpha_3 = math.cos(math.radians(delta))
        alpha_4 = math.cos(math.radians(w))
        alpha_5 = math.cos(math.radians(phi))
        alpha_cos = (alpha_3) * (alpha_4) * (alpha_5)
        alpha_arc = math.asin((alpha_sin) + (alpha_cos))
        alpha_actual = (alpha_arc) * (180 / (math.pi))
        theta_top = ((math.sin(math.radians(w))) * (math.cos(delta))) / (math.cos(math.radians(alpha_actual)))
        theta_actual = (math.asin(theta_top)) * (180 / math.pi)


        # atu = y-axis, Top Motor
        # azo = x-axis, Bottom Motor

        # Determines current altitude and Azimuth values, varies based on hr
        if 13 <= h < 17:
            # Altitude between 1pm and 5pm
            atu = (abs(alpha_actual) + 25)
            print(atu) # For troubleshooting

        if 17 <= h <= 20:
            # Altitude between 5 and 8pm
            atu = ((alpha_actual) * (-1) + 25)
            print(atu) # For troubleshooting

        if 8 <= h < 13:
            atu = (abs(alpha_actual)) # Altitude between 8am and 1pm
            print(atu) # For troubleshooting

            azo = (90 + (h - 8 ) * 10)  # Azimuth between 8am and 1pm
            print(azo) # For troubleshooting

        if 13 <= h < 14:
            # Azimuth between 1pm and 2pm
            azo = (abs(theta_actual) + 180 - 26)
            print(azo)  # For troubleshooting

        if 13 < h <= 16:
            # Azimuth between 1pm and 4pm
            azo = (abs(theta_actual) + 180)
            print(azo) # For troubleshooting

        if 16 < h <= 17:
            # Azimuth between 4pm and 5pm
            azo = (abs(theta_actual) + 180 +15)
            print(azo) # For troubleshooting

        if 17 < h <= 20:
            # Azimuth between 5 and 8pm
            azo = (abs(theta_actual) + 180 + 25 + (10 * (h - 18)))
            print(azo) # For troubleshooting


        ## Calculates # of steps to take based off new sun position
        ySteps = round((atu - prevAtu) / 1.8)     # Number of steps for y-axis, stepper motor moves in 1.8 degree steps (full)
        xSteps = round((azo - prevAzo) / 1.8)     # Number of steps for x-axis

        print(str(xSteps) + ' X') # For troubleshooting
        print(str(ySteps) + ' Y') # For troubleshooting

        # True = CW, False = CCW
        directionTop.value = False # Moves up
        directionBot.value = True # Moves CW

        if ySteps < 0: 
            # If sun lowers, a negative ySteps value is produced, so this changes direction to move the stepper motor down
            ySteps = abs(ySteps)
            directionTop.value = True # Moves down

        ## Moves solar panel based off calculated steps
        for i in range(ySteps):
            stepOnce(directionTop,stepTop) 
        for i in range(xSteps):
            stepOnce(directionBot,stepBot) 

        recordCurrent() # Records current + time, prints out every current reading so far into serial

        time.sleep(10*60) # Checks every 10 min

runProject() # Please Work



### Functions used to film b-roll footage in video ###
def dropDown():
    directionTop.value = True
    for i in range(36):
        stepOnce(directionTop,stepTop)
    while True:
        print("hi")
        time.sleep(1)

#dropDown()


def side2side():
    directionBot.value = False
    for i in range(20):
        stepOnce(directionBot,stepBot)
    for i in range(3):
        directionBot.value = True
        for i in range(40):
            stepOnce(directionBot,stepBot)
        directionBot.value = False
        for i in range(40):
            stepOnce(directionBot,stepBot)
    while True:
        print('hi')
        time.sleep(1)
#side2side()
