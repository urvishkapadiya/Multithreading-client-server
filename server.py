import socket
import random
import string
from threading import Thread
import os
import shutil
from pathlib import Path


def get_working_directory_info(working_directory):
    """
    Creates a string representation of a working directory and its contents.
    :param working_directory: path to the directory
    :return: string of the directory and its contents.
    """
    dirs = '\n-- ' + '\n-- '.join([i.name for i in Path(working_directory).iterdir() if i.is_dir()])
    files = '\n-- ' + '\n-- '.join([i.name for i in Path(working_directory).iterdir() if i.is_file()])
    dir_info = f'Current Directory: {working_directory}:\n|{dirs}{files}'
    return dir_info


def generate_random_eof_token():
    """Helper method to generates a random token that starts with '<' and ends with '>'.
     The total length of the token (including '<' and '>') should be 10.
     Examples: '<1f56xc5d>', '<KfOVnVMV>'
     return: the generated token.
     """
    eof_string = '<'
    for i in range(8):
        eof_string += random.choice(string.ascii_letters + string.digits)

    eof_string += '>'
    return eof_string


def receive_message_ending_with_token(active_socket, buffer_size, eof_token):
    """
    Same implementation as in receive_message_ending_with_token() in client.py
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

def handle_cd(current_working_directory, new_working_directory):
    """
    Handles the client cd commands. Reads the client command and changes the current_working_directory variable 
    accordingly. Returns the absolute path of the new current working directory.
    :param current_working_directory: string of current working directory
    :param new_working_directory: name of the sub directory or '..' for parent
    :return: absolute path of new current working directory
    """

    try:
        dir_string = os.path.join(current_working_directory,new_working_directory)
        os.chdir(dir_string)
        return os.getcwd()
    except NotADirectoryError:
        print("It's not a directory")
    except FileNotFoundError:
        print("There is no such directory at server side.")


def handle_mkdir(current_working_directory, directory_name):
    """
    Handles the client mkdir commands. Creates a new sub directory with the given name in the current working directory.
    :param current_working_directory: string of current working directory
    :param directory_name: name of new sub directory
    """

    dir_string = os.path.join(current_working_directory,directory_name)
    if not os.path.exists(dir_string):
        os.makedirs(dir_string)
    else:
        print("Given directory already exists.")


def handle_rm(current_working_directory, object_name):
    """
    Handles the client rm commands. Removes the given file or sub directory. Uses the appropriate removal method
    based on the object type (directory/file).
    :param current_working_directory: string of current working directory
    :param object_name: name of sub directory or file to remove
    """

    dir_string = os.path.join(current_working_directory,object_name)

    if os.path.exists(dir_string):
        if os.path.isfile(dir_string) :
            os.remove(dir_string)
        else:
            shutil.rmtree(dir_string)
    else:
        print("Given file does not exits")


def handle_ul(current_working_directory, file_name, service_socket, eof_token):
    """
    Handles the client ul commands. First, it reads the payload, i.e. file content from the client, then creates the
    file in the current working directory.
    Use the helper method: receive_message_ending_with_token() to receive the message from the client.
    :param current_working_directory: string of current working directory
    :param file_name: name of the file to be created.
    :param service_socket: active socket with the client to read the payload/contents from.
    :param eof_token: a token to indicate the end of the message.
    """

    dir_string = os.path.join(current_working_directory,file_name)

    file_data = receive_message_ending_with_token(service_socket,4096,eof_token)
    with open(dir_string,"wb") as f:
        f.write(file_data)
        f.close()


def handle_dl(current_working_directory, file_name, service_socket, eof_token):
    """
    Handles the client dl commands. First, it loads the given file as binary, then sends it to the client via the
    given socket.
    :param current_working_directory: string of current working directory
    :param file_name: name of the file to be sent to client
    :param service_socket: active service socket with the client
    :param eof_token: a token to indicate the end of the message.
    """

    dir_string = os.path.join(current_working_directory,file_name)

    if os.path.exists(dir_string):
        with open(dir_string,"rb") as f:
            file_data=f.read()
            service_socket.sendall(file_data + eof_token.encode())
    else:
        service_socket.sendall(("The given file does not exists in server." + eof_token).encode())



class ClientThread(Thread):
    def __init__(self, service_socket : socket.socket, address : str):
        Thread.__init__(self)
        self.service_socket = service_socket
        self.address = address
        self.eof_token=None
        self.current_dir = None

    def run(self):
        print ("Connection from : ", self.address)

        # initialize the connection
        # send random eof token
        self.eof_token = generate_random_eof_token()
        self.service_socket.sendall(self.eof_token.encode())

        # establish working directory
        self.current_dir = os.getcwd()
        dir_info = get_working_directory_info(self.current_dir)

        # send the current dir info
        self.service_socket.sendall((dir_info + self.eof_token).encode())

        while True:
            # get the command and arguments and call the corresponding method

            cmd = receive_message_ending_with_token(self.service_socket,4096,self.eof_token).decode()
            if cmd.startswith("cd"):
                arg = cmd.split()
                self.current_dir = handle_cd(self.current_dir,''.join(arg[1:]))


            elif cmd.startswith('mkdir'):
                arg = cmd.split()
                handle_mkdir(self.current_dir, ''.join(arg[1:]))

            elif cmd.startswith('rm'):
                arg = cmd.split()
                handle_rm(self.current_dir,''.join(arg[1:]))

            elif cmd.startswith('ul'):
                arg = cmd.split()
                handle_ul(self.current_dir, ''.join(arg[1:]), self.service_socket,self.eof_token)

            elif cmd.startswith('dl'):
                arg = cmd.split()
                handle_dl(self.current_dir,''.join(arg[1:]),self.service_socket,self.eof_token)

            else :
                self.service_socket.close()
                print('Connection closed from:', self.address)
                break

            # send current dir info
            dir_info = get_working_directory_info(self.current_dir)
            self.service_socket.sendall((dir_info + self.eof_token).encode())

def main():
    HOST = "127.0.0.1"
    PORT = 65431

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        while True:
            conn, addr = s.accept()
            client_thread = ClientThread(conn, addr)
            client_thread.start()

if __name__ == '__main__':
    main()