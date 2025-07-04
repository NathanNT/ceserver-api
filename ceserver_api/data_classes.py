from dataclasses import dataclass


@dataclass
class ProcessInfo:
    pid: int
    name: str


@dataclass
class ModuleInfo:
    base: int
    part: int
    size: int
    file_offset: int
    name: str
