# get sample.o file as a list
import sys
with open(sys.argv[-1], 'rt') as fileobj:
    file_lines = fileobj.read().split('\n')

# for remove empty lines in sample.o
for i in range(len(file_lines)):
    if not bool(file_lines[i]):
        file_lines.pop(i)

 # ------------------------------------------------------------------------- 이하 26번째 줄까지 세진선배 코드 복사
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
        print(dictionary)
        return dictionary


a = makeDictionary()
a.makeMemory(file_lines)

"""
{4194304: 4331553, 4194308: 6430757, 4194312: 604308690, 4194316: 340992, 4194320: 617031439, 4194324: 14827555, 4194328: 8603687, 4194332: 877265151,
 4194336: 416066, 4194340: 418050, 4194344: 1006899200, 4194348: 881065996, 4194352: 23423012, 4194356: 814612580, 4194360: 686115, 268435516: 1007747
172, 268435520: 604110858, 268435524: 3, 268435528: 123, 268435532: 4346, 268435536: 286331153}
실행 이후 출력 <- 메모리임
"""
# 변수 선언란 -----------------------------------------------------------------------------------------------------
pc = [0x400000]

registers = []
for i in range(32):
    registers.append(0) # 레지스터 초기값 [0, 0, 0, 0, 0, 0, 0 ....,0 0] <- 총 32개의 0이 있음

# Memory Content [0x00000028..0x00000050] :
# ------------------------------------- 출력하는 함수 print mem

def print_memory(addr1, memory): #TODO: 세진선배와 다르게 memory 함수 변수를 추가했다. 나같은 경우엔 class에서 생성된 객체임
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

