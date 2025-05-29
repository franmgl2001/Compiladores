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
    sw   $t0, -8($fp)  # assign to a at offset -8
    # Assignment: a = expression
    # Input function call - store expression value
    li   $t0, 4       # load constant 4
    subu $sp, $sp, 4       # make space on stack
    sw   $t0, 0($sp)       # save left operand
    lw   $t0, -8($fp)  # load a from offset -8
    lw   $t1, 0($sp)       # load left operand into $t1
    addu $sp, $sp, 4       # restore stack pointer
    add  $t0, $t1, $t0     # add: $t0 = $t1 + $t0
    sw   $t0, -4($fp)       # store input value at -4($fp)
    li   $t0, 4       # load constant 4
    subu $sp, $sp, 4       # make space on stack
    sw   $t0, 0($sp)       # save left operand
    lw   $t0, -8($fp)  # load a from offset -8
    lw   $t1, 0($sp)       # load left operand into $t1
    addu $sp, $sp, 4       # restore stack pointer
    add  $t0, $t1, $t0     # add: $t0 = $t1 + $t0
    # Output function call - print stored value
    lw   $t0, -4($fp)       # load stored input value
    move $a0, $t0           # move stored value to $a0
    li   $v0, 1             # syscall 1 = print integer
    syscall                 # print the integer
    li   $v0, 11            # syscall 11 = print character
    li   $a0, 10            # ASCII 10 = newline
    syscall                 # print newline
    # Restore stack and exit
    move $sp, $fp           # restore stack pointer
    li   $v0, 10            # exit program
    syscall
