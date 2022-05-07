# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'server_settings_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DialogSetServer(object):
    def setupUi(self, DialogSetServer):
        DialogSetServer.setObjectName("DialogSetServer")
        DialogSetServer.resize(456, 288)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DialogSetServer.sizePolicy().hasHeightForWidth())
        DialogSetServer.setSizePolicy(sizePolicy)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        DialogSetServer.setPalette(palette)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("gear.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DialogSetServer.setWindowIcon(icon)
        self.layoutWidget = QtWidgets.QWidget(DialogSetServer)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 439, 258))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.labelIPNote = QtWidgets.QLabel(self.layoutWidget)
        self.labelIPNote.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelIPNote.setWordWrap(True)
        self.labelIPNote.setObjectName("labelIPNote")
        self.gridLayout.addWidget(self.labelIPNote, 8, 1, 1, 3)
        self.pushButtonSave = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButtonSave.setObjectName("pushButtonSave")
        self.gridLayout.addWidget(self.pushButtonSave, 9, 2, 1, 1)
        self.lineEditDbFile = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEditDbFile.setObjectName("lineEditDbFile")
        self.gridLayout.addWidget(self.lineEditDbFile, 3, 1, 1, 3)
        spacerItem = QtWidgets.QSpacerItem(20, 18, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 0, 1, 1)
        self.labelPort = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.labelPort.setFont(font)
        self.labelPort.setObjectName("labelPort")
        self.gridLayout.addWidget(self.labelPort, 5, 0, 1, 1)
        self.lineEditDbPath = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEditDbPath.setReadOnly(True)
        self.lineEditDbPath.setObjectName("lineEditDbPath")
        self.gridLayout.addWidget(self.lineEditDbPath, 0, 0, 1, 3)
        self.pushButtonClose = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButtonClose.setObjectName("pushButtonClose")
        self.gridLayout.addWidget(self.pushButtonClose, 9, 3, 1, 1)
        self.pushButtonDbPathSelect = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButtonDbPathSelect.sizePolicy().hasHeightForWidth())
        self.pushButtonDbPathSelect.setSizePolicy(sizePolicy)
        self.pushButtonDbPathSelect.setObjectName("pushButtonDbPathSelect")
        self.gridLayout.addWidget(self.pushButtonDbPathSelect, 0, 3, 1, 1)
        self.labelDbFileLabel = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.labelDbFileLabel.setFont(font)
        self.labelDbFileLabel.setObjectName("labelDbFileLabel")
        self.gridLayout.addWidget(self.labelDbFileLabel, 3, 0, 1, 1)
        self.lineEditPort = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEditPort.setObjectName("lineEditPort")
        self.gridLayout.addWidget(self.lineEditPort, 5, 1, 1, 3)
        self.labelIP = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.labelIP.setFont(font)
        self.labelIP.setObjectName("labelIP")
        self.gridLayout.addWidget(self.labelIP, 7, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 18, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 2, 0, 1, 1)
        self.labelDbPath = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.labelDbPath.setFont(font)
        self.labelDbPath.setObjectName("labelDbPath")
        self.gridLayout.addWidget(self.labelDbPath, 1, 0, 1, 2)
        spacerItem2 = QtWidgets.QSpacerItem(20, 18, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 6, 0, 1, 1)
        self.lineEditIP = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEditIP.setObjectName("lineEditIP")
        self.gridLayout.addWidget(self.lineEditIP, 7, 1, 1, 3)

        self.retranslateUi(DialogSetServer)
        QtCore.QMetaObject.connectSlotsByName(DialogSetServer)

    def retranslateUi(self, DialogSetServer):
        _translate = QtCore.QCoreApplication.translate
        DialogSetServer.setWindowTitle(_translate("DialogSetServer", "Настройки сервера"))
        self.labelIPNote.setText(_translate("DialogSetServer", "Оставьте это поле пустым, чтобы принимать подключения с любого IP"))
        self.pushButtonSave.setText(_translate("DialogSetServer", "Сохранить"))
        self.labelPort.setText(_translate("DialogSetServer", "Номер порта подключений"))
        self.pushButtonClose.setText(_translate("DialogSetServer", "Закрыть"))
        self.pushButtonDbPathSelect.setText(_translate("DialogSetServer", "Обзор"))
        self.labelDbFileLabel.setText(_translate("DialogSetServer", "Файл базы данных"))
        self.labelIP.setText(_translate("DialogSetServer", "С какого IP принимать подключения"))
        self.labelDbPath.setText(_translate("DialogSetServer", "Путь до файла базы данных"))
