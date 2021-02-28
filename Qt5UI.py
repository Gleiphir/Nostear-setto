r"""
Nostear-setto
v1.2.0

https://github.com/Gleiphir
All rights reserved

distributed under MIT license

It's a free software, do NOT pay for this.
此为自由软件，请不要为此付费。

pyinstaller --noconfirm --onedir --windowed --name "Nostear-setto-1.2.0" --clean --add-data "D:/Github/Nostear-setto/settings;settings/" --add-data "D:/Github/Nostear-setto/resources;resources/" --upx-dir "D:\upx-3.96-win64"  "D:/Github/Nostear-setto/Qt5UI.py"


"""

about_text = """ \
v2.1.0\n
https://github.com/Gleiphir\n
All rights reserved\n
\n
It's a free software, do NOT pay for this.\n
此为自由软件，请不要为此付费。\n
\n
辛苦了，各位同传\n
时代变了，这也许能帮上忙
"""

import math
import time
from core.constants import config as conf
from PyQt5.QtWidgets import QApplication, \
    QWidget, QMainWindow, QMessageBox, \
    QFileDialog, QPushButton, QLabel, \
    QGridLayout, QLineEdit, QFrame, \
    QTextEdit,QProgressBar,QSizePolicy

from PyQt5.QtGui import QFont,QKeyEvent,QWheelEvent,QMouseEvent
from PyQt5.QtGui import QTextOption,QTextCursor,QRegExpValidator

from PyQt5.QtGui import QPainter,QColor,QPen,QBrush
from PyQt5.Qt import QTimer,QRect,QRegExp
import os
import sys

import utils

from PyQt5.QtCore import Qt, pyqtSignal,pyqtSlot

import dictRead

from network.req import DanmuHandler

#breakpoint()
font_size = conf['Intval','fontsize']


def HTMLify(text:str)-> str:
    return text.replace('\n','<br />')


class Toggle(QPushButton):
    def __init__(self, parent = None,text_true = "ON",text_false="OFF",border_color=Qt.black,text_color=Qt.white,background_color=Qt.darkGray):
        super().__init__(parent)
        self.text_true = text_true
        self.text_false = text_false
        self.border_color = border_color
        self.background_color = background_color
        self.text_color = text_color

        #print('init')
        self.setCheckable(True)
        self.setMinimumWidth(66)
        self.setMinimumHeight(22)

    def paintEvent(self, event):
        label = self.text_true if self.isChecked() else self.text_false
        bg_color = Qt.darkGreen if self.isChecked() else Qt.red

        radius = 10
        width = 32
        center = self.rect().center()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(center)
        painter.setBrush(QColor(0,0,0))

        pen = QPen(Qt.black)
        pen.setWidth(2)
        painter.setPen(pen)

        painter.drawRoundedRect(QRect(-width, -radius, 2*width, 2*radius), radius, radius)
        painter.setBrush(QBrush(bg_color))
        sw_rect = QRect(-radius, -radius, width + radius, 2*radius)
        if not self.isChecked():
            sw_rect.moveLeft(-width)
        painter.drawRoundedRect(sw_rect, radius, radius)
        painter.setPen(QPen(self.text_color))
        font = painter.font()
        font.setPixelSize(math.ceil(1.8*radius))
        painter.setFont(font)

        painter.drawText(sw_rect, Qt.AlignCenter, label)



class Alt_textArea(QTextEdit):
    PickDict = pyqtSignal(str)

    def __init__(self,parent):
        super(Alt_textArea, self).__init__(parent=parent)


    def keyPressEvent(self, a0: QKeyEvent) -> None:
        #print(a0.text())
        modifiers = QApplication.keyboardModifiers()
        alt = False
        if not modifiers & Qt.AltModifier:
            QTextEdit.keyPressEvent(self,a0)
            return
        else:
            a0.ignore()
            print("Alt-",end='')
            print(a0.text())
            if a0.key() == Qt.Key_Return or a0.key() == Qt.Key_Enter:
                print("ENter")
            else:
                self.PickDict.emit(a0.text().lower())


placeholderSpaces = "\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000"


class mainWindow (QMainWindow):
    def __init__(self):
        super().__init__()

        self.D = None
        self.candidateFrm = QFrame(self)
        self.candidateGrid = QGridLayout()
        self.candidateList = []

        self.prefix = "["
        self.suffix = "]"
        self.TEXTWIDTH = 18

        self.clpb = QApplication.clipboard()

        self.options = []

        self.setFont(QFont('microsoft Yahei',font_size))
        self.setWindowTitle(conf['Text','windowtitle'])

        self.file_path = ''
        #self.maxLineWidthpx = QApplication.desktop().availableGeometry().width() // 2
        #self.maxLineWidth = self.maxLineWidthpx // (font_size * 4 //3)
        # 1px = 0.75point

        self.maxLineWidth = conf['Intval','LineWidth'] # in char

        self.wheelLock = False
        self.ticker = 0
        self.lockTimer = QTimer(self)
        self.lockTimer.setSingleShot(False)
        self.lockTimer.setInterval(800)
        self.lockTimer.timeout.connect(self.unlockwheel)

        self.RoomIDinput = QLineEdit(self)
        numbers = QRegExpValidator(QRegExp("[0-9]{0,13}$"))

        self.RoomIDinput.setValidator(numbers)

        self.userWarnLabel = QLabel(self)

        self.Xffix = QLineEdit(self)
        self.Xffix.setPlaceholderText("前缀~后缀")

        self.UsingDictFile = QLabel(self)
        self.UsingDictFile.setText("meanings:")

        self.Textarea = Alt_textArea(self)
        self.Textarea.textChanged.connect(self.highlightText)
        self.Textarea.PickDict.connect(self.setCandidates)
        self.Textarea.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
        """
        font = self.Textarea.document().defaultFont()  # or another font if you change it
        fontMetrics = QtGui.QFontMetrics(font)  # a QFontMetrics based on our font
        textSize = fontMetrics.size(0, "这是一个十八个字长的汉字构成的字符串")
        self.Textarea.setFixedWidth(textSize.width())
        """

        self.placeholder = QLabel(self)
        self.placeholder.setText(placeholderSpaces)

        self.placeholderL = QLabel(self)
        self.placeholderL.setText(placeholderSpaces[:12])

        self.cookieText = QTextEdit(self)
        self.cookieText.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)

        self.MeaningList = QLabel(self)
        self.MeaningList.setTextInteractionFlags(Qt.TextSelectableByMouse)
        #self.LRTOut.setMaximumWidth(self.maxLineWidth)
        #self.LRTOut.setWordWrap(True)

        self.LHintFile = QLabel(self)
        self.LHintFile.setText(conf['Text', 'hintFile'])

        self.LFileName = QLabel(self)

        self.markBtn = QPushButton(conf['Text','Bmark'], self)
        self.coolDown = QProgressBar(self)

        self.browseBtn = QPushButton(conf['Text','Bbrowse'], self)
        self.browseBtn.clicked.connect(self.browse)

        self.sendBtn = QPushButton("发射！",self)
        self.sendBtn.clicked.connect(self.sendLine)

        self.genFileBtn = QPushButton(conf['Text','Bgenerate'], self)

        self.settingLock = Toggle(self, text_false="", text_true="")
        self.settingLock.clicked.connect(self.settingStatusCheck)

        self.alwaysOnTop = Toggle(self)
        self.alwaysOnTop.clicked.connect(self.windowRefresh)

        self.aboutBtn = QPushButton(conf['Text','Babout'], self)
        self.aboutBtn.clicked.connect(self.about)


        self.QuitBtn = QPushButton(conf['Text','Bquit'], self)
        self.QuitBtn.clicked.connect(self.close)

        self.Cwidget = QFrame(self)

        self.initUI()
        self.lockTimer.start()
        self.wflags = self.windowFlags()
        self.alwaysOnTopFlag = False

        self.reqHandler = DanmuHandler(0) #invalid

    def initUI(self):
        for key in self.__dict__:
            if isinstance(self.__dict__[key],QWidget):
                self.__dict__[key].setObjectName(key)
                #print(key)


        self.setCentralWidget(self.Cwidget)

        grid = QGridLayout()
        grid.setSpacing(5)
        self.Cwidget.setLayout(grid)

        self.candidateGrid.setSpacing(5)


        grid.addWidget(QLabel("锁定房间",self), 0, 0)
        grid.addWidget(self.settingLock, 0, 0)
        grid.addWidget(self.placeholderL, 7, 0)
        grid.addWidget(self.cookieText, 1, 0)
        grid.addWidget(self.RoomIDinput, 2, 0)

        grid.addWidget(self.Xffix, 3, 0)
        grid.addWidget(self.userWarnLabel, 5, 0)
        grid.addWidget(QLabel("总在最前", self), 6, 0)
        grid.addWidget(self.alwaysOnTop, 6, 0)

        grid.addWidget(self.UsingDictFile, 0, 1)
        grid.addWidget(self.Textarea, 1, 1)
        grid.addWidget(self.sendBtn, 1, 2)

        grid.addWidget(self.MeaningList, 2, 1)

        grid.addWidget(self.candidateFrm, 4, 1)
        self.candidateFrm.setLayout(self.candidateGrid)
        #grid.addWidget(self.LHintFile, 4, 0)
        #grid.addWidget(self.genFileBtn, 4, 1)

        grid.addWidget(self.LFileName, 0, 1)
        grid.addWidget(self.browseBtn, 0, 2)

        grid.addWidget(self.placeholder, 7, 1)


        grid.addWidget(self.aboutBtn, 6, 2)
        grid.addWidget(self.QuitBtn, 7, 2)

        self.setLayout(grid)
        self.setGeometry(300, 300, 350, 300)
        #print(conf['customFile','stylish'])
        #self.setStyleSheet('QPushButton{color:red;}')
        self.setStyleSheet(conf['customFile','stylish'])
        self.Textarea.setWordWrapMode(QTextOption.NoWrap)
        self.Textarea.textCursor().setKeepPositionOnInsert(False)

    def settingStatusCheck(self):
        settingLock = self.settingLock.isChecked()
        ###

        self.cookieText.setDisabled(settingLock)
        self.RoomIDinput.setDisabled(settingLock)
        if settingLock:
            try:
                self.reqHandler.setCookie(self.cookieText.toPlainText())
            except KeyError as e:
                self.userWarning("Cookie不合法")
                return

            if len(self.RoomIDinput.text()) < 1:
                self.userWarning("直播间未定义")
                return
            self.reqHandler.setRoom(int(self.RoomIDinput.text()))
            print(self.reqHandler.roomID)

            ###############
            if not self.reqHandler.touch():
                self.userWarning("无法连接到直播间")
                return

            xffix = self.Xffix.text()
            if len(xffix) > 0:
                self.alt_Xffix(xffix)

            self.userWarning("")#safe

    def alt_Xffix(self,s: str):
        if len(s) >= 19:
            self.userWarning("前后缀太长")
            return
        if "~" not in s:
            self.userWarning("前后缀不合法，请使用~分割前后缀")
            return
        l = s.split("~")

        self.prefix = l[-2]
        self.suffix = l[-1]
        self.TEXTWIDTH = 20 - len(self.prefix) - len(self.suffix)


    def userWarning(self,warning:str):
        self.userWarnLabel.setText(warning)

    def UIrefresh(self):
        self.ticker =( self.ticker+1 ) % 50
        ###


        if self.ticker >= 49:
            self.unlockwheel()

    def windowRefresh(self):
        if self.alwaysOnTop.isChecked() and self.alwaysOnTopFlag==False :
            self.setWindowFlags(
                self.wflags | Qt.WindowStaysOnTopHint
            )
            self.show()
            self.alwaysOnTopFlag = True
            return

        elif self.alwaysOnTop.isChecked()==False and self.alwaysOnTopFlag:
            self.setWindowFlags(
                self.wflags
            )
            self.show()
            self.alwaysOnTopFlag = False
            return

    def cpText(self):
        pass

    def clearCandidates(self):
        while self.candidateGrid.count():
            child = self.candidateGrid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def highlightText(self):
        self.Textarea.blockSignals(True)
        _cur = self.Textarea.textCursor()
        _curpos = _cur.position()
        _s = self.Textarea.toPlainText()
        _r = utils.toFixedLns(_s,self.TEXTWIDTH)
        self.Textarea.setText(_r)
        _newcur = QTextCursor(self.Textarea.document())
        _newcur.setPosition(_curpos)
        self.Textarea.setTextCursor(_newcur)
        """
        print(_curpos)
        self.Textarea.textCursor().setPosition(_curpos)
        print(self.Textarea.textCursor().position())
        """
        self.Textarea.blockSignals(False)
        #print(self.Textarea.textCursor().position())


    @pyqtSlot(str)
    def pickWord(self,word):
        m = self.D.Meaning4name(word)
        _m = m[0] #assume len(m) > 0
        self.Textarea.textCursor().insertText(_m)
        self.MeaningList.setText(word + " : " + " ".join(m))


    def makeBtn(self,word):
        B = QPushButton(self.candidateFrm)
        B.setText(word)
        B.setFont(QFont('Courier New', 15))
        B.clicked.connect(lambda : self.pickWord(word))
        return B

    def popLine(self):
        L,S = utils.popLns(self.Textarea.toPlainText(),self.prefix,self.suffix)
        self.clpb.setText(L)
        self.Textarea.setPlainText(S)

    def setCandidates(self,key):
        if not self.D:
            print("D not specified")
            self.LFileName.setText("请选择字典文件")
            return
        words = self.D.ListKey(key)# dict {word: [meaning1 , meaning2, ]}
        self.clearCandidates()
        for word in words: # word
            self.candidateGrid.addWidget(self.makeBtn(word))

    def sendLine(self):
        L, S = utils.popLns(self.Textarea.toPlainText(),self.prefix,self.suffix)
        self.send_cmt(L)
        self.Textarea.setPlainText(S)

    def send_cmt(self,cmt:str):
        self.reqHandler.make_req(cmt)

    def wheelEvent(self, a0: QWheelEvent) -> None:
        #print(a0.angleDelta().y())
        if self.wheelLock:
            return
        else:
            self.popLine()
            self.wheelLock = True
            self.lockTimer.start()

    def unlockwheel(self):
        self.wheelLock = False


    def mousePressEvent(self, a0: QMouseEvent) -> None:
        pass#print(a0.angleDelta().y())

    def about(self):
        QMessageBox.about(self, 'about', '<p align=\"center\">'+ HTMLify(about_text) + "</p>")

    def browse(self):

        self.file_path,filetype= QFileDialog.getOpenFileName(self,"Source File")
        #if filetype
        self.D = dictRead.Dict(fileName=self.file_path)
        hint = os.path.basename(self.file_path) +" - " + self.D.getAuthor() + " - " + self.D.getTime()
        self.LFileName.setText(hint)
        #self.Textarea.PickDict.disconnect()
        self.Textarea.PickDict.connect(self.D.ListKey)
        #SV_file_path.set("source: [  " + file_path + "  ]")








if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainW = mainWindow()
    mainW.show()
    sys.exit(app.exec_())
