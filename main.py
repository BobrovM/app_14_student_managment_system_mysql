from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, \
    QVBoxLayout, QLineEdit, QComboBox, QPushButton, QToolBar, QStatusBar, QGridLayout, QLabel, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sys
import sqlite3
import mysql.connector


class DatabaseConnection:
    def __init__(self, host="localhost", user="root", password="45314531", database="student_management_app"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host, user=self.user,
                                             password=self.password, database=self.database)
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(400)
        self.setFixedWidth(500)
        self.setWindowTitle("Student Management System")

        file_menu_item = self.menuBar().addMenu("&File")
        edit_menu_item = self.menuBar().addMenu("&Edit")
        help_menu_item = self.menuBar().addMenu("&Help")

        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert_student)
        file_menu_item.addAction(add_student_action)

        search_student_action = QAction(QIcon("icons/search.png"), "Search Student", self)
        search_student_action.triggered.connect(self.search_student)
        edit_menu_item.addAction(search_student_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_student_action)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit_cell)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete_cell)

        children = self.findChildren(QPushButton)
        for child in children:
            self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        connection = database.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        data = cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(data):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        cursor.close()
        connection.close()

    def insert_student(self):
        dialog = InsertStudentDialog()
        dialog.exec()

    def search_student(self):
        dialog = SearchStudentDialog()
        dialog.exec()

    def edit_cell(self):
        dialog = EditDialog()
        dialog.exec()

    def delete_cell(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This app was created during the course.
        Feel free to modify it.
        """
        self.setText(content)


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        index = main_window.table.currentRow()
        self.student_id = main_window.table.item(index, 0).text()

        student_name = main_window.table.item(index, 1).text()
        self.student_name_edit = QLineEdit(student_name)
        layout.addWidget(self.student_name_edit)

        course_name = main_window.table.item(index, 2).text()
        self.course_combo = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_combo.addItems(courses)
        self.course_combo.setCurrentText(course_name)
        layout.addWidget(self.course_combo)

        mobile_phone = main_window.table.item(index, 3).text()
        self.mobile_edit = QLineEdit(mobile_phone)
        layout.addWidget(self.mobile_edit)

        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = database.connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s",
                       (self.student_name_edit.text(),
                        self.course_combo.itemText(self.course_combo.currentIndex()),
                        self.mobile_edit.text(),
                        self.student_id
                        ))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.close()

        confirmation_message = QMessageBox()
        confirmation_message.setWindowTitle("Updated")
        confirmation_message.setText("Updated successfully")
        confirmation_message.exec()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student")

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete this data?")
        yes_button = QPushButton("Yes")
        no_button = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes_button, 1, 0)
        layout.addWidget(no_button, 1, 1)
        self.setLayout(layout)

        yes_button.clicked.connect(self.delete_student)

    def delete_student(self):
        index = main_window.table.currentRow()
        student_id = main_window.table.item(index, 0).text()

        connection = database.connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = %s", (student_id,))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.close()

        confirmation_message = QMessageBox()
        confirmation_message.setWindowTitle("Deleted")
        confirmation_message.setText("Deleted successfully")
        confirmation_message.exec()


class InsertStudentDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.student_name_edit = QLineEdit()
        self.student_name_edit.setPlaceholderText("Student's name")
        layout.addWidget(self.student_name_edit)

        self.course_combo = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_combo.addItems(courses)
        layout.addWidget(self.course_combo)

        self.mobile_edit = QLineEdit()
        self.mobile_edit.setPlaceholderText("Mobile phone number")
        layout.addWidget(self.mobile_edit)

        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name_edit.text()
        course = self.course_combo.itemText(self.course_combo.currentIndex())
        mobile = self.mobile_edit.text()
        connection = database.connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (%s, %s, %s)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.close()

        confirmation_message = QMessageBox()
        confirmation_message.setWindowTitle("Added")
        confirmation_message.setText("Added successfully")
        confirmation_message.exec()


class SearchStudentDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(200)

        layout = QVBoxLayout()

        self.student_name_edit = QLineEdit()
        self.student_name_edit.setPlaceholderText("Student's name")
        layout.addWidget(self.student_name_edit)

        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name_edit.text()
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            main_window.table.item(item.row(), 1).setSelected(True)


database = DatabaseConnection()
app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
