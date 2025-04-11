# O-- the simplest programming language i know

Run code with

```bash
python interpreter.py FILE.omm
```

## Basics
To print in `O--` all you need to do is

```rs
p "hello, world!"
```
And the output is

```rs
hello, world!
```

### Variables
Variables are VERY easy all you need to do is

```rs
x = 1
```

Thats it!

### Math
Math is also very easy

```rs
x = 1
p x + 1
```
other symbols work aswell `+,-,/,*`

### If statement's
these are very easy

```rs
x = 6
i x > 5 { p "x is greater than 5" }
```

### Functions
functions are simple

```rs
f func { p "function" }
func
```

output

```rs
function
```

### Waitng / Sleeping

waiting is very simple just do

```rs
w 2
```
the code will wait for 2 seconds. decimals are also supported like `2.5`

### Loops
Loops are simple

```rs
l 3 { p "looped 3 times" }
```

`infinite` loops are not possible but there's a workaround

```rs
l 999999999999999999 { "infinite loop?" }
```

just shove alot of 9's there

### Run Terminal Commands
simple. as always

```rs
t python --version
```
`t` stands for TERMINAL

### Comments
comments are `VERY` simple

```rs
c comment
```
inline comments are not possible yet

### Boop
```rs
b
```

## Musical Note
First thing, if you want it to be easy use the music editor.

making a musical note is not as simple as just `n C4`, that would play the C4 note right? no. this is how

```rs
n 261
```
C4 note is 261 hertz. its not that simple, but the only downside is you have to look up the hertz of every note you want to play.

### Neural networks
You can make simple neural networks in `O--`
`k` is for knowledge

```rs
k _dogs say woof
k dogs say
```
it will output `woof`
the underscore is for silent. meaning it will not output

### EXIT
```rs
e
```