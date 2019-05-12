
# coding: utf-8

# In[1]:

# cmd line arg
import sys
# open input file
with open(sys.argv[-1], 'rt') as fileobj:
    file_content = fileobj.read()
address = 0 # if not 0, print the content in the address range of the memory
d = False # if True, print registers after each instruction is executed
p = False # if True, print pc of each pipeline stages after instruction is executed
if sys.argv[1] != '-atp' and sys.argv[1] != '-antp':
    print('No branch predictor option given. You should either give atp or antp as an option.')
    sys.exit()
branch_predict = sys.argv[1] # -atp or -antp
num_instruction = -1 # -1 if no -n option given
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


# In[ ]:

# global variables
cycles = [0]
IF_pc = ['          ']
ID_pc = ['          ']
EX_pc = ['          ']
MEM_pc = ['          ']
WB_pc = ['          ']
pc = [0x400000]
PCSrc = [0] # when branch taken 1
BR_TARGET = [0]
JU_TARGET = [0]
change_pc = [0] # time to change pc when 1
Jump = [0] 
end = []
ForwardA = [0]
ForwardB = [0]
stall = [0]
Flush = [1] # flush when 0


# In[ ]:

def hex_(num):
    if type(num) == str:
        return num
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
    print('PC:', hex_(pc[0]))
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
    print('CYCLE ', cycles[0], ':', hex_(IF_pc[0]), '|', hex_(ID_pc[0]), '|', hex_(EX_pc[0]), '|', hex_(MEM_pc[0]), '|', hex_(WB_pc[0]), sep = '')
    print()


# In[ ]:

class IF_ID:
    Instr = 0
    NPC = 0
    RegisterRs = 0
    RegisterRt = 0


# In[ ]:

class ID_EX:
    NPC = 0
    ReadData1 = 0
    ReadData2 = 0
    RegDst0 = 0
    RegDSt1 = 0
    IMM = 0
    RegDst = 0
    MemWrite = 0
    MemRead = 0
    MemtoReg = 0
    RegWrite = 0
    Branch = 0
    op = 0
    RegisterRs = 0
    RegisterRt = 0
    ALUSrc = 0


# In[ ]:

class EX_MEM:
    ALU_result = 0
    MemWrite = 0
    MemRead = 0
    MemtoReg = 0
    RegWrite = 0
    Branch = 0   
    WriteReg = 0
    WriteData = 0
    Zero = 0
    op = 0


# In[ ]:

class MEM_WB:
    WriteReg = 0
    ReadData = 0
    WriteData = 0
    RegWrite = 0
    MemtoReg = 0


# In[ ]:

def add(ALU1, ALU2):
    return ALU1 + ALU2 


# In[ ]:

def and_(ALU1, ALU2):
    return ALU1 & ALU2


# In[ ]:

def beq(ALU1, ALU2):
    EX_MEM.Zero = sub(ALU1, ALU2) == 0


# In[ ]:

def bne(ALU1, ALU2):
    EX_MEM.Zero = (sub(ALU1, ALU2) != 0)


# In[ ]:

def lui(ALU1, ALU2):
    return ALU2 << 16


# In[ ]:

def nor(ALU1, ALU2):
    return  ~(ALU1 | ALU2)


# In[ ]:

def or_(ALU1, ALU2):
    return ALU1 | ALU2


# In[ ]:

def slt(ALU1, ALU2):
    if sub(ALU1, ALU2) < 0:
        return 1
    else:
        return 0


# In[ ]:

def sll(ALU1, ALU2):
    shamt = int(ID_EX.IMM[5:10], 2)
    return ALU2 << shamt


# In[ ]:

def srl(ALU1, ALU2):
    shamt = int(ID_EX.IMM[5:10], 2)
    return ALU2 >> shamt


# In[ ]:

def sub(ALU1, ALU2):
    return ALU1 - ALU2


# In[ ]:

op_i = {'001001': add , '001100': and_, '000100': beq, '000101': bne, '001111': lui, '100011': add, '001101': or_, '001011': slt, '101011': add}


# In[ ]:

func = {'100001': add, '100100': and_, '100111': nor, '100101': or_, '101011': slt, '000000': sll, '000010': srl, '100011': sub}


# In[ ]:

# detects load-use hazard
def hazard():
    if (ID_EX.MemRead
       and (ID_EX.RegisterRt == IF_ID.RegisterRs
           or ID_EX.RegisterRt == IF_ID.RegisterRt)):
        # stall the pipeline
        stall[0] = 1


# In[ ]:

# set control signals
def control():
    # r_type
    if ID_EX.op == '000000': # DY: R 타입인 경우
        ID_EX.RegDst = 1
        ID_EX.RegWrite = 1
        ID_EX.MemRead = 0
        ID_EX.MemWrite = 0
        ID_EX.MemtoReg = 0
        ID_EX.ALUSrc = 0
        ID_EX.Branch = 0
        # jr
        if IF_ID.Instr[-6:] == '001000':
            ID_EX.RegWrite = 0
            Jump[0] = 2
    # j_type
    elif ID_EX.op in ['000010', '000011']:
        ID_EX.Branch = 0
        ID_EX.RegWrite = 0
        ID_EX.MemRead = 0
        ID_EX.MemWrite = 0
        Jump[0] = 1
        # jal
        if ID_EX.op == '000011':
            ID_EX.RegWrite = 1
    # i_type
    else:
        ID_EX.RegDst = 0
        ID_EX.RegWrite = 1
        ID_EX.MemRead = 0
        ID_EX.MemWrite = 0
        ID_EX.MemtoReg = 0
        ID_EX.ALUSrc = 1
        ID_EX.Branch = 0
        # sw, beq, bne
        if ID_EX.op in ['101011', '000100', '000101']:
            ID_EX.RegWrite = 0
            # sw
            if ID_EX.op == '101011':
                ID_EX.MemWrite = 1
            # beq, bne
            else:
                ID_EX.Branch = 1
                ID_EX.ALUSrc = 0
        # lw
        if ID_EX.op == '100011':
            ID_EX.MemRead = 1
            ID_EX.MemtoReg = 1    
    if change_pc[0]:
        ID_EX.MemWrite = 0
        ID_EX.RegWrite = 0


# In[ ]:

# forwarding unit
def forward():
    # ForwardA
    # EX hazard
    if (EX_MEM.RegWrite
       and EX_MEM.WriteReg != 0
       and EX_MEM.WriteReg == ID_EX.RegisterRs):
        ForwardA[0] = '10'
    # MEM hazard
    elif (MEM_WB.RegWrite
         and MEM_WB.WriteReg != 0
         and not (EX_MEM.RegWrite and EX_MEM.WriteReg != 0
                 and EX_MEM.WriteReg == ID_EX.RegisterRs)
         and MEM_WB.WriteReg == ID_EX.RegisterRs):
        ForwardA[0] = '01'
    # no hazard
    else:
        ForwardA[0] = '00'
    # ForwardB
    # EX hazard
    if (EX_MEM.RegWrite
       and EX_MEM.WriteReg != 0
       and EX_MEM.WriteReg == ID_EX.RegisterRt):
        ForwardB[0] = '10'
    # MEM hazard 
    elif (MEM_WB.RegWrite
         and MEM_WB.WriteReg != 0
         and not (EX_MEM.RegWrite and EX_MEM.WriteReg != 0
                 and EX_MEM.WriteReg == ID_EX.RegisterRt)
         and MEM_WB.WriteReg == ID_EX.RegisterRt):
        ForwardB[0] = '01'
    # no hazard
    else:
        ForwardB[0] = '00'


# In[ ]:

def IF():
    IF_pc[0] = pc[0]
    if pc[0] not in memory:
        if Jump[0]:
            # jr
            if Jump[0] == 2:
                pc[0] = registers[31] 
            # j, jal
            else:
                pc[0] = JU_TARGET[0] 
        elif ID_EX.Branch:
            if branch_predict == '-antp':
                IF_pc[0] = '          '
        else:
            IF_pc[0] = '          '
            end.append(1)
        return 
    IF_ID.Instr = '{:0>32}'.format('{0:b}'.format(memory[pc[0]]))
    IF_ID.RegisterRs = int(IF_ID.Instr[6:11], 2)
    IF_ID.RegisterRt = int(IF_ID.Instr[11:16], 2)
    hazard()
    if change_pc[0]:
        pc.pop(0)
        IF_ID.Instr = '00000000000000000000000000000000'
    elif ID_EX.Branch:
        if branch_predict == '-atp':
            pc.insert(0, BR_TARGET[0])
        else:
            pc.append(BR_TARGET[0]) 
            pc[0] = IF_pc[0] + 4
    elif stall[0] == 0:
        pc[0] = IF_pc[0] + 4
    if Jump[0]:
        # jr
        if Jump[0] == 2:
            pc[0] = registers[31] 
        # j, jal
        else:
            pc[0] = JU_TARGET[0] 
    IF_ID.NPC = pc[0]


# In[ ]:

def ID():
    if (ID_EX.Branch and branch_predict == '-atp') or Jump[0] or stall[0] or change_pc[0]:
        IF_ID.Instr = '00000000000000000000000000000000'
        Jump[0] = 0
        stall[0] = 0
    if len(end) >= 1:
        ID_pc[0] = '          '
        return
    ID_EX.NPC = IF_ID.NPC
    ID_EX.RegisterRs = IF_ID.RegisterRs
    ID_EX.RegisterRt = IF_ID.RegisterRt
    ID_EX.ReadData1 = registers[ID_EX.RegisterRs]
    ID_EX.ReadData2 = registers[ID_EX.RegisterRt]
    ID_EX.RegDst0 = ID_EX.RegisterRt
    ID_EX.RegDst1 = int(IF_ID.Instr[16:21], 2)
    ID_EX.op = IF_ID.Instr[:6]
    ID_EX.IMM = IF_ID.Instr[16:]
    if int(ID_EX.IMM[0]) == 0:
        imm = int(ID_EX.IMM, 2)
    else:
        imm = int(ID_EX.IMM, 2) - 2 ** 16
    BR_TARGET[0] = (imm << 2) + ID_EX.NPC
    target = int(IF_ID.Instr[6:], 2)
    bin_pc ='{:0>32}'.format('{0:b}'.format(pc[0]))
    JU_TARGET[0] = (int(bin_pc[:4], 2) << 28) + target << 2
    control()
    forward()
    ID_pc[0] = IF_pc[0]
    if IF_ID.Instr == '00000000000000000000000000000000':
        ID_EX.RegWrite = 0
        ID_EX.MemWrite = 0
        if Flush[0]:
            ID_pc[0] = '          '


# In[ ]:

def EX():
    if Flush[0] == 0:
        EX_pc[0] = '          '
        Flush[0] = 1
    else:
        EX_pc[0] = ID_pc[0]
    if change_pc[0]:
        ID_EX.MemWrite = 0
        ID_EX.RegWrite = 0
        Flush[0] = 0
    if len(end) >= 2:
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
    if change_pc[0]:
        #EX_MEM.RegWrite = 0
        #EX_MEM.MemWrite = 0
        MEM_pc[0] = '          '
        change_pc[0] = 0
    else:
        MEM_pc[0] = EX_pc[0]
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
            change_pc[0] = 1
        else:
            pc.pop(1)


# In[ ]:

def WB():
    WB_pc[0] = MEM_pc[0]
    if MEM_WB.RegWrite:
        if MEM_WB.MemtoReg:
            registers[MEM_WB.WriteReg] = MEM_WB.ReadData
        else:
            registers[MEM_WB.WriteReg] = MEM_WB.WriteData


# In[ ]:

# actual execution
while cycles[0] < num_instruction or num_instruction == -1:
    if cycles[0] >= 4:
        WB()
    if cycles[0] >= 3:
        MEM()
    if cycles[0] >= 2:
        EX()
    if cycles[0] >= 1:
        ID()
    IF()
    cycles[0] += 1
    if p:
        print_pc()
    if d:
        print_registers()
        if address:
            print_mem(addr1)
    if IF_pc[0] == ID_pc[0] == EX_pc[0] == MEM_pc[0] == '          ':
        WB_pc[0] = '          '
        break


# In[ ]:

# when program terminates
print('Completion Cycle:', cycles[0])
print()
print_pc()
print_registers()
if address:
    print_mem(addr1)

