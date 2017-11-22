# MO on Rails Transport Bridge
Connects to the embedded software running n a microcontroller board (i.e. Arduino) and exposes its communication channel as a TCP/IP server

# Prerequisites
- Python 2.7 (2.7.9+)
- pySerial (install with `python -m pip install pyserial`)

# Running
python moonrailsbridge.py

# Stopping on Windows
On some environments Ctrl+C might not stop the application. Try Ctrl+Break or Ctrl+Pause combo then.

# TODO
- Minimize global variables usage
- Reduce memory juggling (statically allocate buffers?)
- Create binary transport between bridge and the board
- Learn python


