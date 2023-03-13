#warning codes
#W0001 - line has flag, but no code or data is provided, line is ignored
#error codes
#E0001 - found duplicate flag
#E0002 - command contains wrong args
import json
import database
import os
import re
def exit_function(file, exit_code):
    file.close()
    os.remove(file.name)
    exit(exit_code)
def parse_o_file_to_bin(filename):
    with open(filename + ".o", "r") as inf, open(filename + ".0.bin", "w") as outf0, open(filename + ".1.bin", "w") as outf1:
        outf0.write("v2.0 raw\n")
        outf1.write("v2.0 raw\n")
        values = inf.readline().split()
        for v in values:
            outf0.write(f"{v[-8:]} ")
            outf1.write(f"{v[:-8] if len(v[:-8]) else 0} ")
        outf0.write("\n")
        outf1.write("\n")
    if os.path.isfile(filename + ".o") and delete_o_files == "yes":
        os.remove(filename + ".o")
def parse_file(file_name):
    lines = []
    with open(file_name + ".asm", "r") as inf, open(output_dir + re.split("/|\\\\", file_name)[-1] + ".o", "w") as outf:
        line_index = 1
        for line in inf:
            comment_start = line.find("#")
            flag_end = line.find(":", 0, comment_start if comment_start > -1 else len(line))
            flag = line[0:flag_end if flag_end > -1 else 0]
            line = line[flag_end + 1:comment_start if comment_start > -1 else len(line)].split(";")
            for i in range(len(line)):
                line[i] = line[i].split()
            if (len(line[0])):
                lines.append((flag, line, line_index, file_name))
            elif flag_end > -1:
                print(f"warning: W0001 on line {line_index + 1} in {file_name}.asm file, flag \"{flag}\" ignored")
            line_index += 1
        #print('\n'.join('{}: {}'.format(*val) for val in enumerate(lines)))
    return lines
def compile_parsed(code_data, out_file):
    compile_file = True
    with open(output_dir + re.split("/|\\\\", out_file)[-1] + ".o", "w") as outf:
        for i in range(len(code_data)):
            if (code_data[i][0] != ""):
                for ii in range(i + 1, len(code_data)):
                    if code_data[i][0] == code_data[ii][0]:
                        print(f"error: E0001 on line {code_data[i][2]} in {code_data[i][3]}.asm file, duplicate of flag \"{code_data[i][0]}\" found (near collision on line {code_data[ii][2]} in {code_data[ii][3]}.asm file)")
                        compile_file = False
                        break
            ############################################################################################
            command = 0 #по умолчанию команды идут подряд
            for subinstruction in code_data[i][1]:
                if len(subinstruction) > 0:
                    try:
                        command ^= database.instruction_list[subinstruction[0]](subinstruction[1:], code_data, outf)
                    except:
                        print(f"error: E0002 on line {code_data[i][2]} in {code_data[i][3]}.asm file, wrong command \"{' '.join(str(item) for item in subinstruction)}\"")
                        compile_file = False
            ############################################################################################
            if compile_file:
                outf.write(f"{hex(int(command))[2:]} ")
    if compile_file:
        if cap == 64:
            parse_o_file_to_bin(outf.name[0:-2])
        print(f"compiled {code_data[i][3]}.asm file successfuly, output file: {outf.name}")
    else:
        outf.close()
        os.remove(outf.name)
        print("compilation failed")
with open("config.json", "r") as config:
    dictionary = json.load(config)
    input_files = dictionary.get("input_files", [])
    delete_o_files = dictionary.get("delete_object_files", "yes")
    output_dir = dictionary.get("output_dir", "./")
    cap = dictionary.get("capacity", 64)
for f in input_files:
    compile_parsed(parse_file(f), f)
#print(input("press Enter to close compiler..."))