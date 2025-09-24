# QTableView + modelo para vector de estado

from __future__ import annotations
from PySide6 import QtCore, QtWidgets


class DictTableModel(QtCore.QAbstractTableModel):
    def __init__(self, headers: list[str]):
        super().__init__()
        self._headers = headers
        self._rows: list[dict] = []

    def rowCount(self, parent=None):
        return len(self._rows)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or role != QtCore.Qt.DisplayRole:
            return None
        row = self._rows[index.row()]
        key = self._headers[index.column()]
        val = row.get(key, "")
        # 4 decimales para aleatorios
        if key in {"rnd_demanda", "rnd_demora"} and isinstance(val, (int, float)):
            return f"{val:.4f}"
        # fill_rate en porcentaje con 2 decimales | lo muestra en porcentaje 
        if key == "fill_rate" and isinstance(val, (int, float)):
            return f"{val*100:.2f}%"
        return f"{val}"

    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation == QtCore.Qt.Horizontal:
            return self._headers[section]
        return str(section + 1)

    def append_row(self, row_dict: dict):
        self.beginInsertRows(QtCore.QModelIndex(), len(self._rows), len(self._rows))
        self._rows.append(row_dict)
        self.endInsertRows()

    def clear(self):
        self.beginResetModel()
        self._rows.clear()
        self.endResetModel()
