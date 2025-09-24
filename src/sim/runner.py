# wrapper para correr en QThread y emitir señales
from __future__ import annotations
from PySide6 import QtCore
from dataclasses import asdict
from typing import Optional
from src.sim.engine import Engine

class SimWorker(QtCore.QThread):
    row_ready = QtCore.Signal(dict)     # fila dentro de la ventana j..j+i-1
    progress  = QtCore.Signal(int)      # 0..100
    finished  = QtCore.Signal(dict)     # última fila N
    error     = QtCore.Signal(str)
    canceled  = QtCore.Signal()

    def __init__(self, engine: Engine, j: int, i: int, parent: Optional[QtCore.QObject]=None):
        super().__init__(parent)
        self.engine = engine
        self.j = j
        self.i = i
        self._running = True

    def cancel(self): self._running = False

    def run(self):
        try:
            last_row = None
            N = self.engine.N
            next_pct = 0
            for k, row in enumerate(self.engine.run(), start=1):
                if not self._running:
                    self.canceled.emit()
                    return
                last_row = asdict(row)
                if self.j <= row.dia < self.j + self.i:
                    self.row_ready.emit(asdict(row))
                pct = int(k * 100 / N)
                if pct >= next_pct:
                    self.progress.emit(pct)
                    next_pct = pct + 1
            if last_row:
                self.finished.emit(last_row)
        except Exception as e:
            self.error.emit(str(e))
