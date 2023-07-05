from pathlib import Path

class TextFiles:
    def __init__(self, basedir):
        self._basedir = Path(basedir)
        self._clear()
        if not self._basedir.exists() or not self._basedir.is_dir():
            raise FileNotFoundError
        self._files = [f for f in self._basedir.glob('**/*.txt') if f.is_file()]
    
    def __enter__(self):
        return self
    
    def __exit__(self, *p):
        self._clear()
    
    def __del__(self):
        self._clear()
    
    def _closecur(self):
        if hasattr(self, '_curfile') and self._curfile and not self._curfile.closed:
            self._curfile.close()
        self._curfile = None
        self._curpath = None
        self._text = None
    
    def _clear(self):
        self._closecur()
        self._files = []
    
    def next(self):
        for file in self._files:
            if not file.exists():
                self._clear()
                raise FileNotFoundError
            self._closecur()
            self._curpath = file
            self._curfile = file.open('r', encoding='utf-8')
            yield self._curfile
        else:
            self._clear()
    
    @property
    def opened_file(self):
        if hasattr(self, '_curfile') and self._curfile and not self._curfile.closed:
            return self._curpath
        else:
            return None
    
    @property
    def text(self):
        if self._text is None:
            if hasattr(self, '_curfile') and self._curfile and not self._curfile.closed:
                self._text = self._curfile.read()
            else:
                self._text = None
        return self._text
