from pathlib import Path
import shutil

#
# 元ファイルを残してコピー先ファイルを読み書きするためのクラス
# 1ファイルずつ作成、編集、削除することを前提として編集以外を自動化する
#
class CopiedFiles:
    def __init__(self, basedir: Path, filter=None):
        # 実在するディレクトリでなければエラー
        basedir = Path(basedir)
        if not basedir.is_dir() or not basedir.exists():
            raise FileNotFoundError
        # フィルターが関数でなければエラー
        filter = filter or (lambda f: True)
        if not callable(filter):
            raise TypeError
        
        # インスタンス作成時点で条件に一致するファイルを覚えておく
        self.basedir = basedir
        self.files = [f for f in self.basedir.glob('**/*') if f.is_file() and filter(f)]
        self.openfile = None
        # 作業ディレクトリを作る(スコープから抜けるときに削除する)
        self.tempdir = Path(__file__).parent.joinpath('__files_temporary__')
        self.tempdir.mkdir(parents=True, exist_ok=True)

    # with構文で使えるようにする
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close_opened_file()
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def __del__(self):
        self.__exit__(self)

    def next(self):
        self.close_opened_file()
        for file in self.files:
            self.orgfile = file
            tempfile = self.tempdir.joinpath(file.name)
            shutil.copy(file, tempfile)
            self.openfile = open(tempfile, 'r+')
            yield self.openfile
        # 終わったら忘れる
        self.files = []
        return None

    def close_opened_file(self):
        if self.openfile and not self.openfile.closed:
            self.openfile.close()
        # 忘れる
        self.openfile = None
        self.orgfile = None

    @property
    def filedir(self):
        return self.orgfile.parent if self.openfile and not self.openfile.closed else ""

    @property
    def filename(self):
        return self.orgfile.name if self.openfile and not self.openfile.closed else ""


#
# 使い方
#
def usage():
    desired_files = {
        'basedir': Path.cwd(),
        'filter': lambda f: f.suffix == '.py'
    }
    with CopiedFiles(**desired_files) as files:
        # 1周目(有効)
        print('first')
        for file in files.next():
            print(f'directory: {files.filedir}, file: {files.filename}')
        # 2周目(無効)
        print('second')
        for file in files.next():
            print(f'directory: {files.filedir}, file: {files.filename}')


if __name__ == '__main__':
    usage()
