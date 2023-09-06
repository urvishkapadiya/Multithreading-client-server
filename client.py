import socket
import string
import os


def receive_message_ending_with_token(active_socket, buffer_size, eof_token):
    """
    Same implementation as in receive_message_ending_with_token() in server.py
    A helper method to receives a bytearray message of arbitrary size sent on the socket.
    This method returns the message WITHOUT the eof_token at the end of the last packet.
    :param active_socket: a socket object that is connected to the server
    :param buffer_size: the buffer size of each recv() call
    :param eof_token: a token that denotes the end of the message.
    :return: a bytearray message with the eof_token stripped from the end.
    """

    message = bytearray()
    while True:
        packet = active_socket.recv(buffer_size)
        if packet[-10:] == eof_token.encode():
            message += packet[:-10]
            break
        message += packet

    return message


def initialize(host, port):
    """
    1) Creates a socket object and connects to the server.
    2) receives the random token (10 bytes) used to indicate end of messages.
    3) Displays the current working directory returned from the server (output of get_working_directory_info() at the server).
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param host: the ip address of the server
    :param port: the port number of the server
    :return: the created socket object
    """

    s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    print('Connected to server at IP:', host, 'and Port:', port)

    eof = s.recv(4096)
    eof_token = eof.decode()
    print('Handshake Done. EOF is:', eof_token)

    dir_info = receive_message_ending_with_token(s,4096,eof_token).decode()
    print(f"Current working directory:", dir_info)

    return s,eof_token


def issue_cd(command_and_arg, client_socket, eof_token):
    """
    Sends the full cd command entered by the user to the server. The server changes its cwd accordingly and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    client_socket.sendall((command_and_arg + eof_token).encode())
    print(receive_message_ending_with_token(client_socket,4096,eof_token).decode())


def issue_mkdir(command_and_arg, client_socket, eof_token):
    """
    Sends the full mkdir command entered by the user to the server. The server creates the sub directory and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """

    client_socket.sendall((command_and_arg + eof_token).encode())
    print(receive_message_ending_with_token(client_socket,4096,eof_token).decode())




def issue_rm(command_and_arg, client_socket, eof_token):
    """
    Sends the full rm command entered by the user to the server. The server removes the file or directory and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """

    client_socket.sendall((command_and_arg + eof_token).encode())
    print(receive_message_ending_with_token(client_socket,4096,eof_token).decode())



def issue_ul(command_and_arg, client_socket, eof_token):
    """
    Sends the full ul command entered by the user to the server. Then, it reads the file to be uploaded as binary
    and sends it to the server. The server creates the file on its end and sends back the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """

    list1 = command_and_arg.split()
    file_name = ''.join(list1[1:])
    if os.path.exists(os.getcwd()+file_name):
        client_socket.sendall((command_and_arg + eof_token).encode())
        with open(file_name,"rb") as f :
            file_data = f.read()

            client_socket.sendall(file_data + eof_token.encode())
            f.close()

        print(receive_message_ending_with_token(client_socket,4096,eof_token).decode())

    else:
        print("Given file does not exists.")


def issue_dl(command_and_arg, client_socket, eof_token):
    """
    Sends the full dl command entered by the user to the server. Then, it receives the content of the file via the
    socket and re-creates the file in the local directory of the client. Finally, it receives the latest cwd info from
    the server.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    :return:
    """

    client_socket.sendall((command_and_arg+eof_token).encode())

    file_data = receive_message_ending_with_token(client_socket,4096,eof_token)

    list1 = command_and_arg.split()
    file_name = ''.join(list1[1:])

    with open(file_name,"wb") as f:
        f.write(file_data)
        f.close()

    print(receive_message_ending_with_token(client_socket,4096,eof_token).decode())

def main():
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 65431  # The port used by the server

    # initialize

    s,eof_token = initialize(HOST,PORT)

    while True:
        # get user input
        cmd = input('Enter the command and argument: ')
        # call the corresponding command function or exitcd
        if cmd.startswith('cd'):
            issue_cd(cmd,s,eof_token)

        elif cmd.startswith('mkdir'):
            issue_mkdir(cmd,s,eof_token)

        elif cmd.startswith('rm'):
            issue_rm(cmd,s,eof_token)

        elif cmd.startswith('ul'):
            issue_ul(cmd,s,eof_token)

        elif cmd.startswith('dl'):
            issue_dl(cmd,s,eof_token)

        elif cmd.startswith('exit'):
            s.sendall(("Exit" + eof_token).encode())
            s.close()
            break
        else:
            print('Invalid Command')

    print('Exiting the application.')


if __name__ == '__main__':
    main()