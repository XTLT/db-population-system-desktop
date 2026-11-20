from .._imports import *
from .._consts import *
from ..funcs import *



class LandSubsidyImportWorkerRunMixin:
    def run(self):
        try:
            if self.is_network_mode:
                import os
                import mimetypes
                from network.client import _request_raw

                boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
                with open(self.file_path, 'rb') as f:
                    file_data = f.read()
                content_type = mimetypes.guess_type(self.file_path)[0] or 'application/octet-stream'
                body = (
                    f'--{boundary}\r\n'
                    f'Content-Disposition: form-data; name="subsidy_year"\r\n\r\n'
                    f'{self.subsidy_year}\r\n'
                    f'--{boundary}\r\n'
                    f'Content-Disposition: form-data; name="dry_run"\r\n\r\n'
                    f'{1 if self.dry_run else 0}\r\n'
                    f'--{boundary}\r\n'
                    f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(self.file_path)}"\r\n'
                    f'Content-Type: {content_type}\r\n\r\n'
                ).encode('utf-8') + file_data + f'\r\n--{boundary}--\r\n'.encode('utf-8')
                result = _request_raw('POST', '/api/land_subsidy/import', body,
                                      f'multipart/form-data; boundary={boundary}')
                self.finished.emit(result)
            else:
                from data.excel_importer import import_land_subsidy
                result = import_land_subsidy(self.file_path, self.subsidy_year, self.progress.emit, dry_run=self.dry_run)
                self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
