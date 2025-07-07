import os
import clamd

# Initialize ClamAV client
try:
    cd = clamd.ClamdUnixSocket()  # If using Unix socket
    cd.ping()
except:
    try:
        cd = clamd.ClamdNetworkSocket(host="localhost", port=3310)  # If using TCP
        cd.ping()
    except Exception as e:
        raise RuntimeError(f"Could not connect to ClamAV: {e}")

def scan_file(file_path: str) -> bool:
    """
    Scans the file at file_path for viruses.
    Returns True if the file is clean, False if infected.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    result = cd.scan(file_path)
    if not result:
        return True  # No virus detected

    status = result.get(file_path, (None, None))[0]
    return status == "OK"
