# automation-backup-mikrotik-toS3
Automation backup mikrotik upload to Amazon S3 | Alert notify Telegram (Python script)

Cara pakai:

- Install dependency ($ pip install paramiko boto3 requests)

- Siapkan file mikrotik_list.txt (format: ip,port,user,password,cabang)

- Jalankan ( $ python mikrotik_backup.py )

- atau set via Task Scheduler via Windows / Linux

  NOTE: Tidak perlu menambahkan folder di dalam bucket yang sudah dibuat, akan otomatis terbuat karena melihat nama cabang dari file mikrotik_list.txt

![alt text](https://github.com/ikolaw18/automation-backup-mikrotik-toS3/blob/ca0b8f0f6d3a994482b4af6595d3b74cb6725dd9/notify_telegram.png?raw=true)



![alt text](https://github.com/ikolaw18/automation-backup-mikrotik-toS3/blob/ca0b8f0f6d3a994482b4af6595d3b74cb6725dd9/Bucket_S3.png?raw=true)


