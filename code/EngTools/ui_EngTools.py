# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'EngToolslUCdlZ.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QPushButton,
    QRadioButton, QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(281, 184)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.bt_runHKP = QPushButton(Dialog)
        self.bt_runHKP.setObjectName(u"bt_runHKP")
        self.bt_runHKP.setGeometry(QRect(30, 60, 131, 41))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.bt_runHKP.setFont(font)
        self.bt_runDTP = QPushButton(Dialog)
        self.bt_runDTP.setObjectName(u"bt_runDTP")
        self.bt_runDTP.setGeometry(QRect(30, 110, 131, 41))
        self.bt_runDTP.setFont(font)
        self.label_stsHKP = QLabel(Dialog)
        self.label_stsHKP.setObjectName(u"label_stsHKP")
        self.label_stsHKP.setGeometry(QRect(180, 70, 71, 19))
        self.label_stsHKP.setAlignment(Qt.AlignCenter)
        self.label_stsDTP = QLabel(Dialog)
        self.label_stsDTP.setObjectName(u"label_stsDTP")
        self.label_stsDTP.setGeometry(QRect(180, 120, 71, 19))
        self.label_stsDTP.setAlignment(Qt.AlignCenter)
        self.radio_inst_simul = QRadioButton(Dialog)
        self.radio_inst_simul.setObjectName(u"radio_inst_simul")
        self.radio_inst_simul.setGeometry(QRect(20, 20, 171, 25))
        self.radio_real = QRadioButton(Dialog)
        self.radio_real.setObjectName(u"radio_real")
        self.radio_real.setGeometry(QRect(200, 20, 61, 25))

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"EngTools", None))
        self.bt_runHKP.setText(QCoreApplication.translate("Dialog", u"run HKP", None))
        self.bt_runDTP.setText(QCoreApplication.translate("Dialog", u"run DTP", None))
        self.label_stsHKP.setText(QCoreApplication.translate("Dialog", u"GOOD", None))
        self.label_stsDTP.setText(QCoreApplication.translate("Dialog", u"GOOD", None))
        self.radio_inst_simul.setText(QCoreApplication.translate("Dialog", u"Instrument Simulation", None))
        self.radio_real.setText(QCoreApplication.translate("Dialog", u"Real", None))
    # retranslateUi

