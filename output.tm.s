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
    li   $t0, 3       # load constant 3
    sw   $t0, -12($fp)  # assign to y at offset -12
    # Assignment: y = expression
    # Input function call - store expression value
    li   $t0, 5       # load constant 5
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
    lw   $t0, -12($fp)  # load y from offset -12
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
    # Pushing 2 arguments
    # Evaluate argument 1
    li   $t0, 3       # load constant 3
    subu $sp, $sp, 4       # make space for argument
    sw   $t0, 0($sp)       # push argument 1
    # Evaluate argument 2
    lw   $t0, -8($fp)  # load x from offset -8
    subu $sp, $sp, 4       # make space for argument
    sw   $t0, 0($sp)       # push argument 2
    jal  sum           # call function sum
    addu $sp, $sp, 8  # remove arguments from stack
    move $t0, $v0          # move function result to $t0
    sw   $t0, -16($fp)  # assign to result at offset -16
    # Assignment: result = expression
    # Input function call - store expression value
    lw   $t0, -16($fp)  # load result from offset -16
    sw   $t0, -4($fp)       # store input value at -4($fp)
    # Output function call - print stored value
    lw   $t0, -16($fp)  # load result from offset -16
    move $a0, $t0           # move expression result to $a0
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
    # Copy arguments into parameter locations
    lw   $t0, 8($fp)    # load argument from caller's stack
    sw   $t0, -20($fp) # store into parameter a
    lw   $t0, 4($fp)    # load argument from caller's stack
    sw   $t0, -24($fp) # store into parameter b
    # Function body for sum
    # Compound statement
    # Input function call - store expression value
    lw   $t0, -20($fp)  # load a from offset -20
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
    lw   $t0, -24($fp)  # load b from offset -24
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
    lw   $t0, -20($fp)  # load a from offset -20
    subu $sp, $sp, 4       # make space on stack
    sw   $t0, 0($sp)       # save left operand
    lw   $t0, -24($fp)  # load b from offset -24
    lw   $t1, 0($sp)       # load left operand into $t1
    addu $sp, $sp, 4       # restore stack pointer
    add  $t0, $t1, $t0     # add: $t0 = $t1 + $t0
    move $v0, $t0          # move return value to $v0
    # Function epilogue (return)
    move $sp, $fp          # restore stack pointer
    lw   $fp, 0($sp)       # restore old frame pointer
    addu $sp, $sp, 4       # deallocate space for old $fp
    jr   $ra               # return to caller
    # Function epilogue for <globalTypes.TreeNode object at 0x1011b4650>
    move $sp, $fp          # restore stack pointer
    lw   $fp, 0($sp)       # restore old frame pointer
    addu $sp, $sp, 4       # deallocate space for old $fp
    jr   $ra               # return to caller
