# C- Compilation to MIPS Assembly
# File: output.asm
# Using symbol table offsets for variable access


.text
.globl main
main:
    # Set up stack frame for main
    move $fp, $sp           # frame pointer = stack pointer
    subu $sp, $sp, 100      # allocate space for locals
    # Main function body
    # Compound statement
    li   $t0, 100       # load constant 100
    subu $sp, $sp, 4       # save assignment value
    sw   $t0, 0($sp)       # save value on stack
    li   $t0, 0       # load constant 0
    sll  $t0, $t0, 2       # multiply index by 4
    addi $t1, $fp, -16  # load array base address
    add  $t1, $t1, $t0     # calculate element address
    lw   $t0, 0($sp)       # load assignment value
    sw   $t0, 0($t1)       # store value to array element
    # Array assignment: nums[index] = value
    addu $sp, $sp, 4       # restore stack
    li   $t0, 200       # load constant 200
    subu $sp, $sp, 4       # save assignment value
    sw   $t0, 0($sp)       # save value on stack
    li   $t0, 1       # load constant 1
    sll  $t0, $t0, 2       # multiply index by 4
    addi $t1, $fp, -16  # load array base address
    add  $t1, $t1, $t0     # calculate element address
    lw   $t0, 0($sp)       # load assignment value
    sw   $t0, 0($t1)       # store value to array element
    # Array assignment: nums[index] = value
    addu $sp, $sp, 4       # restore stack
    li   $t0, 300       # load constant 300
    subu $sp, $sp, 4       # save assignment value
    sw   $t0, 0($sp)       # save value on stack
    li   $t0, 2       # load constant 2
    sll  $t0, $t0, 2       # multiply index by 4
    addi $t1, $fp, -16  # load array base address
    add  $t1, $t1, $t0     # calculate element address
    lw   $t0, 0($sp)       # load assignment value
    sw   $t0, 0($t1)       # store value to array element
    # Array assignment: nums[index] = value
    addu $sp, $sp, 4       # restore stack
    # Input function call - store expression value
    li   $t0, 0       # load constant 0
    subu $sp, $sp, 4       # make space for index
    sw   $t0, 0($sp)       # save index on stack
    lw   $t1, 0($sp)       # load index into $t1
    addu $sp, $sp, 4       # restore stack
    sll  $t1, $t1, 2       # multiply index by 4 (shift left 2)
    addi $t2, $fp, -16  # load array base address
    add  $t2, $t2, $t1     # calculate element address
    lw   $t0, 0($t2)       # load array element
    # Array access: nums[index]
    sw   $t0, -4($fp)       # store input value at -4($fp)
    # Output function call - print stored value
    lw   $t0, -4($fp)       # load stored input value
    move $a0, $t0           # move stored value to $a0
    li   $v0, 1             # syscall 1 = print integer
    syscall                 # print the integer
    li   $v0, 11            # syscall 11 = print character
    li   $a0, 10            # ASCII 10 = newline
    syscall                 # print newline
    # Input function call - store expression value
    li   $t0, 2       # load constant 2
    subu $sp, $sp, 4       # make space for index
    sw   $t0, 0($sp)       # save index on stack
    lw   $t1, 0($sp)       # load index into $t1
    addu $sp, $sp, 4       # restore stack
    sll  $t1, $t1, 2       # multiply index by 4 (shift left 2)
    addi $t2, $fp, -16  # load array base address
    add  $t2, $t2, $t1     # calculate element address
    lw   $t0, 0($t2)       # load array element
    # Array access: nums[index]
    sw   $t0, -4($fp)       # store input value at -4($fp)
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
