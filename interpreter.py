#!/usr/bin/env python3
import os
import subprocess
import time
import re
import sys

def lex(code):
    return re.findall(r'"[^"]*"|\S+', code)

def parse(tokens, variables):
    if not tokens:
        return None
    
    # Print
    if tokens[0] == 'p':
        return ('print', ' '.join(tokens[1:]))
    
    # Variable assignment
    elif len(tokens) >= 3 and tokens[1] == '=':
        return ('assign', tokens[0], ' '.join(tokens[2:]))
    
    # If statement
    elif tokens[0] == 'i':
        condition = ' '.join(tokens[1:tokens.index('{')])
        body = ' '.join(tokens[tokens.index('{')+1:-1])
        return ('if', condition, body)
    
    # Loop
    elif tokens[0] == 'l':
        times = int(tokens[1])
        body = ' '.join(tokens[tokens.index('{')+1:-1])
        return ('loop', times, body)
    
    # Function definition
    elif tokens[0] == 'f':
        name = tokens[1]
        body = ' '.join(tokens[tokens.index('{')+1:-1])
        return ('func', name, body)
    
    # Function call
    elif tokens[0] in variables and isinstance(variables[tokens[0]], str):
        return ('call', tokens[0])
    
    # Read input
    elif tokens[0] == 'r':
        prompt = ' '.join(tokens[1:]).strip('"')
        return ('input', prompt)
    
    elif tokens[0] == 'c':
        return ('comment')
    
    elif tokens[0] == 'w':
        seconds = float(tokens[1]) 
        return ('wait', seconds)
    
    # Exit
    elif tokens[0] == 'e':
        return ('exit',)
    
    elif tokens[0] == 't':
        cmd = ' '.join(tokens[1:])
        return ('terminal', cmd)
    
    elif tokens[0] == 'b':
        return ('beep',)
    
    elif tokens[0] == 'n': 
        freq = int(tokens[1]) if len(tokens) > 1 else 440
        return ('freq_beep', freq)
    
    # List operations
    elif tokens[0] == 'a' and len(tokens) > 1 and tokens[1] == '=':
        items = ' '.join(tokens[2:]).strip('[]').split()
        return ('list_create', tokens[0], items)
    
    # Get list item
    elif '[' in tokens[0] and ']' in tokens[0]:
        var = tokens[0].split('[')[0]
        index = tokens[0].split('[')[1].split(']')[0]
        return ('list_get', var, index)
    
    # Set list item
    elif len(tokens) > 2 and tokens[1] == '=' and '[' in tokens[0]:
        var = tokens[0].split('[')[0]
        index = tokens[0].split('[')[1].split(']')[0]
        return ('list_set', var, index, ' '.join(tokens[2:]))

def evaluate(expr, variables):
    try:
        # Replace variable names with their values
        for var in variables:
            if isinstance(variables[var], (int, float, str)) and var in expr:
                expr = expr.replace(var, str(variables[var]))
        return eval(expr)
    except:
        return expr

def interpret(code, variables):
    lines = [line.strip() for line in code.split('\n') if line.strip()]
    for line in lines:
        tokens = lex(line)
        action = parse(tokens, variables)
        if not action:
            continue
            
        # Print
        if action[0] == 'print':
            value = ' '.join(action[1:])
            if '"' in value:
                print(value.strip('"'))
            else:
                print(evaluate(value, variables))
        
        # Assign
        elif action[0] == 'assign':
            variables[action[1]] = evaluate(action[2], variables)
        
        # If statement
        elif action[0] == 'if':
            if evaluate(action[1], variables):
                interpret(action[2], variables)
        
        # Loop
        elif action[0] == 'loop':
            for _ in range(action[1]):
                interpret(action[2], variables)
        
        # Function definition
        elif action[0] == 'func':
            variables[action[1]] = action[2]
        
        # Function call
        elif action[0] == 'call':
            interpret(variables[action[1]], variables)
        
        # Input
        elif action[0] == 'input':
            variables['_'] = input(action[1] + ' ')
        
        # Exit
        elif action[0] == 'exit':
            sys.exit(0)
            
        elif action[0] == 'comment':
            continue

        elif action[0] == 'wait':
            time.sleep(action[1]) 
        
        elif action[0] == 'beep':
            print('\a', end='', flush=True)
        
        elif action[0] == 'freq_beep':
            os.system(f'play -n synth 0.1 sine {action[1]} 2>/dev/null')
        
        elif action[0] == 'terminal':
            print(f"$ {action[1]}")  # Show the command being run
            process = subprocess.Popen(
                action[1],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            for line in process.stdout:
                print(line, end='')  # Print output in real-time
            process.wait()

        # List create
        elif action[0] == 'list_create':
            variables[action[1]] = [evaluate(item, variables) for item in action[2]]
        
        # List get
        elif action[0] == 'list_get':
            index = evaluate(action[2], variables)
            print(variables[action[1]][int(index)])
        
        # List set
        elif action[0] == 'list_set':
            index = evaluate(action[2], variables)
            variables[action[1]][int(index)] = evaluate(action[3], variables)

def main():
    if len(sys.argv) != 2:
        print("Usage: python interpreter.py code.omm")
        sys.exit(1)
    with open(sys.argv[1], 'r') as file:
        code = file.read()
    interpret(code, {})

if __name__ == "__main__":
    main()
