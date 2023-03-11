#load data (1, 1) - for fibonachi line, (0, 1) - for output, 2 - for output shift
clr_cash
unco; mov 0 RAM
dq 1
mov 1 ALU; alu =; sel A 0 #we already has 1, it`s currently available
#reg 2 is start, set reg 3 to continue#
unco; mov 2 RAM
dq 0 #start address for output
mov 3 ALU; alu +; sel A 2; sel B 0 #we already has 1, it`s currently available
unco; mov 4 RAM
dq 2
#cycle
target: write; sel A 0; sel B 2
write; sel A 1; sel B 3
mov 0 ALU; alu +; sel A 1; sel B 0
mov 1 ALU; alu +; sel A 1; sel B 0
mov 2 ALU; alu +; sel A 2; sel B 4
mov 3 ALU; alu +; sel A 3; sel B 4
goto target 5