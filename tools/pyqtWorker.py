from PyQt5.QtCore import QRunnable, QThreadPool, QThread, pyqtSlot
import os
import logging
import time

log = logging.getLogger(__name__)


class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.threadpool = QThreadPool()

    @pyqtSlot()
    def run(self):
        self.fn(*self.args, *self.kwargs)
