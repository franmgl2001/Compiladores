# C- Compilation to MIPS Assembly
# File: output.asm
# Using symbol table offsets for variable access


.text
.globl main
main:
    move $fp, $sp
    subu $sp, $sp, 100
    # Cuerpo de la funcion main
    # Compound statement
    li   $t0, 100
    subu $sp, $sp, 4
    sw   $t0, 0($sp)
    li   $t0, 0
    sll  $t0, $t0, 2
    addi $t1, $fp, -16
    add  $t1, $t1, $t0
    lw   $t0, 0($sp)
    sw   $t0, 0($t1)
    # Array assignment: nums[index] = value
    addu $sp, $sp, 4
    li   $t0, 200
    subu $sp, $sp, 4
    sw   $t0, 0($sp)
    li   $t0, 1
    sll  $t0, $t0, 2
    addi $t1, $fp, -16
    add  $t1, $t1, $t0
    lw   $t0, 0($sp)
    sw   $t0, 0($t1)
    # Array assignment: nums[index] = value
    addu $sp, $sp, 4
    li   $t0, 300
    subu $sp, $sp, 4
    sw   $t0, 0($sp)
    li   $t0, 2
    sll  $t0, $t0, 2
    addi $t1, $fp, -16
    add  $t1, $t1, $t0
    lw   $t0, 0($sp)
    sw   $t0, 0($t1)
    # Array assignment: nums[index] = value
    addu $sp, $sp, 4
    # Input function call
    li   $t0, 0
    subu $sp, $sp, 4
    sw   $t0, 0($sp)
    lw   $t1, 0($sp)
    addu $sp, $sp, 4
    sll  $t1, $t1, 2
    addi $t2, $fp, -16
    add  $t2, $t2, $t1
    lw   $t0, 0($t2)
    # Array access: nums[index]
    sw   $t0, -4($fp)
    # Output function call
    lw   $t0, -4($fp)
    move $a0, $t0
    li   $v0, 1
    syscall
    li   $v0, 11
    li   $a0, 10
    syscall
    # Input function call
    li   $t0, 1
    subu $sp, $sp, 4
    sw   $t0, 0($sp)
    lw   $t1, 0($sp)
    addu $sp, $sp, 4
    sll  $t1, $t1, 2
    addi $t2, $fp, -16
    add  $t2, $t2, $t1
    lw   $t0, 0($t2)
    # Array access: nums[index]
    sw   $t0, -4($fp)
    # Output function call
    lw   $t0, -4($fp)
    move $a0, $t0
    li   $v0, 1
    syscall
    li   $v0, 11
    li   $a0, 10
    syscall
    # Input function call
    li   $t0, 2
    subu $sp, $sp, 4
    sw   $t0, 0($sp)
    lw   $t1, 0($sp)
    addu $sp, $sp, 4
    sll  $t1, $t1, 2
    addi $t2, $fp, -16
    add  $t2, $t2, $t1
    lw   $t0, 0($t2)
    # Array access: nums[index]
    sw   $t0, -4($fp)
    # Output function call
    lw   $t0, -4($fp)
    move $a0, $t0
    li   $v0, 1
    syscall
    li   $v0, 11
    li   $a0, 10
    syscall
    move $sp, $fp
    li   $v0, 10
    syscall
