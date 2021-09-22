

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
#  Sept 8, 2021                                                              --
#   - adding formatting and comments                                         --
#------------------------------------------------------------------------------
#  Sept 10, 2021                                                             --
#   - added Curses based text interface                                      --
#   - class and function was created for GPSProbe                            --
#------------------------------------------------------------------------------
#  Sept 10, 2021                                                             --
#   - added recursive function to decode packets of packets                  --
#------------------------------------------------------------------------------
#                                                                            --
# Credit to other projects:                                                  --
# 
#  Intercepting SIGINT and CTL-C in Curses                                   --
#  - https://gnosis.cx/publish/programming/charming_python_6.html            --
#                                                                            --
#  Meshtastic-python                                                         --
#  - https://github.com/meshtastic/Meshtastic-python                         --
#------------------------------------------------------------------------------





import meshtastic
import time
from datetime import datetime
import traceback
from meshtastic.mesh_pb2 import _HARDWAREMODEL, HardwareModel
from pubsub import pub
import argparse
import collections
import sys
import os

#to help with debugging
import inspect

#For capturing keypresses and drawing text boxes
import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle

#for capturing ctl-c
from signal import signal, SIGINT
from sys import exit

#------------------------------------------------------------------------------
# Variable Declaration                                                       --
#------------------------------------------------------------------------------

NAME = 'MeshTalk'                   
DESCRIPTION = "Send and recieve messages to a MeshTastic device"
DEBUG = False

parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument('-s', '--send',    type=str,   nargs='?', help="send a text message")
parser.add_argument('-t', '--time',    type=int, nargs='?', help="seconds to listen before exiting",default = 36000)
args = parser.parse_args()

#This will now be the default behaviour
#parser.add_argument('-r', '--receive', action='store_true',   help="recieve and display messages")



#process arguments and assign values to local variables
if(args.send):
  SendMessage = True
  TheMessage = args.send
else:
  SendMessage = False

#if(args.receive):
#  ReceiveMessages = True
#else:
#  ReceiveMessages = False

TimeToSleep = args.time


#------------------------------------------------------------------------------
# Initialize Curses                                                          --
#------------------------------------------------------------------------------

#Text windows
#stdscr = curses.initscr()

#hide the cursor
#curses.curs_set(0)

global PrintSleep    #controls how fast the screens scroll
global OldPrintSleep #controls how fast the screens scroll
global TitleWindow
global StatusWindow
global Window1
global Window2
global Window3
global Window4
global Window5
global Window6
global Pad1
global IPAddress
global Interface
global DeviceStatus
global DeviceName
global DevicePort
global PacketsReceived
global PacketsSent
global LastPacketType
global HardwareModel
global MacAddress
global DeviceID
global BatteryLevel
global PauseOutput

PrintSleep    = 0.1
OldPrintSleep = PrintSleep

#------------------------------------------------------------------------------
# Functions / Classes                                                        --
#------------------------------------------------------------------------------

class TextWindow(object):
  def __init__(self,name, rows,columns,y1,x1,y2,x2,ShowBorder,BorderColor,TitleColor):
    self.name              = name
    self.rows              = rows
    self.columns           = columns
    self.y1                = y1
    self.x1                = x1
    self.y2                = y2
    self.x2                = x2
    self.ShowBorder        = ShowBorder
    self.BorderColor       = BorderColor #pre defined text colors 1-7
    self.TextWindow        = curses.newwin(self.rows,self.columns,self.y1,self.x1)
    self.CurrentRow        = 1
    self.StartColumn       = 1
    self.DisplayRows       = self.rows    #we will modify this later, based on if we show borders or not
    self.DisplayColumns    = self.columns #we will modify this later, based on if we show borders or not
    self.PreviousLineText  = ""
    self.PreviousLineRow   = 0
    self.PreviousLineColor = 2
    self.Title             = ""
    self.TitleColor        = TitleColor

    #If we are showing border, we only print inside the lines
    if (self.ShowBorder  == 'Y'):
      self.CurrentRow     = 1
      self.StartColumn    = 1
      self.DisplayRows    = self.rows -2 #we don't want to print over the border
      self.DisplayColumns = self.columns -2 #we don't want to print over the border
      self.TextWindow.attron(curses.color_pair(BorderColor))
      self.TextWindow.border()
      self.TextWindow.attroff(curses.color_pair(BorderColor))
      self.TextWindow.refresh()

    else:
      self.CurrentRow   = 0
      self.StartColumn  = 0


  
  def ScrollPrint(self,PrintLine,Color=2,TimeStamp=False,BoldLine=True): 
    #print(PrintLine)
    #for now the string is printed in the window and the current row is incremented
    #when the counter reaches the end of the window, we will wrap around to the top
    #we don't print on the window border
    #make sure to pad the new string with spaces to overwrite any old text

    current_time = datetime.now().strftime("%H:%M:%S")

    if (TimeStamp):
      PrintLine =   current_time + ": {}".format(PrintLine)

    #expand tabs to X spaces, pad the string with space
    PrintLine = PrintLine.expandtabs(4)
    
    #adjust strings
    #Get a part of the big string that will fit in the window
    PrintableString = ''
    RemainingString = ''
    PrintableString = PrintLine[0:self.DisplayColumns]
    RemainingString = PrintLine[self.DisplayColumns+1:]
  
    #Pad1.PadPrint("PrintLine:{}".format(PrintLine),2,TimeStamp=True)
    #Pad1.PadPrint("Printable:{}".format(PrintableString),2,TimeStamp=True)
    #Pad1.PadPrint("Remaining:{}".format(RemainingString),2,TimeStamp=True)

   

    try:
      
      while (len(PrintableString) > 0):
        
        #padd with spaces
        PrintableString = PrintableString.ljust(self.DisplayColumns,' ')

        #if (self.rows == 1):
        #  #if you print on the last character of a window you get an error
        #  PrintableString = PrintableString[0:-2]
        #  self.TextWindow.addstr(0,0,PrintableString)
        #else:

                
        #unbold Previous line  
        self.TextWindow.attron(curses.color_pair(self.PreviousLineColor))
        self.TextWindow.addstr(self.PreviousLineRow,self.StartColumn,self.PreviousLineText)
        self.TextWindow.attroff(curses.color_pair(self.PreviousLineColor))


        if (BoldLine == True):
          #A_NORMAL        Normal display (no highlight)
          #A_STANDOUT      Best highlighting mode of the terminal
          #A_UNDERLINE     Underlining
          #A_REVERSE       Reverse video
          #A_BLINK         Blinking
          #A_DIM           Half bright
          #A_BOLD          Extra bright or bold
          #A_PROTECT       Protected mode
          #A_INVIS         Invisible or blank mode
          #A_ALTCHARSET    Alternate character set
          #A_CHARTEXT      Bit-mask to extract a character
          #COLOR_PAIR(n)   Color-pair number n

          #print new line in bold        
          self.TextWindow.attron(curses.color_pair(Color))
          self.TextWindow.addstr(self.CurrentRow,self.StartColumn,PrintableString,curses.A_BOLD)
          self.TextWindow.attroff(curses.color_pair(Color))
        else:
          #print new line in Regular
          self.TextWindow.attron(curses.color_pair(Color))
          self.TextWindow.addstr(self.CurrentRow,self.StartColumn,PrintableString)
          self.TextWindow.attroff(curses.color_pair(Color))

        self.PreviousLineText  = PrintableString
        self.PreviousLineColor = Color
        self.PreviousLineRow   = self.CurrentRow
        self.CurrentRow        = self.CurrentRow + 1


        #Adjust strings
        PrintableString = RemainingString[0:self.DisplayColumns]
        RemainingString = RemainingString[self.DisplayColumns:]


        
      if (self.CurrentRow > (self.DisplayRows)):
        if (self.ShowBorder == 'Y'):
          self.CurrentRow = 1
        else:
          self.CurrentRow = 0
    
        


      #erase to end of line
      #self.TextWindow.clrtoeol()
      self.TextWindow.refresh()

    except Exception as ErrorMessage:
      TraceMessage = traceback.format_exc()
      AdditionalInfo = "PrintLine: {}".format(PrintLine)

      ErrorHandler(ErrorMessage,TraceMessage,AdditionalInfo)
      

        
  def WindowPrint(self,y,x,PrintLine,Color=2): 
    #print at a specific coordinate within the window
    #try:
     
      #expand tabs to X spaces, pad the string with space then truncate
      PrintLine = PrintLine.expandtabs(4)
      
      #pad the print line with spaces then truncate at the display length
      PrintLine = PrintLine.ljust(self.DisplayColumns -1)
      PrintLine = PrintLine[0:self.DisplayColumns -x]

      self.TextWindow.attron(curses.color_pair(Color))
      self.TextWindow.addstr(y,x,PrintLine)
      self.TextWindow.attroff(curses.color_pair(Color))

      
      self.TextWindow.refresh()

    #except Exception as ErrorMessage:
    #  TraceMessage = traceback.format_exc()
    #  AdditionalInfo = "PrintLine: {}".format(PrintLine)
    #  ErrorHandler(ErrorMessage,TraceMessage,AdditionalInfo)
        
      


  def DisplayTitle(self): 
    #display the window title 

    Color = 0
    Title = ''

       
  
    try:
      #expand tabs to X spaces, pad the string with space then truncate
      Title = self.Title[0:self.DisplayColumns-3]

      self.TextWindow.attron(curses.color_pair(self.TitleColor))
      if (self.rows > 2):
        #print new line in bold        
        self.TextWindow.addstr(0,2,Title)
      else:
        print ("ERROR - You cannot display title on a window smaller than 3 rows")

      self.TextWindow.attroff(curses.color_pair(self.TitleColor))
      self.TextWindow.refresh()    


    except Exception as ErrorMessage:
      TraceMessage = traceback.format_exc()
      AdditionalInfo = "Title: " + Title
      ErrorHandler(ErrorMessage,TraceMessage,AdditionalInfo)


  def Clear(self):
    self.TextWindow.clear()
    self.TextWindow.attron(curses.color_pair(self.BorderColor))
    self.TextWindow.border()
    self.TextWindow.attroff(curses.color_pair(self.BorderColor))
    self.DisplayTitle()
    



    self.TextWindow.refresh()
    if (self.ShowBorder  == 'Y'):
      self.CurrentRow    = 1
      self.StartColumn   = 1
    else:
      self.CurrentRow   = 0
      self.StartColumn  = 0







class TextPad(object):
  #use this as a virtual notepad
  #write a large amount of data to it, then display a section of it on the screen
  #to have a border, use another window with a border
  def __init__(self,name, rows,columns,y1,x1,y2,x2,ShowBorder,BorderColor):
    self.name              = name
    self.rows              = rows
    self.columns           = columns
    self.y1                = y1 #These are coordinates for the window corners on the screen
    self.x1                = x1 #These are coordinates for the window corners on the screen
    self.y2                = y2 #These are coordinates for the window corners on the screen
    self.x2                = x2 #These are coordinates for the window corners on the screen
    self.ShowBorder        = ShowBorder
    self.BorderColor       = BorderColor #pre defined text colors 1-7
    self.TextPad           = curses.newpad(self.rows,self.columns)
    self.PreviousLineColor = 2
         
  def PadPrint(self,PrintLine,Color=2,TimeStamp=False): 
    #print to the pad
    try:
      self.TextPad.idlok(1)
      self.TextPad.scrollok(1)

      current_time = datetime.now().strftime("%H:%M:%S")
      if (TimeStamp):
        PrintLine = current_time + ": " + PrintLine

      #expand tabs to X spaces, pad the string with space then truncate
      PrintLine = PrintLine.expandtabs(4)
      PrintLine = PrintLine.ljust(self.columns,'.')
      
      self.TextPad.attron(curses.color_pair(Color))
      self.TextPad.addstr(PrintLine)
      self.TextPad.attroff(curses.color_pair(Color))

      #We will refresh afer a series of calls instead of every update
      self.TextPad.refresh(0,0,self.y1,self.x1,self.y2,self.x2)

    except Exception as ErrorMessage:
      TraceMessage = traceback.format_exc()
      AdditionalInfo = "PrintLine: " + PrintLine
      ErrorHandler(ErrorMessage,TraceMessage,AdditionalInfo)
        

  def Clear(self):
    self.TextPad.clear()
    self.TextPad.attron(curses.color_pair(self.BorderColor))
    self.TextPad.border()
    self.TextPad.attroff(curses.color_pair(self.BorderColor))
    self.DisplayTitle()
    self.TextPad.refresh(0,0,self.y1,self.x1,self.y2,self.x2)
    if (self.ShowBorder  == 'Y'):
      self.CurrentRow    = 1
      self.StartColumn   = 1
    else:
      self.CurrentRow   = 0
      self.StartColumn  = 0






def ErrorHandler(ErrorMessage,TraceMessage,AdditionalInfo):
  Window2.ScrollPrint('ErrorHandler',10,TimeStamp=True)
  Window4.ScrollPrint('** Just a moment...**',8)
  CallingFunction =  inspect.stack()[1][3]
  FinalCleanup(stdscr)
  print("")
  print("")
  print("--------------------------------------------------------------")
  print("ERROR - Function (",CallingFunction, ") has encountered an error. ")
  print(ErrorMessage)
  print("")
  print("")
  print("TRACE")
  print(TraceMessage)
  print("")
  print("")
  if (AdditionalInfo != ""):
    print("Additonal info:",AdditionalInfo)
    print("")
    print("")
  print("--------------------------------------------------------------")
  print("")
  print("")
  time.sleep(2)
  #sys.exit('Good by for now...')
  exit(0)


def FinalCleanup(stdscr):
  stdscr.keypad(0)
  curses.echo()
  curses.nocbreak()
  curses.curs_set(1)
  curses.endwin()
  



#--------------------------------------
# Initialize Text window / pads      --
#--------------------------------------
  
def CreateTextWindows():

  global StatusWindow
  global TitleWindow
  global Window1
  global Window2
  global Window3
  global Window4
  global Window5
  global HelpWindow
  global Pad1
  global SendMessageWindow
  global SendMessageBox


  #Colors are numbered, and start_color() initializes 8 
  #basic colors when it activates color mode. 
  #They are: 0:black, 1:red, 2:green, 3:yellow, 4:blue, 5:magenta, 6:cyan, and 7:white.
  #The curses module defines named constants for each of these colors: curses.COLOR_BLACK, curses.COLOR_RED, and so forth.
  #Future Note for pads:  call noutrefresh() on a number of windows to update the data structure, and then call doupdate() to update the screen.

  #Text windows

  stdscr.nodelay (1) # doesn't keep waiting for a key press
  curses.start_color()
  curses.noecho()

  
  #We do a quick check to prevent the screen boxes from being erased.  Weird, I know.  Could not find
  #a solution.  Am happy with this work around.
  c = str(stdscr.getch())


  #NOTE: When making changes, be very careful.  Each Window's position is relative to the other ones on the same 
  #horizontal level.  Change one setting at a time and see how it looks on your screen

  #Window1 Coordinates (info window)
  Window1Height = 12
  Window1Length = 40
  Window1x1 = 0
  Window1y1 = 1
  Window1x2 = Window1x1 + Window1Length
  Window1y2 = Window1y1 + Window1Height
  

  #Window2 Coordinates (small debug window)
  Window2Height = 12
  Window2Length = 40
  Window2x1 = Window1x2 + 1
  Window2y1 = 1
  Window2x2 = Window2x1 + Window2Length
  Window2y2 = Window2y1 + Window2Height

  #Window3 Coordinates (Messages)
  Window3Height = 12
  Window3Length = 100
  Window3x1 = Window2x2 + 1
  Window3y1 = 1
  Window3x2 = Window3x1 + Window3Length
  Window3y2 = Window3y1 + Window3Height





  #Window4 Coordinates (packet data)
  Window4Height = 40
  #Window4Length = Window1Length + Window2Length + Window3Length + 2
  Window4Length = 70
  Window4x1 = 0
  Window4y1 = Window1y2 
  Window4x2 = Window4x1 + Window4Length
  Window4y2 = Window4y1 + Window4Height


  #We are going to put a window here as a border, but have the pad 
  #displayed inside
  #Window5 Coordinates (to the right of window4)
  Window5Height = 40
  Window5Length = 70
  Window5x1 = Window4x2 + 1
  Window5y1 = Window4y1
  Window5x2 = Window5x1 + Window5Length
  Window5y2 = Window5y1 + Window5Height
  
  # Coordinates (scrolling pad/window for showing keys being decoded)
  Pad1Columns = Window5Length -2
  Pad1Lines   = Window5Height -2
  Pad1x1 = Window5x1+1
  Pad1y1 = Window5y1+1
  Pad1x2 = Window5x2 -1
  Pad1y2 = Window5y2 -1

  #Help Window
  HelpWindowHeight = 10
  HelpWindowLength = 30
  HelpWindowx1 = Window5x2 + 1
  HelpWindowy1 = Window5y1
  HelpWindowx2 = HelpWindowx1 + HelpWindowLength
  HelpWindowy2 = HelpWindowy1 + HelpWindowHeight

  #SendMessage Window
  #We won't display the border or title, otherwise the text gather
  #function will include those characters
  SendMessageWindowHeight = 4
  SendMessageWindowLength = 50
  SendMessageWindowx1 = Window5x2 + 1 + 1
  SendMessageWindowy1 = HelpWindowy1 + HelpWindowHeight + 1
  SendMessageWindowx2 = SendMessageWindowx1 + SendMessageWindowLength
  SendMessageWindowy2 = SendMessageWindowy1 + SendMessageWindowHeight
  

  try:

    #stdscr.clear()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)



    #--------------------------------------
    # Draw Screen                        --
    #--------------------------------------

    # Create windows
                              # name,  rows,      columns,   y1,    x1,    y2,    x2,ShowBorder,BorderColor,TitleColor):
    TitleWindow   = TextWindow('TitleWindow',1,50,0,0,0,50,'N',0,0) 
    StatusWindow  = TextWindow('StatusWindow',1,50,0,51,0,100,'N',0,0) 
    StatusWindow2 = TextWindow('StatusWindow2',1,30,0,101,0,130,'N',0,0) 
    Window1       = TextWindow('Window1',Window1Height,Window1Length,Window1y1,Window1x1,Window1y2,Window1x2,'Y',2,2)
    Window2       = TextWindow('Window2',Window2Height,Window2Length,Window2y1,Window2x1,Window2y2,Window2x2,'Y',2,2)
    Window3       = TextWindow('Window3',Window3Height,Window3Length,Window3y1,Window3x1,Window3y2,Window3x2,'Y',3,3)
    Window4       = TextWindow('Window4',Window4Height,Window4Length,Window4y1,Window4x1,Window4y2,Window4x2,'Y',5,5)
    Window5       = TextWindow('Window5',Window5Height,Window5Length,Window5y1,Window5x1,Window5y2,Window5x2,'Y',6,6)
    HelpWindow    = TextWindow('HelpWindow',HelpWindowHeight,HelpWindowLength,HelpWindowy1,HelpWindowx1,HelpWindowy2,HelpWindowx2,'Y',7,7)
    SendMessageWindow = TextWindow('SendMessageWindow',SendMessageWindowHeight,SendMessageWindowLength,SendMessageWindowy1,SendMessageWindowx1,SendMessageWindowy2,SendMessageWindowx2,'N',0,1)
    Pad1              = TextPad('Pad1', Pad1Lines,Pad1Columns,Pad1y1,Pad1x1,Pad1y2,Pad1x2,'N',5)


    

    # Display the title  
        #StatusWindow.ScrollPrint("Preparing devices",6)
    #Window1.ScrollPrint("Channel Info",2)
    #Window2.ScrollPrint("Debug Info",2)
    #Window3.ScrollPrint("Alerts",2)
    #Window4.ScrollPrint("Details",2)
    
    #each title needs to be initialized or you get errors in scrollprint
    TitleWindow.Title,   TitleWindow.TitleColor   = "--MeshTalk 1.0--",2
    StatusWindow.Title,  StatusWindow.TitleColor  = "",2
    StatusWindow2.Title, StatusWindow2.TitleColor = "",2
    Window1.Title, Window1.TitleColor = "Device Info",2
    Window2.Title, Window2.TitleColor = "Debug",2
    Window3.Title, Window3.TitleColor = "Messages",3
    Window4.Title, Window4.TitleColor = "Packets",5
    Window5.Title, Window5.TitleColor = "Keys",6
    HelpWindow.Title, HelpWindow.TitleColor = "Help",7
    #SendMessageWindow.Title, HelpWindow.TitleColor = "Send Message",7
    


    TitleWindow.WindowPrint(0,0,TitleWindow.Title)
    Window1.DisplayTitle()
    Window2.DisplayTitle()
    Window3.DisplayTitle()
    Window4.DisplayTitle()
    Window5.DisplayTitle()
    HelpWindow.DisplayTitle()
    SendMessageWindow.DisplayTitle()
    
    DisplayHelpInfo() 
    
    #Prepare edit window for send message
    SendMessageBox = Textbox(SendMessageWindow.TextWindow)
    

    #draw a box around the editwindow
    #Upper left corner coordinates, lower right coordinate
    rectangle(stdscr, SendMessageWindowy1-1, SendMessageWindowx1-1, SendMessageWindowy2+1, SendMessageWindowx2+1)
    stdscr.addstr(SendMessageWindowy1-1, SendMessageWindowx1+1, "Enter message: (hit Ctrl-G to send)",curses.color_pair(7))
    stdscr.refresh()



    


  except Exception as ErrorMessage:
    TraceMessage = traceback.format_exc()
    AdditionalInfo = "Creating text windows"
    ErrorHandler(ErrorMessage,TraceMessage,AdditionalInfo)


#--------------------------------------
# Meshtastic functions               --
#--------------------------------------

def fromStr(valstr):
    """try to parse as int, float or bool (and fallback to a string as last resort)
    Returns: an int, bool, float, str or byte array (for strings of hex digits)
    Args:
        valstr (string): A user provided string
    """
    if(len(valstr) == 0):  # Treat an emptystring as an empty bytes
        val = bytes()
    elif(valstr.startswith('0x')):
        # if needed convert to string with asBytes.decode('utf-8')
        val = bytes.fromhex(valstr[2:])
    elif valstr in trueTerms:
        val = True
    elif valstr in falseTerms:
        val = False
    else:
        try:
            val = int(valstr)
        except ValueError:
            try:
                val = float(valstr)
            except ValueError:
                val = valstr  # Not a float or an int, assume string

    return val



def DecodePacket(PacketParent,Packet,Filler,FillerChar,PrintSleep=0):
  global DeviceStatus
  global DeviceName
  global DevicePort
  global PacketsReceived
  global PacketsSent
  global LastPacketType
  global HardwareModel
  global DeviceID 
  global BatteryLevl


  #This is a recursive funtion that will decode a packet (get key/value pairs from a dictionary )
  #if the value is itself a dictionary, recurse
  Window2.ScrollPrint("DecodePacket",2,TimeStamp=True)
  #Filler = ('-' *  len(inspect.stack(0)))

  #used to indent packets
  if (PacketParent.upper() != 'MAINPACKET'):
    Filler = Filler + FillerChar
 
  Window4.ScrollPrint("{}".format(PacketParent).upper(),2)


  #adjust the input to slow down the output for that cool retro feel
  if (PrintSleep > 0):
    time.sleep(PrintSleep)
  

  #if the packet is a dictionary, decode it
  if isinstance(Packet, collections.abc.Mapping):

    
    for Key in Packet.keys():
      Value = Packet.get(Key) 

      if (PrintSleep > 0):
        time.sleep(PrintSleep)
  

      #Pad1.PadPrint("{} - {}".format(PacketParent,Key),2)
      Pad1.PadPrint("{} - {}".format(PacketParent,Key),2)

      #if the value paired with this key is another dictionary, keep digging
      if isinstance(Value, collections.abc.Mapping):

        #Print the name/type of the packet
        Window4.ScrollPrint(" ",2)
        #Window4.ScrollPrint("{}".format(Key).upper(),2)
        LastPacketType = Key.upper()

        DecodePacket("{}/{}".format(PacketParent,Key).upper(),Value,Filler,FillerChar,PrintSleep=PrintSleep)  



      else:

        if(Key == 'longName'):
          DeviceName = Value
          UpdateStatusWindow(NewDeviceName=DeviceName,Color=2)

        elif(Key == 'portnum'):
          DevicePort = Value
          UpdateStatusWindow(NewDevicePort=DevicePort,Color=2)
        
        elif(Key == 'hwModel'):
          HardwareModel = Value
          UpdateStatusWindow(NewHardwareModel=HardwareModel,Color=2)

        elif(Key == 'macaddr'):
          MacAddress = Value
          UpdateStatusWindow(NewMacAddress=MacAddress,Color=2)

        elif(Key == 'id' and PacketParent == 'MYNODE/USER'):
          DeviceID = Value
          UpdateStatusWindow(NewDeviceID=DeviceID,Color=2)

        elif(Key == 'batteryLevel'):
          BatteryLevel = Value
          UpdateStatusWindow(NewBatteryLevel=BatteryLevel,Color=2)

        #Print KEY if not RAW (gotta decode those further, or ignore)
        if(Key == 'raw'):
          Window4.ScrollPrint("{}  RAW value not yet suported by DecodePacket function".format(Filler),2)
        else:
          Window4.ScrollPrint("  {}{}: {}".format(Filler,Key,Value),2)


        
  else:
    Window2.ScrollPrint("Warning: Not a packet!",5,TimeStamp=True)
  
  #Window4.ScrollPrint("{}END PACKET: {} ".format(Filler,PacketParent.upper()),2)
  
  

def onReceive(packet, interface): # called when a packet arrives
    global PacketsReceived
    global PacketsSent
    
    PacketsReceived = PacketsReceived + 1
    

    Window2.ScrollPrint("onReceive",2,TimeStamp=True)
    Window4.ScrollPrint(" ",2)    
    Window4.ScrollPrint("==Packet RECEIVED=================================================",2)

    Decoded  = packet.get('decoded')
    Message  = Decoded.get('text')
    To       = packet.get('to')
    From     = packet.get('from')

    #Even better method, use this recursively to decode all the packets of packets
    DecodePacket('MainPacket',packet,Filler='',FillerChar='',PrintSleep=PrintSleep)

    if(Message):
      Window3.ScrollPrint("From: {} - {}".format(From,Message),2,TimeStamp=True)
    Window4.ScrollPrint("=================================================================",2)
    Window4.ScrollPrint(" ",2)    

    #example of scrolling the window
    #Window4.TextWindow.idlok(1)
    #Window4.TextWindow.scrollok(1)
    #Window4.TextWindow.scroll(10)
    #Window4.TextWindow.scrollok(0)
    
    

    time.sleep(0.25)



def onConnectionEstablished(interface, topic=pub.AUTO_TOPIC): # called when we (re)connect to the radio
    #Window2.ScrollPrint('onConnectionEstablished',2,TimeStamp=True)
    #Window1.WindowPrint(1,1,"Status: CONNECTED",2)
    UpdateStatusWindow(NewDeviceStatus = "CONNECTED",Color=2)
    
    From = "BaseStation"
    To   = "All"
    current_time = datetime.now().strftime("%H:%M:%S")
    Message = "MeshTalk active [{}]".format(current_time)
    Window3.ScrollPrint("From: {} - {}".format(From,Message,To),2,TimeStamp=True)
    
    try:
      interface.sendText(Message)
      Window4.ScrollPrint("",2)    
      Window4.ScrollPrint("==Packet SENT=====================================================",3)
      Window4.ScrollPrint("To:     {}:".format(To),3)
      Window4.ScrollPrint("From    {}:".format(From),3)
      Window4.ScrollPrint("Message {}:".format(Message),3)
      Window4.ScrollPrint("==================================================================",3)
      Window4.ScrollPrint("",2)    

    except Exception as ErrorMessage:
      TraceMessage = traceback.format_exc()
      AdditionalInfo = "Sending text message ({})".format(Message)
      ErrorHandler(ErrorMessage,TraceMessage,AdditionalInfo)



def onConnectionLost(interface, topic=pub.AUTO_TOPIC): # called when we (re)connect to the radio
    Window2.ScrollPrint('onConnectionLost',2,TimeStamp=True)
    UpdateStatusWindow(NewDeviceStatus = "DISCONNECTED",Color=1)


def onNodeUpdated(interface, topic=pub.AUTO_TOPIC): # called when we (re)connect to the radio
    Window2.ScrollPrint('onNodeUpdated',2,TimeStamp=True)
    Window1.WindowPrint(1,4,'UPDATE RECEIVED',1,TimeStamp=True)
    
    Window4.ScrollPrint("",2)    
    Window4.ScrollPrint("==NODE UPDATED =======================================",4)

    try:
      DecodePacket('Node',packet,Filler='',FillerChar='  ',PrintSleep = PrintSleep)

    except Exception as ErrorMessage:
      TraceMessage = traceback.format_exc()
      AdditionalInfo = "Decoding onNodeUpdated packet"
      ErrorHandler(ErrorMessage,TraceMessage,AdditionalInfo)


    Window4.ScrollPrint("=======================================================",4)



def SIGINT_handler(signal_received, frame):
  # Handle any cleanup here
  FinalCleanup(stdscr)  
  print('** END OF LINE')
  exit(0)



def PollKeyboard():
  global stdscr
  global Window2
  global interface

  #Window2.ScrollPrint("PollKeyboard",2,TimeStamp=True)
  ReturnChar = ""
  c = ""
  #curses.filter()
  curses.noecho()
 
  try:
    c = chr(stdscr.getch())
  except Exception as ErrorMessage:
    c=""


  #Look for digits (ascii 48-57 == digits 0-9)
  if (c >= '0' and c <= '9'):
    #print ("Digit detected")
    #StatusWindow.ScrollPrint("Digit Detected",2)
    ReturnChar = (c)    

  if (c != ""):
    #print ("----------------")
    #print ("Key Pressed: ",Key)
    #print ("----------------")
    OutputLine = "Key Pressed: " + c
    #Window2.ScrollPrint(OutputLine,4)
    ProcessKeypress(c)
  return ReturnChar



def ProcessKeypress(Key):
  global stdscr
  global StatusWindow
  global Window2
  global Window4
  global interface
  global PauseOutput
  global PrintSleep 
  global OldPrintSleep 
  count  = 0

  OutputLine = "** KEYPRESS: " + str(Key) + " **"
  Window2.ScrollPrint (OutputLine,5)
  # c = clear screen
  # i = get node info
  # p = pause
  # q = quit
  # r = reboot
  # s = Send message


    
  if (Key == "p" or Key == " "):
    PauseOutput = not (PauseOutput)
    if (PauseOutput == True):
      Window2.ScrollPrint("Pausing output",2)
      StatusWindow.WindowPrint(0,0,"** Output SLOW - press SPACE again to cancel **",1)
      PrintSleep = 1

    else:
      Window2.ScrollPrint("Resuming output",2)
      StatusWindow.WindowPrint(0,0," ",3)
      PrintSleep = OldPrintSleep
      #StatusWindow.ScrollPrint("",2)

  #elif (Key == "i"):
  #  IPAddress = ShowIPAddress()
  #  ar.ShowScrollingBanner2(IPAddress,0,225,0,3,0.03)


  elif (Key == "i"):
    Window4.Clear()
    GetMyNodeInfo(interface)
    time.sleep(3)
    

  elif (Key == "q"):
    FinalCleanup(stdscr)
    exit()

  elif (Key == "c"):
    ClearAllWindows()

  elif (Key == "r"):
    Window2.ScrollPrint('** REBOOTING **',1)
    
    FinalCleanup(stdscr)
    os.execl(sys.executable, sys.executable, *sys.argv)

  elif (Key == "s"):
    SendMessagePacket(interface)




def SendMessagePacket(interface, Message=''):
    Window2.ScrollPrint("SendMessagePacket",2)
    
    
    # Let the user edit until Ctrl-G is struck.
    SendMessageBox.edit()
    

    # Get resulting contents
    TheMessage = SendMessageBox.gather()
    
    #remove last character which seems to be interfering with line printing
    TheMessage = TheMessage[0:-1]
  
    #Send the message to the device
    interface.sendText(TheMessage)

    
    Window4.ScrollPrint(" ",2)    
    Window4.ScrollPrint("==Packet SENT===========================================",3)
    Window4.ScrollPrint("To:      All:",3)
    Window4.ScrollPrint("From:    BaseStation",3)
    Window4.ScrollPrint("Message: {}".format(TheMessage),3)
    Window4.ScrollPrint("========================================================",3)
    Window4.ScrollPrint(" ",2)    



    Window3.ScrollPrint("To: All - {}".format(TheMessage),2,TimeStamp=True)


def GoToSleep(TimeToSleep):
  Window2.ScrollPrint("GoToSleep({})".format(TimeToSleep),2,TimeStamp=True)
  for i in range (0,TimeToSleep):
    #Check for keyboard input      --
    Key = PollKeyboard()
    if (Key == 's'):
      SendMessagePacket
      return
    time.sleep(1)

def ClearAllWindows():
  Window1.Clear()
  Window2.Clear()
  Window3.Clear()
  Window4.Clear()
  Window5.Clear()
  Window2.ScrollPrint("**Clearing screens**",2)
  UpdateStatusWindow()


def UpdateStatusWindow(NewDeviceStatus  = '',
                       NewDeviceName    = '',
                       NewDevicePort    = '',
                       NewHardwareModel = '',
                       NewMacAddress    = '',
                       NewDeviceID      = '',
                       NewBatteryLevel  = -1,
                       Color=2
    ):
  #Window2.ScrollPrint("UpdateStatusWindow",2,TimeStamp=True)

  global DeviceStatus
  global DeviceName
  global DevicePort
  global PacketsReceived
  global PacketsSent
  global LastPacketType
  global HardwareModel
  global MacAddress
  global DeviceID
  global BatteryLevel

  x1,y1 = 1,1    #DeviceName
  x2,y2 = 1,2    #HardwareModel
  x3,y3 = 1,3    #DeviceStatus
  x4,y4 = 1,4    #MacAddress
  x5,y5 = 1,5    #DeviceID
  x6,y6 = 1,6    #PacketsDecoded
  x7,y7 = 1,7    #LastPacketType
  x8,y8 = 1,8    #BatteryLevel

  if(NewDeviceName != ''):
    DeviceName = NewDeviceName

  if(NewDeviceStatus != ''):
    DeviceStatus = NewDeviceStatus

  if(NewDevicePort != ''):
    DevicePort = NewDevicePort

  if(NewHardwareModel != ''):
    HardwareModel = NewHardwareModel

  if(NewMacAddress != ''):
    MacAddress = NewMacAddress

  if(NewDeviceID != ''):
    DeviceID = NewDeviceID

  if(NewBatteryLevel >-1):
   BatteryLevel = NewBatteryLevel


  #DeviceName
  Window1.WindowPrint(y1,x1,"UserName:   ",2)
  Window1.WindowPrint(y1,x1+12,DeviceName,Color)

  #DeviceStatus
  Window1.WindowPrint(y2,x2,"Model:      " + HardwareModel,2)
  Window1.WindowPrint(y2,x2+12,HardwareModel,Color)

  #DeviceStatus
  Window1.WindowPrint(y3,x3,"Status:     " + DeviceStatus,2)
  Window1.WindowPrint(y3,x3+12,DeviceStatus,Color)

  #MacAddress
  Window1.WindowPrint(y4,x4,"MacAddress: ",2)
  Window1.WindowPrint(y4,x4+12,MacAddress,Color)

  #DeviceID
  Window1.WindowPrint(y5,x5,"DeviceID:   ",2)
  Window1.WindowPrint(y5,x5+12,DeviceID,Color)

  #PacketsReceived
  Window1.WindowPrint(y6,x6,"Packets Decoded: ",2)
  Window1.WindowPrint(y6,x6+17,"{}".format(PacketsReceived),Color)

  #LastPacketType
  Window1.WindowPrint(y7,x7,"LastPacketType:  ",2)
  Window1.WindowPrint(y7,x7+17,LastPacketType,Color)

  #BatteryLevel
  Window1.WindowPrint(y8,x8,"BatteryLevel:    ",2)
  Window1.WindowPrint(y8,x8+17,"{}".format(BatteryLevel),Color)


def DisplayHelpInfo():
  HelpWindow.ScrollPrint("C - CLEAR Screen",7)
  HelpWindow.ScrollPrint("I - Request node INFO",7)
  HelpWindow.ScrollPrint("Q - QUIT program",7)
  HelpWindow.ScrollPrint("R - RESTART MeshTalk",7)
  HelpWindow.ScrollPrint("S - SEND message",7)
  HelpWindow.ScrollPrint("SPACEBAR - Slow/Fast output",7)
  
  


def GetMyNodeInfo(interface):

    Window4.ScrollPrint(" ",2)
    Window4.ScrollPrint("==MyNodeInfo===================================",3)
    TheNode = interface.getMyNodeInfo()
    DecodePacket('MYNODE',TheNode,'','',PrintSleep =PrintSleep)
    Window4.ScrollPrint("===============================================",3)
    Window4.ScrollPrint(" ",2)
    



#------------------------------------------------------------------------------
#   __  __    _    ___ _   _                                                 --
#  |  \/  |  / \  |_ _| \ | |                                                --
#  | |\/| | / _ \  | ||  \| |                                                --
#  | |  | |/ ___ \ | || |\  |                                                --
#  |_|  |_/_/   \_\___|_| \_|                                                --
#                                                                            --
#  ____  ____   ___   ____ _____ ____ ____ ___ _   _  ____                   --
# |  _ \|  _ \ / _ \ / ___| ____/ ___/ ___|_ _| \ | |/ ___|                  --
# | |_) | |_) | | | | |   |  _| \___ \___ \| ||  \| | |  _                   --
# |  __/|  _ <| |_| | |___| |___ ___) |__) | || |\  | |_| |                  --
# |_|   |_| \_\\___/ \____|_____|____/____/___|_| \_|\____|                  --
#                                                                            --
#------------------------------------------------------------------------------


#--------------------------------------
# Main (function)                    --
#--------------------------------------

def main(stdscr):
  global interface
  global DeviceStatus
  global DeviceName
  global DevicePort
  global PacketsSent
  global PacketsReceived
  global LastPacketType
  global HardwareModel
  global MacAddress
  global DeviceID
  global BatteryLevel
  global PauseOutput

  try:

    DeviceName      = '??'
    DeviceStatus    = '??'
    DevicePort      = '??'
    PacketsReceived = 0
    PacketsSent     = 0
    LastPacketType  = ''
    HardwareModel   = ''
    MacAddress      = ''
    DeviceName      = ''
    DeviceID        = ''
    BatteryLevel    = -1
    PauseOutput     = False


    CreateTextWindows()
    Window4.ScrollPrint("System initiated",2)
    
    
    #Instanciate a meshtastic object
    #By default will try to find a meshtastic device, otherwise provide a device path like /dev/ttyUSB0
    Window4.ScrollPrint("Finding Meshtastic device",2)
    interface = meshtastic.SerialInterface()

    #Get node info for connected device
    Window4.ScrollPrint("Requesting device info",2)
    GetMyNodeInfo(interface)



    #subscribe to connection and receive channels
    pub.subscribe(onConnectionEstablished, "meshtastic.connection.established")
    pub.subscribe(onConnectionLost,        "meshtastic.connection.lost")
    pub.subscribe(onNodeUpdated,           "meshtastic.node.updated")



    #Check for message to be sent (command line option)
    if(SendMessage):
       interface.sendText(TheMessage)

   

    #Go into listening mode
    Window4.ScrollPrint("Listening for: {} seconds".format(TimeToSleep),2)
    Window4.ScrollPrint("Subscribing to interface channels...",2)
    pub.subscribe(onReceive, "meshtastic.receive")


    while (1==1):
      GoToSleep(2)


    interface.close()  
    Window4.ScrollPrint("--End of Line------------",2)
    Window4.ScrollPrint("",2)
    



  except Exception as ErrorMessage:
    TraceMessage = traceback.format_exc()
    AdditionalInfo = "Main function "
    ErrorHandler(ErrorMessage,TraceMessage,AdditionalInfo)



  

#--------------------------------------
# Main (pre-amble                    --
#--------------------------------------

#only execute if we are in main
if __name__=='__main__':
  try:
      #if SIGINT or CTL-C detected, run SIGINT_handler to exit gracefully
      signal(SIGINT, SIGINT_handler)

      # Initialize curses
      stdscr=curses.initscr()
      # Turn off echoing of keys, and enter cbreak mode,
      # where no buffering is performed on keyboard input
      curses.noecho()
      curses.cbreak()
      curses.curs_set(0)

      # In keypad mode, escape sequences for special keys
      # (like the cursor keys) will be interpreted and
      # a special value like curses.KEY_LEFT will be returned
      stdscr.keypad(1)
      main(stdscr)                    # Enter the main loop
      # Set everything back to normal
      FinalCleanup(stdscr)

  except Exception as ErrorMessage:
      # In event of error, restore terminal to sane state.
      TraceMessage = traceback.format_exc()
      AdditionalInfo = "Main pre-amble"
      ErrorHandler(ErrorMessage,TraceMessage,AdditionalInfo)
      exit()

