from PyQt6.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QDateEdit, QMessageBox, QTextEdit, QLabel, QTableWidget,
    QTableWidgetItem
)
from PyQt6.QtCore import QDate
import pymysql

class EquipmentDialog(QDialog):
    def __init__(self, connection, equipo_id=None):
        super().__init__()
        self.connection = connection
        self.equipo_id = equipo_id
        self.setWindowTitle("Agregar Equipo" if equipo_id is None else "Editar Equipo")
        self.resize(800, 600)
        self.init_ui()
        if equipo_id:
            self.load_equipment_data()
            self.load_ficha_tecnica()
            self.load_historial()

    def init_ui(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # Pestaña de Datos del Inventario
        self.tab_datos_inventario = QWidget()
        self.init_datos_inventario_tab()
        self.tabs.addTab(self.tab_datos_inventario, "Datos del Inventario")

        # Pestaña de Ficha Técnica
        self.tab_ficha_tecnica = QWidget()
        self.init_ficha_tecnica_tab()
        self.tabs.addTab(self.tab_ficha_tecnica, "Ficha Técnica")

        # Pestaña de Historial
        self.tab_historial = QWidget()
        self.init_historial_tab()
        self.tabs.addTab(self.tab_historial, "Historial")

        layout.addWidget(self.tabs)

        # Botones Guardar y Cancelar
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Guardar")
        btn_save.clicked.connect(self.save_all)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def init_datos_inventario_tab(self):
        layout = QFormLayout()
        self.equipo_medico_input = QLineEdit()
        self.emdn_input = QLineEdit()
        self.marca_input = QLineEdit()
        self.modelo_input = QLineEdit()
        self.numero_serie_input = QLineEdit()
        self.ubicacion_input = QLineEdit()
        self.estado_input = QLineEdit()
        self.valor_adquisicion_input = QLineEdit()
        self.valor_reposicion_input = QLineEdit()
        self.fecha_adquisicion_input = QDateEdit()
        self.fecha_adquisicion_input.setCalendarPopup(True)
        self.fecha_adquisicion_input.setDate(QDate.currentDate())

        layout.addRow("Equipo Médico:", self.equipo_medico_input)
        layout.addRow("EMDN:", self.emdn_input)
        layout.addRow("Marca:", self.marca_input)
        layout.addRow("Modelo:", self.modelo_input)
        layout.addRow("Número de Serie:", self.numero_serie_input)
        layout.addRow("Ubicación:", self.ubicacion_input)
        layout.addRow("Estado:", self.estado_input)
        layout.addRow("Valor de Adquisición (CLP):", self.valor_adquisicion_input)
        layout.addRow("Valor de Reposición (CLP):", self.valor_reposicion_input)
        layout.addRow("Fecha de Adquisición:", self.fecha_adquisicion_input)

        self.tab_datos_inventario.setLayout(layout)

    def init_ficha_tecnica_tab(self):
        layout = QFormLayout()

        # Campos de entrada para los nuevos datos
        self.datos_tecnicos_input = QTextEdit()
        self.accesorios_input = QTextEdit()
        self.manuales_input = QTextEdit()
        self.observaciones_input = QTextEdit()
        self.frecuencia_mantenimiento_input = QLineEdit()
        self.estado_equipo_input = QLineEdit()
        self.datos_proveedor_input = QTextEdit()

        # Añadir campos al formulario
        layout.addRow("Datos Técnicos:", self.datos_tecnicos_input)
        layout.addRow("Accesorios:", self.accesorios_input)
        layout.addRow("Manuales:", self.manuales_input)
        layout.addRow("Observaciones:", self.observaciones_input)
        layout.addRow("Frecuencia de Mantenimiento:", self.frecuencia_mantenimiento_input)
        layout.addRow("Estado del Equipo:", self.estado_equipo_input)
        layout.addRow("Datos del Proveedor:", self.datos_proveedor_input)

        self.tab_ficha_tecnica.setLayout(layout)

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

    def load_equipment_data(self):
        cursor = self.connection.cursor()
        sql = "SELECT * FROM inventario WHERE id = %s"
        cursor.execute(sql, (self.equipo_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            self.equipo_medico_input.setText(result[1])
            self.emdn_input.setText(result[2])
            self.marca_input.setText(result[3])
            self.modelo_input.setText(result[4])
            self.numero_serie_input.setText(result[5])
            self.ubicacion_input.setText(result[6])
            self.estado_input.setText(result[7])
            self.valor_adquisicion_input.setText(str(result[8]))
            self.valor_reposicion_input.setText(str(result[9]))
            self.fecha_adquisicion_input.setDate(QDate.fromString(str(result[10]), "yyyy-MM-dd"))



    def load_ficha_tecnica(self):
        cursor = self.connection.cursor()
        sql = "SELECT datos_tecnicos, accesorios, manuales, observaciones, frecuencia_mantenimiento, estado_equipo, datos_proveedor FROM ficha_tecnica WHERE equipo_id = %s"
        cursor.execute(sql, (self.equipo_id,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            self.datos_tecnicos_input.setPlainText(result[0] or "")
            self.accesorios_input.setPlainText(result[1] or "")
            self.manuales_input.setPlainText(result[2] or "")
            self.observaciones_input.setPlainText(result[3] or "")
            self.frecuencia_mantenimiento_input.setText(result[4] or "")
            self.estado_equipo_input.setText(result[5] or "")
            self.datos_proveedor_input.setPlainText(result[6] or "")
        else:
            # Limpiar los campos si no hay datos
            self.datos_tecnicos_input.clear()
            self.accesorios_input.clear()
            self.manuales_input.clear()
            self.observaciones_input.clear()
            self.frecuencia_mantenimiento_input.clear()
            self.estado_equipo_input.clear()
            self.datos_proveedor_input.clear()

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

    def save_all(self):
        # Obtener datos del formulario
        equipo_medico = self.equipo_medico_input.text()
        emdn = self.emdn_input.text()
        marca = self.marca_input.text()
        modelo = self.modelo_input.text()
        numero_serie = self.numero_serie_input.text()
        ubicacion = self.ubicacion_input.text()
        estado = self.estado_input.text()
        valor_adquisicion = self.valor_adquisicion_input.text()
        valor_reposicion = self.valor_reposicion_input.text()
        fecha_adquisicion = self.fecha_adquisicion_input.date().toString("yyyy-MM-dd")

        if not equipo_medico or not marca or not modelo:
            QMessageBox.warning(self, "Advertencia", "Por favor, completa los campos obligatorios.")
            return

        cursor = self.connection.cursor()
        if self.equipo_id is None:
            sql_inventario = """
            INSERT INTO inventario (
                equipo_medico, emdn, marca, modelo, numero_serie, ubicacion,
                estado, valor_adquisicion, valor_reposicion, fecha_adquisicion
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            inventario_values = (
                equipo_medico, emdn, marca, modelo, numero_serie, ubicacion,
                estado, valor_adquisicion, valor_reposicion, fecha_adquisicion
            )
        else:
            sql_inventario = """
            UPDATE inventario
            SET equipo_medico=%s, emdn=%s, marca=%s, modelo=%s, numero_serie=%s,
                ubicacion=%s, estado=%s, valor_adquisicion=%s, valor_reposicion=%s,
                fecha_adquisicion=%s
            WHERE id=%s
            """
            inventario_values = (
                equipo_medico, emdn, marca, modelo, numero_serie, ubicacion,
                estado, valor_adquisicion, valor_reposicion, fecha_adquisicion, self.equipo_id
            )
        try:
            if self.equipo_id is None:
                cursor.execute(sql_inventario, inventario_values)
                self.equipo_id = cursor.lastrowid
            else:
                cursor.execute(sql_inventario, inventario_values)
            self.connection.commit()
            # Guardar ficha técnica
            self.save_ficha_tecnica()
            QMessageBox.information(self, "Éxito", "Datos guardados correctamente.")
            self.accept()
        except pymysql.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar los datos:\n{e}")
            self.connection.rollback()
        cursor.close()



    def save_ficha_tecnica(self):
        datos_tecnicos = self.datos_tecnicos_input.toPlainText()
        accesorios = self.accesorios_input.toPlainText()
        manuales = self.manuales_input.toPlainText()
        observaciones = self.observaciones_input.toPlainText()
        frecuencia_mantenimiento = self.frecuencia_mantenimiento_input.text()
        estado_equipo = self.estado_equipo_input.text()
        datos_proveedor = self.datos_proveedor_input.toPlainText()

        cursor = self.connection.cursor()
        sql_select = "SELECT * FROM ficha_tecnica WHERE equipo_id = %s"
        cursor.execute(sql_select, (self.equipo_id,))
        result = cursor.fetchone()
        if result:
            sql = """
            UPDATE ficha_tecnica SET
                datos_tecnicos = %s,
                accesorios = %s,
                manuales = %s,
                observaciones = %s,
                frecuencia_mantenimiento = %s,
                estado_equipo = %s,
                datos_proveedor = %s
            WHERE equipo_id = %s
            """
            values = (
                datos_tecnicos, accesorios, manuales, observaciones,
                frecuencia_mantenimiento, estado_equipo, datos_proveedor, self.equipo_id
            )
        else:
            sql = """
            INSERT INTO ficha_tecnica (
                equipo_id, datos_tecnicos, accesorios, manuales, observaciones,
                frecuencia_mantenimiento, estado_equipo, datos_proveedor
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                self.equipo_id, datos_tecnicos, accesorios, manuales, observaciones,
                frecuencia_mantenimiento, estado_equipo, datos_proveedor
            )
        try:
            cursor.execute(sql, values)
            self.connection.commit()
        except pymysql.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la ficha técnica:\n{e}")
            self.connection.rollback()
        cursor.close()
