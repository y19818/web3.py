import sys

import pywintypes  # noqa: E402
import win32file  # noqa: E402

if sys.platform != 'win32':
    raise ImportError("This module should not be imported on non `win32` platforms")


class NamedPipe:
    def __init__(self, ipc_path):
        try:
            self.handle = win32file.CreateFile(
                ipc_path, win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0, None, win32file.OPEN_EXISTING, 0, None)
        except pywintypes.error as err:
            raise IOError(err)

    def recv(self, max_length):
        (err, data) = win32file.ReadFile(self.handle, max_length)
        if err:
            raise IOError(err)
        return data

    def sendall(self, data):
        return win32file.WriteFile(self.handle, data)

    def close(self):
        self.handle.close()
