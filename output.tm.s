# C- Compilation to MIPS Assembly
# File: output.tm.s
# Using symbol table offsets for variable access


.text
.globl main
main:
    # Set up stack frame for main
    move $fp, $sp           # frame pointer = stack pointer
    subu $sp, $sp, 100      # allocate space for locals
    # Main function body
    # Compound statement
    li   $t0, 4       # load constant 4
    sw   $t0, -8($fp)  # assign to x at offset -8
    # Assignment: x = expression
    # Input function call - store expression value
    li   $t0, 4       # load constant 4
    sw   $t0, -4($fp)       # store input value at -4($fp)
    # Output function call - print stored value
    lw   $t0, -4($fp)       # load stored input value
    move $a0, $t0           # move stored value to $a0
    li   $v0, 1             # syscall 1 = print integer
    syscall                 # print the integer
    li   $v0, 11            # syscall 11 = print character
    li   $a0, 10            # ASCII 10 = newline
    syscall                 # print newline
    # Function call: sum
    # evaluate argument 1
    lw   $t0, -8($fp)  # load x from offset -8
    move $a0, $t0          # argument 1 -> $a0
    jal  sum           # call sum
    move $t0, $v0          # capture return value
    sw   $t0, -12($fp)  # assign to result at offset -12
    # Assignment: result = expression
    # Input function call - store expression value
    lw   $t0, -12($fp)  # load result from offset -12
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

# Function: sum
sum:
    # Function prologue
    subu $sp, $sp, 4       # make space for old $fp
    sw   $fp, 0($sp)       # save old frame pointer
    move $fp, $sp          # set new frame pointer
    subu $sp, $sp, 100     # allocate space for locals
    # Save parameter registers
    sw   $a0, -4($fp)      # save parameter 1
    sw   $a1, -8($fp)      # save parameter 2
    sw   $a2, -12($fp)     # save parameter 3
    sw   $a3, -16($fp)     # save parameter 4
    # Function body for sum
    # Compound statement
    # Input function call - store expression value
    lw   $t0, -4($fp)  # load a from offset -4
    sw   $t0, -4($fp)       # store input value at -4($fp)
    # Output function call - print stored value
    lw   $t0, -4($fp)       # load stored input value
    move $a0, $t0           # move stored value to $a0
    li   $v0, 1             # syscall 1 = print integer
    syscall                 # print the integer
    li   $v0, 11            # syscall 11 = print character
    li   $a0, 10            # ASCII 10 = newline
    syscall                 # print newline
    # Return statement
    lw   $t0, -4($fp)  # load a from offset -4
    subu $sp, $sp, 4       # make space on stack
    sw   $t0, 0($sp)       # save left operand
    li   $t0, 5       # load constant 5
    lw   $t1, 0($sp)       # load left operand into $t1
    addu $sp, $sp, 4       # restore stack pointer
    add  $t0, $t1, $t0     # add: $t0 = $t1 + $t0
    move $v0, $t0          # move return value to $v0
    # Function epilogue (return)
    move $sp, $fp          # restore stack pointer
    lw   $fp, 0($sp)       # restore old frame pointer
    addu $sp, $sp, 4       # deallocate space for old $fp
    jr   $ra               # return to caller
    # Function epilogue for sum
    move $sp, $fp          # restore stack pointer
    lw   $fp, 0($sp)       # restore old frame pointer
    addu $sp, $sp, 4       # deallocate space for old $fp
    jr   $ra               # return to caller
