# jisforjt_QT_Py_Duo_Pop.py
# Version: 1.0
# Author(s): James Tobin

######################################################
#   Version Notes
######################################################
'''

'''

######################################################
#   Import
######################################################
import time
import board
import pulseio
import digitalio
import adafruit_irremote
import neopixel
import pwmio


######################################################
#   Global Variables
######################################################
game_round = []
speaker_enabled = False

# The first 19 buzzer pulses are consistant each time you press the buzzers' buttons
BUZZERS = [ [150,  50, 100,  50, 100, 100,  50,  50, 100,  50],    #100,  50, 100, 100,  50,  50, 100, 50, 100],     # Red
            [150,  50, 100,  50, 100,  50, 100, 100,  50,  50],    #100,  50, 100,  50, 100, 100,  50, 50, 100],     # Blue
            [150, 100,  50,  50, 100, 100,  50,  50, 100, 100],     #50,  50, 100, 100,  50,  50, 100, 50, 100],     # Yellow
            [150,  50, 100, 100,  50,  50, 100, 100,  50,  50]]  #, 100, 100,  50,  50, 100, 100,  50, 50, 100] ]    # Green

RED     = (255,   0,   0)
BLUE    = (  0,   0, 255)
YELLOW  = (255, 255,   0)
GREEN   = (  0, 255,   0)
WHITE   = (100, 100, 100)
OFF     = (  0,   0,   0)

pulsein = pulseio.PulseIn(board.D3, maxlen=264, idle_state=True)       #Set Infrared (IR) pin
decoder = adafruit_irremote.NonblockingGenericDecode(pulsein)           #Set infrared (IR) decoder to Adafruit's generic decoder
button = digitalio.DigitalInOut(board.D6)
button.switch_to_input(pull=digitalio.Pull.UP)
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
led = pwmio.PWMOut(board.P1, frequency=5000, duty_cycle=0)
speaker = pwmio.PWMOut(board.SPEAKER, duty_cycle=0, frequency=440, variable_frequency=True)


######################################################
#   Functions
######################################################
def place(buzzer):
    '''
    buzzer ()
    '''
    global game_round
    for i in game_round:
        if buzzer == i:
            return
    game_round.append(buzzer)
    play_tone(1047,1)
    blink(1, 0.2)
    if len(game_round) == 1:
        pixel.fill(buzzer)

def play_tone(tone, duration):
    '''
    Plays a tone for a set duration.

    tone (integer) =  the frequency of the tones/music notes you want to play
    duration (float) = the number of seconds you want to play the tone

     
        tone     music note
        262    =     C4
        294    =     D4
        330    =     E4
        349    =     F4
        392    =     G4
        440    =     A4
        494    =     B4

    examples:
        play_tone(294, 0.5)
        play_tone(349, 1.0)
        play_tone(440, 2.2)
    '''
    global speaker_enabled
    if speaker_enabled == True:
        speaker.frequency = tone
        speaker.duty_cycle = 65535 // 2  # On 50%
        time.sleep(duration)  # On for 1/4 second
        speaker.duty_cycle = 0  # Off

def blink(brightness, duration):
    '''
    Blinks led on and off.

    brightness (float) =  the brightness percentage in decimal from 0.0 to 1.0
    duration (float) = the number of seconds you want to play the tone

     
        brightness      state
            0.1    =     tenth of full brightness
            0.5    =     half of full brightness
            1.0    =     full brightness

    examples:
        blink(0.1, 0.5)
        blink(0.6, 1.0)
        blink(1.0, 2.2)
    '''
    led.duty_cycle = min(65535, max(0.01, (65535 * brightness )))
    time.sleep(duration)  # On for 1/4 second
    led.duty_cycle = 0  # Off

def glow(number_cylces):
    for k in range(number_cylces):
        for i in range(100):
            if i < 50:
                led.duty_cycle = int(i * 2 * 65535 / 100)  # Up
            else:
                led.duty_cycle = 65535 - int((i - 50) * 2 * 65535 / 100)  # Down
            time.sleep(0.01)


######################################################
#   Main Code
######################################################
pixel.fill(WHITE)
blink(1, 1)
print("Round starting...")
while True:
    if button.value == False:
        led.duty_cycle = 65535
        game_round = []
        pixel.fill(WHITE)
        pulsein.clear()         # Clear any unread packets
        play_tone(494,1)
        # Hold down the button for 4 seconds to enable/disable speaker
        if button.value == False:
            time.sleep(3)
            if button.value == False:
                play_tone(262,1)
                speaker_enabled = not speaker_enabled
                print(speaker_enabled)
                play_tone(262,1)
                time.sleep(1)
    led.duty_cycle = 0
    if len(game_round) < 4:
        for packets in decoder.read():
            if packets != None:          
                normalized = []
                packet = list(packets[0])    # A singple full packet from a buzzer will contain 33 pulses
                if len(packet) > 10:
                    # Convert the packet of raw pulses into normalized pulses in 10s of ms
                    for i in packet:
                        if 300 < i <= 700:
                            normalized.append(50)
                        elif 700 < i <= 1300:
                            normalized.append(100)
                        elif 1300 < i < 1700:
                            normalized.append(150)
                    if normalized[0] == 150:    #Confirm that it is a Buzzer
                        if normalized[0:10] == BUZZERS[0]:
                            #print("RED")
                            place(RED)
                        elif normalized[0:10] == BUZZERS[1]:
                            #print("BLUE")
                            place(BLUE)
                        elif normalized[0:10] == BUZZERS[2]:
                            #print("YELLOW")
                            place(YELLOW)
                        elif normalized[0:10] == BUZZERS[3]:
                            #print("GREEN")
                            place(GREEN)
    else:
        print("Round places are:")
        print(game_round)
        pixel.fill(OFF)
        play_tone(349,2)
        while button.value == True:
            for i in game_round:
                pixel.fill(i)
                blink(1, 0.5)
                time.sleep(0.5)
                if button.value == False:       # Quick check so that the user does not have to whate for all the colors to cycle
                    break
            pixel.fill(OFF)
            #blink(1, 0.5)
            time.sleep(1)

