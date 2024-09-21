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

        # Panel derecho: Tabs para ficha técnica y historial
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

        # Tab para Historial
        self.history_tab = QWidget()
        history_layout = QVBoxLayout()
        self.history_table = QTableWidget()
        history_layout.addWidget(self.history_table)
        self.history_tab.setLayout(history_layout)
        self.tabs.addTab(self.history_tab, "Historial")

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
            sql = "SELECT * FROM inventario WHERE descripcion LIKE %s OR marca LIKE %s OR modelo LIKE %s"
            cursor.execute(sql, (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"))
        else:
            sql = "SELECT * FROM inventario"
            cursor.execute(sql)
        results = cursor.fetchall()
        self.table.setRowCount(len(results))
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["ID", "Descripción", "Marca", "Modelo", "Nº Serie", "Ubicación", "Estado", "Valor", "Fecha Adquisición"])
        for row_num, row_data in enumerate(results):
            for col_num, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                if col_num == 0:
                    item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row_num, col_num, item)
        self.table.resizeColumnsToContents()
        cursor.close()

        # Seleccionar la primera fila si existe
        if self.table.rowCount() > 0:
            self.table.selectRow(0)
        else:
            self.tech_sheet_panel.setPlainText("No hay equipos en el inventario.")
            self.history_table.clearContents()
            self.history_table.setRowCount(0)

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
            self.load_history(equipo_id)
        else:
            self.tech_sheet_panel.setPlainText("Seleccione un equipo para ver la ficha técnica.")
            self.history_table.clearContents()
            self.history_table.setRowCount(0)

    def load_tech_sheet(self, equipo_id):
        cursor = self.connection.cursor()
        sql = "SELECT especificaciones FROM ficha_tecnica WHERE equipo_id = %s"
        try:
            cursor.execute(sql, (equipo_id,))
            result = cursor.fetchone()
            if result and result[0]:
                self.tech_sheet_panel.setPlainText(result[0])
            else:
                self.tech_sheet_panel.setPlainText("No hay ficha técnica disponible para este equipo.")
        except pymysql.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar la ficha técnica:\n{e}")
            self.tech_sheet_panel.setPlainText("Error al cargar la ficha técnica.")
        finally:
            cursor.close()

    def load_history(self, equipo_id):
        cursor = self.connection.cursor()
        sql = "SELECT fecha_evento, descripcion_evento FROM historial_equipo WHERE equipo_id = %s ORDER BY fecha_evento DESC"
        try:
            cursor.execute(sql, (equipo_id,))
            results = cursor.fetchall()
            self.history_table.setRowCount(len(results))
            self.history_table.setColumnCount(2)
            self.history_table.setHorizontalHeaderLabels(["Fecha", "Descripción"])
            for row_num, row_data in enumerate(results):
                self.history_table.setItem(row_num, 0, QTableWidgetItem(str(row_data[0])))
                self.history_table.setItem(row_num, 1, QTableWidgetItem(row_data[1]))
            self.history_table.resizeColumnsToContents()
        except pymysql.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el historial:\n{e}")
            self.history_table.clearContents()
            self.history_table.setRowCount(0)
        finally:
            cursor.close()
