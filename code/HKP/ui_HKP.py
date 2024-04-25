# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'HKPnemKXP.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QCheckBox,
    QDialog, QFrame, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTableWidget,
    QTableWidgetItem, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(782, 470)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        #Dialog.setSizeGripEnabled(False)
        self.label_27 = QLabel(Dialog)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setGeometry(QRect(530, 7, 111, 20))
        font = QFont()
        font.setPointSize(10)
        self.label_27.setFont(font)
        self.label_27.setLayoutDirection(Qt.LeftToRight)
        self.label_27.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.sts_updated = QLabel(Dialog)
        self.sts_updated.setObjectName(u"sts_updated")
        self.sts_updated.setGeometry(QRect(640, 7, 141, 21))
        self.sts_updated.setFont(font)
        self.label_29 = QLabel(Dialog)
        self.label_29.setObjectName(u"label_29")
        self.label_29.setGeometry(QRect(60, 263, 171, 20))
        self.label_29.setFont(font)
        self.sts_pdu_on = QLabel(Dialog)
        self.sts_pdu_on.setObjectName(u"sts_pdu_on")
        self.sts_pdu_on.setGeometry(QRect(36, 264, 19, 20))
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(False)
        self.sts_pdu_on.setFont(font1)
        self.sts_pdu_off = QLabel(Dialog)
        self.sts_pdu_off.setObjectName(u"sts_pdu_off")
        self.sts_pdu_off.setGeometry(QRect(137, 264, 20, 20))
        self.sts_pdu_off.setFont(font1)
        self.sts_interval = QLabel(Dialog)
        self.sts_interval.setObjectName(u"sts_interval")
        self.sts_interval.setGeometry(QRect(589, 30, 171, 20))
        self.sts_interval.setFont(font)
        self.sts_pdu3 = QLabel(Dialog)
        self.sts_pdu3.setObjectName(u"sts_pdu3")
        self.sts_pdu3.setGeometry(QRect(8, 103, 19, 20))
        self.sts_pdu3.setFont(font1)
        self.sts_pdu5 = QLabel(Dialog)
        self.sts_pdu5.setObjectName(u"sts_pdu5")
        self.sts_pdu5.setGeometry(QRect(8, 153, 19, 20))
        self.sts_pdu5.setFont(font1)
        self.sts_pdu4 = QLabel(Dialog)
        self.sts_pdu4.setObjectName(u"sts_pdu4")
        self.sts_pdu4.setGeometry(QRect(8, 128, 19, 20))
        self.sts_pdu4.setFont(font1)
        self.sts_pdu6 = QLabel(Dialog)
        self.sts_pdu6.setObjectName(u"sts_pdu6")
        self.sts_pdu6.setGeometry(QRect(8, 178, 19, 20))
        self.sts_pdu6.setFont(font1)
        self.tb_pdu = QTableWidget(Dialog)
        if (self.tb_pdu.columnCount() < 2):
            self.tb_pdu.setColumnCount(2)
        font2 = QFont()
        font2.setPointSize(9)
        font2.setBold(True)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setFont(font2);
        self.tb_pdu.setHorizontalHeaderItem(0, __qtablewidgetitem)
        font3 = QFont()
        font3.setPointSize(10)
        font3.setBold(True)
        __qtablewidgetitem1 = QTableWidgetItem()
        __qtablewidgetitem1.setFont(font3);
        self.tb_pdu.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        if (self.tb_pdu.rowCount() < 8):
            self.tb_pdu.setRowCount(8)
        __qtablewidgetitem2 = QTableWidgetItem()
        __qtablewidgetitem2.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem2.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(0, 0, __qtablewidgetitem2)
        font4 = QFont()
        font4.setPointSize(9)
        __qtablewidgetitem3 = QTableWidgetItem()
        __qtablewidgetitem3.setFont(font4);
        __qtablewidgetitem3.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(0, 1, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        __qtablewidgetitem4.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem4.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(1, 0, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        __qtablewidgetitem5.setFont(font4);
        __qtablewidgetitem5.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(1, 1, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        __qtablewidgetitem6.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem6.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(2, 0, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        __qtablewidgetitem7.setFont(font4);
        __qtablewidgetitem7.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(2, 1, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        __qtablewidgetitem8.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem8.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(3, 0, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        __qtablewidgetitem9.setFont(font4);
        __qtablewidgetitem9.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(3, 1, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        __qtablewidgetitem10.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem10.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(4, 0, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        __qtablewidgetitem11.setFont(font4);
        __qtablewidgetitem11.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(4, 1, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        __qtablewidgetitem12.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem12.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(5, 0, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        __qtablewidgetitem13.setFont(font4);
        __qtablewidgetitem13.setFlags(Qt.NoItemFlags);
        self.tb_pdu.setItem(5, 1, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        __qtablewidgetitem14.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem14.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(6, 0, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        __qtablewidgetitem15.setFont(font4);
        __qtablewidgetitem15.setFlags(Qt.NoItemFlags);
        self.tb_pdu.setItem(6, 1, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        __qtablewidgetitem16.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem16.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(7, 0, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        __qtablewidgetitem17.setFont(font4);
        __qtablewidgetitem17.setFlags(Qt.NoItemFlags);
        self.tb_pdu.setItem(7, 1, __qtablewidgetitem17)
        self.tb_pdu.setObjectName(u"tb_pdu")
        self.tb_pdu.setGeometry(QRect(30, 29, 211, 221))
        font5 = QFont()
        font5.setPointSize(10)
        font5.setBold(False)
        self.tb_pdu.setFont(font5)
        self.tb_pdu.setTabletTracking(False)
        self.tb_pdu.setFocusPolicy(Qt.NoFocus)
        self.tb_pdu.setFrameShape(QFrame.StyledPanel)
        self.tb_pdu.setFrameShadow(QFrame.Sunken)
        self.tb_pdu.setLineWidth(1)
        self.tb_pdu.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tb_pdu.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tb_pdu.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.tb_pdu.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tb_pdu.setShowGrid(True)
        self.tb_pdu.setGridStyle(Qt.DotLine)
        self.tb_pdu.setSortingEnabled(False)
        self.tb_pdu.setWordWrap(True)
        self.tb_pdu.setRowCount(8)
        self.tb_pdu.setColumnCount(2)
        self.tb_pdu.horizontalHeader().setVisible(True)
        self.tb_pdu.horizontalHeader().setCascadingSectionResizes(True)
        self.tb_pdu.horizontalHeader().setMinimumSectionSize(1)
        self.tb_pdu.horizontalHeader().setDefaultSectionSize(50)
        self.tb_pdu.horizontalHeader().setHighlightSections(False)
        self.tb_pdu.horizontalHeader().setProperty("showSortIndicator", False)
        self.tb_pdu.horizontalHeader().setStretchLastSection(True)
        self.tb_pdu.verticalHeader().setVisible(False)
        self.tb_pdu.verticalHeader().setCascadingSectionResizes(False)
        self.tb_pdu.verticalHeader().setMinimumSectionSize(19)
        self.tb_pdu.verticalHeader().setDefaultSectionSize(25)
        self.tb_pdu.verticalHeader().setHighlightSections(True)
        self.tb_pdu.verticalHeader().setProperty("showSortIndicator", True)
        self.tb_pdu.verticalHeader().setStretchLastSection(True)
        self.sts_pdu2 = QLabel(Dialog)
        self.sts_pdu2.setObjectName(u"sts_pdu2")
        self.sts_pdu2.setGeometry(QRect(8, 78, 19, 20))
        self.sts_pdu2.setFont(font1)
        self.sts_pdu8 = QLabel(Dialog)
        self.sts_pdu8.setObjectName(u"sts_pdu8")
        self.sts_pdu8.setGeometry(QRect(8, 227, 19, 20))
        self.sts_pdu8.setFont(font1)
        self.sts_pdu7 = QLabel(Dialog)
        self.sts_pdu7.setObjectName(u"sts_pdu7")
        self.sts_pdu7.setGeometry(QRect(8, 203, 19, 20))
        self.sts_pdu7.setFont(font1)
        self.sts_pdu1 = QLabel(Dialog)
        self.sts_pdu1.setObjectName(u"sts_pdu1")
        self.sts_pdu1.setGeometry(QRect(8, 53, 19, 20))
        self.sts_pdu1.setFont(font1)
        self.sts_pdu = QLabel(Dialog)
        self.sts_pdu.setObjectName(u"sts_pdu")
        self.sts_pdu.setGeometry(QRect(3, 1, 19, 25))
        font6 = QFont()
        font6.setPointSize(20)
        font6.setBold(True)
        self.sts_pdu.setFont(font6)
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(30, 5, 111, 16))
        font7 = QFont()
        font7.setPointSize(12)
        font7.setBold(True)
        self.label.setFont(font7)
        self.sts_monitor14 = QLabel(Dialog)
        self.sts_monitor14.setObjectName(u"sts_monitor14")
        self.sts_monitor14.setGeometry(QRect(247, 410, 20, 20))
        font8 = QFont()
        font8.setPointSize(16)
        font8.setBold(False)
        self.sts_monitor14.setFont(font8)
        self.label_34 = QLabel(Dialog)
        self.label_34.setObjectName(u"label_34")
        self.label_34.setGeometry(QRect(580, 443, 171, 20))
        self.label_34.setFont(font5)
        self.sts_monitor10 = QLabel(Dialog)
        self.sts_monitor10.setObjectName(u"sts_monitor10")
        self.sts_monitor10.setGeometry(QRect(247, 310, 20, 20))
        self.sts_monitor10.setFont(font8)
        self.sts_monitor8 = QLabel(Dialog)
        self.sts_monitor8.setObjectName(u"sts_monitor8")
        self.sts_monitor8.setGeometry(QRect(247, 260, 20, 20))
        self.sts_monitor8.setFont(font8)
        self.sts_monitor13 = QLabel(Dialog)
        self.sts_monitor13.setObjectName(u"sts_monitor13")
        self.sts_monitor13.setGeometry(QRect(247, 385, 20, 20))
        self.sts_monitor13.setFont(font8)
        self.sts_vacuum = QLabel(Dialog)
        self.sts_vacuum.setObjectName(u"sts_vacuum")
        self.sts_vacuum.setGeometry(QRect(247, 31, 20, 20))
        self.sts_vacuum.setFont(font8)
        self.sts_monitor_error = QLabel(Dialog)
        self.sts_monitor_error.setObjectName(u"sts_monitor_error")
        self.sts_monitor_error.setGeometry(QRect(751, 444, 20, 20))
        self.sts_monitor_error.setFont(font8)
        self.sts_monitor7 = QLabel(Dialog)
        self.sts_monitor7.setObjectName(u"sts_monitor7")
        self.sts_monitor7.setGeometry(QRect(247, 235, 20, 20))
        self.sts_monitor7.setFont(font8)
        self.sts_monitor5 = QLabel(Dialog)
        self.sts_monitor5.setObjectName(u"sts_monitor5")
        self.sts_monitor5.setGeometry(QRect(247, 185, 20, 20))
        self.sts_monitor5.setFont(font8)
        self.sts_monitor9 = QLabel(Dialog)
        self.sts_monitor9.setObjectName(u"sts_monitor9")
        self.sts_monitor9.setGeometry(QRect(247, 285, 20, 20))
        self.sts_monitor9.setFont(font8)
        self.sts_monitor1 = QLabel(Dialog)
        self.sts_monitor1.setObjectName(u"sts_monitor1")
        self.sts_monitor1.setGeometry(QRect(247, 85, 20, 20))
        self.sts_monitor1.setFont(font8)
        self.sts_monitor2 = QLabel(Dialog)
        self.sts_monitor2.setObjectName(u"sts_monitor2")
        self.sts_monitor2.setGeometry(QRect(247, 110, 20, 20))
        self.sts_monitor2.setFont(font8)
        self.sts_monitor11 = QLabel(Dialog)
        self.sts_monitor11.setObjectName(u"sts_monitor11")
        self.sts_monitor11.setGeometry(QRect(247, 335, 20, 20))
        self.sts_monitor11.setFont(font8)
        self.sts_monitor3 = QLabel(Dialog)
        self.sts_monitor3.setObjectName(u"sts_monitor3")
        self.sts_monitor3.setGeometry(QRect(247, 135, 20, 20))
        self.sts_monitor3.setFont(font8)
        self.e_vacuum = QLineEdit(Dialog)
        self.e_vacuum.setObjectName(u"e_vacuum")
        self.e_vacuum.setGeometry(QRect(395, 28, 81, 25))
        self.e_vacuum.setFocusPolicy(Qt.NoFocus)
        self.e_vacuum.setAlignment(Qt.AlignCenter)
        self.e_vacuum.setReadOnly(True)
        self.label_18 = QLabel(Dialog)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setGeometry(QRect(481, 32, 30, 17))
        self.label_18.setFont(font5)
        self.sts_monitor12 = QLabel(Dialog)
        self.sts_monitor12.setObjectName(u"sts_monitor12")
        self.sts_monitor12.setGeometry(QRect(247, 360, 20, 20))
        self.sts_monitor12.setFont(font8)
        self.label_11 = QLabel(Dialog)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setGeometry(QRect(271, 32, 121, 17))
        self.label_11.setFont(font5)
        self.tb_Monitor = QTableWidget(Dialog)
        if (self.tb_Monitor.columnCount() < 5):
            self.tb_Monitor.setColumnCount(5)
        __qtablewidgetitem18 = QTableWidgetItem()
        __qtablewidgetitem18.setFont(font3);
        self.tb_Monitor.setHorizontalHeaderItem(0, __qtablewidgetitem18)
        __qtablewidgetitem19 = QTableWidgetItem()
        __qtablewidgetitem19.setFont(font3);
        self.tb_Monitor.setHorizontalHeaderItem(1, __qtablewidgetitem19)
        __qtablewidgetitem20 = QTableWidgetItem()
        __qtablewidgetitem20.setFont(font3);
        self.tb_Monitor.setHorizontalHeaderItem(2, __qtablewidgetitem20)
        __qtablewidgetitem21 = QTableWidgetItem()
        __qtablewidgetitem21.setFont(font3);
        self.tb_Monitor.setHorizontalHeaderItem(3, __qtablewidgetitem21)
        __qtablewidgetitem22 = QTableWidgetItem()
        __qtablewidgetitem22.setFont(font3);
        self.tb_Monitor.setHorizontalHeaderItem(4, __qtablewidgetitem22)
        if (self.tb_Monitor.rowCount() < 14):
            self.tb_Monitor.setRowCount(14)
        __qtablewidgetitem23 = QTableWidgetItem()
        __qtablewidgetitem23.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem23.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(0, 0, __qtablewidgetitem23)
        __qtablewidgetitem24 = QTableWidgetItem()
        __qtablewidgetitem24.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem24.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(0, 1, __qtablewidgetitem24)
        __qtablewidgetitem25 = QTableWidgetItem()
        __qtablewidgetitem25.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem25.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(0, 2, __qtablewidgetitem25)
        __qtablewidgetitem26 = QTableWidgetItem()
        __qtablewidgetitem26.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem26.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(0, 3, __qtablewidgetitem26)
        __qtablewidgetitem27 = QTableWidgetItem()
        __qtablewidgetitem27.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem27.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(0, 4, __qtablewidgetitem27)
        __qtablewidgetitem28 = QTableWidgetItem()
        __qtablewidgetitem28.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem28.setFlags(Qt.ItemIsDropEnabled|Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(1, 0, __qtablewidgetitem28)
        __qtablewidgetitem29 = QTableWidgetItem()
        __qtablewidgetitem29.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem29.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(1, 1, __qtablewidgetitem29)
        __qtablewidgetitem30 = QTableWidgetItem()
        __qtablewidgetitem30.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem30.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(1, 2, __qtablewidgetitem30)
        __qtablewidgetitem31 = QTableWidgetItem()
        __qtablewidgetitem31.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem31.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(1, 3, __qtablewidgetitem31)
        __qtablewidgetitem32 = QTableWidgetItem()
        __qtablewidgetitem32.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem32.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(1, 4, __qtablewidgetitem32)
        __qtablewidgetitem33 = QTableWidgetItem()
        __qtablewidgetitem33.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem33.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(2, 0, __qtablewidgetitem33)
        __qtablewidgetitem34 = QTableWidgetItem()
        __qtablewidgetitem34.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem34.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(2, 1, __qtablewidgetitem34)
        __qtablewidgetitem35 = QTableWidgetItem()
        __qtablewidgetitem35.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem35.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(2, 2, __qtablewidgetitem35)
        __qtablewidgetitem36 = QTableWidgetItem()
        __qtablewidgetitem36.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem36.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(2, 3, __qtablewidgetitem36)
        __qtablewidgetitem37 = QTableWidgetItem()
        __qtablewidgetitem37.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem37.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(2, 4, __qtablewidgetitem37)
        __qtablewidgetitem38 = QTableWidgetItem()
        __qtablewidgetitem38.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem38.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(3, 0, __qtablewidgetitem38)
        __qtablewidgetitem39 = QTableWidgetItem()
        __qtablewidgetitem39.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem39.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(3, 1, __qtablewidgetitem39)
        __qtablewidgetitem40 = QTableWidgetItem()
        __qtablewidgetitem40.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem40.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(3, 2, __qtablewidgetitem40)
        __qtablewidgetitem41 = QTableWidgetItem()
        __qtablewidgetitem41.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem41.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(3, 3, __qtablewidgetitem41)
        __qtablewidgetitem42 = QTableWidgetItem()
        __qtablewidgetitem42.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem42.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(3, 4, __qtablewidgetitem42)
        __qtablewidgetitem43 = QTableWidgetItem()
        __qtablewidgetitem43.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem43.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(4, 0, __qtablewidgetitem43)
        __qtablewidgetitem44 = QTableWidgetItem()
        __qtablewidgetitem44.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem44.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(4, 1, __qtablewidgetitem44)
        __qtablewidgetitem45 = QTableWidgetItem()
        __qtablewidgetitem45.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem45.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(4, 2, __qtablewidgetitem45)
        __qtablewidgetitem46 = QTableWidgetItem()
        __qtablewidgetitem46.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem46.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(4, 3, __qtablewidgetitem46)
        __qtablewidgetitem47 = QTableWidgetItem()
        __qtablewidgetitem47.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem47.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(4, 4, __qtablewidgetitem47)
        __qtablewidgetitem48 = QTableWidgetItem()
        __qtablewidgetitem48.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem48.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(5, 0, __qtablewidgetitem48)
        __qtablewidgetitem49 = QTableWidgetItem()
        __qtablewidgetitem49.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem49.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(5, 1, __qtablewidgetitem49)
        __qtablewidgetitem50 = QTableWidgetItem()
        __qtablewidgetitem50.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem50.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(5, 2, __qtablewidgetitem50)
        __qtablewidgetitem51 = QTableWidgetItem()
        __qtablewidgetitem51.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem51.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(5, 3, __qtablewidgetitem51)
        __qtablewidgetitem52 = QTableWidgetItem()
        __qtablewidgetitem52.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem52.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(5, 4, __qtablewidgetitem52)
        __qtablewidgetitem53 = QTableWidgetItem()
        __qtablewidgetitem53.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem53.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(6, 0, __qtablewidgetitem53)
        __qtablewidgetitem54 = QTableWidgetItem()
        __qtablewidgetitem54.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem54.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(6, 1, __qtablewidgetitem54)
        __qtablewidgetitem55 = QTableWidgetItem()
        __qtablewidgetitem55.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem55.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(6, 2, __qtablewidgetitem55)
        __qtablewidgetitem56 = QTableWidgetItem()
        __qtablewidgetitem56.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem56.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(6, 3, __qtablewidgetitem56)
        __qtablewidgetitem57 = QTableWidgetItem()
        __qtablewidgetitem57.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem57.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(6, 4, __qtablewidgetitem57)
        __qtablewidgetitem58 = QTableWidgetItem()
        __qtablewidgetitem58.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem58.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(7, 0, __qtablewidgetitem58)
        __qtablewidgetitem59 = QTableWidgetItem()
        __qtablewidgetitem59.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem59.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(7, 1, __qtablewidgetitem59)
        __qtablewidgetitem60 = QTableWidgetItem()
        __qtablewidgetitem60.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem60.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(7, 2, __qtablewidgetitem60)
        __qtablewidgetitem61 = QTableWidgetItem()
        __qtablewidgetitem61.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem61.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(7, 3, __qtablewidgetitem61)
        __qtablewidgetitem62 = QTableWidgetItem()
        __qtablewidgetitem62.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem62.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(7, 4, __qtablewidgetitem62)
        __qtablewidgetitem63 = QTableWidgetItem()
        __qtablewidgetitem63.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem63.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(8, 0, __qtablewidgetitem63)
        __qtablewidgetitem64 = QTableWidgetItem()
        __qtablewidgetitem64.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem64.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(8, 1, __qtablewidgetitem64)
        __qtablewidgetitem65 = QTableWidgetItem()
        __qtablewidgetitem65.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem65.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(8, 2, __qtablewidgetitem65)
        __qtablewidgetitem66 = QTableWidgetItem()
        __qtablewidgetitem66.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem66.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(8, 3, __qtablewidgetitem66)
        __qtablewidgetitem67 = QTableWidgetItem()
        __qtablewidgetitem67.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem67.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(8, 4, __qtablewidgetitem67)
        __qtablewidgetitem68 = QTableWidgetItem()
        __qtablewidgetitem68.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem68.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(9, 0, __qtablewidgetitem68)
        __qtablewidgetitem69 = QTableWidgetItem()
        __qtablewidgetitem69.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem69.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(9, 1, __qtablewidgetitem69)
        __qtablewidgetitem70 = QTableWidgetItem()
        __qtablewidgetitem70.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem70.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(9, 2, __qtablewidgetitem70)
        __qtablewidgetitem71 = QTableWidgetItem()
        __qtablewidgetitem71.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem71.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(9, 3, __qtablewidgetitem71)
        __qtablewidgetitem72 = QTableWidgetItem()
        __qtablewidgetitem72.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem72.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(9, 4, __qtablewidgetitem72)
        __qtablewidgetitem73 = QTableWidgetItem()
        __qtablewidgetitem73.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem73.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(10, 0, __qtablewidgetitem73)
        __qtablewidgetitem74 = QTableWidgetItem()
        __qtablewidgetitem74.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem74.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(10, 1, __qtablewidgetitem74)
        __qtablewidgetitem75 = QTableWidgetItem()
        __qtablewidgetitem75.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem75.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(10, 2, __qtablewidgetitem75)
        __qtablewidgetitem76 = QTableWidgetItem()
        __qtablewidgetitem76.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem76.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(10, 3, __qtablewidgetitem76)
        __qtablewidgetitem77 = QTableWidgetItem()
        __qtablewidgetitem77.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem77.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(10, 4, __qtablewidgetitem77)
        __qtablewidgetitem78 = QTableWidgetItem()
        __qtablewidgetitem78.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem78.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(11, 0, __qtablewidgetitem78)
        __qtablewidgetitem79 = QTableWidgetItem()
        __qtablewidgetitem79.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem79.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(11, 1, __qtablewidgetitem79)
        __qtablewidgetitem80 = QTableWidgetItem()
        __qtablewidgetitem80.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem80.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(11, 2, __qtablewidgetitem80)
        __qtablewidgetitem81 = QTableWidgetItem()
        __qtablewidgetitem81.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem81.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(11, 3, __qtablewidgetitem81)
        __qtablewidgetitem82 = QTableWidgetItem()
        __qtablewidgetitem82.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem82.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(11, 4, __qtablewidgetitem82)
        __qtablewidgetitem83 = QTableWidgetItem()
        __qtablewidgetitem83.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem83.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(12, 0, __qtablewidgetitem83)
        __qtablewidgetitem84 = QTableWidgetItem()
        __qtablewidgetitem84.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem84.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(12, 1, __qtablewidgetitem84)
        __qtablewidgetitem85 = QTableWidgetItem()
        __qtablewidgetitem85.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem85.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(12, 2, __qtablewidgetitem85)
        __qtablewidgetitem86 = QTableWidgetItem()
        __qtablewidgetitem86.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem86.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(12, 3, __qtablewidgetitem86)
        __qtablewidgetitem87 = QTableWidgetItem()
        __qtablewidgetitem87.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem87.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(12, 4, __qtablewidgetitem87)
        __qtablewidgetitem88 = QTableWidgetItem()
        __qtablewidgetitem88.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem88.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(13, 0, __qtablewidgetitem88)
        __qtablewidgetitem89 = QTableWidgetItem()
        __qtablewidgetitem89.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem89.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(13, 1, __qtablewidgetitem89)
        __qtablewidgetitem90 = QTableWidgetItem()
        __qtablewidgetitem90.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem90.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(13, 2, __qtablewidgetitem90)
        __qtablewidgetitem91 = QTableWidgetItem()
        __qtablewidgetitem91.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem91.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(13, 3, __qtablewidgetitem91)
        __qtablewidgetitem92 = QTableWidgetItem()
        __qtablewidgetitem92.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem92.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(13, 4, __qtablewidgetitem92)
        self.tb_Monitor.setObjectName(u"tb_Monitor")
        self.tb_Monitor.setGeometry(QRect(270, 61, 501, 371))
        self.tb_Monitor.setFont(font5)
        self.tb_Monitor.setFocusPolicy(Qt.NoFocus)
        self.tb_Monitor.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tb_Monitor.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tb_Monitor.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.tb_Monitor.setAutoScroll(True)
        self.tb_Monitor.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)
        self.tb_Monitor.setShowGrid(True)
        self.tb_Monitor.setGridStyle(Qt.DotLine)
        self.tb_Monitor.setSortingEnabled(False)
        self.tb_Monitor.setRowCount(14)
        self.tb_Monitor.setColumnCount(5)
        self.tb_Monitor.horizontalHeader().setCascadingSectionResizes(False)
        self.tb_Monitor.horizontalHeader().setMinimumSectionSize(0)
        self.tb_Monitor.horizontalHeader().setDefaultSectionSize(100)
        self.tb_Monitor.horizontalHeader().setHighlightSections(True)
        self.tb_Monitor.horizontalHeader().setProperty("showSortIndicator", False)
        self.tb_Monitor.horizontalHeader().setStretchLastSection(False)
        self.tb_Monitor.verticalHeader().setVisible(False)
        self.tb_Monitor.verticalHeader().setCascadingSectionResizes(False)
        self.tb_Monitor.verticalHeader().setMinimumSectionSize(19)
        self.tb_Monitor.verticalHeader().setDefaultSectionSize(25)
        self.tb_Monitor.verticalHeader().setProperty("showSortIndicator", False)
        self.tb_Monitor.verticalHeader().setStretchLastSection(True)
        self.sts_monitor4 = QLabel(Dialog)
        self.sts_monitor4.setObjectName(u"sts_monitor4")
        self.sts_monitor4.setGeometry(QRect(247, 160, 20, 20))
        self.sts_monitor4.setFont(font8)
        self.sts_monitor_ok = QLabel(Dialog)
        self.sts_monitor_ok.setObjectName(u"sts_monitor_ok")
        self.sts_monitor_ok.setGeometry(QRect(680, 444, 19, 20))
        self.sts_monitor_ok.setFont(font8)
        self.sts_monitor6 = QLabel(Dialog)
        self.sts_monitor6.setObjectName(u"sts_monitor6")
        self.sts_monitor6.setGeometry(QRect(247, 210, 20, 20))
        self.sts_monitor6.setFont(font8)
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(270, 5, 81, 16))
        self.label_2.setFont(font7)
        self.bt_com_tc1 = QPushButton(Dialog)
        self.bt_com_tc1.setObjectName(u"bt_com_tc1")
        self.bt_com_tc1.setGeometry(QRect(80, 404, 71, 26))
        self.bt_com_tc2 = QPushButton(Dialog)
        self.bt_com_tc2.setObjectName(u"bt_com_tc2")
        self.bt_com_tc2.setGeometry(QRect(160, 404, 71, 26))
        self.bt_com_tc3 = QPushButton(Dialog)
        self.bt_com_tc3.setObjectName(u"bt_com_tc3")
        self.bt_com_tc3.setGeometry(QRect(80, 434, 71, 26))
        self.bt_com_tm = QPushButton(Dialog)
        self.bt_com_tm.setObjectName(u"bt_com_tm")
        self.bt_com_tm.setGeometry(QRect(160, 434, 71, 26))
        self.bt_pwr_off1 = QPushButton(Dialog)
        self.bt_pwr_off1.setObjectName(u"bt_pwr_off1")
        self.bt_pwr_off1.setGeometry(QRect(209, 52, 30, 22))
        self.bt_pwr_off1.setFont(font2)
        self.bt_pwr_off2 = QPushButton(Dialog)
        self.bt_pwr_off2.setObjectName(u"bt_pwr_off2")
        self.bt_pwr_off2.setGeometry(QRect(209, 77, 30, 22))
        self.bt_pwr_off2.setFont(font2)
        self.bt_pwr_off3 = QPushButton(Dialog)
        self.bt_pwr_off3.setObjectName(u"bt_pwr_off3")
        self.bt_pwr_off3.setGeometry(QRect(209, 102, 30, 22))
        self.bt_pwr_off3.setFont(font2)
        self.bt_pwr_off4 = QPushButton(Dialog)
        self.bt_pwr_off4.setObjectName(u"bt_pwr_off4")
        self.bt_pwr_off4.setGeometry(QRect(209, 127, 30, 22))
        self.bt_pwr_off4.setFont(font2)
        self.bt_pwr_off5 = QPushButton(Dialog)
        self.bt_pwr_off5.setObjectName(u"bt_pwr_off5")
        self.bt_pwr_off5.setGeometry(QRect(209, 152, 30, 22))
        self.bt_pwr_off5.setFont(font2)
        self.bt_pwr_off6 = QPushButton(Dialog)
        self.bt_pwr_off6.setObjectName(u"bt_pwr_off6")
        self.bt_pwr_off6.setGeometry(QRect(209, 177, 30, 22))
        self.bt_pwr_off6.setFont(font2)
        self.bt_pwr_off7 = QPushButton(Dialog)
        self.bt_pwr_off7.setObjectName(u"bt_pwr_off7")
        self.bt_pwr_off7.setGeometry(QRect(209, 202, 30, 22))
        self.bt_pwr_off7.setFont(font2)
        self.bt_pwr_off8 = QPushButton(Dialog)
        self.bt_pwr_off8.setObjectName(u"bt_pwr_off8")
        self.bt_pwr_off8.setGeometry(QRect(209, 226, 30, 22))
        self.bt_pwr_off8.setFont(font2)
        self.label_13 = QLabel(Dialog)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setGeometry(QRect(10, 344, 61, 21))
        self.label_13.setFont(font1)
        self.label_13.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_sendto = QLineEdit(Dialog)
        self.e_sendto.setObjectName(u"e_sendto")
        self.e_sendto.setGeometry(QRect(80, 344, 151, 26))
        self.e_recv = QLineEdit(Dialog)
        self.e_recv.setObjectName(u"e_recv")
        self.e_recv.setGeometry(QRect(80, 374, 151, 26))
        self.e_recv.setReadOnly(True)
        self.label_14 = QLabel(Dialog)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setGeometry(QRect(10, 374, 61, 21))
        self.label_14.setFont(font1)
        self.label_14.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.chk_manual_test = QCheckBox(Dialog)
        self.chk_manual_test.setObjectName(u"chk_manual_test")
        self.chk_manual_test.setGeometry(QRect(10, 314, 141, 21))
        self.chk_manual_test.setFont(font1)
        self.bt_pwr_on6 = QPushButton(Dialog)
        self.bt_pwr_on6.setObjectName(u"bt_pwr_on6")
        self.bt_pwr_on6.setGeometry(QRect(178, 177, 30, 22))
        self.bt_pwr_on6.setFont(font2)
        self.bt_pwr_on7 = QPushButton(Dialog)
        self.bt_pwr_on7.setObjectName(u"bt_pwr_on7")
        self.bt_pwr_on7.setGeometry(QRect(178, 202, 30, 22))
        self.bt_pwr_on7.setFont(font2)
        self.bt_pwr_on2 = QPushButton(Dialog)
        self.bt_pwr_on2.setObjectName(u"bt_pwr_on2")
        self.bt_pwr_on2.setGeometry(QRect(178, 77, 30, 22))
        self.bt_pwr_on2.setFont(font2)
        self.bt_pwr_on3 = QPushButton(Dialog)
        self.bt_pwr_on3.setObjectName(u"bt_pwr_on3")
        self.bt_pwr_on3.setGeometry(QRect(178, 102, 30, 22))
        self.bt_pwr_on3.setFont(font2)
        self.bt_pwr_on4 = QPushButton(Dialog)
        self.bt_pwr_on4.setObjectName(u"bt_pwr_on4")
        self.bt_pwr_on4.setGeometry(QRect(178, 127, 30, 22))
        self.bt_pwr_on4.setFont(font2)
        self.bt_pwr_on8 = QPushButton(Dialog)
        self.bt_pwr_on8.setObjectName(u"bt_pwr_on8")
        self.bt_pwr_on8.setGeometry(QRect(178, 226, 30, 22))
        self.bt_pwr_on8.setFont(font2)
        self.bt_pwr_on5 = QPushButton(Dialog)
        self.bt_pwr_on5.setObjectName(u"bt_pwr_on5")
        self.bt_pwr_on5.setGeometry(QRect(178, 152, 30, 22))
        self.bt_pwr_on5.setFont(font2)
        self.bt_pwr_on1 = QPushButton(Dialog)
        self.bt_pwr_on1.setObjectName(u"bt_pwr_on1")
        self.bt_pwr_on1.setGeometry(QRect(178, 52, 30, 22))
        self.bt_pwr_on1.setFont(font2)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"House Keeping Package", None))
        self.label_27.setText(QCoreApplication.translate("Dialog", u"Updated Time : ", None))
        self.sts_updated.setText(QCoreApplication.translate("Dialog", u"2021-11-19 15:21:00", None))
        self.label_29.setText(QCoreApplication.translate("Dialog", u"power on             power off", None))
        self.sts_pdu_on.setText(QCoreApplication.translate("Dialog", u"\u2b1b", None))
        self.sts_pdu_off.setText(QCoreApplication.translate("Dialog", u"\u2b1b", None))
        self.sts_interval.setText(QCoreApplication.translate("Dialog", u"interval :", None))
        self.sts_pdu3.setText(QCoreApplication.translate("Dialog", u"\u2b1b", None))
        self.sts_pdu5.setText(QCoreApplication.translate("Dialog", u"\u2b1b", None))
        self.sts_pdu4.setText(QCoreApplication.translate("Dialog", u"\u2b1b", None))
        self.sts_pdu6.setText(QCoreApplication.translate("Dialog", u"\u2b1b", None))
        ___qtablewidgetitem = self.tb_pdu.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("Dialog", u"OUTLET", None));
        ___qtablewidgetitem1 = self.tb_pdu.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("Dialog", u"Connection", None));

        __sortingEnabled = self.tb_pdu.isSortingEnabled()
        self.tb_pdu.setSortingEnabled(False)
        ___qtablewidgetitem2 = self.tb_pdu.item(0, 0)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("Dialog", u"1", None));
        ___qtablewidgetitem3 = self.tb_pdu.item(1, 0)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("Dialog", u"2", None));
        ___qtablewidgetitem4 = self.tb_pdu.item(2, 0)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("Dialog", u"3", None));
        ___qtablewidgetitem5 = self.tb_pdu.item(3, 0)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("Dialog", u"4", None));
        ___qtablewidgetitem6 = self.tb_pdu.item(4, 0)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("Dialog", u"5", None));
        ___qtablewidgetitem7 = self.tb_pdu.item(5, 0)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("Dialog", u"6", None));
        ___qtablewidgetitem8 = self.tb_pdu.item(6, 0)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("Dialog", u"7", None));
        ___qtablewidgetitem9 = self.tb_pdu.item(7, 0)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("Dialog", u"8", None));
        self.tb_pdu.setSortingEnabled(__sortingEnabled)

        self.sts_pdu2.setText(QCoreApplication.translate("Dialog", u"\u2b1b", None))
        self.sts_pdu8.setText(QCoreApplication.translate("Dialog", u"\u2b1b", None))
        self.sts_pdu7.setText(QCoreApplication.translate("Dialog", u"\u2b1b", None))
        self.sts_pdu1.setText(QCoreApplication.translate("Dialog", u"\u2b1b", None))
        self.sts_pdu.setText(QCoreApplication.translate("Dialog", u"\u26a1", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"PDU Status", None))
        self.sts_monitor14.setText(QCoreApplication.translate("Dialog", u"\u26ab", None))
        self.label_34.setText(QCoreApplication.translate("Dialog", u"connection OK            Error", None))
        self.sts_monitor10.setText(QCoreApplication.translate("Dialog", u"\u26ab", None))
        self.sts_monitor8.setText(QCoreApplication.translate("Dialog", u"\u26ab", None))
        self.sts_monitor13.setText(QCoreApplication.translate("Dialog", u"\u26ab", None))
        self.sts_vacuum.setText(QCoreApplication.translate("Dialog", u"\u26ab", None))
        self.sts_monitor_error.setText(QCoreApplication.translate("Dialog", u"\u26ab", None))
        self.sts_monitor7.setText(QCoreApplication.translate("Dialog", u"\u26ab", None))
        self.sts_monitor5.setText(QCoreApplication.translate("Dialog", u"\u26ab", None))
        self.sts_monitor9.setText(QCoreApplication.translate("Dialog", u"\u26ab", None))
        self.sts_monitor1.setText(QCoreApplication.translate("Dialog", u"\u26ab", None))
        self.sts_monitor2.setText(QCoreApplication.translate("Dialog", u"\u26ab", None))
        self.sts_monitor11.setText(QCoreApplication.translate("Dialog", u"\u26ab", None))
        self.sts_monitor3.setText(QCoreApplication.translate("Dialog", u"\u26ab", None))
        self.label_18.setText(QCoreApplication.translate("Dialog", u"Torr", None))
        self.sts_monitor12.setText(QCoreApplication.translate("Dialog", u"\u26ab", None))
        self.label_11.setText(QCoreApplication.translate("Dialog", u"Vacuum Pressure", None))
        ___qtablewidgetitem10 = self.tb_Monitor.horizontalHeaderItem(0)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("Dialog", u"TC / TM", None));
        ___qtablewidgetitem11 = self.tb_Monitor.horizontalHeaderItem(1)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("Dialog", u"Temperature", None));
        ___qtablewidgetitem12 = self.tb_Monitor.horizontalHeaderItem(2)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("Dialog", u"Current", None));
        ___qtablewidgetitem13 = self.tb_Monitor.horizontalHeaderItem(3)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("Dialog", u"Set Point", None));
        ___qtablewidgetitem14 = self.tb_Monitor.horizontalHeaderItem(4)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("Dialog", u"Heat Power", None));

        __sortingEnabled1 = self.tb_Monitor.isSortingEnabled()
        self.tb_Monitor.setSortingEnabled(False)
        self.tb_Monitor.setSortingEnabled(__sortingEnabled1)

        self.sts_monitor4.setText(QCoreApplication.translate("Dialog", u"\u26ab", None))
        self.sts_monitor_ok.setText(QCoreApplication.translate("Dialog", u"\u26ab", None))
        self.sts_monitor6.setText(QCoreApplication.translate("Dialog", u"\u26ab", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Monitor", None))
        self.bt_com_tc1.setText(QCoreApplication.translate("Dialog", u"TMC1", None))
        self.bt_com_tc2.setText(QCoreApplication.translate("Dialog", u"TMC2", None))
        self.bt_com_tc3.setText(QCoreApplication.translate("Dialog", u"TMC3", None))
        self.bt_com_tm.setText(QCoreApplication.translate("Dialog", u"TM", None))
        self.bt_pwr_off1.setText(QCoreApplication.translate("Dialog", u"Off", None))
        self.bt_pwr_off2.setText(QCoreApplication.translate("Dialog", u"Off", None))
        self.bt_pwr_off3.setText(QCoreApplication.translate("Dialog", u"Off", None))
        self.bt_pwr_off4.setText(QCoreApplication.translate("Dialog", u"Off", None))
        self.bt_pwr_off5.setText(QCoreApplication.translate("Dialog", u"Off", None))
        self.bt_pwr_off6.setText(QCoreApplication.translate("Dialog", u"Off", None))
        self.bt_pwr_off7.setText(QCoreApplication.translate("Dialog", u"Off", None))
        self.bt_pwr_off8.setText(QCoreApplication.translate("Dialog", u"Off", None))
        self.label_13.setText(QCoreApplication.translate("Dialog", u"Send:", None))
        self.e_sendto.setText(QCoreApplication.translate("Dialog", u"command", None))
        self.e_recv.setText("")
        self.label_14.setText(QCoreApplication.translate("Dialog", u"Receive:", None))
        self.chk_manual_test.setText(QCoreApplication.translate("Dialog", u"Manual Test", None))
        self.bt_pwr_on6.setText(QCoreApplication.translate("Dialog", u"On", None))
        self.bt_pwr_on7.setText(QCoreApplication.translate("Dialog", u"On", None))
        self.bt_pwr_on2.setText(QCoreApplication.translate("Dialog", u"On", None))
        self.bt_pwr_on3.setText(QCoreApplication.translate("Dialog", u"On", None))
        self.bt_pwr_on4.setText(QCoreApplication.translate("Dialog", u"On", None))
        self.bt_pwr_on8.setText(QCoreApplication.translate("Dialog", u"On", None))
        self.bt_pwr_on5.setText(QCoreApplication.translate("Dialog", u"On", None))
        self.bt_pwr_on1.setText(QCoreApplication.translate("Dialog", u"On", None))
    # retranslateUi

