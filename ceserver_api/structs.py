from construct import Struct, Int32sl, Int8ul, Int32ul, Int64sl, Int64ul, Float32l

# CeVersion
CeVersion = Struct(
    "version" / Int32sl,
    "stringsize" / Int8ul,
    # versionstring se lee por separado usando stringsize
)

# CeCreateToolhelp32Snapshot
CeCreateToolhelp32Snapshot = Struct(
    "dwFlags" / Int32ul,
    "th32ProcessID" / Int32ul,
)

# CeProcessEntry
CeProcessEntry = Struct(
    "result" / Int32sl,
    "pid" / Int32sl,
    "processnamesize" / Int32sl,
    # processname se lee por separado usando processnamesize
)

# CeModuleEntry
CeModuleEntry = Struct(
    "result" / Int32sl,
    "modulebase" / Int64sl,
    "modulepart" / Int32sl,
    "modulesize" / Int32sl,
    "modulefileoffset" / Int32ul,
    "modulenamesize" / Int32sl,
)

# CeVirtualQueryExInput
CeVirtualQueryExInput = Struct(
    "handle" / Int32sl,
    "baseaddress" / Int64ul,
)

# CeVirtualQueryExOutput
CeVirtualQueryExOutput = Struct(
    "result" / Int8ul,
    "protection" / Int32ul,
    "type" / Int32ul,
    "baseaddress" / Int64ul,
    "size" / Int64ul,
)

# CeVirtualQueryExFullInput
CeVirtualQueryExFullInput = Struct(
    "handle" / Int32sl,
    "flags" / Int8ul,
)

# CeVirtualQueryExFullOutput
CeVirtualQueryExFullOutput = Struct(
    "protection" / Int32ul,
    "type" / Int32ul,
    "baseaddress" / Int64ul,
    "size" / Int64ul,
)

# CeReadProcessMemoryInput
CeReadProcessMemoryInput = Struct(
    "handle" / Int32ul,
    "address" / Int64ul,
    "size" / Int32ul,
    "compress" / Int8ul,
)

# CeReadProcessMemoryOutput
CeReadProcessMemoryOutput = Struct(
    "read" / Int32sl,
)

# CeWriteProcessMemoryInput
CeWriteProcessMemoryInput = Struct(
    "handle" / Int32sl,
    "address" / Int64sl,
    "size" / Int32sl,
)

# CeWriteProcessMemoryOutput
CeWriteProcessMemoryOutput = Struct(
    "written" / Int32sl,
)

# CeSetBreapointInput (corrigiendo el typo en el nombre)
CeSetBreakpointInput = Struct(
    "hProcess" / Int32ul,
    "tid" / Int32sl,
    "debugreg" / Int32sl,
    "Address" / Int64ul,
    "bptype" / Int32sl,
    "bpsize" / Int32sl,
)

# CeSetBreapointOutput
CeSetBreakpointOutput = Struct(
    "result" / Int32sl,
)

# CeRemoveBreapointInput
CeRemoveBreakpointInput = Struct(
    "hProcess" / Int32ul,
    "tid" / Int32ul,
    "debugreg" / Int32ul,
    "wasWatchpoint" / Int32ul,
)

# CeRemoveBreapointOutput
CeRemoveBreakpointOutput = Struct(
    "result" / Int32sl,
)

# CeSuspendThreadInput
CeSuspendThreadInput = Struct(
    "hProcess" / Int32ul,
    "tid" / Int32sl,
)

# CeSuspendThreadOutput
CeSuspendThreadOutput = Struct(
    "result" / Int32sl,
)

# CeResumeThreadInput
CeResumeThreadInput = Struct(
    "hProcess" / Int32ul,
    "tid" / Int32sl,
)

# CeResumeThreadOutput
CeResumeThreadOutput = Struct(
    "result" / Int32sl,
)

# CeAllocInput
CeAllocInput = Struct(
    "hProcess" / Int32ul,
    "preferedBase" / Int64ul,
    "size" / Int32ul,
    "windowsprotection" / Int32ul,
)

# CeAllocOutput
CeAllocOutput = Struct(
    "address" / Int64ul,  # 0=fail
)

# CeFreeInput
CeFreeInput = Struct(
    "hProcess" / Int32ul,
    "address" / Int64ul,
    "size" / Int32ul,
)

# CeFreeOutput
CeFreeOutput = Struct(
    "result" / Int32ul,
)

# CeCreateThreadInput
CeCreateThreadInput = Struct(
    "hProcess" / Int32ul,
    "startaddress" / Int64ul,
    "parameter" / Int64ul,
)

# CeCreateThreadOutput
CeCreateThreadOutput = Struct(
    "threadhandle" / Int32ul,
)

# CeLoadModuleInput
CeLoadModuleInput = Struct(
    "hProcess" / Int32ul,
    "modulepathlength" / Int32ul,
    # modulepath se lee por separado usando modulepathlength
)

# CeLoadModuleInputEx
CeLoadModuleInputEx = Struct(
    "hProcess" / Int32ul,
    "dlopenaddress" / Int64ul,
    "modulepathlength" / Int32ul,
    # modulepath se lee por separado usando modulepathlength
)

# CeLoadModuleOutput
CeLoadModuleOutput = Struct(
    "result" / Int32ul,
)

# CeSpeedhackSetSpeedInput
CeSpeedhackSetSpeedInput = Struct(
    "hProcess" / Int32ul,
    "speed" / Float32l,
)

# CeSpeedhackSetSpeedOutput
CeSpeedhackSetSpeedOutput = Struct(
    "result" / Int32ul,
)

# CeChangeMemoryProtection
CeChangeMemoryProtection = Struct(
    "hProcess" / Int32ul,
    "address" / Int64ul,
    "size" / Int32ul,
    "windowsprotection" / Int32ul,
)

# CeReadPipe
CeReadPipe = Struct(
    "hPipe" / Int32ul,
    "size" / Int32ul,
    "timeout" / Int32ul,
)

# CeWritePipe
CeWritePipe = Struct(
    "hPipe" / Int32ul,
    "size" / Int32ul,
    "timeout" / Int32ul,
    # data[size] se lee por separado usando size
)

# CeAobScanInput
CeAobScanInput = Struct(
    "hProcess" / Int32ul,
    "start" / Int64ul,
    "end" / Int64ul,
    "inc" / Int32sl,
    "protection" / Int32sl,
    "scansize" / Int32sl,
)
