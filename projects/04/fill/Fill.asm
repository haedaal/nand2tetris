// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
    @8192
    D=A
    @limit
    M=D
(LOOP)
    @offset
    D=M
    MD=D+1
    @limit
    D=M-D
    @ROUND
    D; JLE
    @INPUT
    0; JMP

(ROUND)
    @offset
    M=0
    @INPUT
    0; JMP

(INPUT)
    @KBD
    D=M
    @PAINT_BLACK
    D; JNE
    @PAINT_WHITE
    0; JMP


(PAINT_BLACK)
    @SCREEN
    D=A
    @offset
    A=D+M
    M=-1
    @LOOP
    0; JMP

(PAINT_WHITE)
    @SCREEN
    D=A
    @offset
    A=D+M
    M=0
    @LOOP
    0; JMP