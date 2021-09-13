

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
from pubsub import pub
import argparse
import collections

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


#------------------------------------------------------------------------------
# Initialize Curses                                                          --
#------------------------------------------------------------------------------

#Text windows
#stdscr = curses.initscr()

#hide the cursor
#curses.curs_set(0)


global TitleWindow
global StatusWindow
global Window1
global Window2
global Window3
global Window4
global Pad1
global IPAddress


#------------------------------------------------------------------------------
# Functions / Classes                                                        --
#------------------------------------------------------------------------------


class TextWindow(object):
  def __init__(self,name, rows,columns,y1,x1,y2,x2,ShowBorder,BorderColor):
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
    self.TitleColor        = 2

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



  def ScrollPrint(self,PrintLine,Color=2,TimeStamp=False,WrapText=True): 
    #for now the string is printed in the window and the current row is incremented
    #when the counter reaches the end of the window, we will wrap around to the top
    #we don't print on the window border

    try:
           
      current_time = datetime.now().strftime("%H:%M:%S")
      if (TimeStamp):
        PrintLine = current_time + ": " + PrintLine

      #expand tabs to X spaces, pad the string with space then truncate
      PrintLine = PrintLine.expandtabs(4)
      PrintLine = PrintLine.ljust(self.DisplayColumns -1,' ')
      PrintLine = PrintLine[0:self.DisplayColumns]

      self.TextWindow.attron(curses.color_pair(Color))
      if (self.rows == 1):
        #if you print on the last character of a window you get an error
        PrintLine = PrintLine[0:self.DisplayColumns-1]
        self.TextWindow.addstr(0,0,PrintLine)
      else:

        #unbold current line  (bold seems to stick, so I am changing)
        self.TextWindow.attron(curses.color_pair(self.PreviousLineColor))
        self.TextWindow.addstr(self.PreviousLineRow,self.StartColumn,self.PreviousLineText)
        #print new line in bold        
        self.TextWindow.addstr(self.CurrentRow,self.StartColumn,PrintLine,curses.A_BOLD)
      self.TextWindow.attroff(curses.color_pair(Color))



      self.PreviousLineText  = PrintLine
      self.PreviousLineColor = Color
      self.PreviousLineRow   = self.CurrentRow
      self.CurrentRow        = self.CurrentRow + 1

        
     
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
      AdditionalInfo = "PrintLine: " + PrintLine 
      ErrorHandler(ErrorMessage,TraceMessage,AdditionalInfo)
      

        
  def WindowPrint(self,y,x,PrintLine,Color=2): 
    #print at a specific coordinate within the window
    try:
     
      #expand tabs to X spaces, pad the string with space then truncate
      PrintLine = PrintLine.expandtabs(4)
      PrintLine = PrintLine.ljust(self.DisplayColumns -1,' ')
      PrintLine = PrintLine[0:self.DisplayColumns]

      self.TextWindow.attron(curses.color_pair(Color))
      self.TextWindow.addstr(y,x,PrintLine)
      self.TextWindow.attroff(curses.color_pair(Color))

      #We will refresh afer a series of calls instead of every update
      #self.TextWindow.refresh()

    except Exception as ErrorMessage:
      TraceMessage = traceback.format_exc()
      AdditionalInfo = "PrintLine: " + PrintLine
      ErrorHandler(ErrorMessage,TraceMessage,AdditionalInfo)
        
      


  def DisplayTitle(self,Title, Color): 
    #display the window title 
    if(Title == ""):
      Title = self.Title
    try:
      #expand tabs to X spaces, pad the string with space then truncate
      Title = Title[0:self.DisplayColumns-3]

      self.TextWindow.attron(curses.color_pair(Color))
      if (self.rows > 2):
        #print new line in bold        
        self.TextWindow.addstr(0,2,Title)
        self.TextWindow.refresh()

      else:
        print ("ERROR - You cannot display title on a window smaller than 3 rows")

    except Exception as ErrorMessage:
      TraceMessage = traceback.format_exc()
      AdditionalInfo = "Title: " + Title
      ErrorHandler(ErrorMessage,TraceMessage,AdditionalInfo)


  def Clear(self):
    self.TextWindow.clear()
    self.TextWindow.attron(curses.color_pair(self.BorderColor))
    self.TextWindow.border()
    self.TextWindow.attroff(curses.color_pair(self.BorderColor))
    self.DisplayTitle(self.Title,self.TitleColor)
    self.TextWindow.refresh()
    if (self.ShowBorder  == 'Y'):
      self.CurrentRow    = 1
      self.StartColumn   = 1
    else:
      self.CurrentRow   = 0
      self.StartColumn  = 0







class TextPad(object):
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
    self.CurrentRow        = y1
    self.StartColumn       = x1
    self.DisplayRows       = self.rows    #we will modify this later, based on if we show borders or not
    self.DisplayColumns    = self.columns #we will modify this later, based on if we show borders or not
    self.PreviousLineText  = ""
    self.PreviousLineRow   = 0
    self.PreviousLineColor = 2
    self.Title             = ""
    self.TitleColor        = 2

    #If we are showing border, we only print inside the lines
    if (self.ShowBorder  == 'Y'):
      self.CurrentRow     = 1
      self.StartColumn    = 1
      self.DisplayRows    = self.rows -2 #we don't want to print over the border
      self.DisplayColumns = self.columns -2 #we don't want to print over the border
      #self.TextPad.attron(curses.color_pair(BorderColor))
      #self.TextPad.border()
      #self.TextPad.attroff(curses.color_pair(BorderColor))
      #yx upper left of pad, yx upper left of window(of the pad), yx lower right corner of window
      #self.TextPad.refresh(y1,x1,y1,x1,y2,x2)

    else:
      self.CurrentRow   = 0
      self.StartColumn  = 0


         
  def PadPrint(self,PrintLine,Color=2): 
    #print to the pad
    try:
      self.TextPad.idlok(1)
      self.TextPad.scrollok(1)
      
      #expand tabs to X spaces, pad the string with space then truncate
      PrintLine = PrintLine.expandtabs(4)
      PrintLine = PrintLine.ljust(self.columns,' ')
      
      self.TextPad.attron(curses.color_pair(Color))
      self.TextPad.addstr(PrintLine)
      self.TextPad.attroff(curses.color_pair(Color))

      #We will refresh afer a series of calls instead of every update
      self.TextPad.refresh(0,0,self.y1,self.x1,self.y2,self.x2)

    except Exception as ErrorMessage:
      TraceMessage = traceback.format_exc()
      AdditionalInfo = "PrintLine: " + PrintLine
      ErrorHandler(ErrorMessage,TraceMessage,AdditionalInfo)
        
      


  def DisplayTitle(self,Title, Color): 
    #display the window title 
    if(Title == ""):
      Title = self.Title
    try:
      #expand tabs to X spaces, pad the string with space then truncate
      Title = Title[0:self.DisplayColumns-3]

      self.TextPad.attron(curses.color_pair(Color))
      if (self.rows > 2):
        #print new line in bold        
        self.TextPad.addstr(0,2,Title)
        self.TextPad.refresh()

      else:
        print ("ERROR - You cannot display title on a window smaller than 3 rows")

    except Exception as ErrorMessage:
      TraceMessage = traceback.format_exc()
      AdditionalInfo = "Title: " + Title
      ErrorHandler(ErrorMessage,TraceMessage,AdditionalInfo)


  def Clear(self):
    self.TextPad.clear()
    self.TextPad.attron(curses.color_pair(self.BorderColor))
    self.TextPad.border()
    self.TextPad.attroff(curses.color_pair(self.BorderColor))
    self.DisplayTitle(self.Title,self.TitleColor)
    self.TextPad.refresh()
    if (self.ShowBorder  == 'Y'):
      self.CurrentRow    = 1
      self.StartColumn   = 1
    else:
      self.CurrentRow   = 0
      self.StartColumn  = 0






def ErrorHandler(ErrorMessage,TraceMessage,AdditionalInfo):
  Window2.ScrollPrint('ErrorHandler',10,TimeStamp=True)
  Window4.ScrollPrint('** Just a moment...**',8)
  time.sleep(1)
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
  global Pad1


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


  #Window1 Coordinates
  Window1Height = 12
  Window1Length = 40
  Window1x1 = 0
  Window1y1 = 1
  Window1x2 = Window1x1 + Window1Length
  Window1y2 = Window1y1 + Window1Height
  

  #Window2 Coordinates
  Window2Height = 12
  Window2Length = 40
  Window2x1 = Window1x2 + 1
  Window2y1 = 1
  Window2x2 = Window2x1 + Window2Length
  Window2y2 = Window2y1 + Window2Height

  #Window3 Coordinates
  Window3Height = 12
  Window3Length = 40
  Window3x1 = Window2x2 + 1
  Window3y1 = 1
  Window3x2 = Window3x1 + Window3Length
  Window3y2 = Window3y1 + Window3Height

  #Window4 Coordinates
  Window4Height = 48
  Window4Length = Window1Length + Window2Length + Window3Length
  Window4x1 = 0
  Window4y1 = Window1y2 
  Window4x2 = Window4x1 + Window4Length
  Window4y2 = Window4y1 + Window4Height

  #Pad1 Coordinates
  Pad1Columns = 40
  Pad1Lines   = 40
  Pad1x1 = Window3x2 + 1
  Pad1y1 = 1
  Pad1x2 = Pad1x1 + Pad1Columns
  Pad1y2 = Pad1y1 + Pad1Lines


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
    TitleWindow   = TextWindow('TitleWindow',1,50,0,0,0,50,'N',0) 
    StatusWindow  = TextWindow('StatusWindow',1,50,0,51,0,100,'N',0) 
    StatusWindow2 = TextWindow('StatusWindow2',1,30,0,101,0,130,'N',0) 
    Window1       = TextWindow('Window1',Window1Height,Window1Length,Window1y1,Window1x1,Window1y2,Window1x2,'Y',2)
    Window2       = TextWindow('Window2',Window2Height,Window2Length,Window2y1,Window2x1,Window2y2,Window2x2,'Y',3)
    Window3       = TextWindow('Window3',Window3Height,Window3Length,Window3y1,Window3x1,Window3y2,Window3x2,'Y',4)
    Window4       = TextWindow('Window4',Window4Height,Window4Length,Window4y1,Window4x1,Window4y2,Window4x2,'Y',6)
    Pad1          = TextPad('Pad1', Pad1Lines,Pad1Columns,Pad1y1,Pad1x1,Pad1y2,Pad1x2,'N',6)
                           # name,  rows,      columns,   y1,    x1,    y2,    x2,ShowBorder,BorderColor):


    

    # Display the title  
    TitleWindow.ScrollPrint("──MeshTalk 2021──",2)
    #StatusWindow.ScrollPrint("Preparing devices",6)
    #Window1.ScrollPrint("Channel Info",2)
    #Window2.ScrollPrint("Debug Info",2)
    #Window3.ScrollPrint("Alerts",2)
    #Window4.ScrollPrint("Details",2)
    
    Window1.DisplayTitle("Info",2)
    Window2.DisplayTitle("Debug",3)
    Window3.DisplayTitle("Messages",5)

    #We will overwrite the title with page information during a report, so we store the original first
    Window4.Title = "──Packets──────────────────────────────────────────────────────────────────────────"
    Window4.DisplayTitle("",6)


    


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



def DecodePacket(PacketParent,Packet,Filler,FillerChar):
  #This is a recursive funtion that will decode a packet (get key/value pairs from a dictionary )
  #if the value is itself a dictionary, recurse
  Window2.ScrollPrint("DecodePacket",2,TimeStamp=True)
  #Filler = ('-' *  len(inspect.stack(0)))

  if (PacketParent.upper() != 'MAINPACKET'):
    Filler = Filler + FillerChar

  #Print the name/type of the packet
  Window4.ScrollPrint("",2)
  Window4.ScrollPrint(  "{}PacketType: {}".format(Filler,PacketParent.upper()),2)

  

  #if the packet is a dictionary, decode it
  if isinstance(Packet, collections.abc.Mapping):
    for Key in Packet.keys():
      Value = Packet.get(Key) 

      Pad1.PadPrint("Analyzing: {} - {}".format(PacketParent,Key),2)

      #if the value paired with this key is another dictionary, keep digging
      if isinstance(Value, collections.abc.Mapping):
        time.sleep(0.25)
        DecodePacket(Key,Value,Filler,FillerChar)  
      else:
        if(Key == 'raw'):
          Window4.ScrollPrint("{}Raw value not yet suported by DecodePacket function".format(Filler),2)
        else:
          Window4.ScrollPrint("  {}{}: {}".format(Filler,Key,Value),2)
          #Window4.ScrollPrint("{}Key: {}".format(Filler,Key),2)
          #Window4.ScrollPrint("{}Val: {}".format(Filler,Value),2)
  else:
    Window2.ScrollPrint("Warning: Not a packet!",5,TimeStamp=True)
  
  #Window4.ScrollPrint("{}END PACKET: {} ".format(Filler,PacketParent.upper()),2)
  
  

def onReceive(packet, interface): # called when a packet arrives
    Window2.ScrollPrint("onReceive",2,TimeStamp=True)
    Window4.ScrollPrint("",2)    
    Window4.ScrollPrint("==Packet Received=======================================",2)

    Decoded  = packet.get('decoded')
    Message  = Decoded.get('text')
    To       = Decoded.get('to')
    From     = Decoded.get('from')

    #Even better method, use this recursively to decode all the packets of packets
    DecodePacket('MainPacket',packet,Filler='',FillerChar='  ')

    if(Message):
      Window3.ScrollPrint("From: {} - {}".format(From,Message),2,TimeStamp=True)

    #example of scrolling the window
    #Window4.TextWindow.idlok(1)
    #Window4.TextWindow.scrollok(1)
    #Window4.TextWindow.scroll(10)
    #Window4.TextWindow.scrollok(0)
    
    

    time.sleep(0.25)



def onConnectionEstablished(interface, topic=pub.AUTO_TOPIC): # called when we (re)connect to the radio
    Window2.ScrollPrint('onConnectionEstablished',2,TimeStamp=True)
    Window1.ScrollPrint('Connected',2,TimeStamp=True)


    # defaults to broadcast, specify a destination ID if you wish
    
    #Window1.ScrollPrint("Connected: {}".format(current_time),2)
    #interface.sendText("meshtalk 1.0 activated")


def onConnectionLost(interface, topic=pub.AUTO_TOPIC): # called when we (re)connect to the radio
    Window2.ScrollPrint('onConnectionLost',2,TimeStamp=True)
    Window1.ScrollPrint('Disconnected',2,TimeStamp=True)




def SIGINT_handler(signal_received, frame):
  # Handle any cleanup here
  FinalCleanup(stdscr)  
  print('** END OF LINE')
  exit(0)



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
  try:

    CreateTextWindows()
    Window1.ScrollPrint("System initiated",2)
    Window4.ScrollPrint("--MeshTalk 1.0--",2)



    #Instanciate a meshtastic object
    #By default will try to find a meshtastic device, otherwise provide a device path like /dev/ttyUSB0
    Window4.ScrollPrint("Finding Meshtastic device...",2)
    interface = meshtastic.SerialInterface()


    #subscribe to connection and receive channels
    pub.subscribe(onConnectionEstablished, "meshtastic.connection.established")
    pub.subscribe(onConnectionLost,        "meshtastic.connection.lost")


    #Check for message to be sent
    if(SendMessage):
      Window4.ScrollPrint("Sending: " + TheMessage,2)
      interface.sendText(TheMessage)
      Window4.ScrollPrint("Message sent",2)

    if(ReceiveMessages):
      Window4.ScrollPrint("Listening for: {} seconds".format(TimeToSleep),2)
      Window4.ScrollPrint("Subscribing to interface channels...",2)
      pub.subscribe(onReceive, "meshtastic.receive")
      time.sleep(TimeToSleep)


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

