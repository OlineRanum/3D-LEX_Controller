"""
File: fileReceiver.py

Description:
This script defines a function `receive_file` to receive files over TCP/IP.
It listens for incoming connections on a specified IP address and port,
receives data packets containing files, and writes the files to the 'output' directory.

Functions:
- receive_file(server_ip, server_port): Main function to receive files over TCP/IP.

Usage:
Ensure the IP address and port in the TCP connection part match the settings in the OSC server.
Run the script to start receiving files.

Note:
To kill a Python task in Windows, use the following commands:
tasklist | FIND "python"
>taskkill /F /PID
"""
import socket
import struct
import os

def receive_file(server_ip, server_port, write_path):
    """
    Receive file on a given IP and port.

    Args:
    - server_ip (str): The IP address to bind the server socket to.
    - server_port (int): The port number to bind the server socket to.

    Description:
    This function creates a TCP socket, binds it to the specified IP address and port,
    and listens for incoming connections. It accepts a single connection at a time
    and receives data packets containing files. The received files are written to
    the 'output' directory. The function handles commands and data packets
    according to the opening of the packet message.
    The function is used to receive blendshapes files from an IPhone running
    Live Link Face.

    Returns:
    None
    """

    # Create a TCP socket, and accept only 1 connection simultaniously
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(1)

    file_name = "NoFileNameGiven"
    os.makedirs("output", exist_ok=True)

    print(f"Server listening on {server_ip}:{server_port}")

    # Serve until we are commanded to quit
    while True:
        # Accept a connection from a client
        client_socket, client_address = server_socket.accept()
        print(f"Connection established from {client_address}")

        try:
            # Receive the int32 representing the total size of the file
            size_data = client_socket.recv(4)
            total_size = struct.unpack('>I', size_data)[0]
            print("Size of msg:", total_size)

            # Receive the full data
            data = b""
            while len(data) < total_size:
                packet = client_socket.recv(total_size - len(data))
                if not packet:
                    break
                data += packet

            data = data.decode()

            if '!' in data:
                cmd, msg = data.split('!', 1)
                if cmd == 'CLOSE':
                    break
                elif cmd == 'ALIVE':
                    print("We are alive")
                elif cmd == 'FILE':
                    file_name = msg
                elif cmd == 'RECORD':
                    print("We are recording")
                else:
                    file_path = os.path.join(write_path, f"{file_name}.csv")
                    print(f"Writing to file: {file_path}")
                    with open(file_path, 'wb') as f:
                        f.write(data.encode())
                    file_name += "_rerecorded"
            else:
                file_path = os.path.join(write_path, f"{file_name}.csv")
                print(f"Writing to file: {file_path}")
                with open(file_path, 'wb') as f:
                    f.write(data.encode())
                file_name += "_rerecorded"

        except Exception as e:
            print("Error:", e)
        finally:
            # Close the client socket
            client_socket.close()

    # Close the server socket
    server_socket.close()

if __name__ == "__main__":
    # Make sure the IP and Port are the same in the TCP connection part of the OSC server
    ip_serve = "192.168.0.180"
    port_serve = 8007 # port is currently the OSC server port + 2
    write_path = r"C:\Users\Public\Documents\Vicon\ShogunLive1.x\Captures\livelinkface"
    print("Starting file receiver...")
    print("Writing files to: ", write_path)
    receive_file(ip_serve, port_serve, write_path)
