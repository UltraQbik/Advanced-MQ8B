#include lib.q

#vardef a      $0
#vardef b      $1
#vardef result $2

#subrut MAIN
    SRA #12 &a
    SRA #12 &b

    ADC &a &b &result
