
import socket
import simulator
import time
from message_parser import receive_message_from_listener


ACK = [
    "MSH|^~\&|||||20240129093837||ACK|||2.5",
    "MSA|AA",
]

TEST_MLLP_PORT = 8440

def to_mllp(segments):
    m = bytes(chr(simulator.MLLP_START_OF_BLOCK), "ascii")
    m += bytes("\r".join(segments) + "\r", "ascii")
    m += bytes(chr(simulator.MLLP_END_OF_BLOCK) + chr(simulator.MLLP_CARRIAGE_RETURN), "ascii")
    return m

def from_mllp(buffer):
    return str(buffer[1:-3], "ascii").split("\r") # Strip MLLP framing and final \r

def listen_for_messages():
    messages = []
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("localhost", TEST_MLLP_PORT))
                print(f"Listening for HL7 messages on 'localhost':{TEST_MLLP_PORT}")
                while True:
                    buffer = s.recv(1024)
                    if len(buffer) == 0:
                        break
                    receive_message_from_listener(from_mllp(buffer))
                    messages.append(from_mllp(buffer))
                    ack = to_mllp(ACK)
                    s.sendall(ack[0:len(ack)//2])
                    time.sleep(1) # Wait for TCP buffer to empty
                    s.sendall(ack[len(ack)//2:])

    
if __name__ == '__main__':
    listen_for_messages()