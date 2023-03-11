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
    if os.path.isfile(filename) and delete_o_files == "yes":
        os.remove(filename)
with open("config.json", "r") as config:
    dictionary = json.load(config)
    input_files = dictionary.get("input_files", [])
    delete_o_files = dictionary.get("delete_object_files", "yes")
    output_dir = dictionary.get("output_dir", "./")
    cap = dictionary.get("capacity", 64)
for f in input_files:
    with open(f + ".asm", "r") as inf, open(output_dir + re.split("/|\\\\", f)[-1] + ".o", "w") as outf:
        lines = []
        line_index = 0
        for line in inf:
            comment_start = line.find("#")
            flag_end = line.find(":")
            flag = line[0:flag_end if flag_end > -1 else 0]
            line = line[flag_end + 1:comment_start if comment_start > -1 else len(line)].split(";")
            for i in range(len(line)):
                line[i] = line[i].split()
            if (len(line[0])):
                lines.append((flag, line, line_index))
            line_index += 1
        print(lines)
        for i in range(len(lines)):
            if (lines[i][0] != ""):
                for ii in range(i + 1, len(lines)):
                    if lines[i][0] == lines[ii][0]:
                        print(f"error on line {ii + 1}: duplicate of flag found")
                        exit_function(outf, -1)
            ############################################################################################
            command = 0 #по умолчанию команды идут подряд
            for subinstruction in lines[i][1]:
                if len(subinstruction) > 0:
                    try:
                        command ^= database.instruction_list[subinstruction[0]](subinstruction[1:], lines, outf)
                    except:
                        print(f"error on line {lines[i][2] + 1} in {f}.asm file")
                        exit_function(outf, -2)
            ############################################################################################
            outf.write(f"{hex(int(command))[2:]} ")
    if cap == 64:
        parse_o_file_to_bin(outf.name.split(".")[0])