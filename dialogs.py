from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDateEdit, QPushButton, QVBoxLayout, QMessageBox
)
from PyQt6.QtCore import QDate
import pymysql

class AddEditEquipmentDialog(QDialog):
    def __init__(self, connection, equipo_id=None):
        super().__init__()
        self.connection = connection
        self.equipo_id = equipo_id
        self.setWindowTitle("Agregar Equipo" if equipo_id is None else "Editar Equipo")
        self.init_ui()
        if equipo_id:
            self.load_equipment_data()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.descripcion_input = QLineEdit()
        self.marca_input = QLineEdit()
        self.modelo_input = QLineEdit()
        self.numero_serie_input = QLineEdit()
        self.ubicacion_input = QLineEdit()
        self.estado_input = QLineEdit()
        self.valor_input = QLineEdit()
        self.fecha_adquisicion_input = QDateEdit()
        self.fecha_adquisicion_input.setCalendarPopup(True)
        self.fecha_adquisicion_input.setDate(QDate.currentDate())

        form_layout.addRow("Descripción:", self.descripcion_input)
        form_layout.addRow("Marca:", self.marca_input)
        form_layout.addRow("Modelo:", self.modelo_input)
        form_layout.addRow("Número de Serie:", self.numero_serie_input)
        form_layout.addRow("Ubicación:", self.ubicacion_input)
        form_layout.addRow("Estado:", self.estado_input)
        form_layout.addRow("Valor:", self.valor_input)
        form_layout.addRow("Fecha de Adquisición:", self.fecha_adquisicion_input)

        layout.addLayout(form_layout)

        btn_save = QPushButton("Guardar")
        btn_save.clicked.connect(self.save_equipment)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def load_equipment_data(self):
        cursor = self.connection.cursor()
        sql = "SELECT * FROM inventario WHERE id = %s"
        cursor.execute(sql, (self.equipo_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            self.descripcion_input.setText(result[1])
            self.marca_input.setText(result[2])
            self.modelo_input.setText(result[3])
            self.numero_serie_input.setText(result[4])
            self.ubicacion_input.setText(result[5])
            self.estado_input.setText(result[6])
            self.valor_input.setText(str(result[7]))
            self.fecha_adquisicion_input.setDate(QDate.fromString(str(result[8]), "yyyy-MM-dd"))

    def save_equipment(self):
        descripcion = self.descripcion_input.text()
        marca = self.marca_input.text()
        modelo = self.modelo_input.text()
        numero_serie = self.numero_serie_input.text()
        ubicacion = self.ubicacion_input.text()
        estado = self.estado_input.text()
        valor = self.valor_input.text()
        fecha_adquisicion = self.fecha_adquisicion_input.date().toString("yyyy-MM-dd")

        if not descripcion or not marca or not modelo:
            QMessageBox.warning(self, "Advertencia", "Por favor, completa los campos obligatorios.")
            return

        cursor = self.connection.cursor()
        if self.equipo_id is None:
            sql = """
            INSERT INTO inventario (descripcion, marca, modelo, numero_serie, ubicacion, estado, valor, fecha_adquisicion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (descripcion, marca, modelo, numero_serie, ubicacion, estado, valor, fecha_adquisicion)
        else:
            sql = """
            UPDATE inventario
            SET descripcion=%s, marca=%s, modelo=%s, numero_serie=%s, ubicacion=%s, estado=%s, valor=%s, fecha_adquisicion=%s
            WHERE id=%s
            """
            values = (descripcion, marca, modelo, numero_serie, ubicacion, estado, valor, fecha_adquisicion, self.equipo_id)
        try:
            cursor.execute(sql, values)
            self.connection.commit()
            QMessageBox.information(self, "Éxito", "Equipo guardado correctamente.")
            self.accept()
        except pymysql.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el equipo:\n{e}")
            self.connection.rollback()
        cursor.close()
