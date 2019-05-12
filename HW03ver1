# version 1
# 예측 및 분기용 ATP O ATP X일때 한번씩

#

# stall execute function
"""
stall == 1
 > 1 and current target == none -> 예측 실패시 원 pc로 돌아가기
 > 3

stall > 0, IFID 
stall > 1, IDEX
stall > 2, EX MEM
stall > 3  MEM WB
Register 초기화하기
stall 끝나면 0으로 초기화

** Data Forwarding Function
R타입의 목적지는 rd고 
R -> EX/MEM to MEM
R -> MEM/WB to EX
MEM/WB to MEM 
"""

"""
1) instruction 실행하는 class 생성
instruction, register(상태별로 보유)
2) class간 데이터포워딩 실행, control harzard 실행
"""
"""
import sys

class InputFile:
    def read_files(self):
        with open(sys.argv[-1], 'rt') as fileobj:
            file_lines = fileobj.read().split('\n')
        for i in range(len(file_lines)):
            if not bool(file_lines[i]):
                file_lines.pop(i)
        return file_lines

    def makeMemory(self, list):
        global dataSize, instSize
        dictionary = {}
        instAddress = 0x400000
        dataAddress = 0x10000000
        self.list = list
        instSize = int(int(list[0], 0) / 4)
        dataSize = int(int(list[1], 0) / 4)
        for i in range(3, len(list)):
            if i < instSize:
                dictionary[instAddress + (i - 3) * 4] = int(list[i], 0)
            else:
                dictionary[dataAddress + (i - 3) * 4] = int(list[i], 0)
        return dictionary

    def StrBinInstruction(self):
        A = InputFile()
        dictionary = A.makeMemory(A.read_files())
        new_dic = {}
        for i in dictionary.keys():
            new_dic[i] = '{:0>32}'.format('{0:b}'.format(dictionary[i]))
            # key = memory, value = str type of 32bit binary value
        print(new_dic)
        return new_dic
-------------------------------------------------------------------------
    # TODO : 여기 버그 있음!!! 버그 A파트

    file = InputFile()
    file.StrBinInstruction() 실행결과 sample2.o
    {4194304: '10001101000010010000000000000000', 4194308: '00000000000010010001000000100001', 4194312: '000011000001
00000000000000000101', 4194316: '00001000000100000000000000001100', 4194320: '00101100010000010000000000000001',
4194324: '00010100001000000000000000000011', 4194328: '00000000011000100001100000100001', 4194332: '0010010001000
0101111111111111111', 4194336: '00001000000100000000000000000101', 268435492: '00000000011000000010000000100001',
 268435496: '00000011111000000000000000001000', 268435500: '00000000000000000000000000000101'}
    """

############################################## 버그 A 수정용 ############################################################
def makeDic(list1, list2):
    temp = {}
    pc = 0x400000
    mem = 0x10000000
    for i in range(len(list1)):
        temp[pc] = '{:0>32}'.format('{0:b}'.format(list1[i]))
        pc += 4
    for k in range(len(list2)):
        temp[mem] = '{:0>32}'.format('{0:b}'.format(list2[k]))
        mem += 4
    return temp
list1 = [0x24020400, 0x421821, 0x622025, 0x240504d2, 0x53400, 0x24c7270f, 0xe24023, 0x834827, 0x344a00ff,
        0x65942, 0x66102, 0x3c041000, 0x3484000c, 0x1656824, 0x308e0064, 0xa7823, 0x3c110064, 0x2402000a]
list12 = [0x3, 0x7b, 0x10fa, 0x11111111]

list2 = [0x3c081000, 0x8d090000, 0x91021, 0xc100005, 0x810000c, 0x2c410001, 0x14200003, 0x621821, 0x2442ffff,
         0x8100005, 0x602021, 0x3e00008]
list22 = [0x5]

list3 = [0x3c061000, 0x8cc10004, 0x8cc20008, 0x8cc50000, 0x24840002, 0x24c6000c, 0xc100008, 0x8100012, 0x85382b,
         0x10e00007, 0x221821, 0x400821, 0x601021, 0xacc30000, 0x24c60004, 0x24840001, 0x8100008, 0x3e00008]
list32 = [0xa, 0x1, 0x1, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]

Sample1 = makeDic(list1, list12)
Sample2 = makeDic(list2, list22)
Sample3 = makeDic(list3, list32)

"""
Sample1 = {4194304: '00100100000000100000010000000000', 4194308: '000000 / 00010 / 00010 / 00011 / 00000 / 100 001', 4194312: '00000000011000
100010000000100101', 4194316: '00100100000001010000010011010010', 4194320: '00000000000001010011010000000000', 4194
324: '00100100110001110010011100001111', 4194328: '00000000111000100100000000100011', 4194332: '0000000010000011010
0100000100111', 4194336: '00110100010010100000000011111111', 4194340: '00000000000001100101100101000010', 4194344:
'00000000000001100110000100000010', 4194348: '00111100000001000001000000000000', 4194352: '001101001000010000000000
00001100', 4194356: '00000001011001010110100000100100', 4194360: '00110000100011100000000001100100', 4194364: '0000
0000000010100111100000100011', 4194368: '00111100000100010000000001100100', 4194372: '00100100000000100000000000001
010', 268435456: '00000000000000000000000000000011', 268435460: '00000000000000000000000001111011', 268435464: '000
00000000000000001000011111010', 268435468: '00010001000100010001000100010001'}
"""

class InstPipeline:
    def __init__(self):
        # 주소 설정
        # self.PC = 0x400000
        """
        버그 A
        A = InputFile()
        self.dictionary = A.StrBinInstruction()"""
        self.cycle = 0 # 사이클 회수 초기화

        self.register = [0] * 32 # 레지스터는 각 번호당 0이 32개 있는 리스트

        # pipeline register state
        self.IF_ID = {'Instr': None, 'InstType': None,'NPC' : None, 'rs' : None, 'rt': None, 'rd': None, 'op': None,
           'shamt': None, 'funct':None,'imm': None}
        self.ID_EX = {'NPC' : None, 'rs':None, 'rt':None, 'rd':None, 'op': None, 'shamt' : None,
           'funct': None, 'imm': None, 'read_data1': None, 'read_data2': None}
        self.EX_MEM= {'NPC': None, 'alu_out': None, 'BR_target': None, 'rs' : None, 'rt':None,
           'rd': None, 'op': None, 'shamt':None, 'funct':None, 'imm': None, 'read_data1': None,
           'read_data2': None}
        self.MEM_WB= {'NPC' : None, 'alu_out': None, 'mem_out': None, 'rs' : None, 'rt': None, 'rd': None,
         'op': None, 'shamt':None, 'funct':None, 'imm':None, 'read_data1': None, 'read_data2': None}


    def initiation(self, MemRegister):
        """
        :param MemRegister: Memory register(IF_ID, ID_EX, EX_MEM, MEM_WB) 중 하나를 받는다 (type: dictionary)
        :return: 레지스터의 모든 항목을 초기화한다.
        """
        for i in MemRegister:
            MemRegister[i] = None
        return MemRegister

    def StallExecute(self, num):
        """
        :param num: stall의 횟수. 0 이상 정수. number가 1이면 IF_ID 초기화, 2면 ID_EX도 초기화 등등
        :return: stall의 횟수에 따라 레지스터를 초기화한다. initiation 함수는 stall 함수 내부에서만 쓰인다.
        """
        if num > 0: self.initiation(self.IF_ID)
        if num > 1: self.initiation(self.ID_EX)
        if num > 2: self.initiation(self.EX_MEM)
        if num > 3: self.initiation(self.MEM_WB)
        return

    def DataForwarding(self):
        pass

    def IF(self, PC):
        i_op_hex = [9, 0xc, 4, 5, 0xf, 0x23, 0xd, 0xb, 0x2b]
        # ["addiu", "andi", "beq", "bne", "lui", "lw", "ori", "sltiu", "sw"]

        j_op_hex = [2, 3]
        # ["j", "jal"]

        r_funct_hex = [0x21, 0x24, 8, 0x27, 0x25, 0x2b, 0, 2, 0x23]
        # ["addu", "and", "jr", "nor", "or", "sltu", "sll", "srl", "subu"]

        # 명령어 인출: PC 주소를 사용해 메모리에서 명령어를 읽어서 IF/ID 파이프라인 레지스터에 저장
        """
        :param PC: PC 주소 0x400000 <= PC < 0x10000000 미만 수까지가 들어감
        :return: IF ID dictionary 업데이트
        """
        # 버그 A self.IF_ID['Instr'] = int(self.dictionary[PC][0:6])
        dictionary = Sample1

        # Step 1: Instruction의 타입을 판단함
        self.IF_ID['Instr'] = int(dictionary[PC][0:6], 2) # input : binary instruction의 초기 6자리가 숫자로 들어감
        if self.IF_ID['Instr'] == 0:
            self.IF_ID['InstType'] = 'R'
        elif self.IF_ID['Instr'] in j_op_hex:
            self.IF_ID['InstType'] = 'J'
        else:
            self.IF_ID['InstType'] = 'I'

        # Step 2: Instruction 타입 별로 rs, rt, rd, op, shamt 등등등의 요소를 지정해줌
        if self.IF_ID['InstType'] == 'R':
            self.IF_ID['op'] = 0
            self.IF_ID['funct'] = int(dictionary[PC][-6:], 2)
            self.IF_ID['rs'] = int(dictionary[PC][6:11], 2) # 7, 8, 9, 10, 11 까지 출력
            self.IF_ID['rt'] = int(dictionary[PC][11:16], 2)
            self.IF_ID['rd'] = int(dictionary[PC][16:21], 2)
            self.IF_ID['shamt'] = int(dictionary[PC][21:26], 2)

        if self.IF_ID['InstType'] == 'I':
            self.IF_ID['op'] = int(dictionary[PC][0:6], 2) # 0xc, 9 등의 숫자가 저장됨
            self.IF_ID['rs'] = int(dictionary[PC][6:11], 2)
            self.IF_ID['rt'] = int(dictionary[PC][11:16], 2)
            self.IF_ID['imm'] = int(dictionary[PC][16:], 2) # imm or offset

        if self.IF_ID['InstType'] == 'J':
            self.IF_ID['op'] = int(dictionary[PC][0:6], 2)  # 0xc, 9 등의 숫자가 저장됨
            # Jump Target 지정 어떻게 하지?


    def ID(self): # Instruction Decode
        # lw, sw가 여기서 실행됨
        # R type instruction
        self.ID_EX['rd'] = self.IF_ID['rd']
        self.ID_EX['rt'] = self.IF_ID['rt']
        self.ID_EX['rs'] = self.IF_ID['rs']
        self.ID_EX['op'] = self.IF_ID['op']
        self.ID_EX['shamt'] = self.IF_ID['shamt']
        self.ID_EX['funct'] = self.IF_ID['funct']
        self.ID_EX['imm'] = self.IF_ID['imm']
        self.ID_EX['read_data1'] = self.ID_EX['rt'] # 레지스터 rt값 읽기
        self.ID_EX['read_data2'] = self.ID_EX['rs'] # 레지스터 rs값 읽기

        if self.IF_ID['InstType'] == 'R':
            if self.IF_ID['funct'] == 0x21: #addu
                pass
            pass

    def Ex(self): # Execute

        pass

    def MA(self):# Memory access
        pass


if __name__ == "__main__":
    pipeline = InstPipeline()
    pipeline.IF(4194308)