import pyqrcode
import png
def qrcode():
	q = pyqrcode.create('pcn,2,crs,3')
	q.png('myQR.png',scale=6)
	print ('QR CODE generated')
if __name__ =='__main__':
	qrcode()

