import serial
import datetime
import os
import csv
import math
import re
import operator
import math
from functools import reduce  
from datetime import date
from struct import *

# might need
#sudo adduser newuser dialout

#sonar
serialPort = serial.Serial(
port='/dev/ttyACM0', baudrate=115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
)
serialString = ""  # Used to hold data coming over UART
# 2nd port for writing nmea data ot
ser = serial.Serial('/dev/ttyS0', baudrate=9600, bytesize=8, timeout=0.25,stopbits=serial.STOPBITS_ONE)
#ser = serial.Serial('/dev/ttyAMA0', baudrate=9600, bytesize=8, timeout=0.25,stopbits=serial.STOPBITS_ONE)


# look for the parameter table and read values
# Specify path
path = './sonar_param.csv'
   
# Check whether the specified
# path exists or not
isExist = os.path.exists(path)
print(path, ' exsists ' ,isExist)

if isExist:
    with open('./sonar_param.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        header = []
        header = next(csv_reader)
        print('Table Values:')
        print(header)
        
        # start range
        row1 = next(csv_reader)
        start_mm=int(row1[1])
        print([row1[0] ,start_mm])
        
        # total range
        row2 = next(csv_reader)
        length_mm=int(row2[1])
        print([row2[0] ,length_mm])
        
        # time between ping
        row3 = next(csv_reader)
        msec_per_ping=int(row3[1])
        print([row3[0] ,msec_per_ping])

        #check timne to make sure request isn't too fast
        if length_mm  <= 2000:
            min_msec_per_ping=100
        elif (length_mm>2000 and length_mm<=15000):
            min_msec_per_ping=200
        elif (length_mm>15000 and  length_mm<=50000):
            min_msec_per_ping=300
        elif (length_mm>50000 and  length_mm<=75000):
            min_msec_per_ping=400
        elif (length_mm>75000 and  length_mm<=100000):
            min_msec_per_ping=500
        elif (length_mm>100000 and  length_mm<=140000):
            min_msec_per_ping=800
        elif (length_mm>140000 ):
            print('MAXIMUM RANGE OF 140 M EXCEEDED. SETTING RANGE TO 140 m')
            min_msec_per_ping=800
            length_mm=140000
        print('min_msec_per_ping=', min_msec_per_ping)
else:
    start_mm=0
    length_mm=10000
    msec_per_ping=200
    print('Default Values:')
    print('start_mm=',start_mm)
    print('length_mm=',length_mm)
    print('msec_per_ping',msec_per_ping)
    
if msec_per_ping<min_msec_per_ping:
    msec_per_ping=min_msec_per_ping
    
print('Used Values:')
print('start_mm =',start_mm)
print('length_mm =',length_mm)
print('msec_per_ping = ',msec_per_ping)



print('configuring sonar')
# configure the sonar with some parameters not in table set here
payload_length=20
msg_id=1015
gain_index=-1
ping_duration_usec=0
report_id=1308 # set to zero to stop
num_results_requested=0
chirp=1
decimation=0
packet = bytearray()
packet.append(ord('B'))#B
packet.append(ord('R'))#R
packet.extend(payload_length.to_bytes(2,'little'))
#packet.append(2)#payload length 2
#packet.append(0)#payload length 1
packet.extend(msg_id.to_bytes(2,'little'))
packet.append(0x00)#src
packet.append(0x00)#dst
packet.extend(start_mm.to_bytes(4,'little'))
packet.extend(length_mm.to_bytes(4,'little'))
packet.extend(gain_index.to_bytes(2,'little', signed=True))
packet.extend(msec_per_ping.to_bytes(2,'little'))
packet.extend(ping_duration_usec.to_bytes(2,'little'))
packet.extend(report_id.to_bytes(2,'little'))
packet.extend(num_results_requested.to_bytes(2,'little'))
packet.extend(chirp.to_bytes(1,'little'))
packet.extend(decimation.to_bytes(1,'little'))

chksum=sum(packet)
packet.extend(chksum.to_bytes(2,'little'))#chksum 2
print(packet.hex('_'))
serialPort.write(packet)

print('done configuring sonar')



#resp=serialPort.read(13)
##print(resp)
#current_datetime = datetime.datetime.now()
#str_current_datetime = str(current_datetime)
currTS2 = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
currTS2 = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
today = date.today()
d4=today.strftime("%m-%d-%Y")
path="./Data/s500/" + d4
isExist = os.path.exists(path)
if not isExist:
    os.mkdir(path)
    print("Made Directory" + path)
  
# create a file object along with extension
file_name = "./Data/s500/" + d4 + "/" + currTS2 + ".dat"
file1 = open(file_name, 'wb')
#file1 = open(r"Data.dat", "wb")
pings_per_file=500
pings_per_print=10
ping_num=1
BRstr='BR'
while 1:
# Wait until there is data waiting in the serial buffer
    if serialPort.in_waiting > 0:
        res1 = serialPort.read(1)
            ##	if not res1:
        ##		file1.close()
        ##		print('End Of File')
        ##		break
        #print(res1)
        file1.write(res1)

        if (res1 == bytes('B','ascii')):
            res2 = serialPort.read(1)
            file1.write(res2)
            if (res2 == bytes('R','ascii')):
                

                datestr=str(datetime.datetime.now())
                ping_num = ping_num + 1
                if (ping_num % pings_per_print) == 0:
                    print(ping_num)
                    print(datestr)
                file1.write(datestr.encode("utf-8"))
                ## decode bytes
                res = serialPort.read(2)
                file1.write(res)
                packet_len=int.from_bytes(res,byteorder='little')
                #print('packet_len=' + str(packet_len))
                res = serialPort.read(2)
                file1.write(res)
                packet_id =int.from_bytes(res,byteorder='little')
                #print('packet_id=' + str(packet_id))

                res = serialPort.read(2)
                file1.write(res)
                if packet_id==1308:
                    fres=serialPort.read(packet_len)
                    file1.write(fres)
                    #print(fres)
                    ping_number =unpack('<I',fres[0:4])
                    this_ping_depth_m=unpack('<f',fres[48:52])
                    smooth_depth_m =unpack('<f',fres[52:56])
                    
                    tst=0
                    if tst:
                        depth = 10+8*math.sin(ping_num/50)
                        
                        print('test nmea depth genereated')
                    else:
                        
                        #start_mm =unpack('<I',fres[4:8])
                        #length__mm =unpack('<I',fres[8:12])
                        #start_ping_hz=unpack('<I',fres[12:16])
                        #end_ping_hz =unpack('<I',fres[16:20])
                        #adc_sample_hz=unpack('<I',fres[20:24])
                        #timestamp_msec=unpack('<I',fres[24:28])
                        #spare2 =unpack('<I',fres[28:32])
                        #pulse_duration_sec =unpack('<f',fres[32:36])
                        #analog_gain =unpack('<f',fres[36:40])
                        #max_pwr_db =unpack('<f',fres[40:44])
                        #min_pwr_db =unpack('<f',fres[44:48])
                        

                        #print('ping_number = ' + '%d'  %ping_number)
                        #print(length_mm)
                        #print(pulse_duration_sec)
                        #print('this_ping_depth_m = ' + '%.3f' %this_ping_depth_m)
                        #print(smooth_depth_m)
                        depth=this_ping_depth_m
                
                        #print(depth)
                        #depth_feet=depth*3.28084
                        #depth_fathoms=depth*.546807
                        # nmeadepth=(f'SDDBT,'+'%.3f' %depth_feet+ ',f,'+'%.3f' %depth+',M,'+'%.3f' %depth_fathoms+',F')
                    #make the nema string
                    nmeadepth=(f'SDDPT,'+'%04.1f' %depth+',M,0,0')
                    

                    #calculated_checksum = reduce(operator.xor, (ord(s) for s in nmeadepth), 0)
                    calculated_checksum = reduce(operator.xor, (ord(s) for s in nmeadepth), 0)

                           # wstr = '$'+ nmeadepth + '*' + str(calculated_checksum).zfill(2) + '\r\n'
                    wstr = '$'+ nmeadepth + '*' + str(calculated_checksum).zfill(2) + '\r\n'

                    #print(wstr) 
                    ser.write(bytes(wstr,'utf-8'))
                if  (ping_num % pings_per_print) == 0:
                    print('packet_id=' + str(packet_id))
                    print('packet_len=' + str(packet_len))
                    print('ping_number = ' + '%d'  %ping_number)
                    print('this_ping_depth_m = ' + '%.3f' %this_ping_depth_m)
                    print('nmea_string = ' + wstr) 

                if (ping_num % pings_per_file) == 0:
                    file1.close()
                    currTS2 = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    file_name = "./Data/s500/" + d4 + "/" + currTS2 + ".dat"
                    file1 = open(file_name, 'wb')
                    print(file_name)
                    file1.write(BRstr.encode("utf-8"))
                    file1.write(datestr.encode("utf-8")) 


file1.close()
serialPort.close()

