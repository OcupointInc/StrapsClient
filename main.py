import socket
import time
import control_pb2 # Assumes this is generated from your provided .proto file

# --- Configuration ---
SERVER_IP = "192.168.1.28"
SERVER_PORT = 5000
BUFFER_SIZE = 4096

def send_packet(sock, packet_to_send):
    """Helper function to serialize, send, and receive a protobuf packet."""
    try:
        # Clear any previous oneof field
        packet_type = packet_to_send.WhichOneof('message_id')
        serialized_data = packet_to_send.SerializeToString()
        print(f"\n> Sending: {packet_type} ({len(serialized_data)} bytes)")

        sock.sendall(serialized_data)
        data_received = sock.recv(BUFFER_SIZE)

        if not data_received:
            print("< No response received from server.")
            return None

        received_packet = control_pb2.Packet()
        received_packet.ParseFromString(data_received)
        response_type = received_packet.WhichOneof('message_id')
        print(f"< Received: {response_type} ({len(data_received)} bytes)")
        return received_packet

    except socket.timeout:
        print("Error: Socket operation timed out.")
        return None
    except Exception as e:
        print(f"An error occurred in send_packet: {e}")
        return None

def get_and_print_status(sock):
    """Sends a GetStatusRequest and prints the received device state."""
    print("\n" + "~"*50)
    print("Requesting Current Device Status...")
    print("~"*50)

    # Create maps to translate enum integers back to strings for printing
    rf_switch_map = {v: k for k, v in control_pb2.RfSwitchOption.items()}
    mixer_switch_map = {v: k for k, v in control_pb2.MixerSwitchOption.items()}
    if_switch_map = {v: k for k, v in control_pb2.IfSwitchOption.items()}

    packet_to_send = control_pb2.Packet()
    # The GetStatusRequest is empty, so we just need to select it
    packet_to_send.get_status_request.SetInParent()

    response_packet = send_packet(sock, packet_to_send)

    if response_packet and response_packet.WhichOneof('message_id') == 'get_status_response':
        status = response_packet.get_status_response
        print("\n" + "*"*20 + " DEVICE STATUS " + "*"*19)
        # Note: Your GetStatusResponse has one 'attenuation_db' field.
        # This example assumes it reflects the FRONTEND attenuation.
        print(f"  LO Frequency         : {status.lo_frequency_mhz} MHz")
        print(f"  Frontend Attenuation : {status.attenuation_db} dB")
        print("-" * 50)
        print(f"  Channels Enabled     : {status.channels_enabled}")
        print(f"  Calibration Enabled  : {status.calibration_enabled}")
        print("-" * 50)
        print(f"  RF Switch            : {rf_switch_map.get(status.rf_switch, 'UNKNOWN')}")
        print(f"  Mixer Switch         : {mixer_switch_map.get(status.mixer_switch, 'UNKNOWN')}")
        print(f"  IF Switch            : {if_switch_map.get(status.if_switch, 'UNKNOWN')}")
        print("*"*50 + "\n")
    else:
        print("Failed to get device status or received an unexpected response.")

def wait_for_enter(prompt="Press Enter to continue..."):
    """Waits for the user to press Enter."""
    input(prompt)

def main():
    """Main function to run the control sequence."""
    print(f"Attempting to connect to server at {SERVER_IP}:{SERVER_PORT}...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(10) # 10-second timeout
            sock.connect((SERVER_IP, SERVER_PORT))
            print("✅ Connection successful.")

            packet = control_pb2.Packet()

            # 1. Get and print initial status
            get_and_print_status(sock)
            wait_for_enter("Press Enter to begin calibration setup...")

            # 2. Go into calibration mode with 0 dB attenuation
            print("\n" + "="*50)
            print("Step 1: Entering Calibration Mode (0 dB Attenuation)")
            print("="*50)
            packet.set_cal_enabled_request.enabled = True
            send_packet(sock, packet)

            packet.set_frontend_attenuation_request.attenuation_db = 0
            send_packet(sock, packet)

            packet.set_cal_attenuation_request.attenuation_db = 0
            send_packet(sock, packet)
            get_and_print_status(sock)
            wait_for_enter()

            # 3. Set calibration attenuation to 30 dB
            print("\n" + "="*50)
            print("Step 2: Setting Calibration Attenuation to 30 dB")
            print("="*50)
            packet.set_cal_attenuation_request.attenuation_db = 30
            send_packet(sock, packet)
            get_and_print_status(sock)
            wait_for_enter()

            # 4. Loop through all RF bands
            print("\n" + "="*50)
            print("Step 3: Looping Through All RF Bands")
            print("="*50)
            # We skip the first item ('RF_BAND_10_900MHZ') if it's a default/placeholder
            # or iterate through all defined bands.
            for band_name, band_value in control_pb2.RfBand.items():
                print(f"--> Setting RF Band to: {band_name}")
                packet.set_rf_band_request.band = band_value
                send_packet(sock, packet)
                time.sleep(0.5) # Brief pause between commands
            get_and_print_status(sock)
            wait_for_enter()

            # 5. Manually set switch states
            print("\n" + "="*50)
            print("Step 4: Manually Setting Switch State")
            print("="*50)
            print("--> Setting: 4GHz LPF, Mixer Bypass, 1.2GHz Bandpass")
            packet.set_switches_request.rf_switch = control_pb2.RF_SWITCH_OPTION_4GHZ_LPF
            packet.set_switches_request.mixer_switch = control_pb2.MIXER_SWITCH_OPTION_BYPASS
            packet.set_switches_request.if_switch = control_pb2.IF_SWITCH_OPTION_1_2GHZ_BANDPASS
            send_packet(sock, packet)
            get_and_print_status(sock)
            wait_for_enter()

            # 6. Manually set LO frequency
            print("\n" + "="*50)
            print("Step 5: Manually Setting LO Frequency to 2250 MHz")
            print("="*50)
            packet.set_pll_frequency_request.frequency_mhz = 2250
            send_packet(sock, packet)
            get_and_print_status(sock)

            print("\n✅ Sequence Finished.")

    except ConnectionRefusedError:
        print(f"❌ Error: Connection refused. Is the server running at {SERVER_IP}:{SERVER_PORT}?")
    except socket.timeout:
        print(f"❌ Error: Connection timed out.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
    finally:
        print("Connection closed.")

if __name__ == "__main__":
    main()