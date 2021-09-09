

#------------------------------------------------------------------------------
#  __  __           _   _____     _ _                                        --
# |  \/  | ___  ___| |_|_   _|_ _| | | __                                    --
# | |\/| |/ _ \/ __| '_ \| |/ _` | | |/ /                                    --
# | |  | |  __/\__ \ | | | | (_| | |   <                                     --
# |_|  |_|\___||___/_| |_|_|\__,_|_|_|\_\                                    --
#                                                                            --
#------------------------------------------------------------------------------
# Author: William McEvoy                                                     --
# Created: Sept 8 2021                                                       --
#                                                                            --
# Purpose:  Send and receive messages from a Mesthtastic device.             --
#                                                                            --
#                                                                            --
#------------------------------------------------------------------------------
#  Sept 8, 2021                                                             --
#   - adding formatting and comments                                         --
#   - added ability to scroll through recent non-friendly records            --
#------------------------------------------------------------------------------


import meshtastic
import time
from pubsub import pub

import argparse

import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle

#to help with debugging
import inspect

#--------------------------------------
# Variable Declaration               --
#--------------------------------------

NAME = 'MeshTalk'                   
DESCRIPTION = "Send and recieve messages to a MeshTastic device"
DEBUG = False

parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument('-s', '--send',    type=str,   nargs='?', help="send a text message")
parser.add_argument('-r', '--receive', action='store_true',   help="recieve and display messages")
parser.add_argument('-t', '--time',    type=float, nargs='?', help="seconds to listen before exiting",default = 60)
args = parser.parse_args()


#process arguments and assign values to local variables
if(args.send):
  SendMessage = True
  TheMessage = args.send
else:
  SendMessage = False

if(args.receive):
  ReceiveMessages = True
else:
  ReceiveMessages = False

TimeToSleep = args.time




#interface.sendText("This is your raspberry pi calling") # or sendData to send binary data, see documentations for other options.
#interface.close()


#------------------------------------------------------------------------------
# Functions                                                                  --
#------------------------------------------------------------------------------


def onReceive(packet, interface): # called when a packet arrives
    print("**MESSAGE RECEIVED**")
    
    for key in packet.keys():
      #print("{}".format(key))
      if (key in ('from','to','rxTime')):
        print("{}: {}".format(key,packet[key]))
        
      if (key == 'decoded'):
        Newpacket = packet[key]
        print ("")
        print("===DECODED==============================================")
        for Newkey in Newpacket.keys():
          if Newkey in ("portnum","payload","requestId","user","long_name","short_name","hw_model","macaddr"):
            print("{}: {}".format(Newkey,Newpacket[Newkey]))
        print("========================================================")

    time.sleep(0.25)
    print("\n")
 
def onConnection(interface, topic=pub.AUTO_TOPIC): # called when we (re)connect to the radio
    # defaults to broadcast, specify a destination ID if you wish
    print("Connection established...")
    #interface.sendText("meshtalk 1.0 activated")


#------------------------------------------------------------------------------
# M A I N   P R O C E S S I N G                                               --
#------------------------------------------------------------------------------


print("--MeshTalk 1.0--")


#Instanciate a meshtastic object
#By default will try to find a meshtastic device, otherwise provide a device path like /dev/ttyUSB0
"Finding Meshtastic device..."
interface = meshtastic.SerialInterface()


#subscribe to connection and receive channels
pub.subscribe(onConnection, "meshtastic.connection.established")


#Check for message to be sent
if(SendMessage):
  print("Sending: ",TheMessage)
  interface.sendText(TheMessage)
  print("Message sent")

if(ReceiveMessages):
  print("Listening for:",TimeToSleep," seconds")
  print("Subscribing to interface channels...")
  pub.subscribe(onReceive, "meshtastic.receive")
  time.sleep(TimeToSleep)


interface.close()  
print ("--End of Line------------")
print ("")
