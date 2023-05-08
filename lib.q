#include libr.q
#define yes $0

RET yes

#vardef a $4
#vardef b $5
#vardef c $63

SRA &a &b
SRA &b &c

ADC &a &b &c
XOR &c &b &a
