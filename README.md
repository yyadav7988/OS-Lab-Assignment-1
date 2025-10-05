# Process Management Assignment (ENCS351)

Files:
- process_management.py    : Main Python script implementing Tasks 1..5
- output.txt               : Sample output (representative)
- report.txt               : Short report content (paste into report.pdf)
- README.md                : This file

Requirements:
- Linux (the code uses os.fork and /proc)
- Python 3.8+
- Run from a terminal (so you can use `ps -el | grep defunct` for Task 3)

How to run:
1. Make script executable:
   chmod +x process_management.py

2. Run:
   ./process_management.py

3. Follow on-screen menu to run individual tasks or run the full demo option.

Notes:
- For Task 2 (exec): default commands are /bin/ls, /bin/date and /bin/ps. You can change them interactively.
- For Task 3 (zombie detection): open another terminal and run:
    ps -el | grep defunct
  while the script sleeps to see the zombie entry.
- For Task 4: you can pass any PID visible to you (e.g., PID of this script shown in the menu)
- For Task 5: to experiment with reducing nice values (increasing priority) you'll need root permissions.

Submission:
- Include process_management.py, output.txt, README.md, and a one-page PDF report (report.txt content can be pasted and converted to PDF).
