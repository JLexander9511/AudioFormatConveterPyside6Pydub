from PySide6.QtCore import QThread, Signal
from typing import Optional
from utils import utils
import subprocess

class ConvertionWorker(QThread):
    """
    Worker que ejecuta ffmpeg en un subprocess y emite progreso.
    Señales:
      progress(int)  -> porcentaje 0-100
      finished(str)  -> ruta de salida al terminar correctamente
      error(str)     -> mensaje de error
    """
    progress = Signal(int)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, input_path: str, output_path: str, formato: str, keep_meta: bool, duration_sec: float):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.formato = formato
        self.keep_meta = keep_meta
        self._proc: Optional[subprocess.Popen] = None
        self._is_killed = False
        self.duration_sec = max(duration_sec, 0.001)

    def run(self):
        try:
            # Construir comando ffmpeg básico
            # -y sobrescribe sin preguntar
            cmd = ["ffmpeg", "-hide_banner", "-y", "-i", self.input_path]

            # Si no queremos metadatos, podemos limpiar tags con -map_metadata -1
            if not self.keep_meta:
                cmd += ["-map_metadata", "-1"]

            # Codec selection minimal: let ffmpeg choose default codec for container
            # For m4a we can set aac codec explicitly
            if self.formato == "m4a":
                cmd += ["-c:a", "aac"]

            # Output file
            cmd += [self.output_path]

            # Lanzar proceso y leer stderr para progreso
            # ffmpeg escribe progreso en stderr
            self._proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)

            # Leer stderr línea a línea
            assert self._proc.stderr is not None
            for line in self._proc.stderr:
                if self._is_killed:
                    # Si se solicitó cancelación, terminar proceso
                    try:
                        self._proc.kill()
                    except Exception:
                        pass
                    self.error.emit("Conversión cancelada por el usuario")
                    return

                # ffmpeg imprime fragmentos con "time=00:00:xx.xx"
                if "time=" in line:
                    # Extraer la parte time=...
                    try:
                        # buscar token time=
                        idx = line.find("time=")
                        time_part = line[idx + len("time="):].split(" ")[0]
                        elapsed = utils._parse_ffmpeg_time(time_part)
                        percent = int((elapsed / self.duration_sec) * 100)
                        percent = max(0, min(100, percent))
                        self.progress.emit(percent)
                    except Exception:
                        pass

            # Esperar a que termine y comprobar código de salida
            ret = self._proc.wait()
            if ret == 0 and not self._is_killed:
                self.progress.emit(100)
                self.finished.emit(self.output_path)
            else:
                if not self._is_killed:
                    self.error.emit(f"ffmpeg finalizó con código {ret}")
        except FileNotFoundError:
            self.error.emit("ffmpeg no encontrado. Asegúrate de tener ffmpeg instalado y en el PATH.")
        except Exception as e:
            self.error.emit(str(e))

    def kill(self):
        self._is_killed = True
        if self._proc:
            try:
                self._proc.kill()
            except Exception:
                pass