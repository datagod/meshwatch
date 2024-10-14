![TheDevice](https://github.com/datagod/meshtalk/blob/main/pics/Meshtastic%20device%20raspberry%20pi.jpg?raw=true "Top Row")



** Summarized by ChatGPT**

- **Program Name:** MeshWatch
- **Purpose:** Interacts with Meshtastic devices to send and receive messages over a mesh network, providing a text-based user interface (UI) using the curses library.

**Main Functionalities:**

1. **Meshtastic Interaction:**
   - Uses the Meshtastic library to communicate with mesh network devices.
   - Sends text messages to nodes in the mesh network.
   - Receives messages from nodes and displays them.

2. **User Interface:**
   - Implements a text-based UI using the curses library.
   - Defines custom classes `TextWindow` and `TextPad` to manage window layouts and text output.
   - Displays multiple windows for device info, debug messages, alerts, data packets, extended information, and help.

3. **Keyboard Interaction:**
   - Captures and processes keyboard input to perform various actions:
     - **'s'** - Send a message.
     - **'i'** - Request node information.
     - **'n'** - Display all nodes in the mesh network.
     - **'l'** - Show system logs (e.g., kernel logs).
     - **'t'** - Test the mesh network by sending messages at intervals.
     - **'c'** - Clear all windows/screens.
     - **'q'** - Quit the program.
     - **'r'** - Restart the MeshWatch program.
     - **Spacebar** - Pause or resume output.

4. **Packet Handling:**
   - Defines `onReceive` callback to handle incoming packets.
   - Implements a recursive `DecodePacket` function to parse and display packet contents.
   - Updates UI with packet details and message content.

5. **Device and Node Management:**
   - Retrieves and displays information about the connected Meshtastic device.
   - Keeps track of device status, name, port, hardware model, MAC address, device ID, battery level, and GPS coordinates.
   - Calculates distance between nodes using latitude and longitude data with the `geopy` library.
   - Displays a list of all nodes in the mesh network with their details.

6. **Logging and Debugging:**
   - Provides functions to display system logs (`DisplayLogs`) and debug information.
   - Uses a priority output mechanism to control the flow of information when displaying logs.

7. **Error Handling and Cleanup:**
   - Implements an `ErrorHandler` function to catch exceptions and display error messages gracefully.
   - Handles `SIGINT` (Ctrl-C) to exit the program cleanly using `SIGINT_handler`.
   - Ensures the terminal state is restored on exit with `FinalCleanup`.

8. **Network Testing:**
   - Includes a `TestMesh` function to send a series of messages at specified intervals to test network reliability.

9. **Command-Line Arguments:**
   - Uses `argparse` to process command-line arguments:
     - **'-s' or '--send'** - Send a specified text message.
     - **'-t' or '--time'** - Set the duration to listen before exiting (default is 36000 seconds).

10. **Miscellaneous:**
    - Calculates tile coordinates for map services using latitude and longitude.
    - Displays help information within the UI.
    - Manages the output speed to create a retro feel and allows pausing/resuming of output.

**Technical Details:**

- **Libraries Used:**
  - `meshtastic` for device communication.
  - `curses` for the text-based UI.
  - `pubsub` for subscribing to Meshtastic events.
  - `geopy.distance` for calculating distances between GPS coordinates.
  - `argparse` for command-line argument parsing.
  - `signal` and `sys` for signal handling and exiting the program.
  - Other standard libraries (`time`, `datetime`, `traceback`, etc.) for various utilities.

- **Program Structure:**
  - **Classes:**
    - `TextWindow` - Manages individual text windows in the UI.
    - `TextPad` - Handles scrolling text pads within windows.
  - **Functions:**
    - UI management (`CreateTextWindows`, `UpdateStatusWindow`, etc.).
    - Meshtastic event handlers (`onReceive`, `onConnectionEstablished`, etc.).
    - Keyboard input processing (`PollKeyboard`, `ProcessKeypress`).
    - Packet decoding (`DecodePacket`).
    - Error handling (`ErrorHandler`).
    - Utility functions for logs and network testing.

- **Execution Flow:**
  - Initializes the curses UI and sets up windows.
  - Connects to the Meshtastic device via the serial interface.
  - Subscribes to necessary Meshtastic events.
  - Enters a loop to listen for messages and handle keyboard input.
  - Cleans up and exits gracefully upon termination.

**Usage Summary:**

- Run the script to start the MeshWatch program.
- Use keyboard commands to interact with the mesh network and perform various actions.
- Monitor the UI windows for real-time updates on device status, messages, and network information.
- Use command-line arguments to send messages or set the listening duration when starting the program.




-------------------------------------------------

# Project: RENAMED
The MeshTalk name is already used, and since this program does so much more I decided now is the time to change the name.

# MeshWatch
MeshWatch is a python3 program that will allow you to send and receive messages from python. The messages are decoded and displayed in a text based interface created with Curses.

I built this project with the goal of learning about the Meshtastic API and to get used to using new development tools such as Visual Studio Code and GitHub.

My progress can be followed here:  https://datagod.hashnode.dev/series/meshtalk-development

Shameless Plug: https://hashnode.com/@datagod/joinme


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

