import time

from tools.threadWorker import Worker
from PyQt5.QtCore import QThread

def function(*args, **kwargs):
    print(1)

thread = QThread()
worker = Worker(function)
worker.moveToThread(thread)
thread.started.connect(worker.run)

thread.start()
time.sleep(1)
thread.start()