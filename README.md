# STRAPS RF Frontend Control Example

This repository contains example Python code to interface with the Black Canyon RF Frontend, demonstrating comprehensive control over its advanced features.

---

## Introduction

This code serves as a foundational example for interacting with the RF Frontend via a TCP/IP connection, utilizing Google's Protocol Buffers for structured and reliable communication. It showcases how to control the unit's core functionalities, including:

* Setting calibration mode and attenuation levels.
* Cycling through predefined RF frequency bands.
* Manually configuring the internal RF, Mixer, and IF switch states.
* Setting the Local Oscillator (LO) frequency.
* Querying the device for its complete operational status.

---

## Features

* **Calibration Control:** Enable or disable the frontend's calibration mode.
* **Dual Attenuation Control:** Independently set attenuation for both the main **frontend** path and the **calibration** path.
* **RF Band Selection:** Easily switch between the system's defined operational frequency bands.
* **Manual Switch Control:** Directly command the state of the RF, Mixer, and IF switch banks for custom signal path configuration.
* **LO Frequency Setting:** Manually set the frequency of the internal PLL/LO synthesizer.
* **Comprehensive Status Inquiry:** Request and display the current operational status of the device, including LO frequency, attenuation levels, switch states, and more.



---

## Hardware Overview

The Black Canyon RF Frontend is a versatile network-attached device. It presents itself as a distinct network device with its own IP address and MAC address. The MAC address for the system is conveniently labeled on the exterior of the enclosure.

**Network Connectivity:** For the device to obtain an IP address, it must be connected to a network that provides DHCP (e.g., a router). You can typically find the assigned IP address through your router's administration interface by looking for the device's MAC address.

**Powering On:** To power on the unit, simply plug it into a power source. Note that the unit does not have external status LEDs, so its operational state must be confirmed via network connectivity and software commands (like `GetStatusRequest` in `main.py`).

---

## Prerequisites

Before running the example code, ensure you have the following installed:

* **Python 3.x:** Download from [python.org](https://www.python.org/).
* **pip:** Python's package installer (usually comes with Python).
* **`protobuf`:** This Python package is required to work with Protocol Buffers.

---

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

---

## Usage

The primary example file is `main.py`.

1.  **Configure the Server IP Address:**
    Open `main.py` and modify the `SERVER_IP` variable to match the IP address of your RF Frontend unit.

    ```python
    # --- Configuration ---
    SERVER_IP = "192.168.1.28" # <--- CHANGE THIS TO YOUR DEVICE'S IP
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

---

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

---

## Troubleshooting

* **`ConnectionRefusedError`:**
    * Ensure the RF Frontend unit is powered on and connected to your network.
    * Verify that the `SERVER_IP` in `main.py` is correct and matches the IP address assigned to your device.
    * Check for firewall rules on your computer or network that might be blocking TCP port `5000`.
* **`socket.timeout`:**
    * This indicates that the client sent data but did not receive a response in time.
    * Check network connectivity and ensure the device is operating correctly. A simple power cycle of the RF frontend may resolve the issue.

---

## License

This example code is provided under the MIT License. Feel free to use, modify, and distribute it as needed.