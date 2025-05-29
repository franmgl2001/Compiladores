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
    li   $t0, 2       # load constant 2
    sw   $t0, -8($fp)  # assign to a at offset -8
    # Assignment: a = expression
    li   $t0, 5       # load constant 5
    sw   $t0, -12($fp)  # assign to b at offset -12
    # Assignment: b = expression
    # If statement
    lw   $t0, -8($fp)  # load a from offset -8
    subu $sp, $sp, 4       # make space on stack
    sw   $t0, 0($sp)       # save left operand
    lw   $t0, -12($fp)  # load b from offset -12
    lw   $t1, 0($sp)       # load left operand into $t1
    addu $sp, $sp, 4       # restore stack pointer
    slt  $t0, $t1, $t0     # set $t0 = 1 if $t1 < $t0, else 0
    beq  $t0, $zero, L1  # branch to else if condition is false
    # Then branch
    # Compound statement
    # Input function call - store expression value
    li   $t0, 1       # load constant 1
    sw   $t0, -4($fp)       # store input value at -4($fp)
    li   $t0, 1       # load constant 1
    # Output function call - print stored value
    lw   $t0, -4($fp)       # load stored input value
    move $a0, $t0           # move stored value to $a0
    li   $v0, 1             # syscall 1 = print integer
    syscall                 # print the integer
    li   $v0, 11            # syscall 11 = print character
    li   $a0, 10            # ASCII 10 = newline
    syscall                 # print newline
    j    L2           # jump to end
L1:
    # Else branch
    # Compound statement
    # Input function call - store expression value
    li   $t0, 0       # load constant 0
    sw   $t0, -4($fp)       # store input value at -4($fp)
    li   $t0, 0       # load constant 0
    # Output function call - print stored value
    lw   $t0, -4($fp)       # load stored input value
    move $a0, $t0           # move stored value to $a0
    li   $v0, 1             # syscall 1 = print integer
    syscall                 # print the integer
    li   $v0, 11            # syscall 11 = print character
    li   $a0, 10            # ASCII 10 = newline
    syscall                 # print newline
L2:
    # End of if statement
    # Input function call - store expression value
    li   $t0, 4       # load constant 4
    subu $sp, $sp, 4       # make space on stack
    sw   $t0, 0($sp)       # save left operand
    lw   $t0, -8($fp)  # load a from offset -8
    lw   $t1, 0($sp)       # load left operand into $t1
    addu $sp, $sp, 4       # restore stack pointer
    div  $t1, $t0          # divide $t1 by $t0
    mflo $t0               # move quotient to $t0
    sw   $t0, -4($fp)       # store input value at -4($fp)
    li   $t0, 4       # load constant 4
    subu $sp, $sp, 4       # make space on stack
    sw   $t0, 0($sp)       # save left operand
    lw   $t0, -8($fp)  # load a from offset -8
    lw   $t1, 0($sp)       # load left operand into $t1
    addu $sp, $sp, 4       # restore stack pointer
    div  $t1, $t0          # divide $t1 by $t0
    mflo $t0               # move quotient to $t0
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
