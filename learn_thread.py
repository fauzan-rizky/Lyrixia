import threading
import time

def worker():
    print("Worker mulai")
    time.sleep(3)
    print("Worker selesai")

thread = threading.Thread(target=worker)

thread.start()
print("Main thread lanjut")


print("ndoanodawnowdber")

print("Semua pekerjaan selesai")