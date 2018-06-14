import qrtools

qr_path = '/home/pi/Desktop/myQR.png'

def med_list(code):
	array = code.split(',')
	med_len = int(len(array)/2)
	answer = {}
	for i in range(med_len):
		answer[array[i*2]] = int(array[(i*2) + 1])
	return answer

def decode_qr(filename):
	qr = qrtools.QR()
	qr.decode(filename)
	return qr.data

code = decode_qr(qr_path)
med_dict = med_list(code)
print med_dict

for i in med_dict:
	spin_motor(i,med_dict[i])
	#function for spinning motor.
	pass
	
"""
dependencies: pip install pypng

Still if any issues in reading the QR code refer to: https://stackoverflow.com/questions/27233351/how-to-decode-a-qr-code-image-in-preferably-pure-python

In case of error : Exception: tostring() has been removed. 
Do: edit line 181 of /usr/lib/python2.7/dist-packages/qrtools.py (location may vary) and replace "tostring" with "tobytes". 
"""

