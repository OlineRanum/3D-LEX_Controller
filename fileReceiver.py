import socket
import struct
import os

# Receive file on a given ip and port
def receive_file(server_ip, server_port):
    # Create a TCP socket, and accept only 1 connection simultaniously
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(1)

    file_name = "NoFileNameGiven"
    take_func = True
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
            print("size of msg: ", total_size)

            # If we aren't expecting a file yet, we are expecting commands
            if take_func:
                data = client_socket.recv(total_size).decode()
                cmd, msg = data.split('!', 1)
                print("Command: ", cmd, "\nmsg: ", msg)
                # Give the ability to close the connection with a CLOSE msg, or receive the file name
                if cmd == 'CLOSE':
                    break
                elif cmd == 'ALIVE':
                    print("we are alive")
                elif cmd == 'FILE':
                    file_name = msg
                elif cmd == 'RECORD':
                    take_func = False
                else:
                    print("Unkown command: ", cmd, "\nWith message: ", msg)
                    print("Please input a different command, we will expect a func")
            # If we have a file name, we are expecting data to put in the file
            else:
                data = client_socket.recv(total_size)
                # Finally, write the file with the file_name to the output path. Then reset the file_name
                f = open(os.path.join(r"C:\Users\Public\Documents\Vicon\ShogunLive1.x\Captures\livelinkface", file_name)+".csv", 'wb') #open in binary
                f.write(data)
                f.close()
                print("Writen to file: output/", file_name)
                file_name = "NoFileNameGiven"
                take_func = True
 
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
    receive_file(ip_serve, port_serve)

# To kill a python task in windows, use the following commands:
# tasklist | FIND "python"
# >taskkill /F /PID
