That's a great addition for a typical lab or field setup. Here's the updated README with the "Direct PC Connection (Static IP)" section added for Windows users, along with a minor update to the "Hardware Overview" for clarity.

-----

# STRAPS RF Frontend Control Example

This repository contains example Python code to interface with the Black Canyon RF Frontend, demonstrating comprehensive control over its advanced features.

-----

## Introduction

This code serves as a foundational example for interacting with the RF Frontend via a TCP/IP connection, utilizing Google's **Protocol Buffers** for structured and reliable communication. It showcases how to control the unit's core functionalities, including:

  * Setting calibration mode and attenuation levels.
  * Cycling through predefined RF frequency bands.
  * Manually configuring the internal RF, Mixer, and IF switch states.
  * Setting the Local Oscillator (LO) frequency.
  * Querying the device for its complete operational status.

-----

## Features

  * **Calibration Control:** Enable or disable the frontend's calibration mode.
  * **Dual Attenuation Control:** Independently set attenuation for both the main **frontend** path and the **calibration** path.
  * **RF Band Selection:** Easily switch between the system's defined operational frequency bands.
  * **Manual Switch Control:** Directly command the state of the RF, Mixer, and IF switch banks for custom signal path configuration.
  * **LO Frequency Setting:** Manually set the frequency of the internal PLL/LO synthesizer.
  * **Comprehensive Status Inquiry:** Request and display the current operational status of the device, including LO frequency, attenuation levels, switch states, and more.

-----

## Hardware Overview

The Black Canyon RF Frontend is a versatile network-attached device. It presents itself as a distinct network device with its own **static IP address** and MAC address. The MAC address for the system is conveniently labeled on the exterior of the enclosure.

**Network Connectivity:**

  * **DHCP Connection:** For the device to obtain an IP address, it must be connected to a network that provides DHCP (e.g., a router). You can typically find the assigned IP address through your router's administration interface by looking for the device's MAC address.
  * **Direct PC Connection:** If your device uses a **static IP address**, you can connect directly to it from your PC without a router (see the new section below).

**Powering On:** To power on the unit, simply plug it into a power source. Note that the unit does not have external status LEDs, so its operational state must be confirmed via network connectivity and software commands (like `GetStatusRequest` in `main.py`).

-----

## Direct PC Connection (Static IP) - Windows

If your RF Frontend unit is configured with a **static IP address** and you need to connect directly from a Windows PC (e.g., using a single Ethernet cable), you must configure your PC's Ethernet adapter to be on the **same subnet** as the device.

Let's assume the **RF Frontend's Static IP is `172.16.22.30`** (and thus its subnet is `172.17.22.x` with a Subnet Mask of `255.255.255.0`).

### 1\. Change PC Ethernet Adapter Settings

1.  Open the **Control Panel** and navigate to **Network and Sharing Center**.
2.  Click **Change adapter settings**.
3.  **Right-click** on the Ethernet connection that you are using to connect to the RF Frontend and select **Properties**.
4.  In the Properties window, find and select **Internet Protocol Version 4 (TCP/IPv4)**, then click **Properties**.
5.  Select **Use the following IP address**.
6.  Enter the following:
      * **IP address:** `172.16.22.10` (or any address on the `172.16.22.x` subnet *except* the device's IP, `172.16.22.30`).
      * **Subnet mask:** `255.255.255.0`
      * **Default gateway:** Leave this blank.
7.  Click **OK** on all windows to save the settings.

### 2\. Test the Connection

1.  Open the **Command Prompt** or **PowerShell**.
2.  Ping the RF Frontend's static IP address to confirm connectivity:
    ```bash
    ping 172.16.22.30
    ```
3.  You should receive four successful replies. If you receive "Request timed out," double-check the cable, power, and IP settings.

You can now proceed to the Usage section and use the RF Frontend's static IP address in your `main.py` configuration.

-----

## Prerequisites

Before running the example code, ensure you have the following installed:

  * **Python 3.x:** Download from [python.org](https://www.python.org/).
  * **pip:** Python's package installer (usually comes with Python).
  * **`protobuf`:** This Python package is required to work with Protocol Buffers.

-----

## Setup

Follow these steps to set up the environment and run the example:

1.  **Clone the Repository:**

    ```bash
    git clone [https://github.com/OcupointInc/BlackCanyonClient.git](https://github.com/OcupointInc/BlackCanyonClient.git)
    cd BlackCanyonClient
    ```

2.  **Install Python Dependencies:**

    ```bash
    pip install protobuf
    ```

-----

## Usage

The primary example file is `main.py`.

1.  **Configure the Server IP Address:**
    Open `main.py` and modify the `SERVER_IP` variable to match the IP address of your RF Frontend unit. This can be the DHCP-assigned IP or the static IP used for a direct connection.

    ```python
    # --- Configuration ---
    SERVER_IP = "172.16.22.30" # <--- CHANGE THIS TO YOUR DEVICE'S IP
    SERVER_PORT = 5000
    ```

2.  **Run the Example Script:**
    Execute the `main.py` script from your terminal:

    ```bash
    python main.py
    ```

### Script Workflow

The `main.py` script will perform a detailed sequence of operations, pausing for user input between major steps. This allows you to observe the effect of each command.

1.  **Connect** to the specified `SERVER_IP`.
2.  **Get Initial Status:** Queries the device and displays its current state upon connection.
3.  **Enter Calibration Mode:** Enables calibration and sets both **frontend** and **calibration** attenuation to 0 dB.
4.  **Set Cal Attenuation:** Increases the **calibration** path attenuation to 30 dB.
5.  **Cycle RF Bands:** Loops through all available RF bands, setting each one sequentially.
6.  **Manually Set Switches:** Sends a single command to configure a custom state for the RF, Mixer, and IF switches.
7.  **Manually Set LO Frequency:** Sets the LO to a specific frequency (e.g., 2250 MHz).
8.  **Disconnect:** Closes the network connection upon completion.

-----

## Protocol Details

Communication with the RF Frontend uses Google Protocol Buffers. The `control.proto` file defines the message structures for all requests and responses. This ensures a robust and extensible communication protocol.

  * `SetCalibrationEnabledRequest`: Turns calibration on/off.
  * `SetFrontendAttenuationRequest`: Sets the frontend path attenuation.
  * `SetCalAttenuationRequest`: Sets the calibration path attenuation.
  * `SetChannelsEnabledRequest`: Turns RF channels on/off.
  * `SetRfBandRequest`: Selects an operational RF band.
  * `SetSwitchesRequest`: Sets the state of all three switch banks.
  * `SetPllFrequencyRequest`: Sets the LO frequency.
  * `GetStatusRequest`: Retrieves the current state of the device.
  * `GetStatusResponse`: The response containing the device's status.
  * `Packet`: A wrapper message that encapsulates all other message types for transport.

-----

## Troubleshooting

  * **`ConnectionRefusedError`:**
      * Ensure the RF Frontend unit is powered on and connected to your network.
      * Verify that the `SERVER_IP` in `main.py` is correct and matches the IP address assigned to your device.
      * Check for firewall rules on your computer or network that might be blocking TCP port `5000`.
  * **`socket.timeout`:**
      * This indicates that the client sent data but did not receive a response in time.
      * Check network connectivity and ensure the device is operating correctly. A simple power cycle of the RF frontend may resolve the issue.

-----

## License

This example code is provided under the MIT License. Feel free to use, modify, and distribute it as needed.