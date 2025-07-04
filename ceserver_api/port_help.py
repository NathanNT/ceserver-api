from enum import IntFlag


class TH32CS(IntFlag):
    SNAPPROCESS = 0x2
    SNAPTHREAD = 0x4
    SNAPMODULE = 0x8
    SNAPFIRSTMODULE = 0x40000000


class PageProtection(IntFlag):
    NOACCESS = 0x1
    READONLY = 0x2
    READWRITE = 0x4
    WRITECOPY = 0x8
    EXECUTE = 0x10
    EXECUTE_READ = 0x20
    EXECUTE_READWRITE = 0x40
