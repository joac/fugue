#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import cv2

from PyQt4 import QtGui, QtCore

class CalibratorApp(QtGui.QWidget):

    def __init__(self, model):
        super(CalibratorApp, self).__init__()
        self.position = QtCore.QPoint(0 , 0)
        self.setWindowTitle('Calibrator - %s' % model)
        self.setMouseTracking(True)
        self.points = []
        self.painter = QtGui.QPainter()
        self.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
        self.sight = QtGui.QPixmap('data/mira.png')
        self.sight.dh = self.sight.height() / 2
        self.sight.dw = self.sight.width() / 2
        self.sight.offset = QtCore.QPoint(self.sight.dw, self.sight.dh)
        self.show()

    def paintEvent(self, event):
        qp = self.painter
        pen = QtGui.QPen(QtGui.QColor(47, 138, 131))
        pen.setWidth(3)
        qp.begin(self)
        qp.fillRect(self.rect(), QtGui.QColor(0,0,0))
        qp.setPen(pen)
        qp.setFont(QtGui.QFont('Decorative', 12))
        mouse_x = self.position.x()
        mouse_y = self.position.y()

        for punto in self.points:
            self.dibujar_punto(punto.x(), punto.y())
        x_max = event.rect().width()
        y_max = event.rect().height()

        qp.drawPixmap(self.position - self.sight.offset, self.sight)
        qp.drawLine(0, mouse_y, mouse_x - self.sight.dw, mouse_y  )
        qp.drawLine(mouse_x + self.sight.dw, mouse_y, x_max, mouse_y)
        qp.drawLine(mouse_x, 0, mouse_x, mouse_y - self.sight.dh)
        qp.drawLine(mouse_x, mouse_y + self.sight.dh, mouse_x, y_max)

        qp.end()

    def dibujar_punto(self, x, y):
        qp = self.painter
        qp.drawLine(x - 5, y - 5, x + 5, y + 5)
        qp.drawLine(x - 5, y + 5, x + 5, y - 5)
        qp.drawText(QtCore.QPoint(x, y), "(%d, %d)" % (x, y ))
        #self.emit(QtCore.SIGNAL('my_signal()'), )

        #Emito señal

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
        """Toggles Application Fullscreen"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def calculater_camera(self):
        """Calculates a camera using cv2"""
        print cv2.calibrateCamera()


class PanelWidget(QtGui.QWidget):

    def __init__(self):
        super(PanelWidget, self).__init__()
        self.buildUI()

    def buildUI(self):
        v_layout = QtGui.QVBoxLayout()

        self.desktop_widget = QtGui.QDesktopWidget()
        self.desktop_widget.screenCountChanged.connect(self.obtain_screens)
        # Main window shows:
        # List of screens, to choose calibration target
        # Button "Calibrate intrinsec parameters"
        # List of calibrated devices
        # Button "Calculate projector position"

        self.screen_list = QtGui.QComboBox()
        self.obtain_screens()

        self.calibrate_button = QtGui.QPushButton('Calibrate Projector')
        self.calibrated_list = QtGui.QComboBox()
        self.calculate_button = QtGui.QPushButton('Calculate Position')
        v_layout.addWidget(self.screen_list)
        v_layout.addWidget(self.calibrate_button)
        v_layout.addWidget(self.calibrated_list)
        v_layout.addWidget(self.calculate_button)

        self.calibrate_button.clicked.connect(self.calibrate)
        self.setLayout(v_layout)
        self.show()

    def calibrate(self):
        target_screen =  self.screen_list.currentIndex()
        target_name =  self.screen_list.itemText(target_screen)
        print target_screen, target_name
        text, ok = QtGui.QInputDialog.getText(self, 'Projector Name', 'Enter projector model:')
        if ok:
            #FIXME Save calibration data of Projector

            self.calibrator = CalibratorApp(text)
            # Conectar señal a ventana de actualizacion
           # self.calibrator.signal.connect(self.view)

    def obtain_screens(self):
        self.screen_list.clear()
        for i in xrange(0, self.desktop_widget.screenCount()):
            geometry = self.desktop_widget.screenGeometry(i)
            label = u'Screen %d - %dx%d' % (i, geometry.width(), geometry.height())
            self.screen_list.addItem(label)




class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.buildUI()

    def buildUI(self):
        exit_action = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit Aplication')
        exit_action.triggered.connect(QtGui.qApp.quit)

        load_projector_action =  QtGui.QAction(QtGui.QIcon('open.png'), '&Load Projector', self)

        load_projector_action.setShortcut('Ctrl+L')
        load_projector_action.setStatusTip('Load intrinsec calibration data for projector')
        load_projector_action.triggered.connect(self.load_projector)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(load_projector_action)
        file_menu.addAction(exit_action)
        self.panel = PanelWidget()
        self.setCentralWidget(self.panel)

        self.setWindowTitle('Fugue - Calibration')
        self.statusBar().showMessage('Ready')
        self.show()

    def load_projector(self):
        print "It works"


def main():

    app = QtGui.QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

