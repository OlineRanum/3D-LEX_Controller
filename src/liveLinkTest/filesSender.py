import socket
import struct

def send_file(server_ip, server_port, file_path):
    # Read the contents of the file
    with open(file_path, 'rb') as file:
        file_content = file.read()

    # Get the total size of the file
    total_size = len(file_content)

    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the server
        client_socket.connect((server_ip, server_port))

        # Send the int32 representing the total size of the file
        client_socket.sendall(struct.pack('>I', total_size))

        # Send the contents of the file
        client_socket.sendall(file_content)

        print("File sent successfully.")

    finally:
        # Close the socket
        client_socket.close()

if __name__ == "__main__":
    # Replace '127.0.0.1' and 9000 with the IP address and port where your server is running
    # Replace 'path/to/your/file' with the actual path to the file you want to send
    send_file("192.168.0.226", 9000, r"C:\users\gotters\livelinkOSC\blabla.txt")
