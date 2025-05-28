# C- Compilation to MIPS Assembly
# File: output.tm.s
# Using symbol table offsets for variable access


.text
.globl main
main:
    # Set up stack frame
    move $fp, $sp           # frame pointer = stack pointer
    subu $sp, $sp, 100      # allocate space for locals
    li   $t0, 1       # load constant 1
    lw   $a0, -4($fp)   # load it back into $a0
    li   $v0, 1         # syscall 1 = print integer
    syscall
    li   $t0, 1         # load the constant 1 into a temp reg
    sw   $t0, -4($fp)   # save it to stack slot at fp–4
    # Restore stack and exit
    move $sp, $fp           # restore stack pointer
    li   $v0, 10            # exit program
    syscall
