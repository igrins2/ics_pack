# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'HKPUvgdqr.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QCheckBox,
    QDialog, QFrame, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTableWidget,
    QTableWidgetItem, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(686, 498)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        #Dialog.setSizeGripEnabled(False)
        self.label_27 = QLabel(Dialog)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setGeometry(QRect(430, 7, 111, 20))
        font = QFont()
        font.setPointSize(10)
        self.label_27.setFont(font)
        self.label_27.setLayoutDirection(Qt.LeftToRight)
        self.label_27.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.sts_updated = QLabel(Dialog)
        self.sts_updated.setObjectName(u"sts_updated")
        self.sts_updated.setGeometry(QRect(540, 7, 141, 21))
        self.sts_updated.setFont(font)
        self.label_29 = QLabel(Dialog)
        self.label_29.setObjectName(u"label_29")
        self.label_29.setGeometry(QRect(60, 289, 171, 20))
        self.label_29.setFont(font)
        self.sts_pdu_on = QLabel(Dialog)
        self.sts_pdu_on.setObjectName(u"sts_pdu_on")
        self.sts_pdu_on.setGeometry(QRect(36, 290, 19, 20))
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(False)
        self.sts_pdu_on.setFont(font1)
        self.sts_pdu_off = QLabel(Dialog)
        self.sts_pdu_off.setObjectName(u"sts_pdu_off")
        self.sts_pdu_off.setGeometry(QRect(137, 290, 20, 20))
        self.sts_pdu_off.setFont(font1)
        self.sts_interval = QLabel(Dialog)
        self.sts_interval.setObjectName(u"sts_interval")
        self.sts_interval.setGeometry(QRect(250, 7, 181, 20))
        self.sts_interval.setFont(font)
        self.sts_interval.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.sts_pdu3 = QLabel(Dialog)
        self.sts_pdu3.setObjectName(u"sts_pdu3")
        self.sts_pdu3.setGeometry(QRect(8, 129, 19, 20))
        self.sts_pdu3.setFont(font1)
        self.sts_pdu5 = QLabel(Dialog)
        self.sts_pdu5.setObjectName(u"sts_pdu5")
        self.sts_pdu5.setGeometry(QRect(8, 179, 19, 20))
        self.sts_pdu5.setFont(font1)
        self.sts_pdu4 = QLabel(Dialog)
        self.sts_pdu4.setObjectName(u"sts_pdu4")
        self.sts_pdu4.setGeometry(QRect(8, 154, 19, 20))
        self.sts_pdu4.setFont(font1)
        self.sts_pdu6 = QLabel(Dialog)
        self.sts_pdu6.setObjectName(u"sts_pdu6")
        self.sts_pdu6.setGeometry(QRect(8, 204, 19, 20))
        self.sts_pdu6.setFont(font1)
        self.tb_pdu = QTableWidget(Dialog)
        if (self.tb_pdu.columnCount() < 2):
            self.tb_pdu.setColumnCount(2)
        font2 = QFont()
        font2.setPointSize(10)
        font2.setBold(True)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setFont(font2);
        self.tb_pdu.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        __qtablewidgetitem1.setFont(font2);
        self.tb_pdu.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        if (self.tb_pdu.rowCount() < 8):
            self.tb_pdu.setRowCount(8)
        __qtablewidgetitem2 = QTableWidgetItem()
        __qtablewidgetitem2.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem2.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(0, 0, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        __qtablewidgetitem3.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(0, 1, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        __qtablewidgetitem4.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem4.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(1, 0, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        __qtablewidgetitem5.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(1, 1, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        __qtablewidgetitem6.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem6.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(2, 0, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        __qtablewidgetitem7.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(2, 1, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        __qtablewidgetitem8.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem8.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(3, 0, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        __qtablewidgetitem9.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(3, 1, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        __qtablewidgetitem10.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem10.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(4, 0, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        __qtablewidgetitem11.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(4, 1, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        __qtablewidgetitem12.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem12.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(5, 0, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        __qtablewidgetitem13.setFlags(Qt.NoItemFlags);
        self.tb_pdu.setItem(5, 1, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        __qtablewidgetitem14.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem14.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(6, 0, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        __qtablewidgetitem15.setFlags(Qt.NoItemFlags);
        self.tb_pdu.setItem(6, 1, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        __qtablewidgetitem16.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem16.setFlags(Qt.ItemIsEnabled);
        self.tb_pdu.setItem(7, 0, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        __qtablewidgetitem17.setFlags(Qt.NoItemFlags);
        self.tb_pdu.setItem(7, 1, __qtablewidgetitem17)
        self.tb_pdu.setObjectName(u"tb_pdu")
        self.tb_pdu.setGeometry(QRect(30, 55, 201, 221))
        font3 = QFont()
        font3.setPointSize(10)
        font3.setBold(False)
        self.tb_pdu.setFont(font3)
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
        self.tb_pdu.horizontalHeader().setDefaultSectionSize(70)
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
        self.sts_pdu2.setGeometry(QRect(8, 104, 19, 20))
        self.sts_pdu2.setFont(font1)
        self.sts_pdu8 = QLabel(Dialog)
        self.sts_pdu8.setObjectName(u"sts_pdu8")
        self.sts_pdu8.setGeometry(QRect(8, 258, 19, 20))
        self.sts_pdu8.setFont(font1)
        self.sts_pdu7 = QLabel(Dialog)
        self.sts_pdu7.setObjectName(u"sts_pdu7")
        self.sts_pdu7.setGeometry(QRect(8, 229, 19, 20))
        self.sts_pdu7.setFont(font1)
        self.sts_pdu1 = QLabel(Dialog)
        self.sts_pdu1.setObjectName(u"sts_pdu1")
        self.sts_pdu1.setGeometry(QRect(8, 79, 19, 20))
        self.sts_pdu1.setFont(font1)
        self.sts_pdu = QLabel(Dialog)
        self.sts_pdu.setObjectName(u"sts_pdu")
        self.sts_pdu.setGeometry(QRect(3, 27, 19, 25))
        font4 = QFont()
        font4.setPointSize(20)
        font4.setBold(True)
        self.sts_pdu.setFont(font4)
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(30, 31, 111, 16))
        font5 = QFont()
        font5.setPointSize(12)
        font5.setBold(True)
        self.label.setFont(font5)
        self.sts_monitor14 = QLabel(Dialog)
        self.sts_monitor14.setObjectName(u"sts_monitor14")
        self.sts_monitor14.setGeometry(QRect(247, 436, 20, 20))
        font6 = QFont()
        font6.setPointSize(16)
        font6.setBold(False)
        self.sts_monitor14.setFont(font6)
        self.label_34 = QLabel(Dialog)
        self.label_34.setObjectName(u"label_34")
        self.label_34.setGeometry(QRect(480, 469, 171, 20))
        self.label_34.setFont(font3)
        self.sts_monitor10 = QLabel(Dialog)
        self.sts_monitor10.setObjectName(u"sts_monitor10")
        self.sts_monitor10.setGeometry(QRect(247, 336, 20, 20))
        self.sts_monitor10.setFont(font6)
        self.sts_monitor8 = QLabel(Dialog)
        self.sts_monitor8.setObjectName(u"sts_monitor8")
        self.sts_monitor8.setGeometry(QRect(247, 286, 20, 20))
        self.sts_monitor8.setFont(font6)
        self.sts_monitor13 = QLabel(Dialog)
        self.sts_monitor13.setObjectName(u"sts_monitor13")
        self.sts_monitor13.setGeometry(QRect(247, 411, 20, 20))
        self.sts_monitor13.setFont(font6)
        self.sts_vacuum = QLabel(Dialog)
        self.sts_vacuum.setObjectName(u"sts_vacuum")
        self.sts_vacuum.setGeometry(QRect(247, 57, 20, 20))
        self.sts_vacuum.setFont(font6)
        self.sts_monitor_error = QLabel(Dialog)
        self.sts_monitor_error.setObjectName(u"sts_monitor_error")
        self.sts_monitor_error.setGeometry(QRect(651, 470, 20, 20))
        self.sts_monitor_error.setFont(font6)
        self.sts_monitor7 = QLabel(Dialog)
        self.sts_monitor7.setObjectName(u"sts_monitor7")
        self.sts_monitor7.setGeometry(QRect(247, 261, 20, 20))
        self.sts_monitor7.setFont(font6)
        self.sts_monitor5 = QLabel(Dialog)
        self.sts_monitor5.setObjectName(u"sts_monitor5")
        self.sts_monitor5.setGeometry(QRect(247, 211, 20, 20))
        self.sts_monitor5.setFont(font6)
        self.sts_monitor9 = QLabel(Dialog)
        self.sts_monitor9.setObjectName(u"sts_monitor9")
        self.sts_monitor9.setGeometry(QRect(247, 311, 20, 20))
        self.sts_monitor9.setFont(font6)
        self.sts_monitor1 = QLabel(Dialog)
        self.sts_monitor1.setObjectName(u"sts_monitor1")
        self.sts_monitor1.setGeometry(QRect(247, 111, 20, 20))
        self.sts_monitor1.setFont(font6)
        self.sts_monitor2 = QLabel(Dialog)
        self.sts_monitor2.setObjectName(u"sts_monitor2")
        self.sts_monitor2.setGeometry(QRect(247, 136, 20, 20))
        self.sts_monitor2.setFont(font6)
        self.sts_monitor11 = QLabel(Dialog)
        self.sts_monitor11.setObjectName(u"sts_monitor11")
        self.sts_monitor11.setGeometry(QRect(247, 361, 20, 20))
        self.sts_monitor11.setFont(font6)
        self.sts_monitor3 = QLabel(Dialog)
        self.sts_monitor3.setObjectName(u"sts_monitor3")
        self.sts_monitor3.setGeometry(QRect(247, 161, 20, 20))
        self.sts_monitor3.setFont(font6)
        self.e_vacuum = QLineEdit(Dialog)
        self.e_vacuum.setObjectName(u"e_vacuum")
        self.e_vacuum.setGeometry(QRect(395, 54, 81, 25))
        self.e_vacuum.setFocusPolicy(Qt.NoFocus)
        self.e_vacuum.setAlignment(Qt.AlignCenter)
        self.e_vacuum.setReadOnly(True)
        self.label_18 = QLabel(Dialog)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setGeometry(QRect(481, 58, 30, 17))
        self.label_18.setFont(font3)
        self.sts_monitor12 = QLabel(Dialog)
        self.sts_monitor12.setObjectName(u"sts_monitor12")
        self.sts_monitor12.setGeometry(QRect(247, 386, 20, 20))
        self.sts_monitor12.setFont(font6)
        self.label_11 = QLabel(Dialog)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setGeometry(QRect(271, 58, 121, 17))
        self.label_11.setFont(font3)
        self.tb_Monitor = QTableWidget(Dialog)
        if (self.tb_Monitor.columnCount() < 4):
            self.tb_Monitor.setColumnCount(4)
        __qtablewidgetitem18 = QTableWidgetItem()
        __qtablewidgetitem18.setFont(font2);
        self.tb_Monitor.setHorizontalHeaderItem(0, __qtablewidgetitem18)
        __qtablewidgetitem19 = QTableWidgetItem()
        __qtablewidgetitem19.setFont(font2);
        self.tb_Monitor.setHorizontalHeaderItem(1, __qtablewidgetitem19)
        __qtablewidgetitem20 = QTableWidgetItem()
        __qtablewidgetitem20.setFont(font2);
        self.tb_Monitor.setHorizontalHeaderItem(2, __qtablewidgetitem20)
        __qtablewidgetitem21 = QTableWidgetItem()
        __qtablewidgetitem21.setFont(font2);
        self.tb_Monitor.setHorizontalHeaderItem(3, __qtablewidgetitem21)
        if (self.tb_Monitor.rowCount() < 14):
            self.tb_Monitor.setRowCount(14)
        __qtablewidgetitem22 = QTableWidgetItem()
        __qtablewidgetitem22.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem22.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(0, 0, __qtablewidgetitem22)
        __qtablewidgetitem23 = QTableWidgetItem()
        __qtablewidgetitem23.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem23.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(0, 1, __qtablewidgetitem23)
        __qtablewidgetitem24 = QTableWidgetItem()
        __qtablewidgetitem24.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem24.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(0, 2, __qtablewidgetitem24)
        __qtablewidgetitem25 = QTableWidgetItem()
        __qtablewidgetitem25.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem25.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(0, 3, __qtablewidgetitem25)
        __qtablewidgetitem26 = QTableWidgetItem()
        __qtablewidgetitem26.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem26.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(1, 0, __qtablewidgetitem26)
        __qtablewidgetitem27 = QTableWidgetItem()
        __qtablewidgetitem27.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem27.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(1, 1, __qtablewidgetitem27)
        __qtablewidgetitem28 = QTableWidgetItem()
        __qtablewidgetitem28.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem28.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(1, 2, __qtablewidgetitem28)
        __qtablewidgetitem29 = QTableWidgetItem()
        __qtablewidgetitem29.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem29.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(1, 3, __qtablewidgetitem29)
        __qtablewidgetitem30 = QTableWidgetItem()
        __qtablewidgetitem30.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem30.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(2, 0, __qtablewidgetitem30)
        __qtablewidgetitem31 = QTableWidgetItem()
        __qtablewidgetitem31.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem31.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(2, 1, __qtablewidgetitem31)
        __qtablewidgetitem32 = QTableWidgetItem()
        __qtablewidgetitem32.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem32.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(2, 2, __qtablewidgetitem32)
        __qtablewidgetitem33 = QTableWidgetItem()
        __qtablewidgetitem33.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem33.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(2, 3, __qtablewidgetitem33)
        __qtablewidgetitem34 = QTableWidgetItem()
        __qtablewidgetitem34.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem34.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(3, 0, __qtablewidgetitem34)
        __qtablewidgetitem35 = QTableWidgetItem()
        __qtablewidgetitem35.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem35.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(3, 1, __qtablewidgetitem35)
        __qtablewidgetitem36 = QTableWidgetItem()
        __qtablewidgetitem36.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem36.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(3, 2, __qtablewidgetitem36)
        __qtablewidgetitem37 = QTableWidgetItem()
        __qtablewidgetitem37.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem37.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(3, 3, __qtablewidgetitem37)
        __qtablewidgetitem38 = QTableWidgetItem()
        __qtablewidgetitem38.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem38.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(4, 0, __qtablewidgetitem38)
        __qtablewidgetitem39 = QTableWidgetItem()
        __qtablewidgetitem39.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem39.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(4, 1, __qtablewidgetitem39)
        __qtablewidgetitem40 = QTableWidgetItem()
        __qtablewidgetitem40.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem40.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(4, 2, __qtablewidgetitem40)
        __qtablewidgetitem41 = QTableWidgetItem()
        __qtablewidgetitem41.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem41.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(4, 3, __qtablewidgetitem41)
        __qtablewidgetitem42 = QTableWidgetItem()
        __qtablewidgetitem42.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem42.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(5, 0, __qtablewidgetitem42)
        __qtablewidgetitem43 = QTableWidgetItem()
        __qtablewidgetitem43.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem43.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(5, 1, __qtablewidgetitem43)
        __qtablewidgetitem44 = QTableWidgetItem()
        __qtablewidgetitem44.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem44.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(5, 2, __qtablewidgetitem44)
        __qtablewidgetitem45 = QTableWidgetItem()
        __qtablewidgetitem45.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem45.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(5, 3, __qtablewidgetitem45)
        __qtablewidgetitem46 = QTableWidgetItem()
        __qtablewidgetitem46.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem46.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(6, 0, __qtablewidgetitem46)
        __qtablewidgetitem47 = QTableWidgetItem()
        __qtablewidgetitem47.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem47.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(6, 1, __qtablewidgetitem47)
        __qtablewidgetitem48 = QTableWidgetItem()
        __qtablewidgetitem48.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem48.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(6, 2, __qtablewidgetitem48)
        __qtablewidgetitem49 = QTableWidgetItem()
        __qtablewidgetitem49.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem49.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(6, 3, __qtablewidgetitem49)
        __qtablewidgetitem50 = QTableWidgetItem()
        __qtablewidgetitem50.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem50.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(7, 0, __qtablewidgetitem50)
        __qtablewidgetitem51 = QTableWidgetItem()
        __qtablewidgetitem51.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem51.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(7, 1, __qtablewidgetitem51)
        __qtablewidgetitem52 = QTableWidgetItem()
        __qtablewidgetitem52.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem52.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(7, 2, __qtablewidgetitem52)
        __qtablewidgetitem53 = QTableWidgetItem()
        __qtablewidgetitem53.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem53.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(7, 3, __qtablewidgetitem53)
        __qtablewidgetitem54 = QTableWidgetItem()
        __qtablewidgetitem54.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem54.setFlags(Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(8, 0, __qtablewidgetitem54)
        __qtablewidgetitem55 = QTableWidgetItem()
        __qtablewidgetitem55.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem55.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(8, 1, __qtablewidgetitem55)
        __qtablewidgetitem56 = QTableWidgetItem()
        __qtablewidgetitem56.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem56.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(8, 2, __qtablewidgetitem56)
        __qtablewidgetitem57 = QTableWidgetItem()
        __qtablewidgetitem57.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem57.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(8, 3, __qtablewidgetitem57)
        __qtablewidgetitem58 = QTableWidgetItem()
        __qtablewidgetitem58.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem58.setFlags(Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(9, 0, __qtablewidgetitem58)
        __qtablewidgetitem59 = QTableWidgetItem()
        __qtablewidgetitem59.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem59.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(9, 1, __qtablewidgetitem59)
        __qtablewidgetitem60 = QTableWidgetItem()
        __qtablewidgetitem60.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem60.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(9, 2, __qtablewidgetitem60)
        __qtablewidgetitem61 = QTableWidgetItem()
        __qtablewidgetitem61.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem61.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(9, 3, __qtablewidgetitem61)
        __qtablewidgetitem62 = QTableWidgetItem()
        __qtablewidgetitem62.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem62.setFlags(Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(10, 0, __qtablewidgetitem62)
        __qtablewidgetitem63 = QTableWidgetItem()
        __qtablewidgetitem63.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem63.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(10, 1, __qtablewidgetitem63)
        __qtablewidgetitem64 = QTableWidgetItem()
        __qtablewidgetitem64.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem64.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(10, 2, __qtablewidgetitem64)
        __qtablewidgetitem65 = QTableWidgetItem()
        __qtablewidgetitem65.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem65.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(10, 3, __qtablewidgetitem65)
        __qtablewidgetitem66 = QTableWidgetItem()
        __qtablewidgetitem66.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem66.setFlags(Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(11, 0, __qtablewidgetitem66)
        __qtablewidgetitem67 = QTableWidgetItem()
        __qtablewidgetitem67.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem67.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(11, 1, __qtablewidgetitem67)
        __qtablewidgetitem68 = QTableWidgetItem()
        __qtablewidgetitem68.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem68.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(11, 2, __qtablewidgetitem68)
        __qtablewidgetitem69 = QTableWidgetItem()
        __qtablewidgetitem69.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem69.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(11, 3, __qtablewidgetitem69)
        __qtablewidgetitem70 = QTableWidgetItem()
        __qtablewidgetitem70.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem70.setFlags(Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(12, 0, __qtablewidgetitem70)
        __qtablewidgetitem71 = QTableWidgetItem()
        __qtablewidgetitem71.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem71.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(12, 1, __qtablewidgetitem71)
        __qtablewidgetitem72 = QTableWidgetItem()
        __qtablewidgetitem72.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem72.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(12, 2, __qtablewidgetitem72)
        __qtablewidgetitem73 = QTableWidgetItem()
        __qtablewidgetitem73.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem73.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(12, 3, __qtablewidgetitem73)
        __qtablewidgetitem74 = QTableWidgetItem()
        __qtablewidgetitem74.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem74.setFlags(Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(13, 0, __qtablewidgetitem74)
        __qtablewidgetitem75 = QTableWidgetItem()
        __qtablewidgetitem75.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem75.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(13, 1, __qtablewidgetitem75)
        __qtablewidgetitem76 = QTableWidgetItem()
        __qtablewidgetitem76.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem76.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(13, 2, __qtablewidgetitem76)
        __qtablewidgetitem77 = QTableWidgetItem()
        __qtablewidgetitem77.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem77.setFlags(Qt.ItemIsEnabled);
        self.tb_Monitor.setItem(13, 3, __qtablewidgetitem77)
        self.tb_Monitor.setObjectName(u"tb_Monitor")
        self.tb_Monitor.setGeometry(QRect(270, 87, 401, 371))
        self.tb_Monitor.setFont(font3)
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
        self.tb_Monitor.setColumnCount(4)
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
        self.sts_monitor4.setGeometry(QRect(247, 186, 20, 20))
        self.sts_monitor4.setFont(font6)
        self.chk_alert = QCheckBox(Dialog)
        self.chk_alert.setObjectName(u"chk_alert")
        self.chk_alert.setGeometry(QRect(273, 469, 201, 21))
        self.chk_alert.setFont(font3)
        self.sts_monitor_ok = QLabel(Dialog)
        self.sts_monitor_ok.setObjectName(u"sts_monitor_ok")
        self.sts_monitor_ok.setGeometry(QRect(580, 470, 19, 20))
        self.sts_monitor_ok.setFont(font6)
        self.sts_monitor6 = QLabel(Dialog)
        self.sts_monitor6.setObjectName(u"sts_monitor6")
        self.sts_monitor6.setGeometry(QRect(247, 236, 20, 20))
        self.sts_monitor6.setFont(font6)
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(270, 31, 81, 16))
        self.label_2.setFont(font5)
        self.alert_status = QLabel(Dialog)
        self.alert_status.setObjectName(u"alert_status")
        self.alert_status.setGeometry(QRect(590, 54, 81, 25))
        font7 = QFont()
        font7.setUnderline(False)
        font7.setStrikeOut(False)
        font7.setKerning(True)
        self.alert_status.setFont(font7)
        self.alert_status.setAutoFillBackground(False)
        self.alert_status.setFrameShape(QFrame.StyledPanel)
        self.alert_status.setFrameShadow(QFrame.Plain)
        self.alert_status.setScaledContents(False)
        self.alert_status.setAlignment(Qt.AlignCenter)
        self.alert_status.setMargin(0)
        self.bt_com_tc1 = QPushButton(Dialog)
        self.bt_com_tc1.setObjectName(u"bt_com_tc1")
        self.bt_com_tc1.setGeometry(QRect(80, 430, 71, 26))
        self.bt_com_tc2 = QPushButton(Dialog)
        self.bt_com_tc2.setObjectName(u"bt_com_tc2")
        self.bt_com_tc2.setGeometry(QRect(160, 430, 71, 26))
        self.bt_com_tc3 = QPushButton(Dialog)
        self.bt_com_tc3.setObjectName(u"bt_com_tc3")
        self.bt_com_tc3.setGeometry(QRect(80, 460, 71, 26))
        self.bt_com_tm = QPushButton(Dialog)
        self.bt_com_tm.setObjectName(u"bt_com_tm")
        self.bt_com_tm.setGeometry(QRect(160, 460, 71, 26))
        self.bt_pwr_onoff1 = QPushButton(Dialog)
        self.bt_pwr_onoff1.setObjectName(u"bt_pwr_onoff1")
        self.bt_pwr_onoff1.setGeometry(QRect(188, 78, 41, 22))
        self.bt_pwr_onoff2 = QPushButton(Dialog)
        self.bt_pwr_onoff2.setObjectName(u"bt_pwr_onoff2")
        self.bt_pwr_onoff2.setGeometry(QRect(188, 103, 41, 22))
        self.bt_pwr_onoff3 = QPushButton(Dialog)
        self.bt_pwr_onoff3.setObjectName(u"bt_pwr_onoff3")
        self.bt_pwr_onoff3.setGeometry(QRect(188, 128, 41, 22))
        self.bt_pwr_onoff4 = QPushButton(Dialog)
        self.bt_pwr_onoff4.setObjectName(u"bt_pwr_onoff4")
        self.bt_pwr_onoff4.setGeometry(QRect(188, 153, 41, 22))
        self.bt_pwr_onoff5 = QPushButton(Dialog)
        self.bt_pwr_onoff5.setObjectName(u"bt_pwr_onoff5")
        self.bt_pwr_onoff5.setGeometry(QRect(188, 178, 41, 22))
        self.bt_pwr_onoff6 = QPushButton(Dialog)
        self.bt_pwr_onoff6.setObjectName(u"bt_pwr_onoff6")
        self.bt_pwr_onoff6.setGeometry(QRect(188, 203, 41, 22))
        self.bt_pwr_onoff7 = QPushButton(Dialog)
        self.bt_pwr_onoff7.setObjectName(u"bt_pwr_onoff7")
        self.bt_pwr_onoff7.setGeometry(QRect(188, 228, 41, 22))
        self.bt_pwr_onoff8 = QPushButton(Dialog)
        self.bt_pwr_onoff8.setObjectName(u"bt_pwr_onoff8")
        self.bt_pwr_onoff8.setGeometry(QRect(188, 252, 41, 22))
        self.label_13 = QLabel(Dialog)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setGeometry(QRect(10, 370, 61, 21))
        self.label_13.setFont(font1)
        self.label_13.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_sendto = QLineEdit(Dialog)
        self.e_sendto.setObjectName(u"e_sendto")
        self.e_sendto.setGeometry(QRect(80, 370, 151, 26))
        self.e_recv = QLineEdit(Dialog)
        self.e_recv.setObjectName(u"e_recv")
        self.e_recv.setGeometry(QRect(80, 400, 151, 26))
        self.e_recv.setReadOnly(True)
        self.label_14 = QLabel(Dialog)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setGeometry(QRect(10, 400, 61, 21))
        self.label_14.setFont(font1)
        self.label_14.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.sts_updated_2 = QLabel(Dialog)
        self.sts_updated_2.setObjectName(u"sts_updated_2")
        self.sts_updated_2.setGeometry(QRect(450, 30, 191, 21))
        self.sts_updated_2.setFont(font)
        self.sts_updated_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.sts_uploading_sts = QLabel(Dialog)
        self.sts_uploading_sts.setObjectName(u"sts_uploading_sts")
        self.sts_uploading_sts.setGeometry(QRect(650, 30, 20, 20))
        self.sts_uploading_sts.setFont(font6)
        self.chk_manual_test = QCheckBox(Dialog)
        self.chk_manual_test.setObjectName(u"chk_manual_test")
        self.chk_manual_test.setGeometry(QRect(10, 340, 141, 21))
        self.chk_manual_test.setFont(font1)

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
        self.sts_interval.setText("")
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
        ___qtablewidgetitem10.setText(QCoreApplication.translate("Dialog", u"Temperature", None));
        ___qtablewidgetitem11 = self.tb_Monitor.horizontalHeaderItem(1)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("Dialog", u"Current", None));
        ___qtablewidgetitem12 = self.tb_Monitor.horizontalHeaderItem(2)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("Dialog", u"Set Point", None));
        ___qtablewidgetitem13 = self.tb_Monitor.horizontalHeaderItem(3)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("Dialog", u"Heat Power", None));

        __sortingEnabled1 = self.tb_Monitor.isSortingEnabled()
        self.tb_Monitor.setSortingEnabled(False)
        self.tb_Monitor.setSortingEnabled(__sortingEnabled1)

        self.sts_monitor4.setText(QCoreApplication.translate("Dialog", u"\u26ab", None))
        self.chk_alert.setText("")
        self.sts_monitor_ok.setText(QCoreApplication.translate("Dialog", u"\u26ab", None))
        self.sts_monitor6.setText(QCoreApplication.translate("Dialog", u"\u26ab", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Monitor", None))
        self.alert_status.setText("")
        self.bt_com_tc1.setText(QCoreApplication.translate("Dialog", u"TMC1", None))
        self.bt_com_tc2.setText(QCoreApplication.translate("Dialog", u"TMC2", None))
        self.bt_com_tc3.setText(QCoreApplication.translate("Dialog", u"TMC3", None))
        self.bt_com_tm.setText(QCoreApplication.translate("Dialog", u"TM", None))
        self.bt_pwr_onoff1.setText(QCoreApplication.translate("Dialog", u"On", None))
        self.bt_pwr_onoff2.setText(QCoreApplication.translate("Dialog", u"On", None))
        self.bt_pwr_onoff3.setText(QCoreApplication.translate("Dialog", u"On", None))
        self.bt_pwr_onoff4.setText(QCoreApplication.translate("Dialog", u"On", None))
        self.bt_pwr_onoff5.setText(QCoreApplication.translate("Dialog", u"On", None))
        self.bt_pwr_onoff6.setText(QCoreApplication.translate("Dialog", u"On", None))
        self.bt_pwr_onoff7.setText(QCoreApplication.translate("Dialog", u"On", None))
        self.bt_pwr_onoff8.setText(QCoreApplication.translate("Dialog", u"On", None))
        self.label_13.setText(QCoreApplication.translate("Dialog", u"Send:", None))
        self.e_sendto.setText(QCoreApplication.translate("Dialog", u"command", None))
        self.e_recv.setText("")
        self.label_14.setText(QCoreApplication.translate("Dialog", u"Receive:", None))
        self.sts_updated_2.setText(QCoreApplication.translate("Dialog", u"WebApp Uploading Status", None))
        self.sts_uploading_sts.setText(QCoreApplication.translate("Dialog", u"\u26ab", None))
        self.chk_manual_test.setText(QCoreApplication.translate("Dialog", u"Manual Test", None))
    # retranslateUi

