import logging
import struct
from socket import socket, AF_INET, SOCK_STREAM

from .commands import CeserverCommand as CE_CMD
from .data_classes import ProcessInfo, ModuleInfo
from .port_help import TH32CS
from .structs import CeVersion, CeProcessEntry, CeReadProcessMemoryInput, CeModuleEntry, CeCreateToolhelp32Snapshot, CeWriteProcessMemoryInput, CeWriteProcessMemoryOutput


class CEServerClient:
    def __init__(self, host='127.0.0.1', port=52736):
        self.log = logging.getLogger(__name__)
        self._sock: socket | None = None
        self.host: str = host
        self.port: int = port
        self.pid: int | None = None
        self.handle: int | None = None

        logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S')

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def _send_command(self, command: CE_CMD, payload=b''):
        self._sock.sendall(command.to_bytes() + payload)

    def connect(self):
        self._sock = socket(AF_INET, SOCK_STREAM)
        self._sock.settimeout(2)
        self._sock.connect((self.host, self.port))
        self.log.info(f"Connected to ceserver in {self.host}:{self.port}")
        self.get_version()

    def get_version(self):
        self._send_command(CE_CMD.CMD_GETVERSION)
        data = self._sock.recv(CeVersion.sizeof())
        ce_version = CeVersion.parse(data)
        version_string = self._sock.recv(ce_version.stringsize)
        self.log.info(f"Server version: {version_string.decode()}")

    def is_android(self) -> bool:
        self._send_command(CE_CMD.CMD_ISANDROID)
        data = self._sock.recv(1)
        return bool(data[0])

    def disconnect(self):
        self._send_command(CE_CMD.CMD_CLOSECONNECTION)
        self._sock.close()
        self.log.info("Disconnected.")

    def enumerate_processes(self) -> list[ProcessInfo]:
        # Paso 1: snapshot
        data = {
            "dwFlags": TH32CS.SNAPPROCESS,
            "th32ProcessID": 0
        }
        payload = CeCreateToolhelp32Snapshot.build(data)
        self._send_command(CE_CMD.CMD_CREATETOOLHELP32SNAPSHOTEX, payload)
        snapshot_handle = self._sock.recv(4)
        processes = []
        # next process
        self._send_command(CE_CMD.CMD_PROCESS32FIRST, snapshot_handle)
        ce_process_entry = self._recv_process_entry()
        if ce_process_entry.result:
            process_name = self._sock.recv(ce_process_entry.processnamesize).decode()
            name = process_name.split()[-1].split('/')[-1]
            processes.append(ProcessInfo(ce_process_entry.pid, name))
            while ce_process_entry.result:
                self._send_command(CE_CMD.CMD_PROCESS32NEXT, snapshot_handle)
                ce_process_entry = self._recv_process_entry()
                if ce_process_entry.result:
                    process_name = self._sock.recv(ce_process_entry.processnamesize).decode()
                    name = process_name.split()[-1].split('/')[-1]
                    processes.append(ProcessInfo(ce_process_entry.pid, name))
        self.close_handle(snapshot_handle)

        return processes

    def _recv_process_entry(self) -> CeProcessEntry:
        size = CeProcessEntry.sizeof()
        data = self._sock.recv(size)
        ce_process_entry = CeProcessEntry.parse(data)
        return ce_process_entry

    def enumerate_modules(self) -> list[ModuleInfo]:
        data = {
            "dwFlags": TH32CS.SNAPMODULE,
            "th32ProcessID": self.pid
        }
        payload = CeCreateToolhelp32Snapshot.build(data)
        self._send_command(CE_CMD.CMD_CREATETOOLHELP32SNAPSHOTEX, payload)
        modules = []
        ce_module_entry = self._recv_module_entry()
        while ce_module_entry.result:
            module_name = self._sock.recv(ce_module_entry.modulenamesize).decode()
            if module_name != "[vdso]":
                name = module_name.split('/')[-1]
                modules.append(ModuleInfo(
                    ce_module_entry.modulebase,
                    ce_module_entry.modulepart,
                    ce_module_entry.modulesize,
                    ce_module_entry.modulefileoffset,
                    name
                ))
            ce_module_entry = self._recv_module_entry()

        return modules

    def _recv_module_entry(self) -> CeModuleEntry:
        size = CeModuleEntry.sizeof()
        data = self._sock.recv(size)
        ce_module_entry = CeModuleEntry.parse(data)
        return ce_module_entry

    def get_module_base(self, module_name: str) -> int | None:
        modules = self.enumerate_modules()
        for module in modules:
            if module_name in module.name:
                self.log.info(f"Module found: {hex(module.base)} - {module.name}")
                return module.base
        return None

    def close_handle(self, handle: bytes):
        self._send_command(CE_CMD.CMD_CLOSEHANDLE, handle)
        self._sock.recv(4)

    def get_handle(self, process_name: str):
        processes_list = self.enumerate_processes()
        for process_info in processes_list:
            name = process_info.name
            pid = process_info.pid
            if process_name in name:
                self.pid = pid
                self.open_process()
                self.log.info(f"Process found: {pid} - {name}")
                return
        raise Exception("Process not found.")

    def open_process(self):
        self._send_command(CE_CMD.CMD_OPENPROCESS, self.pid.to_bytes(4, byteorder='little'))
        raw_handle = self._sock.recv(4)
        self.handle = struct.unpack("<L", raw_handle)[0]

    # Read Section
    def _read_process_memory(self, address: int, size: int, compress: int = 0) -> bytes | None:
        data = {
            "handle": self.handle,
            "address": address,
            "size": size,
            "compress": compress
        }

        payload = CeReadProcessMemoryInput.build(data)
        self._send_command(CE_CMD.CMD_READPROCESSMEMORY, payload)
        value = self._recv_read_response()
        return value

    def _recv_read_response(self) -> bytes | None:
        response_size = struct.unpack("<L", self._sock.recv(4))[0]
        if response_size == 0:
            return
        value = self._sock.recv(response_size)
        return value

    def read_byte(self, address: int, compress: int = 0) -> int | None:
        data = self._read_process_memory(address, 1, compress)
        if data is None:
            return None
        return struct.unpack('<B', data)[0]

    def read_int16(self, address: int, compress: int = 0, signed: bool = True) -> int | None:
        data = self._read_process_memory(address, 2, compress)
        if data is None:
            return None
        fmt = "<h" if signed else "<H"
        return struct.unpack(fmt, data)[0]

    def read_uint16(self, address: int, compress: int = 0) -> int | None:
        return self.read_int16(address, compress, False)

    def read_int32(self, address: int, compress: int = 0, signed: bool = True) -> int | None:
        value = self._read_process_memory(address, 4, compress)
        if value is None:
            return None
        fmt = "<l" if signed else "<L"
        return struct.unpack(fmt, value)[0]

    def read_uint32(self, address: int, compress: int = 0) -> int | None:
        return self.read_int32(address, compress, False)

    def read_int64(self, address: int, compress: int = 0, signed: bool = True) -> int | None:
        value = self._read_process_memory(address, 8, compress)
        if value is None:
            return None
        fmt = "<q" if signed else "<Q"
        return struct.unpack(fmt, value)[0]

    def read_uint64(self, address: int, compress: int = 0) -> int | None:
        return self.read_int64(address, compress, False)

    def read_float(self, address: int, compress: int = 0) -> float | None:
        value = self._read_process_memory(address, 4, compress)
        if value is None:
            return None
        return struct.unpack("<f", value)[0]

    def read_double(self, address: int, compress: int = 0) -> float | None:
        value = self._read_process_memory(address, 8, compress)
        if value is None:
            return None
        return struct.unpack("<d", value)[0]

    def read_bytes(self, address: int, length: int, compress: int = 0):
        return self._read_process_memory(address, length, compress)

    def read_str(self, address: int, length: int = 256, unicode=False, compress: int = 0) -> str | None:
        data = self.read_bytes(address, length, compress)
        if data is None:
            return None

        try:
            string_bytes = data.split(b'\x00', 1)[0]  # cortar en nulo si existe
            encoding = "utf-16" if unicode else "utf-8"
            return string_bytes.decode(encoding, errors='ignore')
        except Exception as e:
            self.log.error(f"[!] Error decoding string: {e}")
            return None

    def read_ptr(self, address: int, compress: int = 0) -> int | None:
        ptr = self.read_uint64(address, compress)
        MIN_ADDR = 0x10000
        if ptr is None or ptr < MIN_ADDR:
            return None
        return ptr

    def read_pointer_chain(self, base: int, offsets: list[int], compress: int = 0) -> int | None:
        addr = base
        for off in offsets:
            ptr = self.read_ptr(addr + off, compress)
            if ptr is None:
                return None
            addr = ptr
        return addr

    # Write Section
    def _write_process_memory(self, address: int, size: int, value: bytes) -> CeWriteProcessMemoryOutput:
        data = {
            "handle": self.handle,
            "address": address,
            "size": size,
        }

        payload = CeWriteProcessMemoryInput.build(data)
        self._send_command(CE_CMD.CMD_WRITEPROCESSMEMORY, payload)
        self._sock.sendall(value)
        response = self._recv_write_response()
        return response

    def _recv_write_response(self) -> CeWriteProcessMemoryOutput:
        r_size = CeWriteProcessMemoryOutput.sizeof()
        r_bytes = self._sock.recv(r_size)
        response = CeWriteProcessMemoryOutput.parse(r_bytes)
        return response

    def write_bytes(self, address: int, value: bytes) -> CeWriteProcessMemoryOutput:
        size = len(value)
        return self._write_process_memory(address, size, value)

    def write_byte(self, address: int, value: bytes) -> CeWriteProcessMemoryOutput:
        size = len(value)
        if size > 1:
            raise Exception("The value to send exceeds the size of a single byte")
        return self._write_process_memory(address, size, value)

    def write_int16(self, address: int, value: int, signed=True) -> CeWriteProcessMemoryOutput:
        s_bytes = value.to_bytes(2, byteorder='little', signed=signed)
        size = len(s_bytes)
        if size > 2:
            raise Exception("The value to send exceeds the size of an int16")
        return self._write_process_memory(address, size, s_bytes)

    def write_uint16(self, address: int, value: int) -> CeWriteProcessMemoryOutput:
        return self.write_int16(address, value, signed=False)

    def write_int32(self, address: int, value: int, signed=True) -> CeWriteProcessMemoryOutput:
        s_bytes = value.to_bytes(4, byteorder='little', signed=signed)
        size = len(s_bytes)
        if size > 4:
            raise Exception("The value to send exceeds the size of an int32")
        return self._write_process_memory(address, size, s_bytes)

    def write_uint32(self, address: int, value: int) -> CeWriteProcessMemoryOutput:
        return self.write_int32(address, value, signed=False)

    def write_int64(self, address: int, value: int, signed=True) -> CeWriteProcessMemoryOutput:
        s_bytes = value.to_bytes(8, byteorder='little', signed=signed)
        size = len(s_bytes)
        if size > 8:
            raise Exception("The value to send exceeds the size of an int64")
        return self._write_process_memory(address, size, s_bytes)

    def write_uint64(self, address: int, value: int) -> CeWriteProcessMemoryOutput:
        return self.write_int64(address, value, signed=False)

    def write_float(self, address: int, value: float) -> CeWriteProcessMemoryOutput:
        s_bytes = struct.pack('<f', value)
        size = len(s_bytes)
        if size > 4:
            raise Exception("The value to send exceeds the size of a float")
        return self._write_process_memory(address, size, s_bytes)

    def write_double(self, address: int, value: float) -> CeWriteProcessMemoryOutput:
        s_bytes = struct.pack('<d', value)
        size = len(s_bytes)
        if size > 8:
            raise Exception("The value to send exceeds the size of a double")
        return self._write_process_memory(address, size, s_bytes)

    def write_str(self, address: int, value: str, unicode=False) -> CeWriteProcessMemoryOutput:
        encode = 'utf-8' if not unicode else 'utf-16'
        s_bytes = value.encode(encoding=encode)
        size = len(s_bytes)
        return self._write_process_memory(address, size, s_bytes)

    # Options Section
    def _recv_string16(self) -> str:
        length_bytes = self._sock.recv(2)
        length = struct.unpack('<H', length_bytes)[0]
        raw = self._sock.recv(length)
        return raw.decode('utf-8', errors='replace')

    def get_options(self) -> list[dict]:
        self._send_command(CE_CMD.CMD_GETOPTIONS, b'\x00\x00\x00')

        count_data = self._sock.recv(2)
        option_count = struct.unpack('<H', count_data)[0]

        options = []
        for i in range(option_count):
            opt = {
                "name": self._recv_string16(),
                "parent": self._recv_string16(),
                "description": self._recv_string16(),
                "acceptable_values": self._recv_string16(),
                "current_value": self._recv_string16(),
                "type": struct.unpack('<I', self._sock.recv(4))[0],
            }
            options.append(opt)

        return options

    def _send_string16(self, text: str):
        encoded = text.encode('utf-8')
        length = len(encoded)
        self._sock.sendall(struct.pack('<H', length))
        if length:
            self._sock.sendall(encoded)

    def get_option_value(self, option_name: str) -> str | None:
        self._send_command(CE_CMD.CMD_GETOPTIONVALUE)

        self._send_string16(option_name)

        result = self._recv_string16()
        return result if result else None

    def set_option_value(self, option_name: str, value: str):
        self._send_command(CE_CMD.CMD_SETOPTIONVALUE)

        # 2. Enviar optname y value como string16 (uint16_len + utf-8 bytes)
        self._send_string16(option_name)
        self._send_string16(value)
