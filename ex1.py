# get sample.o file as a list
import sys
with open(sys.argv[-1], 'rt') as fileobj:
    file_lines = fileobj.read().split('\n')

# for remove empty lines in sample.o
for i in range(len(file_lines)):
    if not bool(file_lines[i]):
        file_lines.pop(i)

class makeDictionary:
    # 주소를 key로, instruction, data를 value로 가짐. key 와 value의 data type은 int
    def makeDict(self, list):
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
a.makeDict(file_lines)


