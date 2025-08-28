import socket
import control_pb2

# --- Configuration ---
BUFFER_SIZE = 4096

def send_packet(sock, packet_to_send):
    """Helper function to serialize, send, and receive a protobuf packet."""
    try:
        packet_type = packet_to_send.WhichOneof('message_id')
        serialized_data = packet_to_send.SerializeToString()
        #print(f"\n> Sending: {packet_type} ({len(serialized_data)} bytes)")

        sock.sendall(serialized_data)
        data_received = sock.recv(BUFFER_SIZE)

        if not data_received:
            print("< No response received from server.")
            return None

        received_packet = control_pb2.Packet()
        received_packet.ParseFromString(data_received)
        response_type = received_packet.WhichOneof('message_id')
        #print(f"< Received: {response_type} ({len(data_received)} bytes)")
        return received_packet

    except socket.timeout:
        print("Error: Socket operation timed out.")
        return None
    except Exception as e:
        print(f"An error occurred in send_packet: {e}")
        return None

def get_and_print_status(sock):
    """Sends a GetStatusRequest and prints the received device state using enum names."""
    #print("\n" + "~"*50)
    #print("Requesting Current Device Status...")
    #print("~"*50)

    packet_to_send = control_pb2.Packet()
    packet_to_send.get_status_request.SetInParent()

    response_packet = send_packet(sock, packet_to_send)

    if response_packet and response_packet.WhichOneof('message_id') == 'get_status_response':
        status = response_packet.get_status_response

        print("\n" + "*"*20 + " DEVICE STATUS " + "*"*19)
        print(f"  Calibration Enabled  : {status.calibration_enabled}")
        print(f"  Frontend Attenuation : {status.attenuation_db} dB")
        print(f"  LO Frequency         : {status.lo_frequency_mhz} MHz")
        print(f"  RF Switch State      : {control_pb2.RfSwitchOption.Name(status.rf_switch)}")
        print(f"  Mixer Switch State   : {control_pb2.MixerSwitchOption.Name(status.mixer_switch)}")
        print(f"  IF Switch State      : {control_pb2.IfSwitchOption.Name(status.if_switch)}")
        print("*"*50 + "\n")
    else:
        print("Failed to get device status or received an unexpected response.")

def wait_for_enter(prompt="Press Enter to continue..."):
    """Waits for the user to press Enter."""
    input(prompt)

def print_step_header(step_number, description):
    """Prints a formatted header for a main step in the sequence."""
    print("\n" + "="*50)
    print(f"Step {step_number}: {description}")
    print("="*50)