# Multithreading-client-server

**Overview**

**Server:** The server initializes its socket and internal variables and waits for incoming connections from clients. When a client connects, the server handles the connection in a new thread, allowing multiple clients to interact simultaneously. The server sends a random 10-byte token to the client, which is used as an End of Message (EOF) indicator. The server sends CWD information to the client before receiving each command, maintaining a separate CWD for each client.

**Client:** The client initializes its internal variables, establishes a connection to the server socket, receives the EOF token, and waits for user commands. Before each command, the client displays the received CWD from the server. After the server executes a command and sends back the updated directory information, the client displays it to the user and waits for the next command. The client can exit gracefully by entering the "exit" command.

Please note that the client assumes a fixed working directory on the client side, where files uploaded or downloaded are saved. The server's CWD can be changed using the "cd" command.

**Functionalities**

The application supports the following commands:

**cd:** Change the current working directory on the server.

cd products
cd ..

**mkdir:** Create a new directory on the server inside the current working directory.

mkdir client_1_files

**rm:** Remove a file or directory from the current working directory on the server.

rm about.txt
rm animals

**ul:** Upload a file from the client to the current working directory on the server.

ul orca.jpg

**dl:** Download a file from the current working directory on the server to the client.

dl about.txt

**exit:** Exit the application.

exit
