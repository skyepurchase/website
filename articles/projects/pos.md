---
title: Pseudo-Operating System
date: 17-08-2023

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

The AST for Brainf\*\*k is basically just a sequence except for the loops which are simple `do ...; x--; while x != 0`.
This constitutes the only control flow in Brainf\*\*k, but the language is still Turing complete and can be seen in comparison to _[register machines](https://en.wikipedia.org/wiki/Register_machine)_ (RMs).

The major difference is that RMs use a form of `goto` rather than loops where control flow happens on decriment.
A decriment operation in an RM is written as such: `Rx- L1 L2` where `x` is the register number and `Lx` is a label to go to.
If the contents of `Rx` are zero jump to `L2` otherwise decriment `Rx` and jump to `L1`.
_note that increment still contains a label `Rx+ L1` and so instructions are not necessary sequential._

Before writing a compiler to 6502 machine code I want to write a transpiler from Brainf\*\*k to RM.
From Brainf\*\*k to RM this should be fairly trivial as `++[>++<]` becomes
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

10-08-2023

---

No progress on the actual code however I noticed a mistake in how I interpretted Brainf\*\*k and found an example of a potentially problematic program.

### Brainf**k

Brainf\*\*k uses 8 characters of which only 7 are practical on an 8-bit machine as input is tricky.
These symbols are `+ - < > [ ] . ,` for increment, decriment, left, right, begin-loop, loop-if-zero, output, and (the removed) input.

Note that `]` is _loop-if-zero_ and thus does not decriment the counter unlike `Rx-` in RMs.
Further more `>` and `<` just increment or decriment a register counter which can be a different value at the start of each loop.

### RMs

RMs have 2 actions `Rx+` (from now on denoted `ADD`) and `Rx-` (from now on denoted `SUB`).
It also has labels that can be jumped to after each `ADD` and `SUB`.
It does not have explicit loops and _it has fixed register operations_!

### The changes

Based on the new interpretation of Brainf\*\*k this means the program `++[>++<]` does not terminate as `R0` remains at `2` throughout.
It must therefore be `++[>++<-]` to prevent non-termination but could also be `++[->++<]` or even `++[>+<->+<]` just to demonstrate that it is difficult to change a loop into a simple `SUB` operation.

If the program contains a `-]` this can be directly converted to a `SUB` with a "zero-jump" back to a previous label.
A "lonely" `-` can be converted to a `SUB` with a "zero-jump" to a `HALT` instructions.
_unfortunately no error codes in Brainf\*\*k_.

Furthermore, `>>[+<]` is a valid program which does halt.
It corresponds to the following RM program:
```
L0 R2+ L1
L1 R1+ L2
L2 HALT
```
Note that the loop has to be unrolled because of the requirement of fixed registers.

### The solution

1. Once the program is tokenized we want to "push" `-` as late as possible so that they may "collide" with a loop character, `[` or `]`.

Example:

`++[->++<]`, `++[><->++<]`, `++[>+<->+<]`, etc. all become  `++[>++<-]` which is the program we can easily convert into RM code.
_NOTE_ no decriment should be pushed outside of or after a loop as this can change the control flow.

2. The `>` and `<` need to be tracked inside of a loop.
If they are balanced then the register count at the start of the loop is the same and thus can be converted to an RM loop.

If they are not balanced the compiler will through an error ... at the moment.
Figuring out how many times a loop will run is not tractable (as it requires running the program to work out) and setting up the operation for all possible starting register counts is also not possible as there are countably infinite possibilities.

Quick notes on this problem:

An RM program exists that can run any Brainf\*\*k program by simulating the register states and interpretting the "compiled" Brainf\*\*k program.
By "compiled" I mean the Godel-esque number ([Godel numbering](https://en.wikipedia.org/wiki/G%C3%B6del_numbering)) corresponding to the the Brainf\*\*k program.
The opposite is also true.
Maybe I'll post an in-depth explanation about this later (the _theory of computation_ is a fascinating concept).

This means that Brainf\*\*k is not "more powerful" than RMs and in fact, by the [Church-Turing thesis](https://en.wikipedia.org/wiki/Church%E2%80%93Turing_thesis), are equally powerful being Turing complete.

However, this does not mean converting from one form to the other is easy (or possible? I'm not confident on that last point, guess I need to prove that these weird loops definitively cannot be converted ... bringing in the Halting problem :eyes:).

_ALSO_ any Brainf\*\*k program can be rewritten to do the same action without using this "hack" but the onous is now on the programmer. This is a common feature of compilers, computers are dumb they can only do so much, think about your code!

