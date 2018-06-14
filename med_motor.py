def rotate_motor(i):
	import RPi.GPIO as GPIO
	import time

	GPIO.setmode(GPIO.BOARD)

	GPIO.setup(i,GPIO.OUT)

	p=GPIO.PWM(i,50)
	p.start(7.5)

	try:
		while True:
			p.ChangeDutyCycle(7.5)
			time.sleep(1)
			p.ChangeDutyCycle(12.5)
			time.sleep(1)
			p.ChangeDutyCycle(2.5)
			time.sleep(1)

	except KeyboardInterrupt:
		p.stop()

		GPIO.cleanup()
def spin_motor(i,j):
	for numRev in range (1,1,j):
		rotate_motor(i)
spin_motor(i,j)  

