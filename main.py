import sys
import pymysql
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHBoxLayout, QLineEdit, QLabel, QTextEdit, QSplitter, QTabWidget
)
from PyQt6.QtCore import Qt

from equipment_dialog import EquipmentDialog  # Asegúrate de importar EquipmentDialog

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Equipos Médicos")
        self.setGeometry(100, 100, 1000, 600)
        self.connection = self.create_connection()
        self.init_ui()

    def create_connection(self):
        try:
            connection = pymysql.connect(
                host='localhost',
                user='root',
                database='equipos_medicos'
            )
            return connection
        except pymysql.Error as e:
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo conectar a la base de datos:\n{e}")
            sys.exit()

    def init_ui(self):
        # Crear un splitter horizontal para dividir la ventana en dos partes
        main_layout = QHBoxLayout()

        # Panel izquierdo: Tabla de inventario y botones
        left_panel = QVBoxLayout()

        # Barra de búsqueda
        search_layout = QHBoxLayout()
        search_label = QLabel("Buscar:")
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.load_data)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        left_panel.addLayout(search_layout)

        # Tabla de inventario
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.doubleClicked.connect(self.open_equipment_details)
        self.table.itemSelectionChanged.connect(self.show_equipment_details)
        left_panel.addWidget(self.table)

        # Botones
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Agregar Equipo")
        btn_add.clicked.connect(self.add_equipment)
        btn_edit = QPushButton("Editar Equipo")
        btn_edit.clicked.connect(self.edit_equipment)
        btn_delete = QPushButton("Eliminar Equipo")
        btn_delete.clicked.connect(self.delete_equipment)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_delete)
        left_panel.addLayout(btn_layout)

        # Panel derecho: Tabs para mostrar detalles
        self.tabs = QTabWidget()

        # Tab para Ficha Técnica
        self.tech_sheet_tab = QWidget()
        tech_sheet_layout = QVBoxLayout()
        self.tech_sheet_panel = QTextEdit()
        self.tech_sheet_panel.setReadOnly(True)
        self.tech_sheet_panel.setPlaceholderText("Seleccione un equipo para ver la ficha técnica.")
        tech_sheet_layout.addWidget(self.tech_sheet_panel)
        self.tech_sheet_tab.setLayout(tech_sheet_layout)
        self.tabs.addTab(self.tech_sheet_tab, "Ficha Técnica")

        # Tab para Historial de Mantenimiento
        self.maintenance_history_tab = QWidget()
        maintenance_layout = QVBoxLayout()
        self.maintenance_table = QTableWidget()
        maintenance_layout.addWidget(self.maintenance_table)

        # Botón para eliminar mantenimiento
        btn_delete_maintenance = QPushButton("Eliminar Seleccionado")
        btn_delete_maintenance.clicked.connect(self.delete_selected_maintenance)
        maintenance_layout.addWidget(btn_delete_maintenance)

        self.maintenance_history_tab.setLayout(maintenance_layout)
        self.tabs.addTab(self.maintenance_history_tab, "Historial de Mantenimiento")

        # Tab para Historial de Ubicación
        self.location_movements_tab = QWidget()
        movements_layout = QVBoxLayout()
        self.movements_table = QTableWidget()
        movements_layout.addWidget(self.movements_table)

        # Botón para eliminar movimiento de ubicación
        btn_delete_movement = QPushButton("Eliminar Seleccionado")
        btn_delete_movement.clicked.connect(self.delete_selected_movement)
        movements_layout.addWidget(btn_delete_movement)

        self.location_movements_tab.setLayout(movements_layout)
        self.tabs.addTab(self.location_movements_tab, "Historial de Ubicación")

        # Añadir los paneles al layout principal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        splitter.addWidget(left_widget)
        splitter.addWidget(self.tabs)
        splitter.setSizes([600, 400])  # Ajustar tamaños iniciales

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        self.load_data()


    def load_data(self):
        cursor = self.connection.cursor()
        search_text = self.search_input.text()
        if search_text:
            sql = """
            SELECT * FROM inventario WHERE
            equipo_medico LIKE %s OR emdn LIKE %s OR marca LIKE %s OR modelo LIKE %s
            """
            cursor.execute(sql, (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"))
        else:
            sql = "SELECT * FROM inventario"
            cursor.execute(sql)
        results = cursor.fetchall()
        self.table.setRowCount(len(results))
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "ID", "Equipo Médico", "EMDN", "Marca", "Modelo", "Nº Serie",
            "Ubicación", "Estado", "Valor de Adquisición (CLP)",
            "Valor de Reposición (CLP)", "Fecha Adquisición"
        ])
        for row_num, row_data in enumerate(results):
            for col_num, data in enumerate(row_data):
                if col_num in [8, 9]:  # Columnas de valores monetarios
                    if data is not None:
                        value = float(data)
                        item = QTableWidgetItem(f"${value:,.2f}")
                    else:
                        item = QTableWidgetItem("$0.00")
                else:
                    item = QTableWidgetItem(str(data) if data is not None else "")
                if col_num == 0:
                    item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row_num, col_num, item)
        self.table.resizeColumnsToContents()
        cursor.close()

        # Seleccionar la primera fila si existe
        if self.table.rowCount() > 0:
            self.table.selectRow(0)
            self.show_equipment_details()
        else:
            self.tech_sheet_panel.setPlainText("No hay equipos en el inventario.")
            self.maintenance_table.clearContents()
            self.maintenance_table.setRowCount(0)
            self.movements_table.clearContents()
            self.movements_table.setRowCount(0)


    def add_equipment(self):
        dialog = EquipmentDialog(self.connection)
        if dialog.exec():
            self.load_data()
            self.show_equipment_details()

    def edit_equipment(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            equipo_id = int(self.table.item(selected_row, 0).text())
            dialog = EquipmentDialog(self.connection, equipo_id)
            if dialog.exec():
                self.load_data()
                # Mantener la selección en el equipo editado
                self.table.selectRow(selected_row)
                self.show_equipment_details()
        else:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona un equipo para editar.")

    def delete_equipment(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            equipo_id = int(self.table.item(selected_row, 0).text())
            reply = QMessageBox.question(
                self, 'Eliminar Equipo',
                f"¿Estás seguro de que deseas eliminar el equipo con ID {equipo_id}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                cursor = self.connection.cursor()
                sql = "DELETE FROM inventario WHERE id = %s"
                try:
                    cursor.execute(sql, (equipo_id,))
                    self.connection.commit()
                    QMessageBox.information(self, "Éxito", "Equipo eliminado correctamente.")
                    self.load_data()
                    self.show_equipment_details()
                except pymysql.Error as e:
                    QMessageBox.critical(self, "Error", f"No se pudo eliminar el equipo:\n{e}")
                    self.connection.rollback()
                cursor.close()
        else:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona un equipo para eliminar.")

    def delete_selected_maintenance(self):
        selected_row = self.maintenance_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona un mantenimiento para eliminar.")
            return

        # Obtener la fecha y tipo de mantenimiento para identificar el registro
        fecha_item = self.maintenance_table.item(selected_row, 0)
        tipo_item = self.maintenance_table.item(selected_row, 1)
        if not fecha_item or not tipo_item:
            QMessageBox.warning(self, "Advertencia", "No se pudo identificar el mantenimiento seleccionado.")
            return

        fecha = fecha_item.text()
        tipo_mantenimiento = tipo_item.text()

        # Confirmar la eliminación
        reply = QMessageBox.question(
            self, 'Confirmar Eliminación',
            f"¿Estás seguro de que deseas eliminar el mantenimiento del {fecha} de tipo '{tipo_mantenimiento}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.connection.cursor()
            # Suponiendo que fecha y tipo_mantenimiento identifican unívocamente el registro
            sql = """
            DELETE FROM historial_mantenimiento
            WHERE equipo_id = %s AND fecha = %s AND tipo_mantenimiento = %s
            """
            equipo_id = self.get_selected_equipo_id()
            try:
                cursor.execute(sql, (equipo_id, fecha, tipo_mantenimiento))
                self.connection.commit()
                QMessageBox.information(self, "Éxito", "Mantenimiento eliminado correctamente.")
                self.load_maintenance_history(equipo_id)
            except pymysql.Error as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el mantenimiento:\n{e}")
                self.connection.rollback()
            cursor.close()

    def delete_selected_movement(self):
        selected_row = self.movements_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona un movimiento de ubicación para eliminar.")
            return

        # Obtener la fecha y nueva ubicación para identificar el registro
        fecha_item = self.movements_table.item(selected_row, 0)
        nueva_ubicacion_item = self.movements_table.item(selected_row, 2)
        if not fecha_item or not nueva_ubicacion_item:
            QMessageBox.warning(self, "Advertencia", "No se pudo identificar el movimiento seleccionado.")
            return

        fecha = fecha_item.text()
        nueva_ubicacion = nueva_ubicacion_item.text()

        # Confirmar la eliminación
        reply = QMessageBox.question(
            self, 'Confirmar Eliminación',
            f"¿Estás seguro de que deseas eliminar el movimiento de ubicación a '{nueva_ubicacion}' del {fecha}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.connection.cursor()
            # Suponiendo que fecha y nueva_ubicacion identifican unívocamente el registro
            sql = """
            DELETE FROM movimientos_ubicacion
            WHERE equipo_id = %s AND fecha = %s AND nueva_ubicacion = %s
            """
            equipo_id = self.get_selected_equipo_id()
            try:
                cursor.execute(sql, (equipo_id, fecha, nueva_ubicacion))
                self.connection.commit()
                QMessageBox.information(self, "Éxito", "Movimiento de ubicación eliminado correctamente.")
                self.load_location_movements(equipo_id)
            except pymysql.Error as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el movimiento de ubicación:\n{e}")
                self.connection.rollback()
            cursor.close()

    def get_selected_equipo_id(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            return int(selected_items[0].text())
        return None

    def open_equipment_details(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            equipo_id = int(self.table.item(selected_row, 0).text())
            dialog = EquipmentDialog(self.connection, equipo_id)
            if dialog.exec():
                self.load_data()
                self.table.selectRow(selected_row)
                self.show_equipment_details()
        else:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona un equipo para ver detalles.")

    def show_equipment_details(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            equipo_id = int(selected_items[0].text())
            self.load_tech_sheet(equipo_id)
            self.load_maintenance_history(equipo_id)
            self.load_location_movements(equipo_id)
        else:
            self.tech_sheet_panel.setPlainText("Seleccione un equipo para ver la ficha técnica.")
            self.maintenance_table.clearContents()
            self.maintenance_table.setRowCount(0)
            self.movements_table.clearContents()
            self.movements_table.setRowCount(0)

    def load_tech_sheet(self, equipo_id):
        cursor = self.connection.cursor()
        sql = """
        SELECT datos_tecnicos, accesorios, manuales, observaciones,
            frecuencia_mantenimiento, estado_equipo, datos_proveedor
        FROM ficha_tecnica WHERE equipo_id = %s
        """
        try:
            cursor.execute(sql, (equipo_id,))
            result = cursor.fetchone()
            if result:
                datos_tecnicos = result[0] or ""
                accesorios = result[1] or ""
                manuales = result[2] or ""
                observaciones = result[3] or ""
                frecuencia_mantenimiento = result[4] or ""
                estado_equipo = result[5] or ""
                datos_proveedor = result[6] or ""

                # Formatear el texto para mostrarlo en el QTextEdit
                ficha_texto = f"""
                <h2>Datos Técnicos</h2>
                <p>{datos_tecnicos}</p>
                <h2>Accesorios</h2>
                <p>{accesorios}</p>
                <h2>Manuales</h2>
                <p>{manuales}</p>
                <h2>Observaciones</h2>
                <p>{observaciones}</p>
                <h2>Frecuencia de Mantenimiento</h2>
                <p>{frecuencia_mantenimiento}</p>
                <h2>Estado del Equipo</h2>
                <p>{estado_equipo}</p>
                <h2>Datos del Proveedor</h2>
                <p>{datos_proveedor}</p>
                """
                self.tech_sheet_panel.setHtml(ficha_texto)
            else:
                self.tech_sheet_panel.setPlainText("No hay ficha técnica disponible para este equipo.")
        except pymysql.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar la ficha técnica:\n{e}")
            self.tech_sheet_panel.setPlainText("Error al cargar la ficha técnica.")
        finally:
            cursor.close()

    def load_maintenance_history(self, equipo_id):
        cursor = self.connection.cursor()
        sql = """
        SELECT fecha, tipo_mantenimiento, actividad_realizada, proveedor_tecnico,
            nombre_responsable, observaciones
        FROM historial_mantenimiento
        WHERE equipo_id = %s
        ORDER BY fecha DESC
        """
        try:
            cursor.execute(sql, (equipo_id,))
            results = cursor.fetchall()
            self.maintenance_table.setRowCount(len(results))
            self.maintenance_table.setColumnCount(6)
            self.maintenance_table.setHorizontalHeaderLabels([
                "Fecha", "Tipo de Mantenimiento", "Actividad Realizada",
                "Proveedor/Técnico", "Nombre Responsable", "Observaciones"
            ])
            for row_num, row_data in enumerate(results):
                for col_num, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    self.maintenance_table.setItem(row_num, col_num, item)
            self.maintenance_table.resizeColumnsToContents()
        except pymysql.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el historial de mantenimiento:\n{e}")
            self.maintenance_table.clearContents()
            self.maintenance_table.setRowCount(0)
        finally:
            cursor.close()

    def load_location_movements(self, equipo_id):
        cursor = self.connection.cursor()
        sql = """
        SELECT fecha, ubicacion_original, nueva_ubicacion,
            nombre_responsable, observaciones
        FROM movimientos_ubicacion
        WHERE equipo_id = %s
        ORDER BY fecha DESC
        """
        try:
            cursor.execute(sql, (equipo_id,))
            results = cursor.fetchall()
            self.movements_table.setRowCount(len(results))
            self.movements_table.setColumnCount(5)
            self.movements_table.setHorizontalHeaderLabels([
                "Fecha", "Ubicación Original", "Nueva Ubicación",
                "Nombre Responsable", "Observaciones"
            ])
            for row_num, row_data in enumerate(results):
                for col_num, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    self.movements_table.setItem(row_num, col_num, item)
            self.movements_table.resizeColumnsToContents()
        except pymysql.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el historial de ubicación:\n{e}")
            self.movements_table.clearContents()
            self.movements_table.setRowCount(0)
        finally:
            cursor.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
