# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> and Zackary Andraka <zackary.andraka@avnet.com> et al.
"""
IoTConnect Self-Updating Client

This application connects to the Avnet IoTConnect platform and provides:
- Telemetry data transmission from local JSON buffer
- Command reception and forwarding to application buffer
- Over-The-Air (OTA) update support
- File download capability via commands
- Graceful shutdown with cleanup
"""

# ============================================================================
# Imports
# ============================================================================

# Standard library imports
import sys
import time
import subprocess
import os
import urllib.request
import json
import fcntl

# Third-party imports
import requests
from avnet.iotconnect.sdk.lite import Client, DeviceConfig, C2dCommand, Callbacks, DeviceConfigError
from avnet.iotconnect.sdk.lite import __version__ as SDK_VERSION
from avnet.iotconnect.sdk.sdklib.mqtt import C2dAck, C2dOta


# ============================================================================
# Configuration Constants
# ============================================================================

DATA_FREQUENCY = 5  # Seconds between telemetry transmissions
COMMAND_BUFFER_PATH = "/home/weston/demo/command-buffer.json"
DATA_BUFFER_PATH = "/home/weston/demo/data-buffer.json"


# ============================================================================
# File I/O Utilities
# ============================================================================

def safe_read_json(path):
    """
    Read JSON file with file locking to prevent race conditions.
    
    Uses a shared lock (LOCK_SH) that allows multiple readers but blocks writers.
    
    Args:
        path (str): Path to JSON file
        
    Returns:
        dict: Parsed JSON data
    """
    with open(path, "r") as f:
        fcntl.flock(f, fcntl.LOCK_SH)  # Acquire shared lock for reading
        data = json.load(f)
        fcntl.flock(f, fcntl.LOCK_UN)  # Release lock
    return data


def safe_write_json(path, data):
    """
    Write JSON file with file locking to prevent race conditions.
    
    Uses an exclusive lock (LOCK_EX) that blocks all other readers and writers.
    
    Args:
        path (str): Path to JSON file
        data (dict): Data to write as JSON
    """
    with open(path, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)  # Acquire exclusive lock for writing
        json.dump(data, f, indent=4)
        fcntl.flock(f, fcntl.LOCK_UN)  # Release lock


def cleanup_command_buffer():
    """
    Delete command buffer file if it exists.
    
    Called during graceful shutdown to prevent stale commands from being
    processed when the application restarts.
    """
    try:
        if os.path.exists(COMMAND_BUFFER_PATH):
            os.remove(COMMAND_BUFFER_PATH)
            print(f"Cleaned up command buffer: {COMMAND_BUFFER_PATH}")
    except Exception as e:
        print(f"Error cleaning up command buffer: {e}")


# ============================================================================
# Package Management
# ============================================================================

def extract_and_run_tar_gz(targz_filename):
    """
    Extract a .tar.gz package and execute install.sh if present.
    
    The install.sh script is automatically deleted after execution to prevent
    it from running again on future package updates that may not include it.
    
    Args:
        targz_filename (str): Path to .tar.gz file
        
    Returns:
        bool: True if extraction and installation successful, False otherwise
    """
    try:
        # Extract the tar.gz archive
        subprocess.run(("tar", "-xzvf", targz_filename, "--overwrite"), check=True)
        
        current_directory = os.getcwd()
        script_file_path = os.path.join(current_directory, "install.sh")
        
        # If install.sh is found, execute it then delete it
        if os.path.isfile(script_file_path):
            try:
                subprocess.run(['bash', script_file_path], check=True)
                os.remove(script_file_path)
                print(f"Successfully executed install.sh")
                return True
            except subprocess.CalledProcessError as e:
                os.remove(script_file_path)
                print(f"Error executing install.sh: {e}")
                return False
            except Exception as e:
                os.remove(script_file_path)
                print(f"An error occurred: {e}")
                return False
        else:
            print("install.sh not found in the current directory.")
            return True
            
    except subprocess.CalledProcessError:
        return False


# ============================================================================
# IoTConnect Callback Handlers
# ============================================================================

def on_command(msg: C2dCommand):
    """
    Handle commands received from IoTConnect cloud.
    
    Supports two command types:
    1. file-download: Downloads a file from provided URL and restarts application
    2. All others: Forwards command to local JSON buffer for application processing
    
    Args:
        msg (C2dCommand): Command message from IoTConnect containing command name,
                         arguments, and acknowledgement ID
    """
    global c
    print("Received command", msg.command_name, msg.command_args, msg.ack_id)
    
    # Special handling for file-download command
    if msg.command_name == "file-download":
        if len(msg.command_args) == 1:
            status_message = "Downloading %s to device" % (msg.command_args[0])
            response = requests.get(msg.command_args[0])
            
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Open the file in binary write mode and save the content
                with open('package.tar.gz', 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192): 
                        file.write(chunk)
                print(f"File downloaded successfully and saved to package.tar.gz")
            else:
                print(f"Failed to download the file. Status code: {response.status_code}")
            
            c.send_command_ack(msg, C2dAck.CMD_SUCCESS_WITH_ACK, status_message)
            print(status_message)
            
            # Extract and install the package
            extraction_success = extract_and_run_tar_gz('package.tar.gz')
            
            print("Download command successful. Will restart the application...")
            print("")  # Print a blank line for cleaner output
            sys.stdout.flush()
            
            # Restart the process to apply updates
            os.execv(sys.executable, [sys.executable, __file__] + [sys.argv[0]])
        else:
            c.send_command_ack(msg, C2dAck.CMD_FAILED, "Expected 1 argument")
            print("Expected 1 command argument, but got", len(msg.command_args))
    
    # Forward all other commands to the local command buffer
    else:
        params = ""
        for param in msg.command_args:
            params = params + " " + param
        print("Forwarding command --- %s %s --- to JSON buffer." % (msg.command_name, params))
        
        # Write command to buffer with timestamp for processing by other application
        comm_dict = {
            "command": msg.command_name,
            "parameters": params,
            "timestamp": int(time.time())
        }
        safe_write_json(COMMAND_BUFFER_PATH, comm_dict)
        
        # Send acknowledgement if required by device template
        if msg.ack_id is not None:
            c.send_command_ack(msg, C2dAck.CMD_SUCCESS_WITH_ACK, "Forwarding command")


def on_ota(msg: C2dOta):
    """
    Handle Over-The-Air (OTA) update messages from IoTConnect.
    
    Downloads all files in the OTA package, extracts .tar.gz files,
    executes any install scripts, and restarts the application if successful.
    
    Args:
        msg (C2dOta): OTA update message from IoTConnect containing version
                     and list of URLs to download
    """
    global c
    print("Starting OTA downloads for version %s" % msg.version)
    c.send_ota_ack(msg, C2dAck.OTA_DOWNLOADING)
    
    extraction_success = False
    
    # Download all files in the OTA package
    for url in msg.urls:
        print("Downloading OTA file %s from %s" % (url.file_name, url.url))
        try:
            urllib.request.urlretrieve(url.url, url.file_name)
        except Exception as e:
            print("Encountered download error", e)
            error_msg = "Download error for %s" % url.file_name
            break
        
        # Process .tar.gz files
        if url.file_name.endswith(".tar.gz"):
            extraction_success = extract_and_run_tar_gz(url.file_name)
            if extraction_success is False:
                break
        else:
            print("ERROR: Unhandled file format for file %s" % url.file_name)
    
    # Restart application if OTA was successful
    if extraction_success is True:
        print("OTA successful. Will restart the application...")
        c.send_ota_ack(msg, C2dAck.OTA_DOWNLOAD_DONE)
        print("")  # Print a blank line for cleaner output
        sys.stdout.flush()
        
        # Restart the process to apply updates
        os.execv(sys.executable, [sys.executable, __file__] + [sys.argv[0]])
    else:
        print('Encountered a download processing error. Not restarting.')


def on_disconnect(reason: str, disconnected_from_server: bool):
    """
    Handle disconnection events from IoTConnect.
    
    Args:
        reason (str): Reason for disconnection
        disconnected_from_server (bool): True if server initiated disconnect,
                                        False if client initiated
    """
    print("Disconnected%s. Reason: %s" % (" from server" if disconnected_from_server else "", reason))


# ============================================================================
# Main Application
# ============================================================================

try:
    # Load device configuration from files
    device_config = DeviceConfig.from_iotc_device_config_json_file(
        device_config_json_path="iotcDeviceConfig.json",
        device_cert_path="device-cert.pem",
        device_pkey_path="device-pkey.pem"
    )

    # Initialize IoTConnect client with callbacks
    c = Client(
        config=device_config,
        callbacks=Callbacks(
            ota_cb=on_ota,
            command_cb=on_command,
            disconnected_cb=on_disconnect
        )
    )
    
    # Main telemetry loop
    while True:
        # Ensure connection is established
        if not c.is_connected():
            print('(re)connecting...')
            c.connect()
            if not c.is_connected():
                # Still unable to connect after retries
                print('Unable to connect. Exiting.')
                cleanup_command_buffer()
                sys.exit(2)

        # Read telemetry data from buffer and transmit to IoTConnect
        telemetry = safe_read_json(DATA_BUFFER_PATH)
        c.send_telemetry(telemetry)
        
        # Wait before next transmission
        time.sleep(DATA_FREQUENCY)

except DeviceConfigError as dce:
    # Handle device configuration errors (invalid config files, missing certs, etc.)
    print(dce)
    cleanup_command_buffer()
    sys.exit(1)

except KeyboardInterrupt:
    # Handle graceful shutdown on Ctrl+C
    print("Exiting.")
    if c.is_connected():
        c.disconnect()
    cleanup_command_buffer()
    sys.exit(0)
