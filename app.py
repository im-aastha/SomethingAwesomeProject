import socket
import threading
import rsa

# here we are generating RSA keys
public_key, private_key = rsa.newkeys(1024)
partner_public_key = None  # holds the public key of the chat partner

# here we ask the user to enter 
def get_user_choice():
    choice = input("Select mode - Host (1) or Connect (2): ")
    if choice not in {"1", "2"}:
        print("Invalid choice. Exiting.")
        exit()
    return choice

# this function is for initialising connection based on what user enters.
def initialize_connection(choice):
    global partner_public_key
    if choice == "1":
        # hosting: create server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("172.28.176.1", 9999)) # my computer's IPV4 address
        server_socket.listen()
        print("Waiting for connection...")
        client_socket, _ = server_socket.accept()
        print("Connected to client.")
        
        # over here we exchange public keys
        client_socket.send(public_key.save_pkcs1("PEM"))
        partner_public_key = rsa.PublicKey.load_pkcs1(client_socket.recv(1024))
        return client_socket
    else:
        #connectingg
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("172.28.176.1", 9999))
        print("Connected to server.")
        
        # exchange public keys
        partner_public_key = rsa.PublicKey.load_pkcs1(client_socket.recv(1024))
        client_socket.send(public_key.save_pkcs1("PEM"))
        return client_socket

# function for sending encrypted messages
def send_encrypted_messages(socket_conn):
    while True:
        message = input()  
        encrypted_message = rsa.encrypt(message.encode(), partner_public_key)
        socket_conn.send(encrypted_message)
        print("You:", message)
       


def receive_encrypted_messages(socket_conn):
    while True:
        encrypted_message = socket_conn.recv(1024)
        if encrypted_message:
            decrypted_message = rsa.decrypt(encrypted_message, private_key).decode()
            print("Friend:", decrypted_message)
        else:
            print("Connection closed by friend.")
            break

def main():
    choice = get_user_choice()
    connection = initialize_connection(choice)

    # we start threads here
    threading.Thread(target=send_encrypted_messages, args=(connection,), daemon=True).start()
    threading.Thread(target=receive_encrypted_messages, args=(connection,), daemon=True).start()

    while True:
        pass

# runningg
if __name__ == "__main__":
    main()
