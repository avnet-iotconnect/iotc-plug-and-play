# /IOTCONNECT Plug and Play Guide

1. [Introduction](#1-introduction)
2. [Device Setup](#2-device-setup)
3. [Add Plug and Play Python App to Your Device](#3-add-plug-and-play-python-app-to-your-device)
4. [Modify Your Application to Send Data to and/or Receive Commands from JSON Buffer](#4-modify-your-application-to-send-data-to-and-or-receive-commands-from-json-buffer)
5. [Device Setup](#5-device-setup)
6. [Onboard Device](#6-onboard-device)
7. [Using the Demo](#7-using-the-demo)
8. [Troubleshooting](#8-troubleshooting)
9. [Resources](#9-resources)

# 1. Introduction

This guide will walk you through how to connect your supported device to /IOTCONNECT using a "socket-style" Python application designed to receive data from any type of 
process via JSON buffer which it can then transmit to /IOTCONNECT as telemetry. The application can also receive commands from /IOTCONNECT and hand them off to your 
application(s) through a similar JSON buffer.

This framework allows users to make **minimal modifications** to their existing application(s) while still reaping the full benefits of the /IOTCONNECT platform, 
and also allows multiple processes to report data to a single /IOTCONNECT cloud connection.

# 2. Device Setup

In the Quickstart guide for your supported board in the [/IOTCONNECT Python Lite Demos repo](https://github.com/avnet-iotconnect/iotc-python-lite-sdk-demos/tree/main), 
follow each of the steps until you reach the "Using the Demo" step. 

This will walk you through how to set up your hardware, configure the software, and onboard your device into /IOTCONNECT.

> [!NOTE]
>  Since these steps can differ board-to-board it is important you look at the Quickstart **for your specific device.**

# 3. Add Plug and Play Python App to Your Device

Navigate to the `/home/weston/demo` directory on your device and download the /IOTCONNECT Plug and Play Python application using these commands in the console:

```
cd /home/weston/demo
wget https://raw.githubusercontent.com/avnet-iotconnect/iotc-plug-and-play/main/iotc-pnp-app.py
```

# 4. Modify Your Application to Send Data to and/or Receive Commands from JSON Buffer



# 7. Using the Demo

Run the basic demo with this command:

```
python3 app.py
```

> [!NOTE]
> Always make sure you are in the ```/home/weston/demo``` directory before running the demo. You can move to this
> directory with the command: ```cd /home/weston/demo```

View the random-integer telemetry data under the "Live Data" tab for your device on /IOTCONNECT.


# 9. Resources
* [/IOTCONNECT Overview](https://www.iotconnect.io/)
* [/IOTCONNECT Knowledgebase](https://help.iotconnect.io/)
