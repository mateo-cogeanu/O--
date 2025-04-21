#!/usr/bin/env python3
import matplotlib # type: ignore
import pygame  # type: ignore
import random
from collections import defaultdict
import os
import subprocess
import time
import re
import sys

class GloopManager:
    def __init__(self):
        self.loaded_files = {}
    
    def parse_glop(self, filename):
        """Parse a .glop file into a dictionary"""
        data = {}
        try:
            with open(filename) as f:
                for line in f:
                    line = line.strip()
                    if line and ':' in line:
                        key, value = line.split(':', 1)
                        data[key.strip()] = self._convert_value(value.strip())
            return data
        except FileNotFoundError:
            print(f"Gloop file {filename} not found")
            return None
    
    def _convert_value(self, value):
        """Convert string values to proper types"""
        value = value.strip('"\'')  # Remove surrounding quotes
        
        # Type conversion
        if value.lower() == 'true': return True
        if value.lower() == 'false': return False
        if value.isdigit(): return int(value)
        try: return float(value)
        except ValueError: return value
    
    def import_file(self, filename):
        """Load .glop file into memory"""
        data = self.parse_glop(filename)
        if data:
            self.loaded_files[filename] = data
            return True
        return False
    
    def get_value(self, filename, key):
        """Get value from loaded .glop file"""
        if filename in self.loaded_files:
            return self.loaded_files[filename].get(key)
        return None

gloop_manager = GloopManager()

class GameEngine:
    def __init__(self):
        self.screen = None
        self.objects = []
        self.running = False
        self.clock = pygame.time.Clock()
    
    def init(self, width, height):
        self.screen = pygame.display.set_mode((width, height))
        self.running = True
        print(f"Game ready! {width}x{height}")
    
    def add_box(self, x, y, w, h, color):
        self.objects.append({
            'type': 'box',
            'x': x, 'y': y,
            'w': w, 'h': h,
            'color': color,
            'vel_y': 0
        })
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.objects[0]['vel_y'] = -15  # Jump
    
    def update(self):
        for obj in self.objects:
            obj['vel_y'] += 0.5  # Gravity
            obj['y'] += obj['vel_y']
            
            # Floor collision
            if obj['y'] > 550:
                obj['y'] = 550
                obj['vel_y'] = 0
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        for obj in self.objects:
            pygame.draw.rect(
                self.screen,
                obj['color'],
                (obj['x'], obj['y'], obj['w'], obj['h'])
            )
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()

game_engine = GameEngine()

class MiniBrain:
    def __init__(self):
        self.memory = defaultdict(list)  # {pattern: [responses]}
        self.triggers = defaultdict(int) # {phrase: count}
    
    def learn(self, input_text):
        words = input_text.lower().split()
        self.triggers[' '.join(words)] += 1
        
        # Store word sequences
        for i in range(len(words)-1):
            pattern = ' '.join(words[:i+1])
            response = words[i+1]
            self.memory[pattern].append(response)
    
    def respond(self, input_text):
        words = input_text.lower().split()
        for i in reversed(range(len(words))):
            pattern = ' '.join(words[:i+1])
            if pattern in self.memory:
                return random.choice(self.memory[pattern])
        return random.choice(["Hmm", "Interesting", "Tell me more"])
    
    def save(self, filename="brain.mem"):
        with open(filename, 'w') as f:
            f.write(str(dict(self.memory)))

    def load(self, filename="brain.mem"):
        try:
            with open(filename) as f:
                self.memory = eval(f.read())
        except:
            self.memory = defaultdict(list)

brain = MiniBrain()

def mandelbrot(width, height, max_iter):
    import numpy as np # type: ignore
    x_min, x_max = -2.0, 1.0
    y_min, y_max = -1.5, 1.5
    image = np.zeros((height, width))

    for row in range(height):
        for col in range(width):
            # Map pixel position to a point in the complex plane
            x = x_min + (x_max - x_min) * col / width
            y = y_min + (y_max - y_min) * row / height
            c = complex(x, y)
            z = 0
            for iteration in range(max_iter):
                if abs(z) > 2:
                    break
                z = z * z + c
            image[row, col] = iteration

    return image

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
    
    elif tokens[0] == 'k':
        return ('brain', ' '.join(tokens[1:]))
    
    elif tokens[0] == 'g':
        if len(tokens) < 2:
            return ('game_help',)
        return ('game', tokens[1], tokens[2:])
    
    elif tokens[0] == 'gl':
        if len(tokens) < 3:
            raise SyntaxError("Usage: gl <i|v> <file.glop> [key]")
        return ('gloop', tokens[1], tokens[2], tokens[3] if len(tokens) > 3 else None)
    
    elif tokens[0] == 'im':
        return ('import', tokens[1])
    
    elif tokens[0] == 'ma':
        if len(tokens) < 4:
            raise SyntaxError("Usage: ma w h m")
        w = int(tokens[1])
        h = int(tokens[2])
        m = int(tokens[3])
        return ('mandelbrot', w, h, m)

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

        elif action[0] == 'brain':
            input_text = action[1]
            if not input_text.startswith('_'):
                print("Brain:", brain.respond(input_text))
            brain.learn(input_text.lstrip('_'))
        
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
        
        elif action[0] == 'game':
            cmd = action[1]
            args = action[2]
    
            if cmd == 'init':
                game_engine.init(int(args[0]), int(args[1]))
    
            elif cmd == 'box':
                color = (int(args[4]), int(args[5]), int(args[6]))
                game_engine.add_box(
                    float(args[0]), float(args[1]),
                    float(args[2]), float(args[3]),
                    color
                )
    
            elif cmd == 'run':
                game_engine.run()
        
        elif action[0] == 'gloop':
            cmd, filename, arg = action[1], action[2], action[3]
    
            if not filename.endswith('.glop'):
                filename += '.glop'
    
            if cmd == 'i':  # Import
                if gloop_manager.import_file(filename):
                    for k, v in gloop_manager.loaded_files[filename].items():
                        variables[k] = v
                    print(f"Imported {filename}")
    
            elif cmd == 'v':  # View value
                value = gloop_manager.get_value(filename, arg)
                print(value if value is not None else f"Key '{arg}' not found")
        
        elif action[0] == 'import':
                filename = action[1]
                if not filename.endswith('.omm'):
                    filename += '.omm'
                try:
                    with open(filename, 'r') as file:
                        imported_code = file.read()
                    interpret(imported_code, variables)
                    print(f"Imported {filename}")
                except FileNotFoundError:
                        print(f"Error: File '{filename}' not found")
        
        elif action[0] == 'mandelbrot':
            import matplotlib.pyplot as plt # type: ignore
            width, height, max_iter = action[1], action[2], action[3]
            print(f"Generating Mandelbrot set ({width}x{height}, {max_iter} iterations)")
            image = mandelbrot(width, height, max_iter)
            plt.imshow(image, extent=(-2, 1, -1.5, 1.5), cmap='hot', interpolation='bilinear')
            plt.colorbar()
            plt.title("Mandelbrot Set")
            plt.show()


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
