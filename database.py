DQ_MAX = 2 ** 64
BS_MAX = 2 ** 6
BS_SHIFT = 8
REG_MAX = 2 ** 14
USE_NEYMAN_COMMAND_ORDER = 1
USE_BOOL_CU = 1 << 1
USE_BOOL = {
    'JUMP': 0,
    'PS': 1 << 2,
    'DTC': 2 << 2,
    'KILL': 3 << 2
}
ALU_OPERATION = {
    '=': 0,
    '+': 1 << 4,
    '-': 2 << 4,
    '*': 3 << 4,
    '0': 4 << 4,
    '/': 5 << 4,
    '%': 6 << 4,
    '!': 7 << 4,
    '&': 8 << 4,
    '|': 9 << 4,
    '^': 10 << 4,
    '<': 11 << 4,
    '<<': 12 << 4,
    '>': 13 << 4,
    '>>': 14 << 4,
    'b#': 15 << 4
}
BOOL_OPERATION = {
    'FALSE': 0,
    'TRUE': 1 << 13,
    '[bit]': 2 << 13,
    '>': 3 << 13,
    '=': 4 << 13,
    '<': 5 << 13,
    '+': 6 << 13,
    '-': 7 << 13,
    '!': 8 << 13
}
WRITE_TO_RAM = 1 << 17
CASH_SOURCE = {
    'RAM': 0,
    'ALU': 1 << 18,
    'PC': 1 << 19
}
CLEAR_CASH = 1 << 20
WRITE_TO_CASH = 1 << 21
R_SHIFT = 22
OUT_REG_CHOOSE = {
    "A": 36,
    "B": 50
}
def dq(args, commands, out):
    try:
        return int(args[0]) % DQ_MAX
    except:
        for i in range(len(commands)):
            if commands[i][0] == args[0]:
                return i % DQ_MAX
        raise
def unco(args, commands, out):
    return USE_NEYMAN_COMMAND_ORDER
def mov(args, commands, out):
    reg_r = (int(args[0]) % REG_MAX) << R_SHIFT
    source = CASH_SOURCE.get(args[1])
    if source == None:
        raise
    return reg_r | WRITE_TO_CASH | source
def sel(args, commands, out):
    return (int(args[1]) % REG_MAX) << OUT_REG_CHOOSE.get(args[0])
def alu(args, commands, out):
    res = ALU_OPERATION.get(args[0])
    if res == None:
        raise
    return res
def bcv(args, commands, out):
    res = USE_BOOL.get(args[0])
    if res == None:
        raise
    return res | USE_BOOL_CU
def bs(args, commands, out):
    res = BOOL_OPERATION.get(args[0])
    select = (int(args[1]) % BS_MAX) << BS_SHIFT if len(args) > 1 else 0
    if res == None:
        raise
    return res | select
def write(args, commands, out):
    return WRITE_TO_RAM
def clr_cash(args, commands, out):
    return CLEAR_CASH
def goto(args, commands, out):
    for i in range(len(commands)):
        if commands[i][0] == args[0]:
            out.write(f"{hex(mov([args[1], 'RAM'], commands, out) | unco(args, commands, out))[2:]} ")
            out.write(f"{hex(dq([i], commands, out))[2:]} ")
            return bcv(["JUMP"], commands, out) | bs(["TRUE"], commands, out) | sel(["B", args[1]], commands, out)
    raise
instruction_list = {
    'dq': dq,
    'mov': mov,
    'unco': unco,
    'sel': sel,
    'alu': alu,
    'bcv': bcv,
    'bs': bs,
    'write': write,
    'clr_cash': clr_cash,
    'goto': goto
    #loop (like goto, but in case while(a--))
}