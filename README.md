![TheDevice](https://github.com/datagod/meshtalk/blob/main/pics/Meshtastic%20device%20raspberry%20pi.jpg?raw=true "Top Row")


# Project: RENAMED
The MeshTalk name is already used, and since this program does so much more I decided now is the time to change the name.

# MeshWatch
MeshWatch is a python3 program that will allow you to send and receive messages from python. The messages are decoded and displayed in a text based interface created with Curses.

I built this project with the goal of learning about the Meshtastic API and to get used to using new development tools such as Visual Studio Code and GitHub.

My progress can be followed here:  https://datagod.hashnode.dev/series/meshtalk-development


# Built with Curses
This project uses Curses to draw text windows and pads to keep the different types of information separated.  You can use a screen directly connected to the pi or use an SSH session.  I have used Kitty in my tests.  If you Kitty screen is not large enough you will recieve strange display errors.


# Screen Layout
The screen has 5 areas of scrolling text.


## Top Row
![Top Row](https://github.com/datagod/meshtalk/blob/main/pics/Meshtalk%20messages.jpg?raw=true "Top Row")

The top row has basic information messages from the system, a debug area that shows the currently executing function, and a spot to show incoming messages.


## Decoded Packets
![Decoded Packets](https://github.com/datagod/meshtalk/blob/main/pics/Meshtalk%20packet.jpg?raw=true "Packet values")

Each packet that is intercepted will be displayed here in, decoded.  Some fields such as RAW are not supported yet.  This type of window is using a wrap around function to display the new lines.


## Extended Info
![Just the Keys](https://github.com/datagod/meshtalk/blob/main/pics/Meshtalk%20extended%20info.jpg?raw=true "Extended Info")

This is a curses text pad that scrolls upwards as new lines are entered.  In this example I am displaying the connected nodes in the mesh.


## Help
![Help is here!](https://github.com/datagod/meshtalk/blob/main/pics/Meshtalk%20help%20window%20send%20message.jpg?raw=true "Help")

This is a curses text pad that scrolls upwards as new lines are entered.  In this example I am displaying the connected nodes in the mesh.

## Send Messages
As per the help instructions, press S to send a message.  Press control+g when finished.

## Viewing Messages
![Messages](https://github.com/datagod/meshtalk/blob/main/pics/Meshtalk%20help%20window%20send%20message%202.jpg?raw=true "Messages")

As messages are sent or received, they are displayed in the Messages text box.  


# Installation

## Meshtastic Python
Make sure to follow the guide here to install the tools needed to connect to the Meshtastic device using Python.
https://meshtastic.org/docs/software/python/python-installation

## MeshWatch

![Install](https://github.com/datagod/meshtalk/blob/main/pics/MeshtalkInstall.jpg?raw=true "Install")

## GeoPy
We use a function from the GeoPy module to calculate distance between nodes.

https://pypi.org/project/geopy/
~~~
pip3 install geopy
~~~

# Connect to Device
Connect your Raspberry Pi to the Meshtastic device via USB cable.
For more information on setting up software to talk to the device, see the following:



# Usage
To receive packets and decode them in a fancy text based display, use the following command:

![Run](https://github.com/datagod/meshtalk/blob/main/pics/MeshtalkHowToRun.jpg?raw=true "How to run")

