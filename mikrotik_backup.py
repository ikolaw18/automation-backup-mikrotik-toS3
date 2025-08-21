import os
import time
import boto3
import paramiko
from datetime import datetime
import requests

# ======== KONFIGURASI AWS S3 & TELEGRAM ========
AWS_ACCESS_KEY_ID = "ISI_KEY_ANDA"
AWS_SECRET_ACCESS_KEY = "ISI_SECRET_ANDA"
AWS_REGION = "ap-southeast-1"
S3_BUCKET = "Backup_Mikrotik"

TELEGRAM_TOKEN = "ISI_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "ISI_CHAT_ID"

# ======== LOKASI BACKUP LOKAL ========
LOCAL_BACKUP_DIR = r"D:\project\backup-mikrotik"  # Ganti dengan path lokal yang sesuai
if not os.path.exists(LOCAL_BACKUP_DIR):
    os.makedirs(LOCAL_BACKUP_DIR)

# ======== INIT BOTO3 S3 ========
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# ======== FUNGSI KIRIM TELEGRAM ========
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})
    except Exception as e:
        print(f"[WARN] Gagal kirim Telegram: {e}")

# ======== FUNGSI CEK FILE DI MIKROTIK ========
def wait_for_file(sftp, filename, retries=10, delay=2):
    """Cek apakah file sudah ada di Mikrotik"""
    for i in range(retries):
        try:
            files = sftp.listdir()
            if filename in files:
                return True
        except Exception:
            pass
        time.sleep(delay)
    return False

# ======== FUNGSI BACKUP PER MIKROTIK ========
def backup_mikrotik(ip, port, user, password, branch):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    backup_filename = f"backup-{branch.lower()}-{date_str}.backup"
    export_filename = f"config-{branch.lower()}-{date_str}.rsc"

    local_backup_path = os.path.join(LOCAL_BACKUP_DIR, backup_filename)
    local_export_path = os.path.join(LOCAL_BACKUP_DIR, export_filename)

    print(f"[INFO] Connect {branch} ({ip}:{port}) ... ")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=int(port), username=user, password=password, timeout=15)

        # Jalankan backup dan export
        ssh.exec_command(f"/system backup save name={backup_filename}")
        ssh.exec_command(f"/export file={export_filename}")
        print(f"[OK] Backup command executed for {branch}")

        # SFTP untuk ambil file
        sftp = ssh.open_sftp()
        print("[INFO] Menunggu file muncul di Mikrotik...")

        if not wait_for_file(sftp, backup_filename) or not wait_for_file(sftp, export_filename):
            raise Exception("File backup belum muncul di Mikrotik setelah timeout")

        # Download file ke lokal
        sftp.get(backup_filename, local_backup_path)
        sftp.get(export_filename, local_export_path)
        print(f"[OK] Downloaded backup to {LOCAL_BACKUP_DIR}")

        # Hapus file lama di Mikrotik
        ssh.exec_command(f"/file remove [find name={backup_filename}]")
        ssh.exec_command(f"/file remove [find name={export_filename}]")
        print(f"[OK] Old backup files deleted in {branch}")

        sftp.close()
        ssh.close()

        # Upload ke S3 folder sesuai cabang
        s3.upload_file(local_backup_path, S3_BUCKET, f"{branch}/{backup_filename}")
        s3.upload_file(local_export_path, S3_BUCKET, f"{branch}/{export_filename}")
        print(f"[OK] Uploaded to S3 in {branch}/")

        send_telegram(f"✅ Backup Berhasil - {branch} ({date_str}) created {time_str}")

    except Exception as e:
        print(f"[ERR] Gagal backup {branch}: {e}")
        send_telegram(f"❌ Backup Gagal - {branch}\n{e}")

# ======== MAIN LOOP ========
if __name__ == "__main__":
    with open("mikrotik_list.txt") as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            ip, port, user, password, branch = line.strip().split(",")
            backup_mikrotik(ip, port, user, password, branch)