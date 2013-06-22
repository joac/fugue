#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import cv2
import numpy

from PyQt4 import QtGui, QtCore

JOINTS = [
    (0, 1), (1, 2), (2, 3),
    (3, 0), (3, 4), (4, 5),
    (5, 0), (4, 6), (6, 2),
    ]


class Notify(QtCore.QObject):

    newPoint = QtCore.pyqtSignal()
    undo = QtCore.pyqtSignal()

class ReferenceWidget(QtGui.QDialog):

    def __init__(self, parent):
        super(ReferenceWidget, self).__init__(parent, QtCore.Qt.Dialog)
        self.painter = QtGui.QPainter()
        self.setWindowTitle('Reference')
        self.calibration_points = [
                (0, 3), (4, 0), (8, 3),
                (4, 6), (4, 11), (0, 8),
                (8, 8)
                ]
        n = 20
        border = 20
        self.calibration_points = [QtCore.QPoint(x * n + border , y * n + border) for x, y in self.calibration_points]
        self.current_point = 0
        self.show()

    def paintEvent(self, event):
        qp = self.painter
        pen = QtGui.QPen(QtGui.QColor(47, 138, 131))
        pen.setWidth(3)
        qp.begin(self)
        qp.fillRect(self.rect(), QtGui.QColor(0,0,0))
        # Dimensions
        qp.setPen(pen)
        for first, second in JOINTS:
            #Draw poligon using pitagoric triangles
            qp.drawLine(self.calibration_points[first], self.calibration_points[second])
        for n, point in enumerate(self.calibration_points):
            qp.save()
            if n == self.current_point:
                qp.setBrush(QtCore.Qt.darkRed)
            else:
                qp.setBrush(QtCore.Qt.black)

            qp.drawEllipse(point, 10, 10)
            qp.restore()
        qp.end()

    def update_point(self):
        self.current_point += 1
        self.update()

    def undo(self):
        self.current_point -= 1
        self.update()


class CalibratorDialog(QtGui.QDialog):

    def __init__(self, model, parent):
        super(CalibratorDialog, self).__init__(parent, QtCore.Qt.Dialog)
        self.position = QtCore.QPoint(0 , 0)
        self.setWindowTitle('Calibrator - %s' % model)
        self.points = []
        self.painter = QtGui.QPainter()
        self.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
        self.sight = QtGui.QPixmap('data/mira.png')
        self.sight.dh = self.sight.height() / 2
        self.sight.dw = self.sight.width() / 2
        self.sight.offset = QtCore.QPoint(self.sight.dw, self.sight.dh)
        self.show()
        self.setMouseTracking(True)
        self.n = Notify()

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

        if self.all_points_aquired():
            qp.save()
            qp.setBrush(QtCore.Qt.white)
            for first, second in JOINTS:
                qp.drawLine(self.points[first], self.points[second])
            qp.restore()

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


    def mouseMoveEvent(self, event):
        self.position = event.pos()
        self.update()


    def mousePressEvent(self, event):
        if event.button() == 1:
            self.add_point(QtCore.QPoint(self.position))
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
        elif event.key() == QtCore.Qt.Key_Space:
            self.add_point(QtCore.QPoint(self.position))
        elif event.key() == QtCore.Qt.Key_Z:
            self.undo()
        self.update()

    def all_points_aquired(self):
        return len(self.points) == 7 # FIXME On real calibration scenario, this number is bigger

    def add_point(self, point):
        if not self.all_points_aquired():
            self.points.append(point)
            self.n.newPoint.emit()

        if self.all_points_aquired():
            self.calibrate()


    def undo(self):
        if self.points:
            self.points = self.points[:-1]
            self.n.undo.emit()


    def toggle_fullscreen(self):
        """Toggles Application Fullscreen"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def calibrate(self):
        """Calculates a camera using cv2
            Coordinates of object are in pattern cordinate system
            In current model of 2x2 points, cube side are equals
            cordinates are in the form:
            C1 --- C3
            |      |
            |      |
            C2 --- C4

        """
        views = [
                [1, 0, 2, 3],
                [3, 4, 2, 6],
                [0, 5, 3, 4],
                ]
        object_points = [
                [[0,0,0], [0, 20,0], [20, 0, 0], [20, 20, 0]],
                [[0,0,0], [0, 20,0], [20, 0, 0], [20, 20, 0]],
                [[0,0,0], [0, 20,0], [20, 0, 0], [20, 20, 0]],
                ]

        object_points = numpy.array(object_points, 'float32')
        image_point_list = []
        for view in views:
            view_list = []
            for point in view:
                point = self.points[point]
                view_list.append([point.x(), point.y()])
            image_point_list.append(view_list)

        image_points = numpy.array(image_point_list, 'float32')

        retval, camera_matrix, dist_coeff, _, _ = cv2.calibrateCamera(
                object_points, image_points, (640, 480)
                )



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
        screen_geometry = self.desktop_widget.screenGeometry(target_screen)
        print target_screen, target_name
        text, ok = QtGui.QInputDialog.getText(self, 'Projector Name', 'Enter projector model:')
        if ok:
            #FIXME Save calibration data of Projector
            self.reference = ReferenceWidget(self)
            self.calibrator = CalibratorDialog(text, self)
            self.calibrator.move(screen_geometry.top(), screen_geometry.left())
            self.calibrator.toggle_fullscreen()
            # Conectar señal a ventana de actualizacion
            self.calibrator.n.newPoint.connect(self.reference.update_point)
            self.calibrator.n.undo.connect(self.reference.undo)

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

