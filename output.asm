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
    # Function call: factorial
    # evaluate argument 1
    li   $t0, 5       # load constant 5
    move $a0, $t0          # argument 1 -> $a0
    jal  factorial           # call factorial
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
    # While statement
L1:
    # While condition
    lw   $t0, -8($fp)  # load x from offset -8
    subu $sp, $sp, 4       # make space on stack
    sw   $t0, 0($sp)       # save left operand
    li   $t0, 1       # load constant 1
    lw   $t1, 0($sp)       # load left operand into $t1
    addu $sp, $sp, 4       # restore stack pointer
    sgt  $t0, $t1, $t0     # set $t0 = 1 if $t1 > $t0, else 0
    beq  $t0, $zero, L2  # exit loop if condition is false
    # While body
    lw   $t0, -8($fp)  # load x from offset -8
    subu $sp, $sp, 4       # make space on stack
    sw   $t0, 0($sp)       # save left operand
    li   $t0, 1       # load constant 1
    lw   $t1, 0($sp)       # load left operand into $t1
    addu $sp, $sp, 4       # restore stack pointer
    sub  $t0, $t1, $t0     # subtract: $t0 = $t1 - $t0
    sw   $t0, -8($fp)  # assign to x at offset -8
    # Assignment: x = expression
    lw   $t0, -16($fp)  # load i from offset -16
    # ERROR: Invalid assignment target
    # Output function call - print stored value
    move $a0, $t0           # move expression result to $a0
    li   $v0, 1             # syscall 1 = print integer
    syscall                 # print the integer
    li   $v0, 11            # syscall 11 = print character
    li   $a0, 10            # ASCII 10 = newline
    syscall                 # print newline
    j    L1          # jump back to condition
L2:
    # End of while statement
    # Restore stack and exit
    move $sp, $fp           # restore stack pointer
    li   $v0, 10            # exit program
    syscall

# Function: factorial
factorial:
    # Function prologue
    subu $sp, $sp, 8       # make space for $ra and $fp
    sw   $ra, 4($sp)       # save return address
    sw   $fp, 0($sp)       # save old frame pointer
    move $fp, $sp          # set new frame pointer
    subu $sp, $sp, 100     # allocate space for locals
    # Save parameter registers
    sw   $a0, -4($fp)      # save parameter 1
    sw   $a1, -8($fp)      # save parameter 2
    sw   $a2, -12($fp)     # save parameter 3
    sw   $a3, -16($fp)     # save parameter 4
    # Function body for factorial
    # Compound statement
    # If statement
    lw   $t0, -4($fp)  # load n from offset -4
    subu $sp, $sp, 4       # make space on stack
    sw   $t0, 0($sp)       # save left operand
    li   $t0, 1       # load constant 1
    lw   $t1, 0($sp)       # load left operand into $t1
    addu $sp, $sp, 4       # restore stack pointer
    sle  $t0, $t1, $t0     # set $t0 = 1 if $t1 <= $t0, else 0
    beq  $t0, $zero, L3  # branch to else if condition is false
    # Then branch
    # Compound statement
    # Return statement
    li   $t0, 1       # load constant 1
    move $v0, $t0          # move return value to $v0
    # Function epilogue (return)
    move $sp, $fp          # restore stack pointer
    lw   $fp, 0($sp)       # restore old frame pointer
    lw   $ra, 4($sp)       # restore return address
    addu $sp, $sp, 8       # deallocate frame
    jr   $ra               # return to caller
    j    L4           # jump to end
L3:
L4:
    # End of if statement
    # Return statement
    lw   $t0, -4($fp)  # load n from offset -4
    subu $sp, $sp, 4       # make space on stack
    sw   $t0, 0($sp)       # save left operand
    # Function call: factorial
    # evaluate argument 1
    lw   $t0, -4($fp)  # load n from offset -4
    subu $sp, $sp, 4       # make space on stack
    sw   $t0, 0($sp)       # save left operand
    li   $t0, 1       # load constant 1
    lw   $t1, 0($sp)       # load left operand into $t1
    addu $sp, $sp, 4       # restore stack pointer
    sub  $t0, $t1, $t0     # subtract: $t0 = $t1 - $t0
    move $a0, $t0          # argument 1 -> $a0
    jal  factorial           # call factorial
    move $t0, $v0          # capture return value
    lw   $t1, 0($sp)       # load left operand into $t1
    addu $sp, $sp, 4       # restore stack pointer
    mul  $t0, $t1, $t0     # multiply: $t0 = $t1 * $t0
    move $v0, $t0          # move return value to $v0
    # Function epilogue (return)
    move $sp, $fp          # restore stack pointer
    lw   $fp, 0($sp)       # restore old frame pointer
    lw   $ra, 4($sp)       # restore return address
    addu $sp, $sp, 8       # deallocate frame
    jr   $ra               # return to caller
    # Function epilogue for factorial
    move $sp, $fp          # restore stack pointer
    lw   $fp, 0($sp)       # restore old frame pointer
    lw   $ra, 4($sp)       # restore return address
    addu $sp, $sp, 8       # deallocate frame
    jr   $ra               # return to caller
