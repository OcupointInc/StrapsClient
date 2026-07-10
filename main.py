import socket
import time
import control_pb2
from utils import send_packet, get_and_print_status, wait_for_enter, print_step_header, source_name

# --- Configuration ---
SERVER_IP = "192.168.0.90"
SERVER_PORT = 5000

def main():
    """Main function to run the control sequence."""
    print(f"Attempting to connect to server at {SERVER_IP}:{SERVER_PORT}...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(10)  # 10-second timeout
            sock.connect((SERVER_IP, SERVER_PORT))
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) # Add this
            print("✅ Connection successful.")

            # 1. Get and print initial status
            print_step_header(1, "Status")
            channels_packet = control_pb2.Packet()
            channels_packet.set_channels_enabled_request.enabled = True
            send_packet(sock, channels_packet)
            get_and_print_status(sock)
            
            print("\n✅ Sequence Finished.")

            # 2. Go into calibration mode with 0 dB attenuation for the frontend
            print_step_header(2, "Entering Calibration Mode (0 dB Attenuation)")
            
            # Set calibration enabled
            cal_packet = control_pb2.Packet()
            cal_packet.set_cal_enabled_request.enabled = True
            send_packet(sock, cal_packet)

            # Set frontend attenuation
            frontend_atten_packet = control_pb2.Packet()
            frontend_atten_packet.set_frontend_attenuation_request.attenuation_db = 0
            send_packet(sock, frontend_atten_packet)
            
            get_and_print_status(sock)
            wait_for_enter()

            # 2. Go into through path mode with 0 dB attenuation for the frontend
            print_step_header(3, "Entering Calibration Mode (0 dB Attenuation)")
            
            # Set calibration enabled
            cal_packet = control_pb2.Packet()
            cal_packet.set_cal_enabled_request.enabled = False
            send_packet(sock, cal_packet)
            
            get_and_print_status(sock)
            wait_for_enter()

            # 3. Set frontend attenuation to 30 dB
            print_step_header(4, "Setting Frontend Attenuation to 30 dB")
            frontend_atten_packet = control_pb2.Packet()
            frontend_atten_packet.set_frontend_attenuation_request.attenuation_db = 30
            send_packet(sock, frontend_atten_packet)
            get_and_print_status(sock)
            wait_for_enter()

            # 4. Set frontend attenuation to 30 dB
            print_step_header(5, "Setting Frontend Attenuation to 0 dB")
            frontend_atten_packet = control_pb2.Packet()
            frontend_atten_packet.set_frontend_attenuation_request.attenuation_db = 0
            send_packet(sock, frontend_atten_packet)
            get_and_print_status(sock)
            wait_for_enter()
            
            # 5. Toggle the calibration source (CAL_SEL) between internal and external.
            #    The internal noise-source amp only comes on when calibration mode
            #    is enabled AND the internal source is selected, so enable cal first.
            print_step_header(6, "Selecting the Calibration Source")
            cal_packet = control_pb2.Packet()
            cal_packet.set_cal_enabled_request.enabled = True
            send_packet(sock, cal_packet)

            for internal in (True, False):
                print(f"\n--- Setting Calibration Source to {source_name(internal)} ---")
                cal_source_packet = control_pb2.Packet()
                cal_source_packet.set_cal_source_request.internal = internal
                send_packet(sock, cal_source_packet)
                get_and_print_status(sock)
                wait_for_enter()

            cal_packet = control_pb2.Packet()
            cal_packet.set_cal_enabled_request.enabled = False
            send_packet(sock, cal_packet)

            # 6. Toggle the reference clock source (CLK_SEL) between the on-board
            #    oscillator and an external reference. This selects what the LMX2595
            #    LO locks to, so it must be set before tuning the PLL below.
            print_step_header(7, "Selecting the Reference Clock Source")
            for internal in (False, True):
                print(f"\n--- Setting Clock Source to {source_name(internal)} ---")
                clock_packet = control_pb2.Packet()
                # CLK_SEL wire field is named `external`, but the board's polarity
                # is inverted from that name, so map `internal` straight through.
                clock_packet.set_clock_source_request.external = internal
                send_packet(sock, clock_packet)
                get_and_print_status(sock)
                wait_for_enter()

            # 7. Loop through all RF bands
            print_step_header(8, "Looping through RF bands")
            # Get a list of all RF band enum values
            rf_bands = control_pb2.RfBand.values()
            
            for band_value in rf_bands:
                band_name = control_pb2.RfBand.Name(band_value)
                print(f"\n--- Setting RF Band to {band_name} ---")
                
                band_packet = control_pb2.Packet()
                band_packet.set_rf_band_request.band = band_value
                send_packet(sock, band_packet)
                
                get_and_print_status(sock)
                wait_for_enter(f"Press Enter to go to the next RF Band...")
        

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