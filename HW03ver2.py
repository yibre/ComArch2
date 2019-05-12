# Step 1: Memory는 Dictionary 형태로
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

registers = [0] * 32

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
##################################################### STEP 1 ################################################
#           memory가 글로벌 변수에 해당함
#           메모리는 딕셔너리 형태로 가져옴, 옵션은 -atp, -antp, n, d, 등등이 있음
#
###########################################################################################################

# TODO: 현재 라인이 세진선배가 한 것의 50번째 줄까지에 해당함

class PipeLine :
    def __init__(self):
        self.cycles = 0
        self.IF_pc = None # 빈공간에서 none으로 바꿈
        self.ID_pc = None
        self.EX_pc = None
        self.MEM_pc = None
        self.WB_pc = None
        self.PC = [0x400000]
        self.PCSrc = 0
        self.BR_TARGET = 0
        self.JU_TARGET = 0
        self.change_pc = [0]
        self.Jump = 0
        self.end = []
        self.ForwardA = 0
        self.ForwardB = 0
        self.stall = 0
        self.Flush = 1  # end를 제외하곤 전부 리스트형임.

        # 한 번 생성되는 객체들, 각 파이프라인 레지스터를 설정함
        self.IF_ID = {'Instr': 0, 'NPC': 0 , 'rs': 0, 'rt': 0}
        self.ID_EX = {'NPC': 0, 'ReadData1': 0, 'ReadData2' : 0, 'RegDst0': 0, 'RegDst1' : 0, 'IMM':0, 'RegDst' : 0,
                      'MemWrite': 0 , 'MemRead':0, 'MemtoReg' : 0, 'RegWrite':0, 'Branch':0, 'op':0, 'rs': 0 ,
                      'rt': 0 , 'ALUSrc':0}
        self.EX_MEM = {'ALU_result': 0, 'MemWrite' : 0, 'MemRead' : 0, 'MemtoReg' : 0, 'RegWrite' : 0, ' Branch':0,
                       'WriteReg' : 0, 'WriteData' : 0, 'Zero': 0, 'op': 0}
        self.MEM_WB = {'WriteReg' : 0, 'ReadData' : 0, 'WriteData': 0, 'RegWrite' : 0, 'MemtoReg' : 0}

    def hex_(self, num): # pc 주소를 쓰는데 사용함
        if type(num) == str:
            return num
        if num == None:
            return
        return '{0:#0{1}x}'.format(num, 10) # 10자리 수의 0x~~~ 꼴로 리턴함

    def print_mem(self, addr1):
        print('Memory Content [' + '{0:#0{1}x}'.format(addr1, 10) + '..' + '{0:#0{1}x}'.format(addr2, 10) + '] :')
        print('-------------------------------------')
        while addr1 <= addr2:
            if addr1 in memory:
                print(self.hex_(addr1) + ':', self.hex_(memory[addr1]))
            else:
                print(self.hex_(addr1) + ':', self.hex_(0))
            addr1 += 4
        print()

    def print_pc(self):
        print('Current pipeline PC state :')
        print('-------------------------------------')
        print('CYCLE ', self.cycles[0], ':', self.hex_(self.IF_pc), '|', self.hex_(self.ID_pc), '|', self.hex_(self.EX_pc[0]),
              '|', self.hex_(self.MEM_pc),'|', self.hex_(self.WB_pc), sep='')
        print()

    # TODO: 세진선배 181~260 코드까지 구현 안함

    ########################################### STEP 2 ################################################################
    #
    #                                           PRINT 관련 함수 구현 완료
    #
    ###################################################################################################################

    def hazard(self): # load- use hazard 발생시 1회 stall
        if (self.ID_EX['MemRead'] and (self.ID_EX['rt'] == self.IF_ID['rs'] or self.ID_EX['rt'] == self.IF_ID['rt'])):
            self.stall = 1
            # stall the pipeline

    def control(self):
        pass
    # TODO: 세진선배 control 함수 구현하기 instruction이 J, Jal 일 경우 점프함

    def forward(self):
        if (self.EX_MEM['RegWrite'] and (self.EX_MEM['RegWrite'] != 0 and self.EX_MEM['WriteReg'] == self.ID_EX['rs'])):
            self.ForwardA = '10'
        elif (self.MEM_WB['RegWrite'] and self.MEM_WB['WriteReg'] != 0
                and not (self.EX_MEM['RegWrite'] and self.EX_MEM['WriteReg'] != 0)
                and self.EX_MEM['WriteReg'] == self.ID_EX['rs'] and self.MEM_WB['WriteReg'] == self.ID_EX['rs']):
            self.ForwardA = '01'
        else: self. ForwardA = '00'

        # Forward B, EX hazard
        if (self.EX_MEM['RegWrite'] and self.EX_MEM['WriteReg'] != 0 and self.EX_MEM['WriteReg'] == self.ID_EX['rt']):
            self.ForwardB = '10'
        elif (self.MEM_WB['RegWrite'] and self.MEM_WB['RegWrite'] != 0
              and not (self.EX_MEM['RegWrite'] and self.EX_MEM['WriteReg'] != 0
                       and self.EX_MEM['WriteReg'] == self.ID_EX['rt'])
              and self.MEM_WB['WriteReg'] == self.ID_EX['rt']):
            self.ForwardB = '01'
        else: self.ForwardB = '00'

    def IF(self):
        self.IF_pc =  self.PC[0]
        if self.PC[0] not in memory:
            if self.Jump:
                # jr
                if self.Jump == 2:
                    self.PC[0] = registers[31]
                else: self.PC[0] = self.JU_TARGET
            elif self.ID_EX['Branch']:
                if branch_predict == '-antp':
                    self.IF_pc = None
            else:
                self.IF_pc = None
                self.end.append(1)
            return
        self.IF_ID['Instr'] = '{:0>32}'.format('{0:b}'.format(memory[self.PC[0]]))
        self.IF_ID['rs'] = int(self.IF_ID['Instr'][6:11], 2)
        self.IF_ID['rt'] = int(self.IF_ID['Instr'][11:16], 2)
        self.hazard()

        if self.change_pc[0]:
            self.change_pc.pop(0)
            self.IF_ID['Instr'] = '00000000000000000000000000000000'
        elif self.ID_EX['Branch']:
            if branch_predict == '-atp':
                self.PC.insert(0, self.BR_TARGET)
            else:
                self.PC.append(self.BR_TARGET)
                self.PC[0] = self.IF_pc + 4
        elif self.stall == 0:
            self.PC[0] = self.IF_pc + 4
        if self.Jump:
            if self.Jump == 2:
                self.PC[0] = registers[31]
            else:
                self.PC[0] = self.JU_TARGET
        self.IF_ID['NPC'] = self.PC[0]

    def ID(self):
        if (self.ID_EX['Branch'] and branch_predict == '-atp') or self.Jump or self.stall or self.change_pc[0]:
            self.IF_ID['Instr'] = '00000000000000000000000000000000'
            self.Jump = 0
            self.stall = 0
        if len(self.end) >= 1:
            self.ID_pc = None
            return
        self.ID_EX['NPC'] = self.IF_ID['NPC']
        self.ID_EX['rs'] = self.IF_ID['rs']
        self.ID_EX['rt'] = self.IF_ID['rt']
        self.ID_EX['ReadData1'] = registers[self.ID_EX['rs']]
        self.ID_EX.ReadData2 = registers[self.ID_EX['rt']]
        self.ID_EX.RegDst0 = self.ID_EX['rt']
        self.ID_EX.RegDst1 = int(self.IF_ID['Instr'][16:21], 2)
        self.ID_EX.op = self.IF_ID['Instr'][:6]
        self.ID_EX.IMM = self.IF_ID['Instr'][16:]
        if int(self.ID_EX['IMM']) == 0:
            imm = int(self.ID_EX['IMM'], 2)
        else:
            imm = int(self.ID_EX['IMM'], 2) - 2 ** 16
        self.BR_TARGET = (imm << 2) + self.ID_EX['NPC']
        target = int(self.IF_ID['Instr'][6:], 2)
        bin_pc ='{:0>32}'.format('{0:b}'.format(self.PC[0]))
        self.JU_TARGET = (int(bin_pc[:4], 2) << 28) + target << 2
        self.control()
        self.forward()
        self.ID_pc = self.IF_pc
        if self.IF_ID['Instr'] == '00000000000000000000000000000000':
            self.ID_EX['RegWrite'] = 0
            self.ID_EX['MemWrite'] = 0
            if self.Flush:
                self.ID_pc = None

    def EX(self):
        pass