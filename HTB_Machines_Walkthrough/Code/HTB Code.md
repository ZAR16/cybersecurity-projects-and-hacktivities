

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXdr0ndDP6fXFqCPlErvcQhIJaPvdBClDqAhdMbJ5J0LfbsxtUpXd1IzdVRnMv1zBuJ1z8sWBXZk84Jy7p6LcoJMYQStkHobTfsyiwlFpVMGPQQl7zQKW1MBn13OALgCKKnW2wBYgg?key=UDACTsp0a3R2z-lctKGusA)

  
  

### Nmap Scan:

  
```nmap_scan
Nmap 7.95 scan initiated Sun Mar 23 00:07:19 2025 as: /usr/lib/nmap/nmap --privileged -sC -sV -oN Code_nmap.txt 10.10.11.62

Nmap scan report for 10.10.11.62 (10.10.11.62)

Host is up (0.46s latency).

Not shown: 998 closed tcp ports (reset)

PORT     STATE SERVICE VERSION

22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.12 (Ubuntu Linux; protocol 2.0)

| ssh-hostkey: 

|   3072 b5:b9:7c:c4:50:32:95:bc:c2:65:17:df:51:a2:7a:bd (RSA)

|   256 94:b5:25:54:9b:68:af:be:40:e1:1d:a8:6b:85:0d:01 (ECDSA)

|_  256 12:8c:dc:97:ad:86:00:b4:88:e2:29:cf:69:b5:65:96 (ED25519)

5000/tcp open  http    Gunicorn 20.0.4

|_http-server-header: gunicorn/20.0.4

|_http-title: Python Code Editor

Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

  

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .

# Nmap done at Sun Mar 23 00:07:49 2025 -- 1 IP address (1 host up) scanned in 30.21 seconds
```
  

Looking in the nmap scan above, we see that there are two services running. The port 5000 is running a Gunicorn 20.0.4 which serves as the webserver and the port 22 which is the default ssh port. 

  
  

## Python Code Editor

The web page is a python code editor as shown in the image below.

  

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXcFmEuJHTipLNAY-awXmNizP3DRpBBkKP8LYD-2TD1qdp7L4VzDZstE1d7ncDZwiN-TXk-h9MAS7dWiludJ8vfl5hK-V33DsztFQezlITMf71xuZdwKn-0tmBb7LPMRXdmqHAfTeg?key=UDACTsp0a3R2z-lctKGusA)

  

Since we can run python codes here in the web server, we can try crafting our Command Injection payload and check if we could find something interesting. I don’t have much knowledge about python since I haven’t mainly used it in any of my projects yet so I tried searching the web and asking LLMs to craft our python script. I found out that there is a Server-Side Template Injection (SSTI) vulnerability in this site, however there are also filters that prohibit the users from running dangerous commands that can be used to dump credentials (see the image below). ![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXfDyiE2GE9TpgtyOP9aC3HDYNC4zppOISEFmU9noqyH3EEHIbgCdExDtf7qWpr1zxD96clZv4l9egbdsbnEYzIjCnxzG6toJ4bo43K8FTkuwWLabAVSV-mVj2D5xguasXr1YRZA?key=UDACTsp0a3R2z-lctKGusA)

  
  

After a lot of trial and error, I finally realized that this web app filters keywords such as import, os, and open. I also found a workaround script to bypass the filters which allowed me to dump the user credentials of the server as shown below:

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXco4EzP3lPplN-Sc5kEkYJswmvXXhhoSDnQbSMw_yKi4UK17AOIy241Y7ZViYTVNmZvxznCLYfodjetdEO6UKuwl_E0XjxSCwlcqGWOtjZXRfVsTE8YY5a-7W2GvlZlN6bHLW1FLg?key=UDACTsp0a3R2z-lctKGusA)

Python script:

```python

try:

    raise Exception(globals())

except Exception as e:

    g = e.args[0]

    User = g['User']

    users = User.query.all()

    for user in users:

        print(user.username, user.password)

  ```  

Result:

development 759b74ce43947f5f4c91aeddc3e5bad3 martin 3de6f30c4a09c27fc71932bfc68474be

  
  
  
  

I used [Crackstation.net](http://crackstation.net) to crack the passwords and surprisingly, it works which means it uses a weak hash/encryption mechanism. Additionally, the password is pretty weak. 

 ![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXcL-CGlwGP0LQYAEwdmtwca7-JTwFLGP_3Q1hXbrSI--1mNU3oJloWp3sVIwU9mXo9ZbwvthjWyqh3UnDNxj2sEJtGq-cLafO9HCIfmrqVApnsEzI0vobUVqb_poLrLCZXPxm76zw?key=UDACTsp0a3R2z-lctKGusA)


  

## Initial Foothold

We got the martin’s password which is nafeelswordsmaster. Now we’re gonna login via ssh to get our initial foothold.

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXfl5pAVFxODU9DucvtwZ72SeGXVuhQvz7bLDivpGaVZ5LUkvR6rDwpx33OBmCJnsf6V2WfvHCMR7wwkplGRadOzQXHP7eCHpLc4EHe9r33MNKBb105ikagD6Fo8v1lPpGStqQTsdQ?key=UDACTsp0a3R2z-lctKGusA)

  

We have successfully logged in as martin. Now we have to enumerate the directories and check for the user.txt file and look interesting files or binaries that could lead us to escalate our privileges.

## Flag 1: user.txt

I haven’t seen the user flag in martin’s home directory so I figured that it was located in another user’s home directory. I saw the task.json file which seems to be used for a binary file to archive files. I ran sudo -l just in case there’s an interesting binary that could lead us to escalate our privileges and surprisingly, there’s an interesting backy(.)sh that martin could run without the root’s password.

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXfyFMWlg_oLuL8piwXSNlDI4ZtuP2LODWNOGFvfXQKPqvcQAClSzFP3vX_qCDhddtYARsYUTCBK-NNObvH18cysNjYZWaijIQphmOqQOpi-mXj-8DuxelfbR2JdtkWCT5TtZy0Mlw?key=UDACTsp0a3R2z-lctKGusA)

  

As I checked the backy(.)sh, it seems like this is the script that archives the files or directories specified in the task.json. ![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXfTBON3B3SwX9i1pfzG-n-vkIR3lKPNexg6mRL-dcQ18a435rmRbTaKXgv2TyMnYl9HAS-E_8Hhbdl9D9qbljhNAIvh7rxg_jSPatw-RujmjxGdwL1B-BQthSdqmI2DhkH9H7rRjA?key=UDACTsp0a3R2z-lctKGusA)

Initially, I checked the directory specified in the task.json if I have the permission to view it but it turns out that our current user doesn't have that privilege.

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXfs49XApxBClDuDvnwL4uUFmZhkcD9s3Po_aCLpg9s0AdxFrpmt1REtATRo3kn_5foy3LFJEX7TxZ18zroQogUoZLh5_ezvjrMFdrXCaHCZGGo9JN8hLOUJnIcjakVXZr7PzhAr?key=UDACTsp0a3R2z-lctKGusA)

  

I modified the task.json a bit to archive the app-production directory as shown below:

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXdQCPdDLDh6hmSTlFUeFXWytmAJkDZ7J0MWBL9NTCE-wfUoGH6msQZqghH-4XU5-rQqfT5Flfsblz4waUexmPbSCYX9YKZRk7Utacp7TPzKkI92cydlS7TYaF99Bs0rPL2m9DNp8g?key=UDACTsp0a3R2z-lctKGusA)

  
  

After running the bash script, you’ll see something like this:

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXcRzeTAmypIhLeb6accfyexgML3enIqkqEMkhMJ6iSnuM3JtQ2iz7zZDSddeG1XjjI5GVagAw-iTjI878G4RParW2taRQv3r6bkWtFNvKzKuwULdKnpZEV8jTKlmrvP4t_NTJttsQ?key=UDACTsp0a3R2z-lctKGusA)

  

Extract the archive by using these commands:

```kali-terminal
tar -xjf <archive.tar.bz2>
```
- This will automatically extract the archive in one command.

or:

```kali-terminal
bunzip2 <archive.tar.bz2>
```
```kali-terminal
tar -xf <archive.tar>
```
- Where -x flag means extract and -f flag to specify the filename.

  
  
After extraction, look for the user.txt and use the cat command to read it.

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXfnLlgt8fHjvD23peNpTstSX4umUwZxwhE6WM9W7CsEZ5_nwb1C2QKgrz33TqCRtu4uQOBO-7l2WyYNKzVGayuq0Vln27ji7jbfII5Ll34QaXt5KCYL3Q1OICd8lYrRfeArHYcnHg?key=UDACTsp0a3R2z-lctKGusA)

  
  
  

## Flag 2: Root Flag

Use the same method of getting the user flag but this time, you have to use a Local File Inclusion (LFI) technique to get the root flag. This is because if you read the backup script, you’ll see that there are directory restrictions wherein only the /home and the /var directories are permitted to be archived. I removed the “exclude” part because it seems like it affects the archive results.

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXd7N5IZgsRmo3Yf6QHUeggo9t5ezUmxF1XfkqKno_m78J9Pcy-FeA7FF_pSdfT1mUdfROdTCQNTsvgVFEVj9nYlZYGlDH5ay8x117EzDwMgN62gbVPZ2-N5XK5NGOL0DSqLf-f-Xg?key=UDACTsp0a3R2z-lctKGusA)
  

If you’ve done it correctly, you’ll be seeing the result similar to the image below:

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXcBAFedDkDlcQxfL7bgTvTXm0oHd5WbyduZyKCvEtwjQK8yrgf9YB6b8REyWR7_DjZ_-PFVLzCvtFXqgssVGJN8_uDsHB_HI1iEEVIvPjuT0r2UK4zZRPy4oiltlZIj78dGQMI2_w?key=UDACTsp0a3R2z-lctKGusA)


## Final Thoughts:
This is labeled as an “Easy” machine which I think doesn’t suit it well. It took me three nights before being able to get the user flag and the root flag.

Warning: This is a very unstable machine and resetting it multiple times could help because files are constantly changing and it really took me a lot of time and patience to hack this machine. Overall, I learned a lot of new things here.
