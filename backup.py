import os
import subprocess
import shutil
from datetime import datetime
from tqdm import tqdm
from colorama import Fore, Style, init

init(autoreset=True)

# --- CONFIG ---
# Folder tujuan utama
BASE_DESTINATION = os.path.expanduser("~/ULTIMATE_ANDROID_BACKUP")

def print_banner():
    print(f"{Fore.RED}{'='*60}")
    print(f"{Fore.YELLOW}       🚀 ULTIMATE ANDROID RECOVERY & BACKUP (NO ROOT) 🚀")
    print(f"{Fore.RED}{'='*60}\n")

def get_device_info():
    try:
        model = subprocess.check_output(["adb", "shell", "getprop", "ro.product.model"]).strip().decode()
        serial = subprocess.check_output(["adb", "get-serialno"]).strip().decode()
        return f"{model}_{serial}"
    except:
        return "Unknown_Device"

def check_pc_space():
    # Cek sisa disk di Linux (dalam GB)
    total, used, free = shutil.disk_usage("/")
    return free // (2**30)

def main():
    print_banner()

    # 1. Cek Koneksi ADB
    check_adb = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    if "device\n" not in check_adb.stdout:
        print(f"{Fore.RED}[!] DEVICE TIDAK TERDETEKSI!")
        print("Pastikan Kabel USB nempel dan USB Debugging AKTIF.")
        return

    device_id = get_device_info()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_path = os.path.join(BASE_DESTINATION, f"{device_id}/{timestamp}")

    # 2. Cek Kapasitas PC
    free_gb = check_pc_space()
    print(f"{Fore.CYAN}[i] Device: {Fore.WHITE}{device_id}")
    print(f"{Fore.CYAN}[i] Lokasi: {Fore.WHITE}{final_path}")
    print(f"{Fore.CYAN}[i] Sisa Disk PC: {Fore.WHITE}{free_gb} GB")
    
    confirm = input(f"\n{Fore.YELLOW}Mulai sedot semua data? (y/n): ")
    if confirm.lower() != 'y': return

    if not os.path.exists(final_path):
        os.makedirs(final_path)

    print(f"\n{Fore.MAGENTA}[*] MEMULAI PROSES SAPU BERSIH (FULL /SDCARD/ PULL)...")
    print(f"{Fore.RED}[!] JANGAN CABUT KABEL USB!")

    # 3. Eksekusi ADB PULL (Seluruh SDCard)
    # Kita arahkan output ke null tapi gunakan TQDM untuk indikator waktu
    start_time = datetime.now()
    
    # Gunakan subprocess.Popen supaya kita bisa pantau baris per baris kalau perlu
    # Tapi untuk kecepatan maksimal, kita biarkan ADB bekerja dalam mode pull direct
    process = subprocess.Popen(
        ["adb", "pull", "/sdcard/.", final_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Spinner/Progress sederhana karena ADB pull tidak kasih info total size di awal
    with tqdm(total=100, desc="Status Sedot Data", bar_format="{l_bar}{bar}| {elapsed} < {remaining}") as pbar:
        while True:
            line = process.stdout.readline()
            if not line:
                break
            # Update progress bar setiap ada file baru yang selesai
            pbar.update(0.1) 
            if "file pulled" in line:
                pbar.update(0.5)

    process.wait()

    # 4. Verifikasi Akhir
    if process.returncode == 0:
        end_time = datetime.now()
        duration = end_time - start_time
        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"{Fore.GREEN}✅ BERHASIL TOTAL!")
        print(f"{Fore.WHITE}Waktu Tempuh : {duration}")
        print(f"{Fore.WHITE}Total Folder : {final_path}")
        print(f"{Fore.GREEN}{'='*60}")
    else:
        print(f"\n{Fore.RED}[!] Selesai dengan beberapa peringatan (biasanya file sistem terkunci).")
        print(f"{Fore.YELLOW}[i] Cek folder backup untuk memastikan file sudah masuk.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Proses dihentikan paksa oleh user.")
