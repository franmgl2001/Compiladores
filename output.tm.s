# C- Compilation to MIPS Assembly
# File: output.tm.s
# Using symbol table offsets for variable access


.text
.globl main
main:
    # Set up stack frame
    move $fp, $sp           # frame pointer = stack pointer
    subu $sp, $sp, 100      # allocate space for locals
    lw   $t0, -4($fp)  # load y from offset -4
    li   $t0, 1       # load constant 1
    li   $t0, 2       # load constant 2
    sw   $t0, -4($fp)  # assign to y at offset -4
    # Assignment: y = expression
    li   $t0, 1       # load constant 1
    li   $t0, 2       # load constant 2
    # Restore stack and exit
    move $sp, $fp           # restore stack pointer
    li   $v0, 10            # exit program
    syscall
