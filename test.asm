MVI A, FFH
MVI B, 1H 
ADD B ;;opcode: 80H
ADI 10H ;; opcode: C6H
PUSH B ;; opcode: C5H
POP D ;; opcode: C1H
HLT ;; opcode: 76H
