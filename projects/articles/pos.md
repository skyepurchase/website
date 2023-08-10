---
title: Pseudo-Operating System
date: 10-08-2023

---

# Pseudo-Operating System 

<a href="https://github.com/skyepurchase/POS">
    <img src="https://github-readme-stats.vercel.app/api/pin/?username=skyepurchase&repo=POS&theme=dracula&hide_border=false"/>
</a>

The first project listed on my website!

04-08-2023

---

## Project Log

---

Slow progress as I struggled to open a file in C using Clang as the compiler. 
Switching to GCC resulted in the code working as I had assumed.
I will look into the issue further and hopefully gain a better understanding of the differences.

Since this change I have implemented a basic file handler in `file_handler.c` and finished a tokenizer in `parser.c`.

The AST for brainf\*\*k is basically just a sequence except for the loops which are simple `do ...; x--; while x != 0`.
This constitutes the only control flow in brainf\*\*k, but the language is still Turing complete and can be seen in comparison to _[register machines](https://en.wikipedia.org/wiki/Register_machine)_ (RMs).

The major difference is that RMs use a form of `goto` rather than loops where control flow happens on decriment.
A decriment operation in an RM is written as such: `Rx- L1 L2` where `x` is the register number and `Lx` is a label to go to.
If the contents of `Rx` are zero jump to `L2` otherwise decriment `Rx` and jump to `L1`.
_note that increment still contains a label `Rx+ L1` and so instructions are not necessary sequential._

Before writing a compiler to 6502 machine code I want to write a transpiler from brainf\*\*k to RM.
From brainf\*\*k to RM this should be fairly trivial as `++[>++<]` becomes
```
L0 R0+ L1       +
L1 R0+ L2       +

L2 R1+ L3       [>+
L3 R1+ L4       +
L4 R0- L2 L5    <]

L5 HALT
```
In this case the loop is identified and a decriment added at the end jumping to the beginning of the loop or falling through.
The code is made sequential.

Decriment can then have a fail condition which jumps to the final halt of the program.
Thus `++>+[<->]` becomes
```
L0 R0+ L1       +
L1 R0+ L2       +
L2 R1+ L3       >+

L3 R0- L4 L5    [<-
L4 R1- L3 L6    >]

L5 HALT
L6 HALT
```
_note that with a minor optimisation the `HALT`s can be combined_

So the next step is to parse the tokens into an AST where all decriments are control flow and all loops are converted to decriments.

