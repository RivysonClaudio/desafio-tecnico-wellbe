import zipfile
import io

class ZipBuilder:
    def __init__(self):
        self._buffer = io.BytesIO()
        self._zip_file = None

    def builder(self):
        self._zip_file = zipfile.ZipFile(self._buffer, "w", zipfile.ZIP_DEFLATED)
        return self

    def add_file(self, filename: str, data: bytes):
        if self._zip_file is None:
            raise RuntimeError("Você deve chamar .builder() antes de adicionar arquivos.")
        
        self._zip_file.writestr(filename, data)
        return self

    def build(self) -> bytes:
        if self._zip_file:
            self._zip_file.close()
        
        self._buffer.seek(0)
        return self._buffer.getvalue()