class Player:

    def __init__(self, name):
        self.name = name
        self.time = 0.0

from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import mpu6050 # import MPU6050
import utime

led = Pin(28, Pin.OUT)
led.low()


# Init Display
i2c = I2C(0,sda=Pin(4),scl=Pin(5),freq=40000)
oled = SSD1306_I2C(128,64,i2c)
print("Before")
mpu = mpu6050.MPU6050(0, 0x68, scl=Pin(5), sda=Pin(4))
#mpu.setSampleRate(200)
#mpu.setGResolution(2)
print("Here")

players = {}
for i in range(6):
    playerName = 'Player ' + (i + 1)
    player = new Player(playerName)
    players[playerName] = player
while True:
   led.toggle()
   print("Toggle")
   oled.fill(0)
   xVal = mpu.readData().Gx
   yVal = mpu.readData().Gy
   zVal = mpu.readData().Gz
   if abs(xVal) > abs(yVal) and abs(xVal) > abs(zVal):
       if xVal > 0:
           player = players['Player 1']
       else:
           player = players['Player 2']
   elif abs(yVal) > abs(xVal) and abs(yVal) > abs(zVal):
       if yVal > 0:
           player = players['Player 3']
       else:
           player = players['Player 4']
   else:
       if zVal > 0:
           player = players['Player 5']
       else:
           player = players['Player 6']
   player.time += 1
   oled.text(player.name,0,0)
   oled.text(player.time,0,16)
   #oled.text(str(yVal),0,32)
   #oled.text(str(zVal),0,48)
   oled.show()
   utime.sleep(1)
   
   #0x78