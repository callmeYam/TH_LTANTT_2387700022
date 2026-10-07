import os, shutil, subprocess, logging
from datetime import datetime

logging.basicConfig(filename='netrecon.log', level=logging.INFO)

def log(msg):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"[{now}] {msg}")

def detect_service(ip, ports):
    ports_str = ','.join(str(p) for p in ports)
    nmap_bin = "nmap"
    if not shutil.which(nmap_bin):
        for candidate in [
            r"C:\Program Files (x86)\Nmap\nmap.exe",
            r"C:\Program Files\Nmap\nmap.exe"
        ]:
            if os.path.isfile(candidate):
                nmap_bin = candidate
                break

    cmd = [nmap_bin, "-sV", "-p", ports_str, ip]
    log(f"Running service detection on {ip}:{ports_str}")
    try:
        result = subprocess.check_output(cmd).decode()
        log(result)
        return result
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output.decode() if e.output else str(e)}"
    except FileNotFoundError:
        return "Error: nmap is not installed or not in PATH."
    except Exception as e:
        return f"Error: {e}"
