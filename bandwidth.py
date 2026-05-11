import psutil
import time

def get_network_speed():
    # Pehla snapshot
    stats1 = psutil.net_io_counters()
    time.sleep(1)
    # Doosra snapshot
    stats2 = psutil.net_io_counters()

    # Difference = speed
    sent = round((stats2.bytes_sent - stats1.bytes_sent) / (1024 * 1024), 3)
    recv = round((stats2.bytes_recv - stats1.bytes_recv) / (1024 * 1024), 3)

    return sent, recv

if __name__ == "__main__":
    print("📡 Network speed monitor chalu...\n")
    print("YouTube ya kuch bhi chalao browser me!\n")

    for i in range(10):
        sent, recv = get_network_speed()
        print(f"⬆️  Upload:   {sent} MB/s")
        print(f"⬇️  Download: {recv} MB/s")
        print("-" * 30)