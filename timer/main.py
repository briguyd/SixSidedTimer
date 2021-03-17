class Player:
    def __init__(self, name):
        self.name = name
        self.time = 0.0

class State(object):
    COUNT_DOWN_RUNNING = 0
    COUNT_DOWN_PAUSED = 1
    COUNT_DOWN_MENU = 2
    COUNT_DOWN_READY = 3
    COUNT_UP_RUNNING = 4
    COUNT_UP_PAUSED = 5
    COUNT_UP_READY = 6
    TOP_MENU = 7

    
from machine import Pin, I2C, Timer
from ssd1306 import SSD1306_I2C
import mpu6050 # import MPU6050
import utime

BUTTON_DELAY = 80
pauseButtonPressedRecently = False
upButtonPressedRecently = False
downButtonPressedRecently = False
pauseButtonTimer = Timer()
upButtonTimer = Timer()
downButtonTimer = Timer()
led = Pin(28, Pin.OUT)
led.low()

# Init Display
i2c = I2C(0,sda=Pin(4),scl=Pin(5),freq=40000)
oled = SSD1306_I2C(128,64,i2c)
mpu = mpu6050.MPU6050(0, 0x68, scl=Pin(5), sda=Pin(4))
#mpu.setSampleRate(200)
#mpu.setGResolution(2)

pauseButton = machine.Pin(20, machine.Pin.IN, machine.Pin.PULL_DOWN)
upButton = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_DOWN)
downButton = machine.Pin(11, machine.Pin.IN, machine.Pin.PULL_DOWN)

def drawSelectTriangle(x, y):
    oled.line(x, y, x, y+8, 0xffff)
    oled.line(x, y, x+6, y+4, 0xffff)
    oled.line(x, y+8, x+6, y+4, 0xffff)
   
class SixSidedTimer(object):
    
    def __init__(self):
        print("init")
        self.intro()
        self.state = State.TOP_MENU
        self.selectedMode = "DOWN"
        self.maxTime = 10
        self.players = {}
        for i in range(6):
            playerName = 'Player ' + str(i + 1)
            player = Player(playerName)
            self.players[playerName] = player
        self.activePlayer = self.players["Player 1"]

        pauseButton.irq(trigger=Pin.IRQ_RISING, handler=self.pauseButtonCallback)
        upButton.irq(trigger=Pin.IRQ_RISING, handler=self.upButtonCallback)
        downButton.irq(trigger=Pin.IRQ_RISING, handler=self.downButtonCallback)
        self.optionsLoop()

    def intro(self):
        oled.fill(0)
        oled.text("Welcome", 0, 0)
        oled.show()
        utime.sleep(1)
    
    def optionsLoop(self):
        while True:
            if self.state == State.TOP_MENU:
                self.topMenu()
            if self.state == State.COUNT_DOWN_MENU:
                self.countDownMenu()
            if self.state == State.COUNT_UP_READY:
                self.countUpReady()
            if self.state == State.COUNT_DOWN_READY:
                self.countDownReady()
            if self.state == State.COUNT_DOWN_RUNNING:
                self.countDownRunning()
            if self.state == State.COUNT_DOWN_PAUSED:
                self.countDownPaused()
    
    def topMenu(self):
        while self.state==State.TOP_MENU:
            oled.fill(0)
            oled.text("Select Mode", 0, 0)
            oled.text("Count Down", 8, 16)
            oled.text("Count Up", 8, 32)
            selectedOption = 0;
            if self.selectedMode == "UP":
                selectedOption = 1
            drawSelectTriangle(0, 16 + (16 * selectedOption))
            oled.show()

    def countDownMenu(self):
        oled.fill(0)
        oled.text("Timer Length", 0, 0)
        oled.text(str(self.maxTime) + " Minutes", 8, 16)
        oled.show()
            
    def countUpReady(self):
        oled.fill(0)
        oled.text("Count Up", 0, 0)
        oled.text("Press Start", 0, 16)
        oled.show()
            
    def countDownReady(self):
        oled.fill(0)
        oled.text("Count Down", 0, 0)
        oled.text(str(self.maxTime) + "m / Player", 0, 16)
        oled.text("Press Start", 0, 32)
        oled.show()
            
    def countDownRunning(self):
        self.checkActivePlayer()
        oled.fill(0)
        oled.text(self.activePlayer.name, 0, 0)
        remainingTime = self.maxTime * 60 - self.activePlayer.time
        m, s = divmod(remainingTime, 60)
        oled.text(str(int(m)) + "m" + str(int(s)) + "s", 0, 16)
        oled.show()
        self.activePlayer.time += 1
        utime.sleep(1)

    def countDownPaused(self):
            oled.fill(0)
            oled.text("Count Down", 0, 0)
            oled.text(str(self.maxTime) + "m / Player", 0, 16)
            oled.text("Press Start", 0, 32)
            oled.show()
            
    def pauseButtonTimerCallback(self, t):
        global pauseButtonPressedRecently
        pauseButtonPressedRecently = False
        
    def pauseButtonCallback(self, p):
        global pauseButtonPressedRecently
        if pauseButtonPressedRecently:
            print("ignoring, pressed recently")
        else:
            # Menus
            if self.state==State.TOP_MENU:
                if self.selectedMode == "DOWN":
                    self.state = State.COUNT_DOWN_MENU
                else:
                    self.state = State.COUNT_UP_READY
            elif self.state==State.COUNT_DOWN_MENU:
                self.state = State.COUNT_DOWN_READY
            elif self.state==State.COUNT_DOWN_READY:
                self.state = State.COUNT_DOWN_RUNNING
            elif self.state==State.COUNT_UP_READY:
                self.state = State.COUNT_UP_RUNNING
                
            # Count Down Running <-> Paused
            elif self.state==State.COUNT_DOWN_RUNNING:
                self.state = State.COUNT_DOWN_PAUSED
            elif self.state==State.COUNT_DOWN_PAUSED:
                self.state = State.COUNT_DOWN_RUNNING
              
            # Count Up Running <-> Paused
            elif self.state==State.COUNT_UP_RUNNING:
                self.state = State.COUNT_UP_PAUSED
            elif self.state==State.COUNT_UP_PAUSED:
                self.state = State.COUNT_UP_RUNNING
            pauseButtonPressedRecently = True
            pauseButtonTimer.init(mode=Timer.ONE_SHOT, period=BUTTON_DELAY, callback=self.pauseButtonTimerCallback)


    def upButtonTimerCallback(self, t):
        global upButtonPressedRecently
        upButtonPressedRecently = False
        
    def upButtonCallback(self, p):
        global upButtonPressedRecently
        if upButtonPressedRecently:
            print("ignoring, pressed recently")
        else:
            if self.state==State.TOP_MENU:
                if self.selectedMode == "DOWN":
                    self.selectedMode = "UP"
                else:
                    self.selectedMode = "DOWN"
            if self.state==State.COUNT_DOWN_MENU:
                self.maxTime = self.maxTime + 1
            upButtonPressedRecently = True
            upButtonTimer.init(mode=Timer.ONE_SHOT, period=BUTTON_DELAY, callback=self.upButtonTimerCallback)
            
    def downButtonTimerCallback(self, t):
        global downButtonPressedRecently
        downButtonPressedRecently = False
        
    def downButtonCallback(self, p):
        global downButtonPressedRecently
        if downButtonPressedRecently:
            print("ignoring, pressed recently")
        else:
            if self.state==State.TOP_MENU:
                if self.selectedMode == "DOWN":
                    self.selectedMode = "UP"
                else:
                    self.selectedMode = "DOWN"
            if self.state==State.COUNT_DOWN_MENU:
                self.maxTime = self.maxTime - 1
                if self.maxTime < 0:
                    self.maxTime = 0
            downButtonPressedRecently = True
            downButtonTimer.init(mode=Timer.ONE_SHOT, period=BUTTON_DELAY, callback=self.downButtonTimerCallback)
    
    def checkActivePlayer(self):
       xVal = mpu.readData().Gx
       yVal = mpu.readData().Gy
       zVal = mpu.readData().Gz
       if abs(xVal) > abs(yVal) and abs(xVal) > abs(zVal):
           if xVal > 0:
               self.activePlayer = self.players['Player 1']
           else:
               self.activePlayer = self.players['Player 2']
       elif abs(yVal) > abs(xVal) and abs(yVal) > abs(zVal):
           if yVal > 0:
               self.activePlayer = self.players['Player 3']
           else:
               self.activePlayer = self.players['Player 4']
       else:
           if zVal > 0:
               self.activePlayer = self.players['Player 5']
           else:
               self.activePlayer = self.players['Player 6']
        
sTimer = SixSidedTimer()