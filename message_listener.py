import socket
from hl7apy.parser import parse_message  # Make sure to install hl7apy

class MessageListener:

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen()
            print(f"Listening for HL7 messages on {self.host}:{self.port}")

            while True:
                connection, address = server_socket.accept()
                with connection:
                    print(f"Connected by {address}")
                    while True:
                        # Receive data using the MLLP protocol
                        data = connection.recv(1024)
                        if not data:
                            break

                        # MLLP starts and ends with byte flags
                        if data.startswith(b'\x0b') and data.endswith(b'\x1c\r'):
                            # Extract the message without MLLP flags
                            message_data = data[1:-2]
                            hl7_message = message_data.decode('utf-8')

                            # Parse the HL7 message
                            parsed_message = parse_message(hl7_message)
                            
                            # Here you would handle the parsed_message as needed
                            print(f"Received message: {parsed_message}")

                            # Send an MLLP ACK
                            ack = self.create_ack(parsed_message)
                            connection.sendall(ack)
                        else:
                            print("Received data not conforming to MLLP protocol")

    def create_ack(self, hl7_message):
        # Create an HL7 ACK message in response to hl7_message
        # This is a placeholder function, you need to create an actual ACK
        # message based on the specifics of the hl7_message received
        ack_message = '...create HL7 ACK message...'
        mllp_ack = b'\x0b' + ack_message.encode('utf-8') + b'\x1c\r'
        return mllp_ack


if __name__ == '__main__':
    HOST = 'localhost'  # Standard loopback interface address
    PORT = 12345        # Port to listen on (non-privileged ports are > 1023)

    listener = MessageListener(HOST, PORT)
    listener.start_server()
