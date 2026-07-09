import socket
import control_pb2

# --- Configuration ---
BUFFER_SIZE = 128

# The calibration-source (CAL_SEL) and clock-source (CLK_SEL) selects are both
# carried on the wire as a single `internal` bool. Spell them as words on the
# way in and out, so a config file never has to encode which way the bool goes.
_INTERNAL_ALIASES = ("internal", "int", "onboard", "on", "noise", "true")
_EXTERNAL_ALIASES = ("external", "ext", "ref", "off", "false")

def parse_source(value, what):
    """Coerce a JSON value into the protobuf `internal` bool.

    Accepts a real bool, or any of the internal/external aliases as a string.
    Raises ValueError on anything else rather than silently picking a default —
    quietly guessing 'external' here would mistune the LO.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        v = value.strip().lower()
        if v in _INTERNAL_ALIASES:
            return True
        if v in _EXTERNAL_ALIASES:
            return False
    raise ValueError(
        f"invalid {what} {value!r}: expected 'internal' or 'external' (or a bool)"
    )

def source_name(internal):
    """Render an `internal` bool back as the word used in configs and logs."""
    return "internal" if internal else "external"

def send_packet(sock, packet_to_send):
    """Helper function to serialize, send, and receive a protobuf packet."""
    try:
        packet_type = packet_to_send.WhichOneof('message_id')
        serialized_data = packet_to_send.SerializeToString()
        print(f"\n> Sending: {packet_type} ({len(serialized_data)} bytes) {serialized_data}")

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
        print(f"  Calibration Source   : {source_name(status.cal_source_internal)}")
        print(f"  Clock Source         : {source_name(status.clock_source_internal)}")
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