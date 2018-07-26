#!/usr/bin/env python

#Library
import RPi.GPIO as GPIO        
from time import sleep
import picamera
import gpiozero
import os
import qrtools
import Adafruit_CharLCD as LCD
from pad4pi import rpi_gpio
import time
import sys
import urllib
import urllib2

"""
IMPORTANT AND EXTREMELY URGENT:
    * Replace sys.exit functions with pointers redirecting back to initial functions
    * Powering at startup should show developer options: log cases
"""

cancelFlag = 0

# Setup Keypad
KEYPAD = [
        ["1","2","3","A"],
        ["4","5","6","B"],
        ["7","8","9","C"],
        ["*","0","#","D"]
]

buffer = ""

flagA = 0
flagB = 0
flagC = 0
OTC_med_list_input = []

payment_url = "http://p-y.tm/z1h84sqsg"
txtMsg = 'Thank you for choosing MediSpencer! Please click on the link to complete your payment via PayTM: %s' % payment_url

quant_available = {'crocin': 10, 'paracetamol': 10, 'vix': 10, 'abc': 10,'xyz':10 }
print("Initialising...")

#functions
#converting string from qr code to input dict.
def decode_string(qr):
    med_list_input = {}
    temp = qr.split(',')
    for word in range(int(len(temp)/2)):
            med_list_input[temp[2*word]] = int((temp[2*word+1]))
    return med_list_input

#meds that will come out, need to calculate as whole quantity may not be present at all times.
def meds_output(med_list_input,quant_available):
    output_meds = {}
    for med in med_list_input:
            if (quant_available[med] >= med_list_input[med]):
                    output_meds[med] = med_list_input[med]
            else:
                    output_meds[med] = quant_available[med]
    return output_meds

#updating quantity available in machine
def update_quant(med_list,quant_available):
    for med in med_list:
            quant_available[med] = quant_available[med] - med_list[med]
            if quant_available[med]<0:
                    quant_available[med] = 0
    return quant_available

#calculating price of the medicines
def price(output_meds,cost_list):
    price = 0	
    for med in output_meds:
            temp = output_meds[med]*cost_list[med]
            price = price + temp
    return price

#display for user
#lcd_display(string):

#some payment fucntion
#idk how... help.. pilij

#To spin correct motors required number of times
def execute_motors(outpin,NOT):
    '''pwm = GPIO.PWM(outpin,50)              
    pwm.start(0)                             
    for run in range(NOT):
            duty = 360/18 +2
            GPIO.output(outpin,True)
            pwm.ChangeDutyCycle(duty)
            sleep(1)
            GPIO.output(03,False)
            pwm.ChangeDutyCycle(0)
            pwm.stop()
    return None'''
    """
    servo = gpiozero.Servo(outpin)
    for i in range(2*NOT):
            servo.min()	
            sleep(1)
            servo.max()
            sleep(1)
    """
    servo = gpiozero.Servo(outpin,min_pulse_width=0.0005,max_pulse_width=0.001)
    print(servo.value)
    servo.min()
    print(servo.value)

    for i in range(NOT):
            if (i%2 ==0):
                    print("Dispensing one unit...")
                    servo.min()
                    print(servo.value)
                    sleep(1)
                    servo.max()
                    print(servo.value)
                    sleep(1)
                    
            else:
                    print("Dispensing one unit...")
                    servo.min()
                    print(servo.value)
                    sleep(1)
                    servo.max()
                    print(servo.value)
                    sleep(1)

#scanning qr code
def decode_qr(filename):
    qr = qrtools.QR()
    qr.decode(filename)
    q = qr.data
    x = str(q)
    return x

def sendSMS(apikey, numbers, sender, message):
    data =  urllib.urlencode({'apikey': apikey, 'numbers': numbers,
        'message' : message, 'sender': sender})
    data = data.encode('utf-8')
    request = urllib2.Request("https://api.textlocal.in/send/?",data)
    f = urllib2.urlopen(request)
    fr = f.read()
    return(fr)

def getKeyboardInput():
  return buffer

def play_conveyor(n,time):
    for i in range(n):
                GPIO.output(21,1)
                sleep(time)
                GPIO.output(21,0)
                sleep(time)

def printKey(key):
  global txtMsg
  global buffer
  global flagA
  global flagB
  global flagC
  global OTC_med_list_input
  
  if (key=="1"):
    buffer = buffer + "1"
  elif (key=="2"):
    buffer = buffer + "2"
  elif (key=="3"):
    buffer = buffer + "3"
  elif (key=="4"):
    buffer = buffer + "4"
  elif (key=="5"):
    buffer = buffer + "5"
  elif (key=="6"):
    buffer = buffer + "6"
  elif (key=="7"):
    buffer = buffer + "7"
  elif (key=="8"):
    buffer = buffer + "8"
  elif (key=="9"):
    buffer = buffer + "9"
  elif (key=="0"):
    buffer = buffer + "0"
  elif (key=="A"):
    # OK/Enter key
    if flagA == 1 and flagC == 0:
        # Entire OTC medicine functionality
        buffer = ""
        OTC_med_list_input = []
        # Make user enter OTC_med_list_input
        lcd_display(0x01,LCD_CMD)
        lcd_string("Press medicine number then press A: ",LCD_LINE_1)
        lcd_string("B: Cancel, C: Clear, D: Dispense",LCD_LINE_2)
        key = " "
        #keypad.registerKeyPressHandler(printKey)
        try:
            while(key != "A"):
                lcd_display(0x01,LCD_CMD)
                msg = "Press medicine number then press A: %s" % getKeyboardInput()
                print(msg)
                lcd_string(msg,LCD_LINE_1)
                lcd_string("B: Cancel, C: Clear, D: Dispense",LCD_LINE_2)
                time.sleep(0.2)
        except:
            keypad.cleanup()

        OTC_key = {1:'paracetamol',2:'crocin'}
        OTC_med_list_input.append(OTC_key[buffer])
        flagC = 1 # makes key A inactive after entering medicine name
        OTC_med_list_input.append('1')
        """
        lcd_display(0x01,LCD_CMD)
        lcd_string("Press quantity then press D: ",LCD_LINE_1)
        key = " "
        try:
            while(key != "A"):
                time.sleep(0.2)

        med_list_input.append(getKeyboardInput())
        """
        OTCFunc(OTC_med_list_input)
        
    if flagB == 1 and flagC == 0:
        s = getKeyboardInput()
        s = "91" + s
        print("Sending SMS to number below:")
        print(s)
        resp =  sendSMS('mX3zFqrzu/w-eB5Dd1oPc9g3nKPnvD9sQ8VV31uV6H',
                    s,
                    'TXTLCL',
                    txtMsg)
        print (resp)
        flagB = 1
  elif (key=="B"):
    # Cancel key
    print("Ending process...")
    print("Goodbye!")
    main()
  elif (key=="C"):
    # Clear key
    print("Clearing buffer")
    buffer = ""
  elif (key=="D"):
    # Unused
    pass
  else:
    print("Invalid key value received in buffer")
    pass

  if len(buffer) > 10:
    buffer = buffer[len(buffer)-10:]
  print(buffer)

def OTCFunc(OTC_med_list_input):
    global quant_available
    OTC_cost_list = {'crocin': 200, 'paracetamol': 300}
    OTC_quant_available = {'crocin': 10, 'paracetamol': 10}
    OTC_motor_map = {'crocin':27, 'paracetamol':2}

    final_med_list = meds_output(OTC_med_list_input,OTC_quant_available)
    # SYNCHRONIZE OTC LISTS AND REGULAR LISTS
    quant_available = update_quant(OTC_med_list_input,OTC_quant_available)
    price = price(final_med_list,OTC_cost_list)
    print("Price calculated.")
    print (price)
    dispenseAndPay(price,final_med_list,motor_map)
    lcd_display(0x01,LCD_CMD)
    lcd_string("Thanks for using MedSpenser!",LCD_LINE_1)
    lcd_string("Rate us on the App Store!",LCD_LINE_2)
    main()

def lcd_init():
  # Define some device constants
  LCD_WIDTH = 16    # Maximum characters per line
  LCD_CHR = True
  LCD_CMD = False
  
  # Timing constants
  E_PULSE = 0.0005
  E_DELAY = 0.0005
  
  lcd_display(0x28,LCD_CMD) # Selecting 4 - bit mode with two rows
  lcd_display(0x0C,LCD_CMD) # Display On,Cursor Off, Blink Off
  lcd_display(0x01,LCD_CMD) # Clear display

  sleep(E_DELAY)
 
def lcd_display(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command
 
  # Define GPIO to LCD mapping
  LCD_RS = 5
  LCD_E  = 6
  LCD_D4 = 7
  LCD_D5 = 8
  LCD_D6 = 9
  LCD_D7 = 10
   
  # Define some device constants
  LCD_WIDTH = 16    # Maximum characters per line
  LCD_CHR = True
  LCD_CMD = False
   
  LCD_LINE_1 = 0x81 # LCD RAM address for the 1st line
  LCD_LINE_2 = 0xC1 # LCD RAM address for the 2nd line
   
  # Timing constants
  E_PULSE = 0.0005
  E_DELAY = 0.0005
  
  GPIO.output(LCD_RS, mode) # RS
  
  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)
  
  # Toggle 'Enable' pin
  lcd_toggle_enable()
  
  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)
  
  # Toggle 'Enable' pin
  lcd_toggle_enable()
  
 
def lcd_toggle_enable():
  # Define GPIO to LCD mapping
  LCD_RS = 5
  LCD_E  = 6
  LCD_D4 = 7
  LCD_D5 = 8
  LCD_D6 = 9
  LCD_D7 = 10

  # Timing constants
  E_PULSE = 0.0005
  E_DELAY = 0.0005
  
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)
 
def lcd_string(message,line):
  # Define some device constants
  LCD_WIDTH = 16    # Maximum characters per line
  LCD_CHR = True
  LCD_CMD = False

  # Send string to display
  message = message.ljust(LCD_WIDTH," ")
  lcd_display(line, LCD_CMD)
  
  for i in range(LCD_WIDTH):
    lcd_display(ord(message[i]),LCD_CHR)

def dispenseAndPay(price,final_med_list,motor_map):
    lcd_display(0x01,LCD_CMD)
    msg = "Amount: %s " % str(price)
    lcd_string(msg,LCD_LINE_1)
    lcd_string("Enter mobile number: ",LCD_LINE_2)

    keypad.registerKeyPressHandler(printKey)
    buffer = ""
    try:
        while(True):
            time.sleep(0.2)
    except:
        keypad.cleanup()
    
    #A fucntion which responds when payment is done
    #spining motor
    """
    try:
      while(True):
        if flagB == 1:
            break
        else:
            time.sleep(0.2)
    except:
     keypad.cleanup()
    """

    for med in final_med_list:
        if (med == 'xyz'):
            t = 5
            play_conveyor(final_med_list[med],1)
        else:
            
            execute_motors(motor_map[med],final_med_list[med])
    print("All done. About to test output now.")
    #test output
    print (final_med_list)
    
    

#print("Functions defined.")

def main():
    
    print("Getting to the task at hand...")
    
    #Setup
    GPIO.setmode(11)
    GPIO.setwarnings(False)
    GPIO.setup(21,GPIO.OUT)
    
    global buffer
    global flagA
    global flagB
    global flagC
    global OTC_med_list_input
    global quant_available
    
    flagA = 0
    flagB = 0
    flagC = 0
    buffer = ""
    OTC_med_list_input = []
			
    qr_path = '/home/pi/Desktop/picampics/myqr.png'

    # LCD pin setup
    # Define GPIO to LCD mapping
    LCD_RS = 5
    LCD_E  = 6
    LCD_D4 = 7
    LCD_D5 = 8
    LCD_D6 = 9
    LCD_D7 = 10
     
    # Define some device constants
    LCD_WIDTH = 16    # Maximum characters per line
    LCD_CHR = True
    LCD_CMD = False
     
    LCD_LINE_1 = 0x81 # LCD RAM address for the 1st line
    LCD_LINE_2 = 0xC1 # LCD RAM address for the 2nd line
     
    # Timing constants
    E_PULSE = 0.0005
    E_DELAY = 0.0005

    GPIO.setup(LCD_E, GPIO.OUT)  # E
    GPIO.setup(LCD_RS, GPIO.OUT) # RS
    GPIO.setup(LCD_D4, GPIO.OUT) # DB4
    GPIO.setup(LCD_D5, GPIO.OUT) # DB5
    GPIO.setup(LCD_D6, GPIO.OUT) # DB6
    GPIO.setup(LCD_D7, GPIO.OUT) # DB7

    lcd_init()
    
    """
    lcd_rs = 12
    lcd_en = 25
    lcd_d4 = 21
    lcd_d5 = 16
    lcd_d6 = 20
    lcd_d7 = 26
    lcd_backlight = 2

    # Define LCD column and row size for 16x2 LCD.
    lcd_columns = 16
    lcd_rows = 2

    lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)
    lcd.clear()
    """
    #camera = picamera.PiCamera()
    print("Setup complete.")
    
    #constants
    # String from qr, required in this code coz kamera nahi hai
    string = 'crocin,2,paracetamol,3,vix,15'
    #cost of meds
    cost_list = {'crocin': 200, 'paracetamol': 300, 'vix': 10, 'abc':0,'xyz': 50}
    #quant in machine initially
    quant_available = {'crocin': 10, 'paracetamol': 10, 'vix': 10, 'abc': 10,'xyz':10 }
    #motor mapping dict
    motor_map = {'crocin':27, 'paracetamol':2, 'vix':3, 'abc':4, 'xyz':22 }
    #print("Values taken into account")
    
    # same as calling: factory.create_4_by_4_keypad, still we put here fyi:
    ROW_PINS = [11, 12, 13, 14]# BCM numbering
    COL_PINS = [15, 16, 17, 18] # BCM numbering
    
    factory = rpi_gpio.KeypadFactory()
    
    # Try factory.create_4_by_3_keypad
    # and factory.create_4_by_4_keypad for reasonable defaults
    keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)
    
    #keypad.cleanup()
    '''
    Phase 1

    1) lcd_display ('plz press the button )
    2) user presses the button
    3) camera activates and takes pic
    '''
    """
    lcd.clear()
    lcd.message('Press OK to proceed\nShow QR Code to cam')
    """
    
    #Waiting for button to be pressed
    keypad.registerKeyPressHandler(printKey)

    """
    Keypad flow:
    Default value of flag is 0
    Flag is set to 1 to break out of infinite loop when A is pressed to switch camera on
    Flag remains 1 thereafter
    Flag is set to 
    Flag is set to 2 when A is pressed to confirm input of mobile number
    """
    """

    try:
      while(True):
        if flagA == 1:
            break
        else:
            time.sleep(0.2)
    except:
     keypad.cleanup()
    """
    print("About to be active...")
    try:
        while(True):
            print("Active as hell")
            
            flagA = 1 # Flag for OTC mode
            GPIO.setup(LCD_RS, GPIO.OUT) # RS
            lcd_display(0x01,LCD_CMD)
            print("Seems to break here")
            lcd_string("Welcome to MedSpenser!",LCD_LINE_1)
            print("Shit")
            lcd_string("Show QR code to cam",LCD_LINE_2)
            print("Show QR code to cam")
            
            #Capturing image
            print("Ready to capture QR code")
            os.system('raspistill -o /home/pi/Desktop/picampics/myqr.png')
            lcd_display(0x01,LCD_CMD)
            lcd_string("Press A to get OTC med",LCD_LINE_1)
            lcd_string("Or show QR code to cam",LCD_LINE_2)
            #saving string
            time.sleep(0.1)
            string = decode_qr(qr_path)
            #print("String decoded.")
            print("QR extracted.")
            print("Extracted text: %s" % string)
            '''
            Phase 2

            1)decode qr
            2)create output med list
            3)calculate price
            '''
            if string == "NULL":
                print("There seems to be no QR code in front of the camera. Activating camera...")
                lcd_display(0x01,LCD_CMD)
                lcd_string("I'm waiting to be used!",LCD_LINE_1)
                lcd_string("Please show valid QR code", LCD_LINE_2)
                time.sleep(3)
            else:
                print("Continuing ahead...")
                break           
            
    except:
        keypad.cleanup()

    flagA = 0
    '''
    Phase 3

    1) lcd displays price
    2) user pays SOMEHOW
    3) motors go round round round
    '''
    #Creating input dictionary
    med_list_input = decode_string(string)
    #Creating final dictionary
    final_med_list = meds_output(med_list_input,quant_available)
    #Updating quantity available
    quant_available = update_quant(med_list_input,quant_available)
    #Calculating price
    price = price(final_med_list,cost_list)
    print("Price calculated.")
    print (price)
    time.sleep(1)
    dispenseAndPay(price,final_med_list,motor_map)
    print (med_list_input)
    print (quant_available)

if __name__ == "__main__":
                  try:
                      main()
                  except KeyboardInterrupt:
                      print(": Ctrl+C external interrupt executed.")
                  finally:
                      print("Something seems wrong with the machine.")
                      
