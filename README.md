# meshtalk
MeshTalk is a python3 program that will allow you to send and receive messages from python. The messages are decoded and displayed in a text based interface created with Curses.

I built this project with the goal of learning about the Meshtastic API and to get used to using new development tools such as Visual Studio Code and GitHub.

My progress can be followed here:  https://datagod.hashnode.dev/series/meshtalk-development

# Built with Curses
This project uses Curses to draw text windows and pads to keep the different types of information separated.  You can use a screen directly connected to the pi or use an SSH session.  I have used Kitty in my tests.  If you Kitty screen is not large enough you will recieve strange display errors.

# Screen Layout
The screen has 5 areas of scrolling text.

![Top Row](https://github.com/datagod/meshtalk/blob/main/pics/Meshtalk%20messages.jpg?raw=true "Top Row")


![Decoded Packets](https://github.com/datagod/meshtalk/blob/main/pics/Meshtalk%20packet.jpg?raw=true "Packet values")


![Just the Keys](https://github.com/datagod/meshtalk/blob/main/pics/meshtalk%20packet%20keys.jpg?raw=true "Packet keys")


