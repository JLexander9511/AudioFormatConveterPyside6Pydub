from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QToolBar, QStatusBar, QFileDialog, QMessageBox, QHBoxLayout, QComboBox, QCheckBox, QPushButton, QProgressBar
from PySide6.QtGui import QAction
from PySide6.QtCore import Slot
from pydub import AudioSegment
from utils import utils
from modules.ConvertionWorker import ConvertionWorker
import os

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Convertor de Audio")
        self.resize(200, 300) #200x300
        

        self.audio = None
        self.audio_ruta = None
        self._worker = None

        central = QWidget()
        self.setCentralWidget(central)
        container = QVBoxLayout(central)

        self.info_audio = QLabel("No hay archivo cargado")
        self.info_audio.setStyleSheet("font-size 13px;")
        container.addWidget(self.info_audio)

        form_row = QHBoxLayout()

        self.select_formato = QComboBox()
        self.select_formato.addItems(["mp3", "wav", "flac", "ogg", "m4a"])
        form_row.addWidget(QLabel("Formato destino:"))
        form_row.addWidget(self.select_formato)

        self.meta_opc = QCheckBox("Mantener Metadatos")
        self.meta_opc.setChecked(True)
        form_row.addWidget(self.meta_opc)
        
        self.btn_convertir = QPushButton("Convertir")
        self.btn_convertir.clicked.connect(self.convertir_audio)

        container.addLayout(form_row)
        container.addWidget(self.btn_convertir)

        progress_bar = QHBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        progress_bar.addWidget(self.progress_bar)

        self.cancel_boton = QPushButton("Cancelar")
        self.cancel_boton.setEnabled(False)
        self.cancel_boton.clicked.connect(self.cancel_button)
        progress_bar.addWidget(self.cancel_boton)

        container.addLayout(progress_bar)

        self._create_actions()
        self._create_menu()
        self._create_toolbar()
        self._create_statusbar()

    def _create_actions(self):
        self.open_action = QAction("Abrir", self)
        self.convert_action = QAction("Convertir", self)
        self.exit_action = QAction("Salir", self)

        #Gatillos de evento
        self.exit_action.triggered.connect(self.close)
        self.open_action.triggered.connect(self.abrir_archivo)

    def _create_menu(self):
        menu = self.menuBar()
        archivo = menu.addMenu("Archivo")
        archivo.addAction(self.open_action)
        archivo.addAction(self.exit_action)

        ayuda = menu.addMenu("Ayuda")
        # Crear la acción y conectarla correctamente al slot
        self.about_action = QAction("Acerca de", self)
        self.about_action.triggered.connect(self.mostrar_acerca_de)
        ayuda.addAction(self.about_action)

    def _create_toolbar(self):
        toolbar = QToolBar("Principal")
        self.addToolBar(toolbar)
        toolbar.addAction(self.open_action)

    def _create_statusbar(self):
        status = QStatusBar()
        self.setStatusBar(status)
        status.showMessage("Listo para usar")

    def abrir_archivo(self):
        tipos_archivos = "Audio (*.mp3 *.wav *.flac *.ogg *.aac *.m4a);; Todos (*.*)"
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccione su archivo de audio", "", tipos_archivos)

        if not ruta:
            self.statusBar().showMessage("Seleccion Cancelada")
            return
        
        try:
            audio = AudioSegment.from_file(ruta)
            self.audio = audio
            self.audio_ruta = ruta

            nombre = os.path.basename(ruta)
            extension = os.path.splitext(ruta)[1].lower().lstrip(".")
            self.duracion_segundos = len(audio) / 1000.0
            peso = os.path.getsize(ruta)

            self.info_audio.setText(
                f"Archivo: {nombre}\n"
                f"Formato: {extension}\n"
                f"Duracion: {self.duracion_segundos}\n"
                f"Tamaño: {utils.human_size(peso)}\n"
                f"Ruta: {ruta}\n"
            )

            self.statusBar().showMessage("Archivo cargado correctamente")
        except Exception as e:
            self.info_audio.setText("Error al abrir el archivo")
            self.statusBar().showMessage("Error al cargar el archivo")
            QMessageBox(self, "Error al abrir el archivo", "No se pudo abrir el archivo seleccionado")

    def convertir_audio(self):
        if not self.audio or not self.audio_ruta:
            QMessageBox.warning(self, "Sin archivo seleccionado", "Primero debes cargar un archivo de audio")
            return
        
        formato = self.select_formato.currentText()
        meta = self.meta_opc.isChecked()

        nombre_convertido = os.path.splitext(os.path.basename(self.audio_ruta))[0] + f"-converted.{formato}"

        ruta_salida, _ = QFileDialog.getSaveFileName(self, "Guardar como", nombre_convertido, f"{formato.upper()} Audios (*.{formato})")

        if not ruta_salida: 
            self.statusBar().showMessage("Conversion cancelada")
            return
        
        self._desactivar_botones(False)
        self.cancel_boton.setEnabled(True)
        self.statusBar().showMessage(f"Iniciando conversion..")

        self._worker = ConvertionWorker(
            input_path = self.audio_ruta,
            output_path = ruta_salida,
            formato = formato,
            keep_meta = meta,
            duration_sec = self.duracion_segundos
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)

        self._worker.start()

    def cancel_button(self):
        if self._worker:
            self._worker.kill()
            self.statusBar().showMessage(f"Cancelando conversion...")

    def _desactivar_botones(self, activado:bool):
        self.open_action.setEnabled(activado)
        self.btn_convertir.setEnabled(activado)
        self.convert_action.setEnabled(activado)
        self.select_formato.setEnabled(activado)
        self.meta_opc.setEnabled(activado)

    @Slot(int)
    def _on_progress(self, value: int):
        self.progress_bar.setValue(value)
        self.statusBar().showMessage(f"Convirtiendo... {value}%")

    @Slot(str)
    def _on_finished(self, output_path:str):
        self.progress_bar.setValue(100)
        self.statusBar().showMessage(f"Conversion Finalizada")
        QMessageBox.information(self, "Conversion completada", f"Archivo convertido:\n{output_path}")
        self._activar_ui_despues_conversion()

    @Slot(str)
    def _on_error(self, mensaje:str):
        self.statusBar().showMessage(f"Conversion Fallida")
        QMessageBox.critical(self, "Error", f"Ocurrio un error durante la conversion:\n{mensaje}")

    def _activar_ui_despues_conversion(self):
        self._desactivar_botones(True)
        self.progress_bar.setValue(0)
        self.cancel_boton.setEnabled(False)
        self._worker = None
    
    def mostrar_acerca_de(self):
        QMessageBox.information(self, "Acerca de", f"Programa desarrollado para la materia Lenguajes de programacion II")

