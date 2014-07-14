import sys
import fcntl
import termios
import struct

def terminal_height_width():
    """
    Attempt to determine size of terminal window, and set to 25x80 if an exception is thrown.
    """
    try:
        height, width = struct.unpack('hh',  fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ, '1234'))
    except IOError:
        height, width = 25, 80

    return height, width

if __name__ == "__main__":
    term_height, term_width = terminal_height_width()
    print "The terminal has", term_height, "rows and", term_width, "columns"
