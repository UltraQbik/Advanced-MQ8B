; Simple addition program

.vardef a       auto
.vardef b       auto
.vardef result  auto
.vardef cmd     auto

SRA #10 $1

UI &cmd
UI &a
UI &b

JMPZ @ADD
dec
JMPZ @SUB
JMPZ @ERROR

.subrut ADD
    ADC &a &b &result
    JMP @END

.subrut SUB
    SBC &a &b &result
    JMP @END

.subrut ERROR
    JMP @END

.subrut END
    HALT
