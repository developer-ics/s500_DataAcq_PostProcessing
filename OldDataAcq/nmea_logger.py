import serial
import datetime
import os
from datetime import date

#serialPort = serial.Serial(
#port='/dev/ttyACM0', baudrate=115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
#)

with serial.Serial(
port='/dev/ttyACM1', baudrate=115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
) as ser:
    currTS2 = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    today = date.today()
    d4=today.strftime("%m-%d-%Y")
    path="./Data/nmeadata/" + d4
    isExist = os.path.exists(path)
    if not isExist:
        os.mkdir(path)
        print("Made Directory" + path)
  
    file_name = "./Data/nmeadata/" + d4 + "/" + currTS2 + ".dat"
    file1 = open(file_name, 'w')
    line_num=1
    lines_per_file=100
    # read  lines from the serial output
    while 1:
        line = ser.readline().decode('ascii', errors='replace')
        line_num = line_num + 1
        datestr=str(datetime.datetime.now())
        file1.write('###' + datestr)

     
        print('###'+datestr+line.strip()) 
        file1.writelines(line)
        if (line_num % lines_per_file) == 0:
            file1.close()
            currTS2 = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = "./Data/nmeadata/" + d4 + "/" + currTS2 + ".dat"
            file1 = open(file_name, 'w')
