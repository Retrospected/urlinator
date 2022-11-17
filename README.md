# URLinator

URLinator tries to identify if the target IP and PORT combination supports HTTP and/or HTTPS.\
It can take a single target or an input file containing IP:PORT targets on separate lines.

URLinator supports multithreading with a default of 10.

## Usage:

```
usage: urlinator.py [-h] (-i <input file> | -t <IP:PORT>) [-T <threads>] [-O <output file>] [-debug]

optional arguments:
  -h, --help        show this help message and exit
  -i <input file>   Input file containing IP:PORT targets on separate lines
  -t <IP:PORT>      Single target to test
  -T <threads>      Number of threads (default 10)
  -O <output file>  Results file
  -debug            Turn DEBUG output ON
```