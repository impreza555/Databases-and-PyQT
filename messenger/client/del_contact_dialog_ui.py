# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'del_contact_dialog_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DelContact(object):
    def setupUi(self, DelContact):
        DelContact.setObjectName("DelContact")
        DelContact.resize(372, 124)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 170, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        DelContact.setPalette(palette)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("minus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DelContact.setWindowIcon(icon)
        self.layoutWidget = QtWidgets.QWidget(DelContact)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 351, 101))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.comboBoxSelectUser = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBoxSelectUser.setObjectName("comboBoxSelectUser")
        self.gridLayout.addWidget(self.comboBoxSelectUser, 1, 0, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(198, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 1, 1, 1)
        self.labelSelectUser = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.labelSelectUser.setFont(font)
        self.labelSelectUser.setObjectName("labelSelectUser")
        self.gridLayout.addWidget(self.labelSelectUser, 0, 0, 1, 2)
        self.pushButtonCancel = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.gridLayout.addWidget(self.pushButtonCancel, 3, 2, 1, 1)
        self.pushButtonDelUser = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButtonDelUser.setObjectName("pushButtonDelUser")
        self.gridLayout.addWidget(self.pushButtonDelUser, 1, 2, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 13, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 2, 0, 1, 1)

        self.retranslateUi(DelContact)
        QtCore.QMetaObject.connectSlotsByName(DelContact)

    def retranslateUi(self, DelContact):
        _translate = QtCore.QCoreApplication.translate
        DelContact.setWindowTitle(_translate("DelContact", "Выберете контак для удаления"))
        self.labelSelectUser.setText(_translate("DelContact", "Выберите контакт для удаления:"))
        self.pushButtonCancel.setText(_translate("DelContact", "Отмена"))
        self.pushButtonDelUser.setText(_translate("DelContact", "Удалить"))
