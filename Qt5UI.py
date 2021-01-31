"""
Nostear-setto
v1.2.0

https://github.com/Gleiphir
All rights reserved

distributed under MIT license

It's a free software, do NOT pay for this.
此为自由软件，请不要为此付费。
これはフリーソフトであるので無料です。

"""

about_text = """ \
v0.1.0\n
https://github.com/Gleiphir\n
All rights reserved\n
\n
distributed under MIT license\n
\n
It's a free software, do NOT pay for this.\n
此为自由软件，请不要为此付费。\n
\n
辛苦了，各位同传\n
时代变了，这也许能帮上忙
"""


import time
from core.constants import config as conf

from PyQt5.QtWidgets import QApplication, \
    QWidget, QMainWindow, QMessageBox, \
    QFileDialog, QPushButton, QLabel, \
    QGridLayout, QLineEdit, QFrame, \
    QTextEdit
from PyQt5 import QtGui
from PyQt5.QtGui import QFont
from PyQt5 import QtCore
from PyQt5.Qt import Qt,QTimer
import os
import sys
from utils import toFixedLns,popLns

from PyQt5.QtCore import Qt, pyqtSignal,pyqtSlot

import dictRead

#breakpoint()
font_size = conf['Intval','fontsize']


def HTMLify(text:str)-> str:
    return text.replace('\n','<br />')

class Alt_textArea(QTextEdit):
    PickDict = pyqtSignal(str)

    def __init__(self,parent):
        super(Alt_textArea, self).__init__(parent=parent)


    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        #print(a0.text())
        modifiers = QApplication.keyboardModifiers()
        alt = False
        if not modifiers & QtCore.Qt.AltModifier:
            QTextEdit.keyPressEvent(self,a0)
            return
        else:
            a0.ignore()
            print("Alt-",end='')
            print(a0.text())
            self.PickDict.emit(a0.text().lower())


placeholderSpaces = "\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000"


class mainWindow (QMainWindow):
    def __init__(self):
        super().__init__()

        self.D = None
        self.candidateFrm = QFrame(self)
        self.candidateGrid = QGridLayout()
        self.candidateList = []


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
        self.lockTimer = QTimer(self)
        self.lockTimer.setSingleShot(True)
        self.lockTimer.setInterval(1000)
        self.lockTimer.timeout.connect(self.unlockwheel)


        self.UsingDictFile = QLabel(self)
        self.UsingDictFile.setText("meanings:")

        self.Textarea = Alt_textArea(self)
        self.Textarea.textChanged.connect(self.highlightText)
        self.Textarea.PickDict.connect(self.setCandidates)
        """
        font = self.Textarea.document().defaultFont()  # or another font if you change it
        fontMetrics = QtGui.QFontMetrics(font)  # a QFontMetrics based on our font
        textSize = fontMetrics.size(0, "这是一个十八个字长的汉字构成的字符串")
        self.Textarea.setFixedWidth(textSize.width())
        """

        self.placeholder = QLabel(self)
        self.placeholder.setText(placeholderSpaces)

        self.MeaningList = QLabel(self)
        #self.LRTOut.setMaximumWidth(self.maxLineWidth)
        #self.LRTOut.setWordWrap(True)

        self.LHintFile = QLabel(self)
        self.LHintFile.setText(conf['Text', 'hintFile'])

        self.LFileName = QLabel(self)

        self.markBtn = QPushButton(conf['Text','Bmark'], self)


        self.browseBtn = QPushButton(conf['Text','Bbrowse'], self)
        self.browseBtn.clicked.connect(self.browse)

        self.genFileBtn = QPushButton(conf['Text','Bgenerate'], self)



        self.aboutBtn = QPushButton(conf['Text','Babout'], self)
        self.aboutBtn.clicked.connect(self.about)


        self.QuitBtn = QPushButton(conf['Text','Bquit'], self)
        self.QuitBtn.clicked.connect(self.close)

        self.Cwidget = QFrame(self)

        self.initUI()

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

        grid.addWidget(self.UsingDictFile, 0, 0)
        grid.addWidget(self.Textarea, 1, 0)
        #grid.addWidget(self.markBtn, 1, 1)
        grid.addWidget(self.MeaningList, 2, 0)

        grid.addWidget(self.candidateFrm, 4, 0)
        self.candidateFrm.setLayout(self.candidateGrid)
        #grid.addWidget(self.LHintFile, 4, 0)
        #grid.addWidget(self.genFileBtn, 4, 1)

        grid.addWidget(self.LFileName, 0, 0)
        grid.addWidget(self.browseBtn, 0, 1)

        grid.addWidget(self.placeholder, 7, 0)


        grid.addWidget(self.aboutBtn, 6, 1)
        grid.addWidget(self.QuitBtn, 7, 1)

        self.setLayout(grid)
        self.setGeometry(300, 300, 350, 300)
        #print(conf['customFile','stylish'])
        #self.setStyleSheet('QPushButton{color:red;}')
        self.setStyleSheet(conf['customFile','stylish'])

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
        _s = self.Textarea.toPlainText()
        _r = toFixedLns(_s)
        self.Textarea.setText(_r)
        self.Textarea.setTextCursor(_cur)
        self.Textarea.blockSignals(False)

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
        L,S = popLns(self.Textarea.toPlainText())
        self.clpb.setText(L)
        self.Textarea.setPlainText(S)

    def setCandidates(self,key):
        if not self.D:
            self.UsingDictFile.setText("请选择字典文件")
            return
        words = self.D.ListKey(key)# dict {word: [meaning1 , meaning2, ]}
        self.clearCandidates()
        for word in words: # word
            self.candidateGrid.addWidget(self.makeBtn(word))



    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        #print(a0.angleDelta().y())
        if self.wheelLock:
            return
        else:
            self.popLine()
            self.wheelLock = True
            self.lockTimer.start()

    def unlockwheel(self):
        self.wheelLock = False


    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        pass#print(a0.angleDelta().y())

    def about(self):
        QMessageBox.about(self, 'about', '<p align=\"center\">'+ HTMLify(about_text) + "</p>")

    def browse(self):

        self.file_path,filetype= QFileDialog.getOpenFileName(self,"Source File")
        #if filetype
        self.D = dictRead.Dict(fileName=self.file_path)
        hint = os.path.basename(self.file_path) +" - " + self.D.author()
        self.LFileName.setText(hint)
        self.Textarea.PickDict.connect(self.D.ListKey)
        #SV_file_path.set("source: [  " + file_path + "  ]")








if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainW = mainWindow()
    mainW.show()
    sys.exit(app.exec_())
