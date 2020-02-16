import subprocess

from pathlib import Path

from typing import (
    List,
    Tuple,
    Union,
)


class Source:
    def __init__(self, path: Union[List[Path], Path]):
        self.path = path
        p = path if isinstance(path, Path) else path[0]
        self.ext = p.suffix.lower()[1:]
        self.validate()

    def validate(self):
        def _val(p: Path):
            if not p.exists() or p.is_dir():
                raise Exception(f"invalid source: {p}")
        if isinstance(self.path, list):
            for p in self.path:
                _val(p)
        else:
            _val(self.path)


class Installer(Source):
    PLATFORM_WINDOWS = "windows"
    PLATFORM_LINUX = "linux"

    TYPE_INNOSETUP = "innosetup"
    TYPE_MOJOSETUP = "mojosetup"

    SUBTYPE_GOG = "gog"

    def __init__(self, path: Union[List[Path], Path]):
        super().__init__(path)
        self.platform = self.detect_platform()
        self.type, self.subtype = self.detect_installer_type()

    def detect_platform(self) -> str:
        if self.ext in ["exe", "msi"]:
            return self.PLATFORM_WINDOWS
        elif self.ext in ["sh"]:
            return self.PLATFORM_LINUX
        else:
            # TODO: try to detect dy source content
            raise Exception(f"can't detect installer platform: {self.path}")

    def detect_installer_type(self) -> Tuple[str, str]:
        itype = None
        subtype = None
        if self.platform == self.PLATFORM_WINDOWS:
            res = subprocess.run(["innoextract", "--gog-game-id", str(self.path)], stdout=subprocess.PIPE)
            res_str = res.stdout.decode("utf-8")
            if 'GOG.com game ID is' in res_str:
                itype = self.TYPE_INNOSETUP
                subtype = self.SUBTYPE_GOG
            elif 'No GOG.com game ID' in res_str:
                itype = self.TYPE_INNOSETUP
        elif self.platform == self.PLATFORM_LINUX:
            with open(self.path, 'rb') as f:
                head_data = f.read(500)
            if "GOG.com" in head_data.decode('utf-8'):
                itype = self.TYPE_MOJOSETUP
                subtype = self.SUBTYPE_GOG
        return itype, subtype


class Image(Source):
    def __init__(self, path: Union[List[Path], Path]):
        super().__init__(path)


def get(path: Union[List[Path], Path]) -> Source:
    p = path if isinstance(path, Path) else path[0]
    ext = p.suffix.lower()[1:]
    if ext:
        if ext in ["iso", "img", "cue"]:
            return Image(path)
        else:
            return Installer(path)
    else:
        # TODO: try to detect dy source data
        raise Exception(f"can't detect source type: {path}")
