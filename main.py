from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QPixmap, QPainter, QMovie, QIcon, QFontDatabase
from pyqtgraph import GraphicsLayoutWidget
from gui.windows.mainWindow import MainWindow
from mainModel import MainModel
import sys
import ctypes
import logging
import logging.config
from logging.handlers import RotatingFileHandler
import os




