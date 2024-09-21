from PyQt6.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QTextEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QLabel, QMessageBox, QLineEdit, QDateEdit
)
from PyQt6.QtCore import QDate
import pymysql

class EquipmentDetailsDialog(QDialog):
    def __init__(self, connection, equipo_id):
        super().__init__()
        self.connection = connection
        self.equipo_id = equipo_id
        self.setWindowTitle("Detalles del Equipo")
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        tabs = QTabWidget()

        # Pestaña de Ficha Técnica
        self.tab_ficha_tecnica = QWidget()
        self.init_ficha_tecnica_tab()
        tabs.addTab(self.tab_ficha_tecnica, "Ficha Técnica")

        # Pestaña de Historial
        self.tab_historial = QWidget()
        self.init_historial_tab()
        tabs.addTab(self.tab_historial, "Historial")

        layout.addWidget(tabs)
        self.setLayout(layout)

    def init_ficha_tecnica_tab(self):
        layout = QVBoxLayout()
        self.especificaciones_text = QTextEdit()
        layout.addWidget(self.especificaciones_text)

        btn_save = QPushButton("Guardar Ficha Técnica")
        btn_save.clicked.connect(self.save_ficha_tecnica)
        layout.addWidget(btn_save)

        self.tab_ficha_tecnica.setLayout(layout)
        self.load_ficha_tecnica()

    def load_ficha_tecnica(self):
        cursor = self.connection.cursor()
        sql = "SELECT especificaciones FROM ficha_tecnica WHERE equipo_id = %s"
        cursor.execute(sql, (self.equipo_id,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            self.especificaciones_text.setText(result[0])
        else:
            self.especificaciones_text.setText("")

    def save_ficha_tecnica(self):
        especificaciones = self.especificaciones_text.toPlainText()
        cursor = self.connection.cursor()
        sql_select = "SELECT * FROM ficha_tecnica WHERE equipo_id = %s"
        cursor.execute(sql_select, (self.equipo_id,))
        result = cursor.fetchone()
        if result:
            sql = "UPDATE ficha_tecnica SET especificaciones = %s WHERE equipo_id = %s"
            values = (especificaciones, self.equipo_id)
        else:
            sql = "INSERT INTO ficha_tecnica (equipo_id, especificaciones) VALUES (%s, %s)"
            values = (self.equipo_id, especificaciones)
        try:
            cursor.execute(sql, values)
            self.connection.commit()
            QMessageBox.information(self, "Éxito", "Ficha técnica guardada correctamente.")
        except pymysql.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la ficha técnica:\n{e}")
            self.connection.rollback()
        cursor.close()

    def init_historial_tab(self):
        layout = QVBoxLayout()

        # Tabla de historial
        self.historial_table = QTableWidget()
        layout.addWidget(self.historial_table)

        # Formulario para agregar evento
        form_layout = QHBoxLayout()
        self.fecha_evento_input = QDateEdit()
        self.fecha_evento_input.setCalendarPopup(True)
        self.fecha_evento_input.setDate(QDate.currentDate())
        self.descripcion_evento_input = QLineEdit()
        btn_add_event = QPushButton("Agregar Evento")
        btn_add_event.clicked.connect(self.add_historial_event)

        form_layout.addWidget(QLabel("Fecha:"))
        form_layout.addWidget(self.fecha_evento_input)
        form_layout.addWidget(QLabel("Descripción:"))
        form_layout.addWidget(self.descripcion_evento_input)
        form_layout.addWidget(btn_add_event)

        layout.addLayout(form_layout)
        self.tab_historial.setLayout(layout)
        self.load_historial()

    def load_historial(self):
        cursor = self.connection.cursor()
        sql = "SELECT fecha_evento, descripcion_evento FROM historial_equipo WHERE equipo_id = %s ORDER BY fecha_evento DESC"
        cursor.execute(sql, (self.equipo_id,))
        results = cursor.fetchall()
        cursor.close()

        self.historial_table.setRowCount(len(results))
        self.historial_table.setColumnCount(2)
        self.historial_table.setHorizontalHeaderLabels(["Fecha", "Descripción"])
        for row_num, row_data in enumerate(results):
            self.historial_table.setItem(row_num, 0, QTableWidgetItem(str(row_data[0])))
            self.historial_table.setItem(row_num, 1, QTableWidgetItem(row_data[1]))
        self.historial_table.resizeColumnsToContents()

    def add_historial_event(self):
        fecha_evento = self.fecha_evento_input.date().toString("yyyy-MM-dd")
        descripcion_evento = self.descripcion_evento_input.text()
        if not descripcion_evento:
            QMessageBox.warning(self, "Advertencia", "Por favor, ingresa la descripción del evento.")
            return
        cursor = self.connection.cursor()
        sql = "INSERT INTO historial_equipo (equipo_id, fecha_evento, descripcion_evento) VALUES (%s, %s, %s)"
        values = (self.equipo_id, fecha_evento, descripcion_evento)
        try:
            cursor.execute(sql, values)
            self.connection.commit()
            QMessageBox.information(self, "Éxito", "Evento agregado al historial.")
            self.descripcion_evento_input.clear()
            self.load_historial()
        except pymysql.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar el evento:\n{e}")
            self.connection.rollback()
        cursor.close()
