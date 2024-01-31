import socket
import struct

def receive_file(server_ip, server_port, output_file_path):
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(1)

    print(f"Server listening on {server_ip}:{server_port}")

    # Accept a connection from a client
    client_socket, client_address = server_socket.accept()
    print(f"Connection established from {client_address}")

    try:
        # Receive the int32 representing the total size of the file
        size_data = client_socket.recv(4)
        total_size = struct.unpack('>I', size_data)[0]

        print(f"Total file size: {total_size} bytes")

        # Receive the contents of the file
        received_data = b""
        while len(received_data) < total_size:
            data = client_socket.recv(total_size - len(received_data))
            if not data:
                break
            received_data += data

        print("File received successfully.")

        # Do something with the received_data, e.g., save it to a file
        # For simplicity, printing the first 100 characters
        print("File contents:", received_data)

        with open(output_file_path, 'wb') as file:
          file.write(received_data)
          print(f"File saved to {output_file_path}")

    finally:
        # Close the sockets
        client_socket.close()
        server_socket.close()

if __name__ == "__main__":
    # Replace '127.0.0.1' and 9000 with the desired IP address and port for your server
    receive_file("192.168.0.226", 9000, "output_file.txt")
