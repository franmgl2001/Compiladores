# C- Compilation to MIPS Assembly
# File: output.tm.s
# Using symbol table offsets for variable access


.text
.globl main
main:
    # Set up stack frame
    move $fp, $sp           # frame pointer = stack pointer
    subu $sp, $sp, 100      # allocate space for locals
    # Compound statement
    li   $t0, 0       # load constant 0
    sw   $t0, -8($fp)  # assign to i at offset -8
    # Assignment: i = expression
    # While statement
L1:
    # While condition
    lw   $t0, -8($fp)  # load i from offset -8
    subu $sp, $sp, 4       # make space on stack
    sw   $t0, 0($sp)       # save left operand
    li   $t0, 3       # load constant 3
    lw   $t1, 0($sp)       # load left operand into $t1
    addu $sp, $sp, 4       # restore stack pointer
    slt  $t0, $t1, $t0     # set $t0 = 1 if $t1 < $t0, else 0
    beq  $t0, $zero, L2  # exit loop if condition is false
    # While body
    # Output function call - print stored value
    lw   $t0, -8($fp)  # load i from offset -8
    move $a0, $t0           # move expression result to $a0
    li   $v0, 1             # syscall 1 = print integer
    syscall                 # print the integer
    li   $v0, 11            # syscall 11 = print character
    li   $a0, 10            # ASCII 10 = newline
    syscall                 # print newline
    lw   $t0, -8($fp)  # load i from offset -8
    lw   $t0, -8($fp)  # load i from offset -8
    subu $sp, $sp, 4       # make space on stack
    sw   $t0, 0($sp)       # save left operand
    li   $t0, 1       # load constant 1
    lw   $t1, 0($sp)       # load left operand into $t1
    addu $sp, $sp, 4       # restore stack pointer
    add  $t0, $t1, $t0     # add: $t0 = $t1 + $t0
    sw   $t0, -8($fp)  # assign to i at offset -8
    # Assignment: i = expression
    j    L1          # jump back to condition
L2:
    # End of while statement
    # Output function call - print stored value
    li   $t0, 999       # load constant 999
    move $a0, $t0           # move expression result to $a0
    li   $v0, 1             # syscall 1 = print integer
    syscall                 # print the integer
    li   $v0, 11            # syscall 11 = print character
    li   $a0, 10            # ASCII 10 = newline
    syscall                 # print newline
    li   $t0, 999       # load constant 999
    # Restore stack and exit
    move $sp, $fp           # restore stack pointer
    li   $v0, 10            # exit program
    syscall
