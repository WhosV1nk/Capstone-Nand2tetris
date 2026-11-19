// Box.asm — Vinayak Sharma, roll no. 2501410003, K=3
// Draws a 64-pixel-wide (4-word) by 20-pixel-high black rectangle.
// Top row = 3. Rectangle begins at the left edge.
// While any key is pressed, fill the rectangle with black (all 1s).
// When no key is pressed, clear it to white (all 0s).

(START)
    @KBD
    D=M
    @DRAW
    D;JGT

// No key: clear the rectangle.
(CLEAR)
    @SCREEN
    D=A
    @32
    D=D+A
    @32
    D=D+A
    @32
    D=D+A
    @R13
    M=D
    @20
    D=A
    @R14
    M=D

(CLEAR_ROW)
    @R13
    A=M
    M=0
    A=A+1
    M=0
    A=A+1
    M=0
    A=A+1
    M=0
    @R13
    D=M
    @32
    D=D+A
    @R13
    M=D
    @R14
    MD=M-1
    @CLEAR_ROW
    D;JGT
    @START
    0;JMP

// Key pressed: draw the rectangle.
(DRAW)
    @SCREEN
    D=A
    @32
    D=D+A
    @32
    D=D+A
    @32
    D=D+A
    @R13
    M=D
    @20
    D=A
    @R14
    M=D

(DRAW_ROW)
    @R13
    A=M
    M=-1
    A=A+1
    M=-1
    A=A+1
    M=-1
    A=A+1
    M=-1
    @R13
    D=M
    @32
    D=D+A
    @R13
    M=D
    @R14
    MD=M-1
    @DRAW_ROW
    D;JGT
    @START
    0;JMP
