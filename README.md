# automation-backup-mikrotik-toS3
Automation backup mikrotik upload to Amazon S3 | Alert notify Telegram (Python script)

Cara pakai:

- Install dependency ($ pip install paramiko boto3 requests)

- Siapkan file mikrotik_list.txt (format: ip,port,user,password,cabang)

- Jalankan ( $ python mikrotik_backup.py )

- atau set via Task Scheduler via Windows / Linux
