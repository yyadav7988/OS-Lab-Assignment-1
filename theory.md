🧩 Task 1: Process Creation using fork()

Theory:
Every process in Unix/Linux is created using fork(). It duplicates the current process into a parent and child. The child gets a unique PID and can run concurrently.
os.fork() returns:

0 to the child process

Child’s PID to the parent process

The parent uses os.wait() to collect the child’s exit status and avoid zombies.

Concepts Used: Process creation, parent–child relationship, blocking wait.

⚙️ Task 2: Executing Commands using exec()

Theory:
The exec() family replaces the current process image with a new program. After a successful exec, the original program code is fully replaced and does not return to the caller.
In Python, os.execvp() is used to execute a system command (e.g., ls, date, ps) from the child created by fork().

Concepts Used: Process replacement, command execution, system calls.

💀 Task 3: Zombie and Orphan Processes

Theory:

A zombie process is a dead child process whose exit status has not yet been read by the parent (i.e., parent didn’t call wait() yet).

An orphan process is a child whose parent has terminated; it gets adopted by init (PID 1).

These illustrate process lifecycle management in the OS.

Concepts Used: Process states, adoption by init, defunct processes.

🧾 Task 4: Process Inspection using /proc

Theory:
The /proc filesystem in Linux is a virtual directory that stores runtime information about processes.
For a given PID:

/proc/[pid]/status → name, state, and memory usage

/proc/[pid]/exe → actual binary path

/proc/[pid]/fd/ → open file descriptors

This demonstrates how the OS exposes process metadata.

Concepts Used: Virtual file system, process information retrieval.

🧮 Task 5: Process Prioritization using nice()

Theory:
Process priority controls how the CPU scheduler allocates time.
nice() sets the niceness value (–20 = highest priority, +19 = lowest).
Processes with lower priority (higher nice value) get less CPU time, showing how scheduling works.

Concepts Used: CPU scheduling, process priority, multitasking control.
