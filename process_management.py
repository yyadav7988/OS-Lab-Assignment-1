#!/usr/bin/env python3
"""
process_management.py

Assignment: Process Creation and Management Using Python OS Module
Implements Tasks 1..5 from the lab sheet.

Notes:
- Run on Linux.
- Some tasks (zombie/orphan observation, priority effects) require running in a terminal
  where you can run `ps -el | grep defunct` or check process states.
- Use python3.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def task1_create_children(n=3):
    """
    Task 1: create N child processes using os.fork()
    Each child prints its PID, parent PID and a custom message.
    Parent waits for all children.
    """
    print(f"[Task1] Creating {n} child processes...")
    children = []
    for i in range(n):
        pid = os.fork()
        if pid == 0:
            # In child
            print(f"Child #{i+1}: PID={os.getpid()}, PPID={os.getppid()} -- Hello from child {i+1}")
            # small sleep to make output readable
            time.sleep(0.5)
            # Child should exit cleanly
            os._exit(0)
        else:
            # In parent: record child's PID
            children.append(pid)
            print(f"[Parent] Forked child {i+1} with PID {pid}")
    # Parent waits for all children
    for _ in children:
        waited_pid, status = os.wait()
        print(f"[Parent] Reaped child PID={waited_pid}, status={status}")
    print("[Task1] All children finished.\n")


def task2_exec_commands(commands=None):
    """
    Task 2: modify Task1 so that each child executes a system command using os.execvp()
    or subprocess.run(). Here we use os.execvp() to showcase exec behaviour.
    """
    if commands is None:
        commands = [["/bin/ls", "-l"], ["/bin/date"], ["/bin/ps", "aux"]]

    print("[Task2] Spawning children that will exec commands ...")
    for i, cmd in enumerate(commands):
        pid = os.fork()
        if pid == 0:
            # Child executes the command replacing its image
            try:
                print(f"[Child {i+1}] (PID {os.getpid()}) executing: {' '.join(cmd)}")
                # execvp takes program name and args list (argv[0] is program)
                os.execvp(cmd[0], cmd)
            except Exception as e:
                print(f"[Child {i+1}] exec failed: {e}", file=sys.stderr)
                os._exit(1)
        else:
            print(f"[Parent] Forked child {i+1} PID {pid} to run: {' '.join(cmd)}")
    # Parent waits
    for _ in range(len(commands)):
        waited_pid, status = os.wait()
        print(f"[Parent] Reaped child PID={waited_pid}, status={status}")
    print("[Task2] Done.\n")


def task3_zombie_and_orphan():
    """
    Task 3: Demonstrate zombie and orphan processes.
    - Zombie: parent doesn't wait immediately.
    - Orphan: parent exits before child; child continues.
    """
    print("[Task3] Demonstrating zombie and orphan processes.")
    print("1) Zombie demo: parent will fork child and NOT wait immediately. Run `ps -el | grep defunct` in another terminal to see defunct.")
    pid = os.fork()
    if pid == 0:
        # Child: exit quickly to become defunct until parent waits
        print(f"[Zombie-child] I am child PID={os.getpid()}; exiting immediately to become zombie until parent waits.")
        os._exit(0)
    else:
        print(f"[Parent] Forked child PID={pid}; sleeping for 6s without waiting to allow zombie state observation.")
        time.sleep(6)
        # Now wait; this will remove the zombie
        waited_pid, status = os.wait()
        print(f"[Parent] Now reaped child PID={waited_pid}. Zombie gone. (status={status})")

    time.sleep(1)
    print("\n2) Orphan demo: parent will fork child and exit immediately; child will continue (adopted by init/systemd).")
    pid2 = os.fork()
    if pid2 == 0:
        # Child: run a longer job and print its PPID to show adoption
        for i in range(5):
            print(f"[Orphan-child] PID={os.getpid()}, PPID={os.getppid()} - working ({i+1}/5)")
            time.sleep(1)
        print("[Orphan-child] Done.")
        os._exit(0)
    else:
        print(f"[Parent] Forked orphanable child PID={pid2}; parent exiting immediately so child becomes orphan.")
        # Parent exits without waiting; child becomes orphan and is adopted by init/systemd
        return  # parent returns to shell / exits this function

def read_proc_status(pid):
    status_path = Path(f"/proc/{pid}/status")
    info = {}
    if not status_path.exists():
        raise FileNotFoundError(f"/proc/{pid}/status not found (process may not exist or you lack permissions).")
    with status_path.open() as f:
        for line in f:
            if line.startswith("Name:"):
                info['Name'] = line.split(":",1)[1].strip()
            elif line.startswith("State:"):
                info['State'] = line.split(":",1)[1].strip()
            elif line.startswith("VmRSS:") or line.startswith("VmSize:"):
                # record first memory metric found
                key = line.split(":",1)[0].strip()
                info[key] = line.split(":",1)[1].strip()
    return info

def task4_inspect_proc(pid):
    """
    Task 4: Take a PID as input and print:
      - Process name, state, memory usage from /proc/[pid]/status
      - Executable path from /proc/[pid]/exe
      - Open file descriptors from /proc/[pid]/fd
    """
    print(f"[Task4] Inspecting PID={pid}")
    try:
        info = read_proc_status(pid)
        print("Status info:")
        for k, v in info.items():
            print(f"  {k}: {v}")
    except Exception as e:
        print(f"Could not read /proc/{pid}/status: {e}")

    exe_path = Path(f"/proc/{pid}/exe")
    try:
        real_exe = exe_path.resolve()
        print(f"Executable path: {real_exe}")
    except Exception as e:
        print(f"Could not resolve executable path: {e}")

    fd_dir = Path(f"/proc/{pid}/fd")
    if fd_dir.exists():
        print("Open file descriptors:")
        for fd in sorted(fd_dir.iterdir(), key=lambda p: int(p.name)):
            try:
                target = os.readlink(fd)
            except Exception:
                target = "unknown"
            print(f"  fd {fd.name} -> {target}")
    else:
        print(f"/proc/{pid}/fd not accessible or does not exist.")

    print("[Task4] Done.\n")

def cpu_intensive_work(duration_sec=3):
    """
    Busy-loop for 'duration_sec' seconds to consume CPU.
    """
    end = time.time() + duration_sec
    x = 0
    while time.time() < end:
        x += 1  # trivial op to keep CPU busy
    return x

def task5_prioritization(child_count=4):
    """
    Task 5: Create multiple CPU-intensive child processes with different nice() values.
    Observe execution order or completion times.
    """
    print(f"[Task5] Creating {child_count} CPU-intensive processes with different nice values.")
    pids = []
    # assign nice values: lower number -> higher priority (but only root can decrease nice)
    nice_values = [0, 5, 10, 15][:child_count]

    children_info = []
    for i in range(child_count):
        pid = os.fork()
        if pid == 0:
            # child
            try:
                # set nice value (increase niceness -> lower priority)
                os.nice(nice_values[i])
            except Exception as e:
                print(f"[Child {i}] Could not set nice: {e}")
            start = time.time()
            print(f"[Child {i}] PID={os.getpid()} starting busy work with nice={nice_values[i]} (PPID={os.getppid()})")
            cpu_intensive_work(duration_sec=4)  # CPU-bound for 4 sec
            end = time.time()
            elapsed = end - start
            print(f"[Child {i}] PID={os.getpid()} finished. elapsed={elapsed:.3f} sec. nice={nice_values[i]}")
            os._exit(0)
        else:
            # parent
            pids.append(pid)
            children_info.append((pid, nice_values[i]))
            print(f"[Parent] Launched child {i} PID={pid} with requested nice {nice_values[i]}")

    # parent waits and records finish times
    for _ in pids:
        waited_pid, status = os.wait()
        print(f"[Parent] Reaped child PID={waited_pid}, status={status}")
    print("[Task5] Done. Observe the finish order printed above to infer scheduler impact.\n")


def print_menu():
    print("Process Management Assignment - Menu")
    print("1. Task 1: Create N children (fork & wait)")
    print("2. Task 2: Children exec commands (execvp)")
    print("3. Task 3: Show Zombie & Orphan")
    print("4. Task 4: Inspect /proc for a given PID")
    print("5. Task 5: Prioritization (nice values & CPU load)")
    print("6. Run full demo (1->5)")
    print("0. Exit")

def main():
    if os.geteuid() != 0:
        # Running as non-root is fine for this lab; just warn that changing to lower nice may need privileges.
        pass

    while True:
        print_menu()
        choice = input("Choose option: ").strip()
        if choice == "1":
            n = input("How many children? [default 3]: ").strip()
            n = int(n) if n else 3
            task1_create_children(n)
        elif choice == "2":
            print("Default commands: ls, date, ps")
            use_default = input("Use default commands? (y/n): ").strip().lower()
            if use_default in ("", "y", "yes"):
                task2_exec_commands()
            else:
                raw = input("Enter commands separated by ';' (e.g. '/bin/ls -l;/bin/date'):\n")
                cmds = []
                for part in raw.split(";"):
                    part = part.strip()
                    if not part:
                        continue
                    parts = part.split()
                    cmds.append(parts)
                task2_exec_commands(cmds)
        elif choice == "3":
            task3_zombie_and_orphan()
            print("Note: After the parent returned during the orphan demo, you may see the orphan child's PPID become 1 (systemd/init).")
        elif choice == "4":
            pid = input("Enter PID to inspect (numeric): ").strip()
            if not pid.isdigit():
                print("PID must be numeric.")
            else:
                task4_inspect_proc(pid)
        elif choice == "5":
            cnt = input("How many CPU children? [default 4]: ").strip()
            cnt = int(cnt) if cnt else 4
            task5_prioritization(cnt)
        elif choice == "6":
            print("Running full demo (Task 1..5).")
            task1_create_children(3)
            task2_exec_commands()
            print("For zombie/orphan demo, follow on-screen instructions.")
            task3_zombie_and_orphan()
            # Wait a bit so orphan child prints after parent exit
            time.sleep(2)
            # Inspect current process (this script) as example for /proc
            print("Inspecting this script's PID for Task4 sample.")
            task4_inspect_proc(str(os.getpid()))
            task5_prioritization(4)
        elif choice == "0":
            print("Exiting.")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")
        sys.exit(0)
