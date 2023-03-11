unco; mov 0 RAM
dq 6
unco; mov 1 RAM
dq 1
unco; mov 2 RAM
dq 0
target: mov 2 ALU; alu +; sel A 1; sel B 2 
bcv JUMP; bs TRUE; sel B 0
#goto target 0
#a = 0
#while True: a += 1

#220001 6 620001 1 a20001 0 8001000a40010 4002 