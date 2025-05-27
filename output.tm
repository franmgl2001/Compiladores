* TINY Compilation to TM Code
* File: output.tm
* Standard prelude:
  0: LD    6,0(0)	load maxaddress
  1: ST    0,0(0)	clear loc 0
* End of standard prelude.
* -> Op
  2: ST    0,0(6)	push left
* -> Const
  3: LDC   0,1(0)	load const 1
* <- Const
  4: LD    1,0(6)	pop left
  5: SUB   0,1,0	==
  6: JEQ   0,2(7)	br if true
  7: LDC   0,0(0)	false
  8: LDA   7,1(7)	jmp next
  9: LDC   0,1(0)	true
* <- Op
* -> Op
* -> Id
 10: LD    0,11(5)	load id cont
* <- Id
 11: ST    0,0(6)	push left
* -> Id
 12: LD    0,8(5)	load id k
* <- Id
 13: LD    1,0(6)	pop left
 14: SUB   0,1,0	==
 15: JEQ   0,2(7)	br if true
 16: LDC   0,0(0)	false
 17: LDA   7,1(7)	jmp next
 18: LDC   0,1(0)	true
* <- Op
* End of execution.
 19: HALT  0,0,0	
