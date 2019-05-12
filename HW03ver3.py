# coding: utf-8

# In[1]:

# cmd line arg
import sys

# open input file
with open(sys.argv[-1], 'rt') as fileobj:
    file_content = fileobj.read()
address = 0  # if not 0, print the content in the address range of the memory
d = False  # if True, print registers after each instruction is executed
p = False  # if True, print pc of each pipeline stages after instruction is executed
if sys.argv[1] != '-atp' and sys.argv[1] != '-antp':
    print('No branch predictor option given. You should either give atp or antp as an option.')
    sys.exit()
branch_predict = sys.argv[1]  # -atp or -antp
num_instruction = -1  # -1 if no -n option given
for i in range(len(sys.argv)):
    if sys.argv[i] == '-m':
        address = sys.argv[i + 1]
    elif sys.argv[i] == '-d':
        d = True
    elif sys.argv[i] == '-n':
        num_instruction = int(sys.argv[i + 1])
    elif sys.argv[i] == '-p':
        p = True
if address:
    address2 = address.split(':')
    addr1 = int(address2[0], 16)
    addr2 = int(address2[1], 16)

registers = []
for i in range(32):
    registers.append(0)

# In[ ]:

instructions = file_content.splitlines()
text_section_size = int(instructions.pop(0), 16)
data_section_size = int(instructions.pop(0), 16)
text = instructions[:text_section_size // 4]
data = instructions[text_section_size // 4:]
memory = {}
for i in range(len(text)):
    memory[0x400000 + 4 * i] = int(text[i], 16)
for i in range(len(data)):
    memory[0x10000000 + 4 * i] = int(data[i], 16)

############################################## STEP 1 #################################################################
#
# 데이터를 읽어오고 분기예측기를 사용함
#
#######################################################################################################################

Cycles = [0]
PC = [0x400000]
CyclesPC = [None, None, None, None, None] # 각각 IF, ID, EX, MEM, WB의 pc 주소를 나타냄
PCSrc = [0]
BR_TARGET = [0]
JU_TARGET = [0]
ChangePC = [0]
Jump = [0]
End = []
ForwardA = [0]
ForwardB = [0]
Stall = [0]
Flush = [1]

IF_ID = {'Instr': 0, 'NPC': 0 , 'rs': 0, 'rt': 0}
ID_EX = {'NPC': 0, 'ReadData1': 0, 'ReadData2': 0, 'RegDst0': 0, 'RegDst1': 0, 'IMM':0, 'RegDst': 0, 'MemWrite': 0,
         'MemRead':0, 'MemtoReg': 0, 'RegWrite': 0, 'Branch':0, 'op':0, 'rs': 0,'rt': 0 , 'ALUSrc': 0}
EX_MEM = {'ALU_result': 0, 'MemWrite' : 0, 'MemRead': 0, 'MemtoReg': 0, 'RegWrite': 0, ' Branch': 0, 'WriteReg': 0,
          'WriteData': 0, 'Zero': 0, 'op': 0}
MEM_WB = {'WriteReg': 0, 'ReadData': 0, 'WriteData': 0, 'RegWrite' : 0, 'MemtoReg': 0}

def hex_(num):
    if type(num) == str:
        return num
    elif num == None: return ''
    return '{0:#0{1}x}'.format(num, 10)


# In[ ]:

# call when program terminates if address:
# call after each instruction has been executed if (d and address):
def print_mem(addr1):
    print('Memory Content [' + '{0:#0{1}x}'.format(addr1, 10) + '..' + '{0:#0{1}x}'.format(addr2, 10) + '] :')
    print('-------------------------------------')
    while addr1 <= addr2:
        if addr1 in memory:
            print(hex_(addr1) + ':', hex_(memory[addr1]))
        else:
            print(hex_(addr1) + ':', hex_(0))
        addr1 += 4
    print()


# In[ ]:

# call when program terminates
# call after each instruction has been executed if d:
def print_registers():
    print('Current register values :')
    print('-------------------------------------')
    print('PC:', hex_(PC[0]))
    print('Registers:')
    for i in range(32):
        if registers[i] < 0:
            print('R', i, ': ', hex_(registers[i] + 2 ** 32), sep = '')
        else:
            print('R', i, ': ', hex_(registers[i]), sep = '')
    print()


# In[ ]:

def print_pc():
    print('Current pipeline PC state :')
    print('-------------------------------------')
    print('CYCLE ', Cycles, ':', hex_(CyclesPC[0]), '|', hex_(CyclesPC[1]), '|', hex_(CyclesPC[2]), '|',
          hex_(CyclesPC[3]), '|', hex_(CyclesPC[4]), sep = '')
    print()


def control():
    if ID_EX['op'] == '000000':
        pass
    pass

def forward():
    pass

def IF():
    CyclesPC[0] = PC[0]
    if PC[0] not in memory:
        if Jump[0]:
            # jr
            if Jump[0] == 2:
                PC[0] = registers[31]
                # j, jal
            else:
                PC[0] = JU_TARGET[0]
        elif ID_EX['Branch']:
            if branch_predict == '-antp':
                CyclesPC[0] =  None
        else:
            CyclesPC[0] =  None
            End.append(1)
        return
    IF_ID.Instr = '{:0>32}'.format('{0:b}'.format(memory[PC[0]]))
    IF_ID.RegisterRs = int(IF_ID.Instr[6:11], 2)
    IF_ID.RegisterRt = int(IF_ID.Instr[11:16], 2)

    # hazard detect
    if (ID_EX['MemRead'] and (ID_EX['rt'] == IF_ID['rs'] or ID_EX['rt'] == IF_ID['rt'])):
        Stall[0] = 1

    if ChangePC[0]:
        PC.pop(0)
        IF_ID['Instr'] = '00000000000000000000000000000000'
    elif ID_EX['Branch']:
        if branch_predict == '-atp':
            PC.insert(0, BR_TARGET[0])
        else:
            PC.append(BR_TARGET[0])
            PC[0] = CyclesPC[0] + 4
    elif Stall[0] == 0:
        PC[0] = CyclesPC[0] + 4
    if Jump[0]:
        # jr
        if Jump[0] == 2:
            PC[0] = registers[31]
            # j, jal
        else:
            PC[0] = JU_TARGET[0]
    IF_ID['NPC'] = PC[0]

# asdf
def ID():
    if (ID_EX['Branch'] and branch_predict == '-atp') or Jump[0] or Stall[0] or ChangePC[0]:
        IF_ID['Instr'] = '00000000000000000000000000000000'
        Jump[0] = 0
        Stall[0] = 0
    if len(End) >= 1:
        CyclesPC[1] = None
        return
    ID_EX['NPC'] = IF_ID['NPC']
    ID_EX['rs'] = IF_ID['rs']
    ID_EX['rt'] = IF_ID['rt']
    ID_EX['ReadData1'] = registers[ID_EX['rs']]
    ID_EX['ReadData2'] = registers[ID_EX['rt']]
    ID_EX['RegDst0'] = ID_EX['RegisterRt']
    ID_EX['RegDst1'] = int(IF_ID['Instr'][16:21], 2)
    ID_EX['op'] = IF_ID['Instr'][:6]
    ID_EX['IMM'] = IF_ID['Instr'][16:]
    if int(ID_EX['IMM'][0]) == 0:
        imm = int(ID_EX['IMM'], 2)
    else:
        imm = int(ID_EX['IMM'], 2) - 2 ** 16
    BR_TARGET[0] = (imm << 2) + ID_EX['NPC']
    target = int(IF_ID['Instr'][6:], 2)
    bin_pc ='{:0>32}'.format('{0:b}'.format(PC[0]))
    JU_TARGET[0] = (int(bin_pc[:4], 2) << 28) + target << 2
    control()
    forward()
    CyclesPC[1] = CyclesPC[0]
    if IF_ID['Instr'] == '00000000000000000000000000000000':
        ID_EX['RegWrite'] = 0
        ID_EX['MemWrite'] = 0
        if Flush[0]:
            CyclesPC[1] = None


def EX():
    if Flush[0] == 0:
        CyclesPC[2] = None
        Flush[0] = 1
    else:
        CyclesPC[2] = CyclesPC[1]
    if ChangePC[0]:
        ID_EX.MemWrite = 0
        ID_EX.RegWrite = 0
        Flush[0] = 0
    if len(End) >= 2:
        return
    EX_MEM.MemWrite = ID_EX.MemWrite
    EX_MEM.RegWrite = ID_EX.RegWrite
    EX_MEM.MemRead = ID_EX.MemRead
    EX_MEM.MemtoReg = ID_EX.MemtoReg
    EX_MEM.Branch = ID_EX.Branch
    EX_MEM.WriteData = ID_EX.ReadData2
    EX_MEM.op = ID_EX.op
    if int(ID_EX.IMM[0]) == 0:
        imm = int(ID_EX.IMM, 2)
    else:
        imm = int(ID_EX.IMM, 2) - 2 ** 16
    # ForwardA
    if ForwardA[0] == '00':
        ALU1 = ID_EX.ReadData1
    elif ForwardA[0] == '10':
        ALU1 = EX_MEM.ALU_result
    else:
        ALU1 = registers[ID_EX.RegisterRs]
        # ForwardB
    if ForwardB[0] == '00':
        ALU2 = ID_EX.ReadData2
    elif ForwardB[0] == '10':
        ALU2 = EX_MEM.ALU_result
    else:
        ALU2 = registers[ID_EX.RegisterRt]
    if ID_EX.ALUSrc:
        ALU2 = imm
        # r_type
    if ID_EX.op == '000000':
        # jr
        if ID_EX.IMM[-6:] == '001000':
            return
        else:
            EX_MEM.ALU_result = func[ID_EX.IMM[-6:]](ALU1, ALU2)
    # j
    elif ID_EX.op == '000010':
        return
    # jal
    elif ID_EX.op == '000011':
        EX_MEM.WriteData = ID_EX.NPC

    # i_type
    else:
        EX_MEM.ALU_result = op_i[ID_EX.op](ALU1, ALU2)
    if ID_EX.RegDst == 0:
        EX_MEM.WriteReg = ID_EX.RegDst0
    else:
        EX_MEM.WriteReg = ID_EX.RegDst1


# In[ ]:

def MEM():
    if ChangePC[0]:
        # EX_MEM.RegWrite = 0
        # EX_MEM.MemWrite = 0
        CyclesPC[3] = '          '
        ChangePC[0] = 0
    else:
        CyclesPC[3] = CyclesPC[2]
    if len(end) >= 3:
        return
    MEM_WB.WriteReg = EX_MEM.WriteReg
    MEM_WB.WriteData = EX_MEM.ALU_result
    MEM_WB.RegWrite = EX_MEM.RegWrite
    MEM_WB.MemtoReg = EX_MEM.MemtoReg
    # jal
    if EX_MEM.op == '000011':
        MEM_WB.WriteData = EX_MEM.WriteData
        MEM_WB.WriteReg = 31
        # sw
    if EX_MEM.MemWrite:
        memory[EX_MEM.ALU_result] = EX_MEM.WriteData
    # lw
    if EX_MEM.MemRead:
        MEM_WB.ReadData = memory[EX_MEM.ALU_result]
    if len(PCSrc) > 1:
        PCSrc.append(EX_MEM.Branch & EX_MEM.Zero)
    else:
        PCSrc[0] = EX_MEM.Branch & EX_MEM.Zero
    if EX_MEM.op in ['000100', '000101']:
        # when mispredicted
        if (branch_predict == '-atp' and PCSrc[0] == 0) or (branch_predict == '-antp' and PCSrc[0] == 1):
            ChangePC[0] = 1
        else:
            pc.pop(1)


# In[ ]:

def WB():
    WB_PC[0] = CyclesPC[3]
    if MEM_WB.RegWrite:
        if MEM_WB.MemtoReg:
            registers[MEM_WB.WriteReg] = MEM_WB.ReadData
        else:
            registers[MEM_WB.WriteReg] = MEM_WB.WriteData


# In[ ]:

# actual execution
while Cycles[0] < num_instruction or num_instruction == -1:
    if Cycles[0] >= 4:
        WB()
    if Cycles[0] >= 3:
        MEM()
    if Cycles[0] >= 2:
        EX()
    if Cycles[0] >= 1:
        ID()
    IF()
    Cycles[0] += 1
    if p:
        print_pc()
    if d:
        print_registers()
        if address:
            print_mem(addr1)
    if CyclesPC[0] == CyclesPC[1] == CyclesPC[2] == CyclesPC[3] == '          ':
        WB_PC[0] = '          '
        break

# In[ ]:

# when program terminates
print('Completion Cycle:', Cycles[0])
print()
print_pc()
print_registers()
if address:
    print_mem(addr1)
