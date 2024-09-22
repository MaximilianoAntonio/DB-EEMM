from PyQt6.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QDateEdit, QMessageBox, QTextEdit, QLabel, QTableWidget,
    QTableWidgetItem, QComboBox
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
            self.load_historial_mantenimiento()
            self.load_movimientos_ubicacion()

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

        # Pestaña de Historial de Mantenimiento
        self.tab_historial_mantenimiento = QWidget()
        self.init_historial_mantenimiento_tab()
        self.tabs.addTab(self.tab_historial_mantenimiento, "Historial de Mantenimiento")

        # Pestaña de Movimientos de Ubicación
        self.tab_movimientos_ubicacion = QWidget()
        self.init_movimientos_ubicacion_tab()
        self.tabs.addTab(self.tab_movimientos_ubicacion, "Movimientos de Ubicación")

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


    def init_historial_mantenimiento_tab(self):
        layout = QVBoxLayout()

        # Tabla para mostrar el historial de mantenimiento
        self.historial_mantenimiento_table = QTableWidget()
        layout.addWidget(self.historial_mantenimiento_table)

        # Formulario para agregar nuevo mantenimiento
        form_layout = QFormLayout()
        self.fecha_mantenimiento_input = QDateEdit()
        self.fecha_mantenimiento_input.setCalendarPopup(True)
        self.fecha_mantenimiento_input.setDate(QDate.currentDate())
        self.tipo_mantenimiento_input = QComboBox()
        self.tipo_mantenimiento_input.addItems(["Preventivo", "Correctivo", "Otro"])
        self.actividad_realizada_input = QLineEdit()
        self.proveedor_tecnico_input = QLineEdit()
        self.nombre_responsable_input = QLineEdit()
        self.observaciones_mantenimiento_input = QTextEdit()

        form_layout.addRow("Fecha:", self.fecha_mantenimiento_input)
        form_layout.addRow("Tipo de Mantenimiento:", self.tipo_mantenimiento_input)
        form_layout.addRow("Actividad Realizada:", self.actividad_realizada_input)
        form_layout.addRow("Proveedor/Técnico:", self.proveedor_tecnico_input)
        form_layout.addRow("Nombre Responsable:", self.nombre_responsable_input)
        form_layout.addRow("Observaciones:", self.observaciones_mantenimiento_input)

        btn_add_mantenimiento = QPushButton("Agregar Mantenimiento")
        btn_add_mantenimiento.clicked.connect(self.add_historial_mantenimiento)

        layout.addLayout(form_layout)
        layout.addWidget(btn_add_mantenimiento)

        self.tab_historial_mantenimiento.setLayout(layout)

    def init_movimientos_ubicacion_tab(self):
        layout = QVBoxLayout()

        # Tabla para mostrar los movimientos de ubicación
        self.movimientos_ubicacion_table = QTableWidget()
        layout.addWidget(self.movimientos_ubicacion_table)

        # Formulario para agregar nuevo movimiento
        form_layout = QFormLayout()
        self.fecha_movimiento_input = QDateEdit()
        self.fecha_movimiento_input.setCalendarPopup(True)
        self.fecha_movimiento_input.setDate(QDate.currentDate())
        self.ubicacion_original_input = QLineEdit()
        self.nueva_ubicacion_input = QLineEdit()
        self.nombre_responsable_mov_input = QLineEdit()
        self.observaciones_movimiento_input = QTextEdit()

        form_layout.addRow("Fecha:", self.fecha_movimiento_input)
        form_layout.addRow("Ubicación Original:", self.ubicacion_original_input)
        form_layout.addRow("Nueva Ubicación:", self.nueva_ubicacion_input)
        form_layout.addRow("Nombre Responsable:", self.nombre_responsable_mov_input)
        form_layout.addRow("Observaciones:", self.observaciones_movimiento_input)

        btn_add_movimiento = QPushButton("Agregar Movimiento")
        btn_add_movimiento.clicked.connect(self.add_movimiento_ubicacion)

        layout.addLayout(form_layout)
        layout.addWidget(btn_add_movimiento)

        self.tab_movimientos_ubicacion.setLayout(layout)


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

    def load_historial_mantenimiento(self):
        cursor = self.connection.cursor()
        sql = """
        SELECT fecha, tipo_mantenimiento, actividad_realizada, proveedor_tecnico,
            nombre_responsable, observaciones
        FROM historial_mantenimiento
        WHERE equipo_id = %s
        ORDER BY fecha DESC
        """
        try:
            cursor.execute(sql, (self.equipo_id,))
            results = cursor.fetchall()
            self.historial_mantenimiento_table.setRowCount(len(results))
            self.historial_mantenimiento_table.setColumnCount(6)
            self.historial_mantenimiento_table.setHorizontalHeaderLabels([
                "Fecha", "Tipo de Mantenimiento", "Actividad Realizada",
                "Proveedor/Técnico", "Nombre Responsable", "Observaciones"
            ])
            for row_num, row_data in enumerate(results):
                for col_num, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    self.historial_mantenimiento_table.setItem(row_num, col_num, item)
            self.historial_mantenimiento_table.resizeColumnsToContents()
        except pymysql.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el historial de mantenimiento:\n{e}")
        finally:
            cursor.close()

    def load_movimientos_ubicacion(self):
        cursor = self.connection.cursor()
        sql = """
        SELECT fecha, ubicacion_original, nueva_ubicacion,
            nombre_responsable, observaciones
        FROM movimientos_ubicacion
        WHERE equipo_id = %s
        ORDER BY fecha DESC
        """
        try:
            cursor.execute(sql, (self.equipo_id,))
            results = cursor.fetchall()
            self.movimientos_ubicacion_table.setRowCount(len(results))
            self.movimientos_ubicacion_table.setColumnCount(5)
            self.movimientos_ubicacion_table.setHorizontalHeaderLabels([
                "Fecha", "Ubicación Original", "Nueva Ubicación",
                "Nombre Responsable", "Observaciones"
            ])
            for row_num, row_data in enumerate(results):
                for col_num, data in enumerate(results[row_num]):
                    item = QTableWidgetItem(str(data))
                    self.movimientos_ubicacion_table.setItem(row_num, col_num, item)
            self.movimientos_ubicacion_table.resizeColumnsToContents()
        except pymysql.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar los movimientos de ubicación:\n{e}")
        finally:
            cursor.close()

    def add_historial_mantenimiento(self):
        fecha = self.fecha_mantenimiento_input.date().toString("yyyy-MM-dd")
        tipo_mantenimiento = self.tipo_mantenimiento_input.currentText()
        actividad_realizada = self.actividad_realizada_input.text()
        proveedor_tecnico = self.proveedor_tecnico_input.text()
        nombre_responsable = self.nombre_responsable_input.text()
        observaciones = self.observaciones_mantenimiento_input.toPlainText()

        cursor = self.connection.cursor()
        sql = """
        INSERT INTO historial_mantenimiento (
            equipo_id, fecha, tipo_mantenimiento, actividad_realizada,
            proveedor_tecnico, nombre_responsable, observaciones
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            self.equipo_id, fecha, tipo_mantenimiento, actividad_realizada,
            proveedor_tecnico, nombre_responsable, observaciones
        )
        try:
            cursor.execute(sql, values)
            self.connection.commit()
            QMessageBox.information(self, "Éxito", "Mantenimiento agregado al historial.")
            # Limpiar campos
            self.actividad_realizada_input.clear()
            self.proveedor_tecnico_input.clear()
            self.nombre_responsable_input.clear()
            self.observaciones_mantenimiento_input.clear()
            self.load_historial_mantenimiento()
        except pymysql.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar el mantenimiento:\n{e}")
            self.connection.rollback()
        cursor.close()

    def add_movimiento_ubicacion(self):
        fecha = self.fecha_movimiento_input.date().toString("yyyy-MM-dd")
        ubicacion_original = self.ubicacion_original_input.text()
        nueva_ubicacion = self.nueva_ubicacion_input.text()
        nombre_responsable = self.nombre_responsable_mov_input.text()
        observaciones = self.observaciones_movimiento_input.toPlainText()

        cursor = self.connection.cursor()
        sql = """
        INSERT INTO movimientos_ubicacion (
            equipo_id, fecha, ubicacion_original, nueva_ubicacion,
            nombre_responsable, observaciones
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            self.equipo_id, fecha, ubicacion_original, nueva_ubicacion,
            nombre_responsable, observaciones
        )
        try:
            cursor.execute(sql, values)
            self.connection.commit()
            QMessageBox.information(self, "Éxito", "Movimiento de ubicación agregado.")
            # Limpiar campos
            self.ubicacion_original_input.clear()
            self.nueva_ubicacion_input.clear()
            self.nombre_responsable_mov_input.clear()
            self.observaciones_movimiento_input.clear()
            self.load_movimientos_ubicacion()
        except pymysql.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar el movimiento:\n{e}")
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
