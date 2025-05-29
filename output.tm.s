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
    subu $sp, $sp, 4       # make space on stack
    sw   $t0, 0($sp)       # save left operand
    li   $t0, 2       # load constant 2
    lw   $t1, 0($sp)       # load left operand into $t1
    addu $sp, $sp, 4       # restore stack pointer
    add  $t0, $t1, $t0     # add: $t0 = $t1 + $t0
    sw   $t0, -8($fp)  # assign to a at offset -8
    # Assignment: a = expression
    lw   $t0, -8($fp)  # load a from offset -8
    # Output function call
    move $a0, $t0           # move value to $a0 for printing
    li   $v0, 1             # syscall 1 = print integer
    syscall                 # print the integer
    li   $v0, 11            # syscall 11 = print character
    li   $a0, 32            # ASCII 32 = space
    syscall                 # print space
    lw   $t0, -8($fp)  # load a from offset -8
    li   $t0, 5       # load constant 5
    subu $sp, $sp, 4       # make space on stack
    sw   $t0, 0($sp)       # save left operand
    li   $t0, 3       # load constant 3
    lw   $t1, 0($sp)       # load left operand into $t1
    addu $sp, $sp, 4       # restore stack pointer
    mul  $t0, $t1, $t0     # multiply: $t0 = $t1 * $t0
    sw   $t0, -12($fp)  # assign to b at offset -12
    # Assignment: b = expression
    lw   $t0, -12($fp)  # load b from offset -12
    # Output function call
    move $a0, $t0           # move value to $a0 for printing
    li   $v0, 1             # syscall 1 = print integer
    syscall                 # print the integer
    li   $v0, 11            # syscall 11 = print character
    li   $a0, 32            # ASCII 32 = space
    syscall                 # print space
    lw   $t0, -12($fp)  # load b from offset -12
    # Restore stack and exit
    move $sp, $fp           # restore stack pointer
    li   $v0, 10            # exit program
    syscall
