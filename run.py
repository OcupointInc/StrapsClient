import socket
import json
import argparse
import logging
import time
import control_pb2
from utils import parse_source, source_name

# --- Setup Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def execute_command(sock, key, val):
    """
    Builds and sends a single protobuf packet over an existing socket.
    Returns the parsed response or None.
    """
    packet = control_pb2.Packet()
    
    try:
        # Build the Packet based on the key/val from JSON
        if key == "set_channels_enabled":
            packet.set_channels_enabled_request.enabled = val
        elif key == "set_cal_enabled":
            packet.set_cal_enabled_request.enabled = val
        elif key == "set_cal_source":
            packet.set_cal_source_request.internal = parse_source(val, "cal source")
        elif key == "set_clock_source":
            # The clock select is spelled `external` on the wire, so negate.
            packet.set_clock_source_request.external = not parse_source(val, "clock source")
        elif key == "set_frontend_attenuation":
            packet.set_frontend_attenuation_request.attenuation_db = val
        elif key == "set_rf_band":
            packet.set_rf_band_request.band = control_pb2.RfBand.Value(val)
        elif key == "set_pll_frequency":
            packet.set_pll_frequency_request.frequency_mhz = val
        elif key == "set_switches":
            req = packet.set_switches_request
            if "rf_switch" in val:
                req.rf_switch = control_pb2.RfSwitchOption.Value(val['rf_switch'])
            if "mixer_switch" in val:
                req.mixer_switch = control_pb2.MixerSwitchOption.Value(val['mixer_switch'])
            if "if_switch" in val:
                req.if_switch = control_pb2.IfSwitchOption.Value(val['if_switch'])
        elif key == "get_status":
            packet.get_status_request.SetInParent()
        else:
            logger.warning(f"Unknown command '{key}'. Skipping.")
            return None

        # Serialize and Send
        data_to_send = packet.SerializeToString()
        sock.sendall(data_to_send)
        
        # Wait for Response
        data_received = sock.recv(256) # Increased slightly for status packets
        if not data_received:
            logger.error(f"❌ Device closed the connection unexpectedly during command '{key}'.")
            return None

        response = control_pb2.Packet()
        response.ParseFromString(data_received)
        return response

    except Exception as e:
        logger.error(f"❌ Error during command '{key}': {e}")
        return None

def run_cli():
    parser = argparse.ArgumentParser(description="Hardware Control CLI")
    parser.add_argument("config", help="Path to JSON config file")
    parser.add_argument("--ip", help="Override Server IP")
    parser.add_argument("--port", type=int, help="Override Port")
    args = parser.parse_args()

    # Load JSON Configuration
    try:
        with open(args.config, 'r') as f:
            conf = json.load(f)
        logger.info(f"Successfully loaded config: {args.config}")
    except Exception as e:
        logger.critical(f"Failed to load JSON file: {e}")
        return

    ip = args.ip or conf.get("server_ip")
    port = args.port or conf.get("server_port", 5000)
    cmds = conf.get("commands", {})

    if not ip or not cmds:
        logger.critical("Invalid config: Missing IP or commands.")
        return

    # --- REORDER COMMANDS ---
    # A few commands are order-sensitive regardless of where they sit in the
    # JSON file:
    #   set_clock_source selects the LMX2595's reference, so it has to land
    #     before anything that tunes the LO (set_pll_frequency, set_rf_band).
    #   set_frontend_attenuation goes last, since a band/switch change resets it.
    first_keys = ["set_clock_source"]
    last_keys = ["set_frontend_attenuation"]

    ordered_cmds = [(k, cmds[k]) for k in first_keys if k in cmds]
    ordered_cmds += [(k, v) for k, v in cmds.items()
                     if k not in first_keys and k not in last_keys]
    ordered_cmds += [(k, cmds[k]) for k in last_keys if k in cmds]

    logger.info(f"Opening session with Hardware at {ip}:{port}")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.settimeout(5.0)
            
            sock.connect((ip, port))
            logger.info("Connected successfully.")

            # Iterate through the reordered list
            for key, val in ordered_cmds:
                logger.info(f"Sending: '{key}'")
                
                response = execute_command(sock, key, val)
                
                if response:
                    msg_id = response.WhichOneof('message_id')
                    logger.info(f"✅ Success: {msg_id}")
                    
                    if msg_id == 'get_status_response':
                        s = response.get_status_response
                        logger.info(f"   [Status] Attn: {s.attenuation_db}dB, LO: {s.lo_frequency_mhz}MHz, "
                                    f"Cal: {source_name(s.cal_source_internal)}, "
                                    f"Clock: {source_name(not s.clock_source_external)}")
                
                # Small delay to let hardware settle
                time.sleep(0.05)

    except ConnectionRefusedError:
        logger.error(f"❌ Connection Refused: Is the server running at {ip}:{port}?")
    except socket.timeout:
        logger.error("❌ Connection Timed Out.")
    except Exception as e:
        logger.error(f"❌ Session Error: {e}")

    logger.info("Session closed.")
    
if __name__ == "__main__":
    run_cli()