from dataclasses import dataclass


@dataclass
class Request:
    url: str
    isrc: str
    name: str
    artist: str

    def __str__(self):
        return f"{self.name} - {self.artist} [{self.isrc}]"


@dataclass
class Download:
    source: str
    path: str
