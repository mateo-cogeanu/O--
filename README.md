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
other symbols work aswell `+,-,/`

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
the code will wait for 2 seconds
decimals are also supported like `2.5`

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

### Comments
comments are `VERY` simple

```rs
c comment
```
inline comments are not possible yet

### EXIT
```rs
e
```