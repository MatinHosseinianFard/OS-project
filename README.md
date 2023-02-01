# OS-project
Operating systems course project

# Step 1
The contents of some files of Ghokho servers (Ghorob Khokho) are apparently changed unintentionally.
We want to design a system to validate the files and confirm that the files have not been changed unintentionally.

Implement three categories of processes: server, client and worker processes.

- At the beginning, create a server process and five workers.
- If one of these workers terminates due to an error, the server creates a new worker.
- The server process waits for commander and workers to connect.
- After connecting to the server, the commander processes transfer the address of a number of files to the server.
- Worker processes connect to the server and receive the addresses of some of these files.
- In each request, the address of a maximum of five files is given to the worker.
- If the address of the filer server is not available, the worker must wait.
- Note that each file address must be sent to exactly one user.
- Each worker reads the files it receives, then calculates the MD5 value of its contents
and saves a file with the address of the same file but with the suffix "md5." For example, if the input file is "var/dat.iso/", the output is stored in the address "var/dat.iso.md5/".
- MD5 value is written as a hexadecimal string with 32 digits.
- After processing the received files, the worker requests the address of the number of files from the server again.
- For communication between the server process, employers and workers, you can use pipe, network socket, shared memory. (shm_open()) or use the REST programming interface.
- To calculate MD5, you can use libraries or code fragments available on the Internet.
- To test, gradually transfer a large number of files to the server with the help of a number of client processes.


# Step 2

In this step, you expand the commander program in the first step.

- The commander program has six threads that run concurrently.
- One of these threads recursively extracts the list of system files.
- Five other threads are responsible for checking each of the collected files.
- Note that each file should be checked by only one thread, and as the list of files is extracted by the first thread,
the other threads check the collected files.
- Each of the evaluator threads iteratively receives an address from the collected addresses (if the list is empty, it waits for an address to be added). For example for
Checking the "/var/dat.iso" file, first checks whether the "/var/dat.iso.md5" file exists or not.
If it does not exist, it sends the address of this file to the server to calculate the value of "/var/dat.iso.md5"
and adds this address to the list of addresses to be checked again in the future. If the file "/var/dat.iso.md5" exists,
the MD5 thread recalculates the file "/var/dat.iso" and compares it with the contents of the file "/var/dat.iso.md5".
If they are not equal, it prints a message indicating that the MD5 value has changed.
- Only one thread can send requests to the server at a time (synchronization is required).
- To access the collected addresses and send the request to the server, there should not be a race condition.
- To test and see the results of this section, the student must automatically change the values of one file
to the desired value (null or string or number) or randomly from every 3 files produced by the workers.

# Extra

In this section of Bad Disks in Gokhu, we want to identify the malicious workers.

For this purpose, consider a penalty for the worker process that produced this file for each file
whose MD5 string was inconsistent with the value calculated by one of the employer's threads.
If a worker receives more than 2 warnings, he must be stopped immediately.

- All information should be saved in a file called penalties.
- A message must be printed for each worker who is deleted.
- Stopping the worker should be immediate, that is, if he was preparing a file, he should not be allowed to end the process.
- It is obvious that the testing process as well as the printing of the results should be done automatically by the student
take
