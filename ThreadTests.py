import time
from tools.pyqtWorker import Worker
from PyQt5.QtCore import QThreadPool

def jpp():
    print(3)
    lmao()

def lmao():
    print(2)
    jpp()

def function(progress_callback):
    print(1)
    lmao()

thread = QThreadPool()
worker = Worker(function)
thread.start(worker)
