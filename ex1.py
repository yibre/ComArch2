# get sample.o file as a list
import sys
with open(sys.argv[-1], 'rt') as fileobj:
    file_lines = fileobj.read().split('\n')

# for remove empty lines in sample.o
for i in range(len(file_lines)):
    if not bool(file_lines[i]):
        file_lines.pop(i)

address = 0  # if not 0, print the content in the address range of the memory
d = False  # if True, print registers after each instruction is executed

for i in range(len(sys.argv)):
    if sys.argv[i] == '-m':
        address = sys.argv[i + 1]
    elif sys.argv[i] == '-d':
        d = True
    elif sys.argv[i] == '-n':
        num_instruction = int(sys.argv[i + 1])

if address:
    address2 = address.split(':')
    addr1 = int(address2[0], 16)
    addr2 = int(address2[1], 16)

class makeDictionary:
    # 주소를 key로, instruction, data를 value로 가짐. key 와 value의 data type은 int
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
                dictionary[instAddress + (i-3)*4] = int(list[i], 0)
            else:
                dictionary[dataAddress + (i-3)*4] = int(list[i], 0)
        # print(dictionary)
        return dictionary

    def StrBinInstruction(self, dictionary):
        self.dictionary = dictionary
        new_dic = {}
        for i in dictionary.keys():
            new_dic[i] = '{:0>32}'.format('{0:b}'.format(dictionary[i]))
            # key = memory, value = str type of 32bit binary value
        # print(new_dic)
        return new_dic

"""
{4194304: 4331553, 4194308: 6430757, 4194312: 604308690, 4194316: 340992, 4194320: 617031439, 4194324: 14827555, 4194328: 8603687, 4194332: 877265151,
 4194336: 416066, 4194340: 418050, 4194344: 1006899200, 4194348: 881065996, 4194352: 23423012, 4194356: 814612580, 4194360: 686115, 268435516: 1007747
172, 268435520: 604110858, 268435524: 3, 268435528: 123, 268435532: 4346, 268435536: 286331153}
실행 이후 출력 <- 메모리임

{4194304: '00000000010000100001100000100001', 4194308: '00000000011000100010000000100101', 4194312: '001001000000010100000
10011010010', 4194316: '00000000000001010011010000000000', 4194320: '00100100110001110010011100001111', 4194324: '00000000
111000100100000000100011', 4194328: '00000000100000110100100000100111', 4194332: '00110100010010100000000011111111', 41943
36: '00000000000001100101100101000010', 4194340: '00000000000001100110000100000010', 4194344: '001111000000010000010000000
00000', 4194348: '00110100100001000000000000001100', 4194352: '00000001011001010110100000100100', 4194356: '00110000100011
100000000001100100', 4194360: '00000000000010100111100000100011', 268435516: '00111100000100010000000001100100', 268435520
: '00100100000000100000000000001010', 268435524: '00000000000000000000000000000011', 268435528: '0000000000000000000000000
1111011', 268435532: '00000000000000000001000011111010', 268435536: '00010001000100010001000100010001'}


"""
# 변수 선언란 -----------------------------------------------------------------------------------------------------
pc = [0x400000]
memory = makeDictionary().makeMemory(file_lines)
bin_memory = makeDictionary().StrBinInstruction(memory)
registers = []
for i in range(32):
    registers.append(0) # 레지스터 초기값 [0, 0, 0, 0, 0, 0, 0 ....,0 0] <- 총 32개의 0이 있음

# Memory Content [0x00000028..0x00000050] :
# ------------------------------------- 출력하는 함수 print mem

def print_memory(addr1):
    print('Memory Content [' + '{0:#0{1}x}'.format(addr1, 10) + '..' + '{0:#0{1}x}'.format(addr2, 10) + '] :')
    print('-------------------------------------')
    while addr1 <= addr2:
        if addr1 in memory:
            print('{0:#0{1}x}'.format(addr1, 10) + ':', '{0:#0{1}x}'.format(memory[addr1], 10))
        else:
            print('{0:#0{1}x}'.format(addr1, 10) + ':', '{0:#0{1}x}'.format(0, 10))
        addr1 += 4
    print()

def print_registers():
    print('Current register values : ')
    print('-------------------------------------')
    print('PC:', '{0:#0{1}x}'.format(pc[0], 10))
    for i in range(32):
        if registers[i] < 0:
            print('R', i, ': ', '{0:#0{1}x}'.format(registers[i] + 2 ** 32, 10), sep='')
        else:
            print('R', i, ': ', '{0:#0{1}x}'.format(registers[i], 10), sep='')
    print()


def i_type(bin_inst):
    rs = int(bin_inst[6:11], 2)
    rt = int(bin_inst[11:16], 2)
    # str to signed int
    if int(bin_inst[16]) == 0:
        imm = int(bin_inst[16:], 2)
    else:
        imm = int(bin_inst[16:], 2) - 2 ** 16
    return [rs, rt, imm]



def r_type(bin_inst):
    rs = int(bin_inst[6:11], 2)
    rt = int(bin_inst[11:16], 2)
    rd = int(bin_inst[16:21], 2)
    shamt = int(bin_inst[21:26], 2)
    return [rs, rt, rd, shamt]

def j_type(bin_inst):
    target = int(bin_inst[6:], 2)
    bin_pc = '{:0>32}'.format('{0:b}'.format(pc[0]))
    jump_target = (int(bin_pc[:4], 2) << 28) + target << 2
    return jump_target


def addiu(bin_inst):
    rs, rt, imm = i_type(bin_inst)
    registers[rt] = registers[rs] + imm


def addu(bin_inst):
    rs, rt, rd, shamt = r_type(bin_inst)
    registers[rd] = registers[rs] + registers[rt]


def and_(bin_inst):
    rs, rt, rd, shamt = r_type(bin_inst)
    registers[rd] = registers[rs] & registers[rt]


def andi(bin_inst):
    rs, rt, imm = i_type(bin_inst)
    registers[rt] = registers[rs] & imm


def beq(bin_inst):
    rs, rt, imm = i_type(bin_inst)
    if (registers[rs] == registers[rt]):
        target = pc[0] + (imm << 2)
        pc[0] = target

def bne(bin_inst):
    rs, rt, imm = i_type(bin_inst)
    if (registers[rs] != registers[rt]):
        target = pc[0] + (imm << 2)
        pc[0] = target


def j(bin_inst):
    jump_target = j_type(bin_inst)
    pc[0] = jump_target


def jal(bin_inst):
    jump_target = j_type(bin_inst)
    registers[31] = pc[0]
    pc[0] = jump_target


def jr(bin_inst):
    rs, rt, rd, shamt = r_type(bin_inst)
    pc[0] = registers[rs]


def lui(bin_inst):
    rs, rt, imm = i_type(bin_inst)
    registers[rt] = imm << 16


def lw(bin_inst):
    rs, rt, imm = i_type(bin_inst)
    registers[rt] = memory[registers[rs] + imm]

def nor(bin_inst):
    rs, rt, rd, shamt = r_type(bin_inst)
    registers[rd] = ~(registers[rs] | registers[rt])


def or_(bin_inst):
    rs, rt, rd, shamt = r_type(bin_inst)
    registers[rd] = registers[rs] | registers[rt]


def ori(bin_inst):
    rs, rt, imm = i_type(bin_inst)
    registers[rt] = registers[rs] | imm


def sltiu(bin_inst):
    rs, rt, imm = i_type(bin_inst)
    if registers[rs] < imm:
        registers[rt] = 1
    else:
        registers[rt] = 0


def sltu(bin_inst):
    rs, rt, rd, shamt = r_type(bin_inst)
    if registers[rs] < registers[rt]:
        registers[rd] = 1
    else:
        registers[rd] = 0


def sll(bin_inst):
    rs, rt, rd, shamt = r_type(bin_inst)
    registers[rd] = registers[rt] << shamt


def srl(bin_inst):
    rs, rt, rd, shamt = r_type(bin_inst)
    registers[rd] = registers[rt] >> shamt

def sw(bin_inst):
    rs, rt, imm = i_type(bin_inst)
    memory[registers[rs] + imm] = registers[rt]


def subu(bin_inst):
    rs, rt, rd, shamt = r_type(bin_inst)
    registers[rd] = registers[rs] - registers[rt]

op_dic = {'001001': addiu, '001100': andi, '000100': beq, '000101': bne, '000010': j, '000011': jal, '001111': lui,
      '100011': lw, '001101': ori, '001011': sltiu, '101011': sw} # i type과 j type의 처음 6자리 이진수로 알아냄 dictionary
func_dic = {'100001': addu, '100100': and_, '001000': jr, '100111': nor, '100101': or_, '101011': sltu, '000000': sll,
        '000010': srl, '100011': subu} # r type의 뒷자리 func 부분, r 타입은 op가 전부 000000임.

def execute_inst():
    if pc[0] not in memory:
        return
    bin_inst = bin_memory[pc[0]]
    pc[0] += 4
    # if r_type
    if bin_inst[:6] == '000000':
        func_dic[bin_inst[-6:]](bin_inst)
    else:
        op_dic[bin_inst[:6]](bin_inst)
    if d:
        print_registers()
        if address:
            print_memory(addr1)

for i in range(num_instruction):
    execute_inst()

# when program terminates
print_registers()
if address:
    print_memory(addr1)