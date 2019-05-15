import sys

class PipelineSimulator:
    def read_files(self, file_name):
        f = open(file_name, 'r')
        text_section_lines = int(f.readline(), 0)//4
        data_section_lines = int(f.readline(), 0)//4
        self.pc = 0x00400000
        for _ in range(text_section_lines):
            line = f.readline()
            bin_str = format(int(line, 0), '032b')
            self.instructions[self.pc] = bin_str
            self.pc += 0x00000004

        self.pc = 0x10000000
        for _ in range(data_section_lines):
            line = f.readline()
            value = self._signed_bin(int(line, 0), bin_length=32)  # int(line,0)
            self.memory[self.pc] = value
            self.pc += 0x00000004

        f.close()