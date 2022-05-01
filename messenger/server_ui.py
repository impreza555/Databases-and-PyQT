# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'server_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ServerGui(object):
    def setupUi(self, ServerGui):
        ServerGui.setObjectName("ServerGui")
        ServerGui.resize(621, 519)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ServerGui.sizePolicy().hasHeightForWidth())
        ServerGui.setSizePolicy(sizePolicy)
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
        ServerGui.setPalette(palette)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("server.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ServerGui.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(ServerGui)
        self.centralwidget.setObjectName("centralwidget")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(10, 10, 601, 459))
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.labelListClients = QtWidgets.QLabel(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelListClients.sizePolicy().hasHeightForWidth())
        self.labelListClients.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.labelListClients.setFont(font)
        self.labelListClients.setObjectName("labelListClients")
        self.gridLayout.addWidget(self.labelListClients, 0, 0, 1, 1)
        self.tableViewListClients = QtWidgets.QTableView(self.widget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.tableViewListClients.setFont(font)
        self.tableViewListClients.setObjectName("tableViewListClients")
        self.gridLayout.addWidget(self.tableViewListClients, 1, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 17, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        self.labelStatClients = QtWidgets.QLabel(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelStatClients.sizePolicy().hasHeightForWidth())
        self.labelStatClients.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.labelStatClients.setFont(font)
        self.labelStatClients.setObjectName("labelStatClients")
        self.gridLayout.addWidget(self.labelStatClients, 3, 0, 1, 1)
        self.tableViewStatClients = QtWidgets.QTableView(self.widget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.tableViewStatClients.setFont(font)
        self.tableViewStatClients.setObjectName("tableViewStatClients")
        self.gridLayout.addWidget(self.tableViewStatClients, 4, 0, 1, 1)
        ServerGui.setCentralWidget(self.centralwidget)
        self.statusbarServer = QtWidgets.QStatusBar(ServerGui)
        self.statusbarServer.setObjectName("statusbarServer")
        ServerGui.setStatusBar(self.statusbarServer)
        self.toolBar = QtWidgets.QToolBar(ServerGui)
        self.toolBar.setObjectName("toolBar")
        ServerGui.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.exitAction = QtWidgets.QAction(ServerGui)
        self.exitAction.setCheckable(True)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.exitAction.setFont(font)
        self.exitAction.setObjectName("exitAction")
        self.refreshAction = QtWidgets.QAction(ServerGui)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.refreshAction.setFont(font)
        self.refreshAction.setObjectName("refreshAction")
        self.configAction = QtWidgets.QAction(ServerGui)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.configAction.setFont(font)
        self.configAction.setObjectName("configAction")
        self.toolBar.addAction(self.exitAction)
        self.toolBar.addAction(self.refreshAction)
        self.toolBar.addAction(self.configAction)

        self.retranslateUi(ServerGui)
        QtCore.QMetaObject.connectSlotsByName(ServerGui)

    def retranslateUi(self, ServerGui):
        _translate = QtCore.QCoreApplication.translate
        ServerGui.setWindowTitle(_translate("ServerGui", "Сервер"))
        self.labelListClients.setText(_translate("ServerGui", "Список подключённых клиентов"))
        self.labelStatClients.setText(_translate("ServerGui", "Статистика клиентов"))
        self.toolBar.setWindowTitle(_translate("ServerGui", "toolBar"))
        self.exitAction.setText(_translate("ServerGui", "Выход"))
        self.exitAction.setToolTip(_translate("ServerGui", "Выход"))
        self.exitAction.setShortcut(_translate("ServerGui", "Ctrl+Q"))
        self.refreshAction.setText(_translate("ServerGui", "Обновить список"))
        self.refreshAction.setToolTip(_translate("ServerGui", "Обновить список"))
        self.configAction.setText(_translate("ServerGui", "Настройки сервера"))
        self.configAction.setToolTip(_translate("ServerGui", "Настройки сервера"))
