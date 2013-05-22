#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore

class CalibratorApp(QtGui.QWidget):

    def __init__(self):
        super(CalibratorApp, self).__init__()
        self.position = QtCore.QPoint(0 , 0)
        self.setWindowTitle('Calibrator')
        self.setMouseTracking(True)
        self.points = []
        self.painter = QtGui.QPainter()
        self.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
        self.show()

    def paintEvent(self, event):
        qp = self.painter
        qp.begin(self)
        qp.fillRect(self.rect(), QtGui.QColor(0,0,0))
        qp.setPen(QtGui.QColor(168, 34, 3))
        qp.setFont(QtGui.QFont('Decorative', 12))
        mouse_x = self.position.x()
        mouse_y = self.position.y()

        for punto in self.points:
            self.dibujar_punto(punto.x(), punto.y())
        x_max = event.rect().width()
        y_max = event.rect().height()
        qp.drawLine(0, mouse_y, x_max, mouse_y  )
        qp.drawLine(mouse_x, 0, mouse_x, y_max)
        qp.drawRect(mouse_x - 5, mouse_y - 5, 10, 10)
        qp.end()

    def dibujar_punto(self, x, y):
        qp = self.painter
        qp.drawLine(x - 5, y - 5, x + 5, y + 5)
        qp.drawLine(x - 5, y + 5, x + 5, y - 5)
        qp.drawText(QtCore.QPoint(x, y), "(%d, %d)" % (x, y ))

    def mouseMoveEvent(self, event):
        self.position = event.pos()
        self.update()

    def mousePressEvent(self, event):
        if event.button() == 1:
            self.points.append(event.pos())
        self.update()


    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.close()
        elif event.key() == QtCore.Qt.Key_F:
            self.toggle_fullscreen() #toggle fullscreen
        elif event.key() == QtCore.Qt.Key_Up:
            self.position += QtCore.QPoint(0, -1)
        elif event.key() == QtCore.Qt.Key_Down:
            self.position += QtCore.QPoint(0, 1)
        elif event.key() == QtCore.Qt.Key_Left:
            self.position += QtCore.QPoint(-1, 0)
        elif event.key() == QtCore.Qt.Key_Right:
            self.position += QtCore.QPoint(1, 0)
        elif event.key() == QtCore.Qt.Key_Return:
            self.points.append(QtCore.QPoint(self.position))

        self.update()


    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

def main():

    app = QtGui.QApplication(sys.argv)
    widget = CalibratorApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

