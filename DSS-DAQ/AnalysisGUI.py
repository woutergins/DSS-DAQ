import DSSDAQ
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

class AnalysisGUI(object):
    def __init__(self):
        super(AnalysisGUI, self).__init__()

        self.app = QtGui.QApplication([])
        self.mainWin = QtGui.QMainWindow()

        # Fitting group
        self.fittingGroup = QtGui.QGroupBox("Fitting")
        fittingLayout = QtGui.QGridLayout()

        self.addPeak = QtGui.QPushButton("Add Peak to fitting")
        self.removePeaks = QtGui.QPushButton("Remove all peaks from settings")
        self.fitPeaks = QtGui.QPushButton("Fit the peaks")
        self.results = QtGui.QLabel("Results will be displayed here somehow")

        fittingLayout.addWidget(self.addPeak, 0, 0)
        fittingLayout.addWidget(self.removePeaks, 0, 1)
        fittingLayout.addWidget(self.fitPeaks, 1, 0, 1, 2)
        fittingLayout.addWidget(self.results, 2, 0, 1, 2)

        self.fittingGroup.setLayout(fittingLayout)

        # Plotting group
        self.plottingGroup = QtGui.QGroupBox("Plotting")
        plottingLayout = QtGui.QVBoxLayout()
        self.plot = pg.PlotWidget()
        self.plot.setTitle("")
        self.plot.setLabel('left', 'Counts')
        self.plot.setLabel('bottom', 'Channel/Energy')
        self.spectrumCurve = self.plot.plot([0], [0], pen='k', fillevel=0.0, brush=(100, 100, 200, 100))
        self.plot.showGrid(x=True, y=True)
        plottingLayout.addWidget(self.plot)
        self.plottingGroup.setLayout(plottingLayout)

        # File selection and cutting group
        self.selectionGroup = QtGui.QGroupBox("Selection of data")
        selectionLayout = QtGui.QGridLayout()

        self.selectFile = QtGui.QLabel("Select file:")
        self.selectedFile = pg.ComboBox()
        self.loadFile = QtGui.QPushButton("Load file")

        selectionLayout.addWidget(self.selectFile, 0, 0)
        selectionLayout.addWidget(self.selectedFile, 0, 1)
        selectionLayout.addWidget(self.loadFile, 0, 2)
        self.selectionGroup.setLayout(selectionLayout)

        mainLayout = QtGui.QGridLayout()
        mainLayout.addWidget(self.fittingGroup, 0, 0)
        mainLayout.addWidget(self.plottingGroup, 0, 1)
        mainLayout.addWidget(self.selectionGroup, 1, 0, 1, 2)

        mainWidget = QtGui.QWidget()
        mainWidget.setLayout(mainLayout)
        self.mainWin.setCentralWidget(mainWidget)
        self.mainWin.setWindowTitle('DSS Analysis Tool')

    def show(self):
        self.mainWin.show()

if __name__ == '__main__':
    import sys
    gui = AnalysisGUI()
    gui.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
