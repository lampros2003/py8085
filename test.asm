
        MVI A, 42H    ; Load 42H into A
        MOV B, A      ; Copy A to B
        STA 2000H     ; Store A at memory location 2000H
        HLT           ; Stop
        