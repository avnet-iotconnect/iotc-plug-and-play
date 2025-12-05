# /IOTCONNECT Plug and Play Guide

1. [Introduction](#1-introduction)
2. [Device Setup](#2-device-setup)
3. [Add Plug and Play Python App to Your Device](#3-add-plug-and-play-python-app-to-your-device)
4. [Modify Your Application to Send Data and/or Receive Commands](#4-modify-your-application-to-send-data-andor-receive-commands)
5. [Update Device Template](#5-update-device-template)
9. [Resources](#9-resources)

# 1. Introduction

This guide will walk you through how to connect your supported device to /IOTCONNECT using a "socket-style" 
Python application designed to receive data from any type of process via JSON buffer which it can then 
transmit to /IOTCONNECT as telemetry. The application can also receive commands from /IOTCONNECT and hand 
them off to your application(s) through a similar JSON buffer.

This framework allows users to make **minimal modifications** to their existing application(s) while still 
reaping the full benefits of the /IOTCONNECT platform, and also allows multiple processes to report data to 
a single /IOTCONNECT cloud connection.

This guide also includes a working example application and detailed instructions on the modifications that could
be used to "plug it into" the /IOTCONNECT system to enable telemetry reporting and cloud-command handling.

After following this guide you should be able to connect your own custom application to /IOTCONNECT with ease!

# 2. Device Setup

In the Quickstart guide for your supported board in the [/IOTCONNECT Python Lite Demos repo](https://github.com/avnet-iotconnect/iotc-python-lite-sdk-demos/tree/main), 
follow each of the steps until you reach the "Using the Demo" step. 

This will walk you through how to set up your hardware, configure the software, and onboard your device into /IOTCONNECT.

> [!NOTE]
>  Since these steps can differ board-to-board it is important you look at the Quickstart **for your specific device.**

# 3. Add Plug and Play Python App to Your Device

Navigate to the `/home/weston/demo` directory on your device and download the /IOTCONNECT Plug and Play Python 
application using these commands in the console:

```
cd /home/weston/demo
wget https://raw.githubusercontent.com/avnet-iotconnect/iotc-plug-and-play/main/iotc-pnp-app.py
```

# 4. Modify Your Application to Send Data and/or Receive Commands

The /IOTCONNECT Plug and Play application will periodically read data from a local JSON file, so to get your data 
to /IOTCONNECT all you need to do is send it to that JSON.

Additionally, the /IOTCONNECT Plug and Play application can receive cloud commands that will be relayed (along with 
any paramaters as well as a Unix timestamp) to another local JSON buffer. To receive those commands in your application 
all you need to do is periodically read from that JSON.

> [!NOTE]
> By default, the /IOTCONNECT Plug and Play application will look for the JSON called `data-buffer.json` located in
> the `/home/weston/demo` directory. Similarly, the /IOTCONNECT Plug and Play application will report commands to a
> JSON called `command-buffer.json` in the same directory. You can modify this file name or directory by altering the
> `DATA_BUFFER_PATH` and `COMMAND_BUFFER_PATH` values towards the top of the `iotc-pnp-app.py` application file.

Here is a basic Python script that can represent your existing application:

```
#!/usr/bin/env python3
"""
Random Data Generator

Generates a random integer (0-100) and random color every 5 seconds.
"""

import time
import random
from datetime import datetime


# List of colors to choose from
COLORS = ["red", "blue", "green", "yellow", "orange", "purple", "black", "white"]


def generate_random_data():
    random_int = random.randint(0, 100)
    random_color = random.choice(COLORS)
    return random_int, random_color


def main():
    try:
        while True:
            number, color = generate_random_data()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Number: {number}, Color: {color}")
            time.sleep(5)


if __name__ == "__main__":
    main()
```

To report the random integer and color to the JSON buffer to be picked up by the /IOTCONNECT app, 
here is how you would modify the main loop in the example script:

```
def main():
    try:
        while True:
            number, color = generate_random_data()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Number: {number}, Color: {color}")

            # ----------------- ADD THIS -----------------
            data = {"random_number": number, "random_color": color}
            with open(DATA_BUFFER_PATH, "w") as f:
                json.dump(data, f)
            # --------------------------------------------

            time.sleep(5)

```
> [!IMPORTANT]
> If you plan to report data to /IOTCONNECT from multiple concurrent applications, you will need to use file-locking
> to ensure that only 1 application is modifying the data buffer at a time. In that case you would need to add
> `import fcntl` and then your modified main loop would instead be:
>```
>def main():
>    try:
>        while True:
>            number, color = generate_random_data()
>            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
>            print(f"[{timestamp}] Number: {number}, Color: {color}")
>
>            # ----------------- ADD THIS -----------------
>            data = {"random_number": number, "random_color": color}
>            with open(DATA_BUFFER_PATH, "w") as f:
>                fcntl.flock(f, fcntl.LOCK_EX)  # Acquire exclusive lock for writing
>                json.dump(data, f)
>                fcntl.flock(f, fcntl.LOCK_UN)  # Release lock
>            # --------------------------------------------
>
>            time.sleep(5)
>```

To add the functionality to receive and act upon cloud commands, you would simply create a function 
(and a timestamp global variable) to handle the incoming commands similar to this:

```
last_processed_timestamp = None

def handle_cloud_command(command_name, command_parameters, timestamp):
    global last_processed_timestamp

    # Check if command has already been processed
    if timestamp == last_processed_timestamp:
        return

    # Check if command is recognized
    if command_name not in ["Command_A", "Command_B"]:
        print(f"Command not recognized: {command_name}")
        return
    
    # Update the last processed timestamp
    last_processed_timestamp = timestamp
    
    # Process the recognized command
    print(f"Command received: {command_name}")
    
    if command_name == "Command_A":
        print(f"Executing protocol for Command_A with parameters: {command_parameters}")
    elif command_name == "Command_B":
        print(f"Executing protocol for Command_B with parameters: {command_parameters}")
```

Then in your main loop you could periodically check the command buffer JSON and call the command handler like this:

```
def main():
    try:
        while True:
            number, color = generate_random_data()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Number: {number}, Color: {color}")

            # ----------------- ADD THIS -----------------
            with open(COMMAND_BUFFER_PATH, "r") as f:
                command_dict = json.load(f)
            handle_cloud_command(command_dict["command_name"], command_dict["parameters"], command["timestamp"]
            # --------------------------------------------

            time.sleep(5)

```
> [!NOTE]
> The command JSON is always going to be structured with these 3 keys: "command_name" (string), "parameters"
> (string including all parameters space-separated), and "timestamp" (float value of Unix timestamp).

To include both the data-reporting and command-receiving functionalities as well as the required imports and definitions, 
the new version of the overall example script would be:

```
#!/usr/bin/env python3
"""
Random Data Generator

Generates a random integer (0-100) and random color every 5 seconds.
"""

import time
import random
from datetime import datetime
import json


# List of colors to choose from
COLORS = ["red", "blue", "green", "yellow", "orange", "purple", "black", "white"]

COMMAND_BUFFER_PATH = "/home/weston/demo/command-buffer.json"
DATA_BUFFER_PATH = "/home/weston/demo/data-buffer.json"

last_processed_timestamp = None

def handle_cloud_command(command_name, command_parameters, timestamp):
    global last_processed_timestamp

    # Check if command has already been processed
    if timestamp == last_processed_timestamp:
        return

    # Check if command is recognized
    if command_name not in ["Command_A", "Command_B"]:
        print(f"Command not recognized: {command_name}")
        return
    
    # Update the last processed timestamp
    last_processed_timestamp = timestamp
    
    # Process the recognized command
    print(f"Command received: {command_name}")
    
    if command_name == "Command_A":
        print(f"Executing protocol for Command_A with parameters: {command_parameters}")
    elif command_name == "Command_B":
        print(f"Executing protocol for Command_B with parameters: {command_parameters}")


def generate_random_data():
    random_int = random.randint(0, 100)
    random_color = random.choice(COLORS)
    return random_int, random_color


def main():
    try:
        while True:
            number, color = generate_random_data()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Number: {number}, Color: {color}")
            data = {"random_number": number, "random_color": color}
            with open(DATA_BUFFER_PATH, "w") as f:
                json.dump(data, f)
            with open(COMMAND_BUFFER_PATH, "r") as f:
                command_dict = json.load(f)
            handle_cloud_command(command_dict["command"], command_dict["parameters"], command["timestamp"]
            time.sleep(5)

if __name__ == "__main__":
    main()
```

# 5. Update Device Template

For /IOTCONNECT to recognize the data attributes you report and send commands to your device, the template for your device 
will need to be updated.

To create a new template, log into your /IOTCONNECT account at https://console.iotconnect.io/login and then in the blue 
vertical toolbar on the left side of the page, hover over the processor icon and then click "Device" in the resulting dropdown.

<img src="./media/device-page.png">

Now in the Devices page, in the blue horizontal toolbar at the bottom of the screen click on the "Templates" button.

<img src="./media/templates-button.png">

In the Templates page, click on the blue "Create Template" button in the top-right corner.

<img src="./media/create-template-button.png">

Fill in the Template Code and Template Name fields with your desired alpha-numeric values (must start with a letter), and leave the 
Authentication Type and Device Message Version on their default values. Then click "Save".

> [!TIP]
> For simplicity we recommend making the Template Code and Template Name the same values.

In the resulting page, you can add your data attributes, cloud commands, and adjust your data frequency.

If your Data Frequency is not set to 5 by default, it is recommended to change it to 5 since that is the frequency that the Plug and
Play application expects by default.

> [!NOTE]
> If the /IOTCONNECT UI says you cannot set the Data Frequency as low as you would like, submit a support ticket (bottom of the vertical
> toolbar on the left edge of the page) requesting the value be changed to 5 for that template.

To add Attributes (data fields) to your template, click on the "Attributes" tab.

<img src="./media/attributes-tab.png">

Populate the "Local Name" with the exact key name you used for that data field to send it to the JSON buffer. For the example script from above,
the Local Names for the 2 attributes would be `random_color` and `random_number`.

Use the "Data Type" dropdown and select the type that matches the data being reported. For the example script from above,
the Data Type for `random_color` would be STRING and the Data Type for `random_number` would be INTEGER.

> [!TIP]
> For any non-whole number data, it is recomended that the DECIMAL data type be used.

If you are reporting data objects, you can use the OBJECT data type and then add member-attributes of specific types within that object. 

> [!IMPORTANT]
> Ensure that the Local Names are **identical** to the key names used for sending the data to the JSON buffer, as no modifications to the data
> are made by the /IOTCONNECT application.

After an attribute is configured, click the "Save" button to add it to the template.

To add Cloud Commands, click on the "Commands" tab.

<img src="./media/commands-tab.png">

Fill in the "Command Name" and "Command" fields with the values your command handler expects to receive for the "command" key.

> [!NOTE]
> For simplicity, populate the "Command Name" and "Command" fields with the same values.

If the nature of your command would require a parameter, toggle the "Parameter Required" switch to the "ON" position. This will 
prevent a user from accidentally sending a command without a necessary parameter.

Toggle the "Receipt Required" switch to the "ON" position for all commands you add, since the Plug and Play /IOTCONNECT application 
is programmed to send an acknowledgement back to cloud whenever a command is received.

For the example script from above, you would enter `Command_A` for both fields for the first command and then `Command_B` for 
both fields for the second command. The "Parameter Required" switch can be left OFF but the "Receipt Required" should be turned ON.

After a command is configured, click the "Save" button to add it to the template.

Once all desired attributes and commands have been added, navigate back to the "Device" page of /IOTCONNECT and then click on your specific
device name to be taken to your device's page.

In your device's page, click on the pen-and-paper icon next to the "Template" selection.

<img src="./media/edit-template.png">

In the resulting drop-down, select the name of the new template you just created and that new template will instantly be assigned to your device.



# 9. Resources
* [/IOTCONNECT Overview](https://www.iotconnect.io/)
* [/IOTCONNECT Knowledgebase](https://help.iotconnect.io/)
