# gui.py

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QMenu
from PyQt5.QtCore import Qt, QThread

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.MainWindow = QtWidgets.QMainWindow()
        self.setupUi(self.MainWindow)
        self.retranslateUi(self.MainWindow)
        
        # Connect context menu to token creation log
        self.ui_token_creation_log.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui_token_creation_log.customContextMenuRequested.connect(self.show_context_menu)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1129, 698)
        
        # Central widget and layouts
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        
        # Token address input and label
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.ui_token_address = QtWidgets.QLineEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.ui_token_address.setFont(font)
        self.ui_token_address.setObjectName("ui_token_address")
        self.horizontalLayout_2.addWidget(self.ui_token_address)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        
        # Buy and sell amount input fields and buttons
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.ui_buy_token_amount = QtWidgets.QLineEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.ui_buy_token_amount.setFont(font)
        self.ui_buy_token_amount.setObjectName("ui_buy_token_amount")
        self.verticalLayout.addWidget(self.ui_buy_token_amount)
        self.ui_buy_btn = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.ui_buy_btn.setFont(font)
        self.ui_buy_btn.setObjectName("ui_buy_btn")
        self.verticalLayout.addWidget(self.ui_buy_btn)
        self.horizontalLayout.addLayout(self.verticalLayout)
        
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.ui_sell_token_amount = QtWidgets.QLineEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.ui_sell_token_amount.setFont(font)
        self.ui_sell_token_amount.setObjectName("ui_sell_token_amount")
        self.verticalLayout_2.addWidget(self.ui_sell_token_amount)
        self.ui_sell_btn = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.ui_sell_btn.setFont(font)
        self.ui_sell_btn.setObjectName("ui_sell_btn")
        self.verticalLayout_2.addWidget(self.ui_sell_btn)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        
        # Log group box
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.ui_token_trade_log = QtWidgets.QPlainTextEdit(self.groupBox)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.ui_token_trade_log.setFont(font)
        self.ui_token_trade_log.setObjectName("ui_token_trade_log")
        self.gridLayout.addWidget(self.ui_token_trade_log, 0, 0, 1, 1)
        self.verticalLayout_4.addWidget(self.groupBox)
        
        # Newly created token group box
        self.horizontalLayout_3.addLayout(self.verticalLayout_4)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_2)
        self.ui_token_creation_log = QListWidget(self.groupBox_2)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.ui_token_creation_log.setFont(font)
        self.ui_token_creation_log.setObjectName("ui_token_creation_log")
        self.gridLayout_2.addWidget(self.ui_token_creation_log, 0, 0, 1, 1)
        self.horizontalLayout_3.addWidget(self.groupBox_2)
        
        self.gridLayout_3.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)
        
        self.ui_token_creation_log.itemClicked.connect(self.on_token_clicked)

        # Wallet balance label
        self.ui_wallet_balance = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.ui_wallet_balance.setFont(font)
        self.ui_wallet_balance.setObjectName("ui_wallet_balance")
        self.gridLayout_3.addWidget(self.ui_wallet_balance, 1, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        
        # Menu bar and status bar
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1129, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("PumpFunSnipperBot", "PumpFunSnipperBot"))
        self.label.setText(_translate("MainWindow", "Token Adress:"))
        self.ui_buy_token_amount.setPlaceholderText(_translate("MainWindow", "Buy Amount"))
        self.ui_buy_btn.setText(_translate("MainWindow", "Buy"))
        self.ui_sell_token_amount.setPlaceholderText(_translate("MainWindow", "Sell Amount"))
        self.ui_sell_btn.setText(_translate("MainWindow", "Sell"))
        self.groupBox.setTitle(_translate("MainWindow", "Log"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Newly Created Token"))

    def show(self):
        self.MainWindow.show()

    def update_balance_ui(self, balance):
        self.ui_wallet_balance.setText(f"Wallet Balance: {balance} SOL")
        
    def show_context_menu(self, position):
        context_menu = QMenu()
        copy_action = context_menu.addAction("Copy Token Address")
        action = context_menu.exec_(self.ui_token_creation_log.mapToGlobal(position))
        if action == copy_action:
            cursor = self.ui_token_creation_log.textCursor()
            selected_text = cursor.selectedText()
            if selected_text:
                # Remove the '#' if it's present
                token_address = selected_text[1:] if selected_text.startswith('#') else selected_text
                QtWidgets.QApplication.clipboard().setText(token_address)
                self.statusbar.showMessage("Token address copied to clipboard", 3000)  # Show for 3 seconds

    def on_token_clicked(self, item):
        # Remove the '#' from the beginning of the token address
        token_address = item.text()[1:]
        self.ui_token_address.setText(token_address)

    def append_token_creation_log(self, message):
        self.ui_token_creation_log.addItem(QListWidgetItem(message))

    def append_token_trade_log(self, message):
        self.ui_token_trade_log.appendPlainText(message)
    
    def run_background_task(self, func, *args):
        # Create a QThread for running the task in the background
        self.thread = QThread()
        self.worker = WorkerThread(func, *args)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

class WorkerThread(QtCore.QObject):
    finished = QtCore.pyqtSignal()

    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args

    def run(self):
        self.func(*self.args)
        self.finished.emit()
