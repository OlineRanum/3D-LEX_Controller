import socket
import struct
import os

def receive_file(server_ip, server_port):
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(1)

    print(f"Server listening on {server_ip}:{server_port}")

    os.makedirs("output", exist_ok=True)

    while True:
        # Accept a connection from a client
        client_socket, client_address = server_socket.accept()
        print(f"Connection established from {client_address}")

        try:
            # Receive the int32 representing the total size of the file
            size_data = client_socket.recv(4)
            total_size = struct.unpack('>I', size_data)[0]

            print(f"Total file size: {total_size} bytes")

            # Receive the file name
            # Receive the length of the file name
            name_length_data = client_socket.recv(4)
            name_length = struct.unpack('>I', name_length_data)[0]
            file_name = client_socket.recv(name_length).decode()
            print("Received file name:", file_name)

            # file_name = client_socket.recv(1024).decode()
            # print("Received file name:", file_name)

            # Give the ability to close the connection with a CLOSE msg
            if file_name == '!CLOSE:':
                print("!!!!!!!!!!!!!!!!!!!!!")
                break

            # Receive the contents of the file
            # received_data = b""
            # while len(received_data) < total_size:
            #     data = client_socket.recv(total_size - len(received_data))
            #     if not data:
            #         break
            #     received_data += data

            f = open(os.path.join("output", file_name), 'wb') #open in binary
            l = 1
            while (l):       
                # receive data and write it to file
                l = client_socket.recv(1024)
                while (l):
                    f.write(l)
                    l = client_socket.recv(1024)
                

            f.close()

            # Do something with the received_data, e.g., save it to a file
            # For simplicity, printing the first 100 characters
            # print("File contents:", received_data)
            # file_path = os.path.join("output", file_name)
            # with open(file_path, 'wb') as file:
            #     file.write(received_data)
            #     print(f"File saved to {file_path}")

        except Exception as e:
            print("Error:", e)
        finally:
            # Close the client socket
            client_socket.close()

    server_socket.close()

if __name__ == "__main__":
    # Replace '127.0.0.1' and 9000 with the desired IP address and port for your server
    receive_file("192.168.0.180", 8007)
