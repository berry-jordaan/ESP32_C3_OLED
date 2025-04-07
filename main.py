'''
The framebuffer is actually a 1-bit framebuffer, so the width and height
are 128 x 64, multiple of 8.

The ssd1306 driver is a subclass of the framebuf module, and this implementation will automatically 
offset the framebuffer by 28 pixels in the x direction and 24 pixels in the y direction.

Tested with the ESP32_GENERIC_C3-20241129-v1.24.1.bin firmware.

Make sure you have the **esp32_c3_oled.py** driver in the same directory as this file on your **EPS32-C3-OLED** board, 
so upload both the main and the esp32_c3_oled.py file to the board.
No fonts are supported and you can only draw 3 rows of text at a time.
'''
# ESP32-C3-OLED MicroPython Code
import machine
import time
import esp32_c3_oled as ssd1306

# Configure LED pin (Common LED pin on ESP32-C3 is 8)
led = machine.Pin(8, machine.Pin.OUT)

i2c = machine.SoftI2C(scl=machine.Pin(6), sda=machine.Pin(5)) # getting the correrct pins for the ESP32-C3 can be a chore
oled = ssd1306.ESP32_C3_OLED(i2c, external_vcc=False)
oled.fill(0) # fill the sceen with black
oled.rect(0, 0, 72, 40, 1) # draw a white border around the parimiter of the screen
oled.text("Hello ", 2, 2) # Say hello
oled.text("World", 2, 13) # Say world
oled.text("Foo Bar!", 2, 24) # Say foo bar
oled.line(3, 35, 69, 35, 1) # horizontal line at the bottom

# Face :)
oled.ellipse(56, 11, 10, 8, 1) # White eclipse
oled.ellipse(60, 10, 3, 3, 0) # Right eye
oled.pixel(60, 10, 1) # right eye pupil
oled.ellipse(52, 10, 3, 3, 0) # Left eye
oled.pixel(52, 10, 1) # left eye pupil
oled.rect(54, 15, 6, 2, 0) # mouth

def flash_led(): # flash the LED
    led.on()
    time.sleep(0.02)
    led.off()

counter = 0

# draw at 25 frames per second (0.02 pause per frame and 0.02 pause for the LED)
while True:
    counter = counter + 1 # increment the counter
    if counter > 67:
        counter = 0
        oled.rect(1, 36, 69, 2, 0) # clear the bottom line
    oled.hline( 3, 37, counter, 1) # draw a white bar at the bottom. Looks like a loader bar :)

    # clear the mouth
    oled.fill_rect(54, 14, 6, 5, 1) # clear the mouth area by filling it with white
    oled.fill_rect(54, 15, 6, counter % 3 + 2, 0) # animate the mouth

    oled.show() # draw to the screen
    flash_led() # Flash the LED when the fame redraws
    time.sleep(0.02) # slight pause 
    