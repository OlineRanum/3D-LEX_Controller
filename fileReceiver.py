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
import asyncio
from src.config.setup import SetUp

def receive_file(server_ip, server_port, write_path, mode="csv"):
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

    print(f"[{mode}] Server listening on {server_ip}:{server_port}")
    print(f"[{mode}] Writing files to: {write_path}")

    # Serve until we are commanded to quit
    while True:
        # Accept a connection from a client
        client_socket, client_address = server_socket.accept()
        print(f"[{mode}] Connection established from {client_address}")

        try:
            # Receive the int32 representing the total size of the file
            size_data = client_socket.recv(4)
            total_size = struct.unpack('>I', size_data)[0]
            print(f"[{mode}] Size of msg:", total_size)

            # Receive the full data
            data = b""
            while len(data) < total_size:
                packet = client_socket.recv(total_size - len(data))
                if not packet:
                    break
                data += packet


            if data.startswith(b"COMMAND:"):
            # if '!' in data:
                data = data.decode("utf-8").lstrip("COMMAND:")
                cmd, msg = data.split('!', 1)
                if cmd == 'CLOSE':
                    break
                elif cmd == 'ALIVE':
                    print(f"[{mode}] We are alive")
                elif cmd == 'FILE':
                    file_name = msg
                elif cmd == 'RECORD':
                    print(f"[{mode}] We are recording")
                else:
                    print(f"[{mode}] Unknown command: {cmd}")
            else:
                file_path = os.path.join(write_path, f"{file_name}.{mode}")
                print(f"[{mode}] Writing to file: {file_path}")
                with open(file_path, 'wb') as f:
                    f.write(data)
                file_name += "_rerecorded"

        except Exception as e:
            print(f"[{mode}] Error:", e)
        finally:
            # Close the client socket
            client_socket.close()

    # Close the server socket
    server_socket.close()

if __name__ == "__main__":
    args = SetUp("config.yaml")

    # Make sure the IP and Port are the same in the TCP connection part of the OSC server
    # write_path = r"C:\Users\Public\Documents\Vicon\ShogunLive1.x\Captures\livelinkface"
    csv_path = args.llf_csv_save_path
    video_path = args.llf_video_save_path
    print("Starting file receiver...")
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(None, receive_file, args.target_ip, args.receive_csv_port, csv_path),
        loop.run_in_executor(None, receive_file, args.target_ip, args.receive_video_port, video_path, "mov")
    ]
    loop.run_until_complete(asyncio.wait(tasks))
