


import meshtastic
import time
from datetime import datetime
import traceback
from pubsub import pub
import argparse
import collections
import sys

#to help with debugging
import inspect

#For capturing keypresses and drawing text boxes
import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle

#for capturing ctl-c
from signal import signal, SIGINT
from sys import exit




def ScrollPrint(PrintLine,Columns): 
    
    print("Original String: ",PrintLine)

    PrintableString = ''
    RemainingString = ''
    
    #Adjust strings
    PrintableString = PrintLine[0:Columns]
    print("PrintableString: ",PrintableString,'*')
    RemainingString = PrintLine[Columns:]
    print("RemainingString: ",RemainingString,'*')


    #print("Printable:",PrintableString)
    #print("ReaminingString:",RemainingString)



    while (len(PrintableString) > 0):
    #Get a part of the big string that will fit in the window
        
        #Main Display
        print("Length of printable:",(len(PrintableString)),"* string: ",PrintableString, '* remaining:',RemainingString,'*')
        
        #Adjust strings
        PrintableString = RemainingString[0:Columns]
        RemainingString = RemainingString[Columns:]

        time.sleep(0.05)





#ScrollPrint ("123456789A123456789B123456789C123456789D123456789E123456789F123456789G123456789H123456789I",40)

ScrollPrint ("That is how you mine stuff in minecraft, Isaac.  Don't be so silly!",10)