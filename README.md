# DDD
Data Driven Debugger - A new way to debug and see data

DDD is a script in python that communicates with Gdb (Debugger) and trace all variables for a specified executable, using
DDD you can focus on data, it will show all variables values of all runnable code.
On this example on the left you can see the code and on the right the output of DDD.

![alt text](https://raw.githubusercontent.com/paulorb/DDD/master/ddd_example.jpg)

## How to use?
```Shell
pip install pygdbmi
./ddd.py executable.out  --break functionname  --args arguments
```
