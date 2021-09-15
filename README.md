# MeshTalk
MeshTalk is a python3 program that will allow you to send and receive messages from python. The messages are decoded and displayed in a text based interface created with Curses.

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

# Just the keys
![Just the Keys](https://github.com/datagod/meshtalk/blob/main/pics/meshtalk%20packet%20keys.jpg?raw=true "Packet keys")

I wanted to see just a list of the keys for each received package so I list them here.  This is a curses pad, which will keep scrolling as new data arrives.

# Usage
![How to run](https://github.com/datagod/meshtalk/blob/main/pics/MeshtalkUsage1.jpg?raw=true "Usage")


