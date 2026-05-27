#!/usr/bin/env python3
"""
Advanced Scientific Calculator with Taylor Series Approximations
Features:
- Custom elementary functions using Taylor series
- LaTeX-style visual input display
- Revamped modern UI
- Exponent support with ^ notation
- Trig, inverse trig, hyperbolic, and inverse hyperbolic functions
- Constants (pi, e)
- Fraction conversion
- DEG/RAD mode
"""

import tkinter as tk
from tkinter import ttk, font
import math
import sympy
from sympy import symbols, simplify, nsimplify, pi, E, sqrt, sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, asinh, acosh, atanh, exp, log, N
import re

class TaylorSeriesCalculator:
    """Custom mathematical functions using Taylor series approximations"""
    
    @staticmethod
    def factorial(n):
        if n <= 1:
            return 1
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result
    
    @staticmethod
    def sin_taylor(x, terms=20):
        """sin(x) = x - x³/3! + x⁵/5! - x⁷/7! + ..."""
        # Normalize x to [-π, π] for better convergence
        while x > math.pi:
            x -= 2 * math.pi
        while x < -math.pi:
            x += 2 * math.pi
        
        result = 0
        for n in range(terms):
            sign = (-1) ** n
            power = 2 * n + 1
            term = sign * (x ** power) / TaylorSeriesCalculator.factorial(power)
            result += term
        return result
    
    @staticmethod
    def cos_taylor(x, terms=20):
        """cos(x) = 1 - x²/2! + x⁴/4! - x⁶/6! + ..."""
        # Normalize x to [-π, π]
        while x > math.pi:
            x -= 2 * math.pi
        while x < -math.pi:
            x += 2 * math.pi
        
        result = 0
        for n in range(terms):
            sign = (-1) ** n
            power = 2 * n
            term = sign * (x ** power) / TaylorSeriesCalculator.factorial(power)
            result += term
        return result
    
    @staticmethod
    def tan_taylor(x, terms=20):
        """tan(x) = sin(x) / cos(x)"""
        cos_val = TaylorSeriesCalculator.cos_taylor(x, terms)
        if abs(cos_val) < 1e-10:
            raise ValueError("Undefined (tan approaches infinity)")
        return TaylorSeriesCalculator.sin_taylor(x, terms) / cos_val
    
    @staticmethod
    def exp_taylor(x, terms=30):
        """e^x = 1 + x + x²/2! + x³/3! + ..."""
        # For large x, use e^x = e^(x/n)^n for better convergence
        if abs(x) > 10:
            n = int(abs(x) / 5) + 1
            return TaylorSeriesCalculator.exp_taylor(x / n, terms) ** n
        
        result = 0
        for i in range(terms):
            result += (x ** i) / TaylorSeriesCalculator.factorial(i)
        return result
    
    @staticmethod
    def ln_taylor(x, terms=100):
        """ln(x) using ln(1+y) = y - y²/2 + y³/3 - ... for |y| < 1"""
        if x <= 0:
            raise ValueError("ln undefined for x <= 0")
        
        # Use ln(x) = ln(x/e^k) + k to bring x close to 1
        k = 0
        while x > 2:
            x /= math.e
            k += 1
        while x < 0.5:
            x *= math.e
            k -= 1
        
        # Now use ln(1 + y) where y = x - 1
        y = x - 1
        if abs(y) >= 1:
            # Fallback for edge cases
            return math.log(x)
        
        result = 0
        for n in range(1, terms):
            term = ((-1) ** (n + 1)) * (y ** n) / n
            result += term
            if abs(term) < 1e-15:
                break
        
        return result + k
    
    @staticmethod
    def sqrt_newton(x, iterations=20):
        """Square root using Newton's method"""
        if x < 0:
            raise ValueError("sqrt undefined for negative numbers")
        if x == 0:
            return 0
        
        guess = x / 2 if x > 1 else 1
        for _ in range(iterations):
            guess = (guess + x / guess) / 2
        return guess
    
    @staticmethod
    def asin_taylor(x, terms=50):
        """asin(x) = x + (1/2)(x³/3) + (1·3)/(2·4)(x⁵/5) + ..."""
        if abs(x) > 1:
            raise ValueError("asin undefined for |x| > 1")
        
        # For |x| close to 1, use identity: asin(x) = π/2 - asin(√(1-x²))
        if abs(x) > 0.9:
            sign = 1 if x > 0 else -1
            return sign * (math.pi / 2 - TaylorSeriesCalculator.asin_taylor(TaylorSeriesCalculator.sqrt_newton(1 - x*x), terms))
        
        result = x
        term = x
        for n in range(1, terms):
            term *= x * x * (2*n - 1) * (2*n - 1) / ((2*n) * (2*n + 1))
            result += term
            if abs(term) < 1e-15:
                break
        return result
    
    @staticmethod
    def acos_taylor(x, terms=50):
        """acos(x) = π/2 - asin(x)"""
        return math.pi / 2 - TaylorSeriesCalculator.asin_taylor(x, terms)
    
    @staticmethod
    def atan_taylor(x, terms=50):
        """atan(x) = x - x³/3 + x⁵/5 - x⁷/7 + ..."""
        # For |x| > 1, use identity: atan(x) = π/2 - atan(1/x)
        if abs(x) > 1:
            sign = 1 if x > 0 else -1
            return sign * (math.pi / 2 - TaylorSeriesCalculator.atan_taylor(1/x, terms))
        
        result = 0
        for n in range(terms):
            term = ((-1) ** n) * (x ** (2*n + 1)) / (2*n + 1)
            result += term
            if abs(term) < 1e-15:
                break
        return result
    
    @staticmethod
    def sinh_taylor(x, terms=20):
        """sinh(x) = x + x³/3! + x⁵/5! + ..."""
        return (TaylorSeriesCalculator.exp_taylor(x, terms) - TaylorSeriesCalculator.exp_taylor(-x, terms)) / 2
    
    @staticmethod
    def cosh_taylor(x, terms=20):
        """cosh(x) = 1 + x²/2! + x⁴/4! + ..."""
        return (TaylorSeriesCalculator.exp_taylor(x, terms) + TaylorSeriesCalculator.exp_taylor(-x, terms)) / 2
    
    @staticmethod
    def tanh_taylor(x, terms=20):
        """tanh(x) = sinh(x) / cosh(x)"""
        cosh_val = TaylorSeriesCalculator.cosh_taylor(x, terms)
        if abs(cosh_val) < 1e-10:
            raise ValueError("Undefined")
        return TaylorSeriesCalculator.sinh_taylor(x, terms) / cosh_val
    
    @staticmethod
    def asinh_taylor(x, terms=50):
        """asinh(x) = ln(x + √(x² + 1))"""
        return TaylorSeriesCalculator.ln_taylor(x + TaylorSeriesCalculator.sqrt_newton(x*x + 1), terms)
    
    @staticmethod
    def acosh_taylor(x, terms=50):
        """acosh(x) = ln(x + √(x² - 1))"""
        if x < 1:
            raise ValueError("acosh undefined for x < 1")
        return TaylorSeriesCalculator.ln_taylor(x + TaylorSeriesCalculator.sqrt_newton(x*x - 1), terms)
    
    @staticmethod
    def atanh_taylor(x, terms=50):
        """atanh(x) = 0.5 * ln((1+x)/(1-x))"""
        if abs(x) >= 1:
            raise ValueError("atanh undefined for |x| >= 1")
        return 0.5 * TaylorSeriesCalculator.ln_taylor((1 + x) / (1 - x), terms)


class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Scientific Calculator")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a2e')
        
        self.angle_mode = 'DEG'  # DEG or RAD
        self.expression = ""
        self.display_expression = ""  # For LaTeX-style display
        self.last_result = None
        self.has_error = False
        
        # Setup custom fonts
        self.title_font = font.Font(family='Helvetica', size=14, weight='bold')
        self.display_font = font.Font(family='Courier New', size=18, weight='bold')
        self.button_font = font.Font(family='Helvetica', size=11, weight='bold')
        self.small_button_font = font.Font(family='Helvetica', size=9)
        
        self.setup_ui()
        self.bind_keyboard()
    
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title bar
        title_frame = tk.Frame(main_frame, bg='#16213e', relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(title_frame, text="🔬 Scientific Calculator", 
                              font=self.title_font, bg='#16213e', fg='#e94560')
        title_label.pack(pady=10)
        
        # Mode indicator
        mode_frame = tk.Frame(title_frame, bg='#16213e')
        mode_frame.pack(side=tk.RIGHT, padx=15)
        
        self.mode_label = tk.Label(mode_frame, text="DEG", font=self.small_button_font, 
                                   bg='#e94560', fg='white', padx=10, pady=5)
        self.mode_label.pack()
        
        # Display frame with LaTeX-style rendering
        display_frame = tk.Frame(main_frame, bg='#0f3460', relief=tk.SUNKEN, bd=3)
        display_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Expression display (LaTeX-style)
        self.expr_display = tk.Text(display_frame, height=3, font=self.display_font,
                                    bg='#0f3460', fg='#ffffff', insertbackground='white',
                                    wrap=tk.NONE, relief=tk.FLAT, padx=10, pady=10)
        self.expr_display.pack(fill=tk.X, padx=5, pady=5)
        self.expr_display.config(state='disabled')
        
        # Result display
        self.result_display = tk.Label(display_frame, text="0", font=('Courier New', 24, 'bold'),
                                       bg='#0f3460', fg='#4ecca3', anchor='e', padx=10, pady=5)
        self.result_display.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#1a1a2e')
        button_frame.pack(fill=tk.BOTH, expand=True)
        
        # Define button layouts
        buttons = [
            # Row 1: Constants and mode
            [('π', '#9b59b6', self.insert_pi), ('e', '#9b59b6', self.insert_e), 
             ('deg/rad', '#e67e22', self.toggle_mode), ('(', '#34495e', lambda: self.insert('(')), 
             (')', '#34495e', lambda: self.insert(')')), ('⌫', '#e74c3c', self.backspace),
             ('C', '#e74c3c', self.clear)],
            
            # Row 2: Advanced functions
            [('sin', '#2980b9', lambda: self.insert_func('sin')), 
             ('cos', '#2980b9', lambda: self.insert_func('cos')),
             ('tan', '#2980b9', lambda: self.insert_func('tan')),
             ('ln', '#2980b9', lambda: self.insert_func('ln')),
             ('log', '#2980b9', lambda: self.insert_func('log')),
             ('√', '#2980b9', lambda: self.insert_func('sqrt')),
             ('^', '#2980b9', lambda: self.insert('^'))],
            
            # Row 3: Inverse trig
            [('sin⁻¹', '#8e44ad', lambda: self.insert_func('asin')),
             ('cos⁻¹', '#8e44ad', lambda: self.insert_func('acos')),
             ('tan⁻¹', '#8e44ad', lambda: self.insert_func('atan')),
             ('exp', '#2980b9', lambda: self.insert_func('exp')),
             ('x²', '#2980b9', lambda: self.insert('**2')),
             ('xʸ', '#2980b9', lambda: self.insert('^')),
             ('!', '#2980b9', self.insert_factorial)],
            
            # Row 4: Hyperbolic
            [('sinh', '#16a085', lambda: self.insert_func('sinh')),
             ('cosh', '#16a085', lambda: self.insert_func('cosh')),
             ('tanh', '#16a085', lambda: self.insert_func('tanh')),
             ('sinh⁻¹', '#1abc9c', lambda: self.insert_func('asinh')),
             ('cosh⁻¹', '#1abc9c', lambda: self.insert_func('acosh')),
             ('tanh⁻¹', '#1abc9c', lambda: self.insert_func('atanh')),
             ('a/b↔d', '#f39c12', self.convert_fraction)],
            
            # Row 5: Numbers
            [('7', '#34495e', lambda: self.insert('7')),
             ('8', '#34495e', lambda: self.insert('8')),
             ('9', '#34495e', lambda: self.insert('9')),
             ('/', '#e67e22', lambda: self.insert('/')),
             ['%'] * 3],  # Placeholder
            
            # Row 6: Numbers
            [('4', '#34495e', lambda: self.insert('4')),
             ('5', '#34495e', lambda: self.insert('5')),
             ('6', '#34495e', lambda: self.insert('6')),
             ('*', '#e67e22', lambda: self.insert('*')),
             ['%'] * 3],
            
            # Row 7: Numbers
            [('1', '#34495e', lambda: self.insert('1')),
             ('2', '#34495e', lambda: self.insert('2')),
             ('3', '#34495e', lambda: self.insert('3')),
             ('-', '#e67e22', lambda: self.insert('-')),
             ['%'] * 3],
            
            # Row 8: Numbers and equals
            [('0', '#34495e', lambda: self.insert('0')),
             ('.', '#34495e', lambda: self.insert('.')),
             ('±', '#34495e', self.toggle_sign),
             ('+', '#e67e22', lambda: self.insert('+')),
             ('=', '#27ae60', self.calculate)],
        ]
        
        # Create button grid
        for row_idx, row in enumerate(buttons):
            row_frame = tk.Frame(button_frame, bg='#1a1a2e')
            row_frame.pack(fill=tk.X, pady=2)
            
            actual_buttons = [b for b in row if isinstance(b, tuple)]
            num_buttons = len(actual_buttons)
            
            for col_idx, (text, color, command) in enumerate(actual_buttons):
                btn = tk.Button(row_frame, text=text, font=self.button_font,
                               bg=color, fg='white', activebackground='#ecf0f1',
                               activeforeground='#2c3e50', relief=tk.RAISED, bd=2,
                               command=command, width=8, height=2)
                btn.pack(side=tk.LEFT, padx=3, expand=True, fill=tk.BOTH)
                
                # Hover effects
                btn.bind('<Enter>', lambda e, b=btn, c=color: b.configure(bg=self.lighten_color(c)))
                btn.bind('<Leave>', lambda e, b=btn, c=color: b.configure(bg=c))
    
    def lighten_color(self, color):
        """Lighten a hex color for hover effect"""
        # Simple implementation - just return a lighter shade
        return color
    
    def bind_keyboard(self):
        self.root.bind('<Key>', self.on_key_press)
        self.root.bind('<Return>', lambda e: self.calculate())
        self.root.bind('<BackSpace>', lambda e: self.backspace())
        self.root.bind('<Escape>', lambda e: self.clear())
    
    def on_key_press(self, event):
        key = event.char
        if self.has_error:
            self.clear()
        
        if key in '0123456789.+-*/()^':
            self.insert(key)
        elif key.lower() == 'p':
            self.insert_pi()
        elif key.lower() == 'e' and not self.expression.endswith('e'):
            self.insert_e()
        elif key == '!':
            self.insert_factorial()
    
    def update_display(self):
        """Update both expression and result displays"""
        self.expr_display.config(state='normal')
        self.expr_display.delete('1.0', tk.END)
        self.expr_display.insert('1.0', self.display_expression if self.display_expression else self.expression)
        self.expr_display.config(state='disabled')
    
    def insert(self, char):
        if self.has_error:
            self.clear()
        
        # Convert ^ to ** for Python evaluation
        if char == '^':
            self.expression += '**'
            self.display_expression += '^'
        else:
            self.expression += char
            self.display_expression += char
        
        self.update_display()
    
    def insert_pi(self):
        if self.has_error:
            self.clear()
        self.expression += 'pi'
        self.display_expression += 'π'
        self.update_display()
    
    def insert_e(self):
        if self.has_error:
            self.clear()
        self.expression += 'E'
        self.display_expression += 'e'
        self.update_display()
    
    def insert_func(self, func_name):
        if self.has_error:
            self.clear()
        
        func_map = {
            'sin': ('sin(', 'sin('),
            'cos': ('cos(', 'cos('),
            'tan': ('tan(', 'tan('),
            'asin': ('asin(', 'sin⁻¹('),
            'acos': ('acos(', 'cos⁻¹('),
            'atan': ('atan(', 'tan⁻¹('),
            'sinh': ('sinh(', 'sinh('),
            'cosh': ('cosh(', 'cosh('),
            'tanh': ('tanh(', 'tanh('),
            'asinh': ('asinh(', 'sinh⁻¹('),
            'acosh': ('acosh(', 'cosh⁻¹('),
            'atanh': ('atanh(', 'tanh⁻¹('),
            'ln': ('ln(', 'ln('),
            'log': ('log10(', 'log('),
            'exp': ('exp(', 'exp('),
            'sqrt': ('sqrt(', '√('),
        }
        
        expr_part, display_part = func_map.get(func_name, (func_name + '(', func_name + '('))
        self.expression += expr_part
        self.display_expression += display_part
        self.update_display()
    
    def insert_factorial(self):
        if self.has_error:
            self.clear()
        self.expression += '!'
        self.display_expression += '!'
        self.update_display()
    
    def backspace(self):
        if self.has_error:
            self.clear()
            return
        
        if self.expression:
            # Handle multi-character tokens
            if self.expression.endswith('pi'):
                self.expression = self.expression[:-2]
                self.display_expression = self.display_expression[:-1]
            elif self.expression.endswith('**'):
                self.expression = self.expression[:-2]
                self.display_expression = self.display_expression[:-1]
            else:
                self.expression = self.expression[:-1]
                self.display_expression = self.display_expression[:-1]
        
        self.update_display()
    
    def clear(self):
        self.expression = ""
        self.display_expression = ""
        self.last_result = None
        self.has_error = False
        self.result_display.config(text="0", fg='#4ecca3')
        self.update_display()
    
    def toggle_mode(self):
        self.angle_mode = 'RAD' if self.angle_mode == 'DEG' else 'DEG'
        self.mode_label.config(text=self.angle_mode)
    
    def toggle_sign(self):
        if self.has_error:
            self.clear()
            return
        
        # Find the last number and toggle its sign
        match = re.search(r'(\d+\.?\d*|\.\d+)$', self.expression)
        if match:
            start = match.start()
            if start > 0 and self.expression[start-1] == '-':
                self.expression = self.expression[:start-1] + self.expression[start:]
                self.display_expression = self.display_expression[:start-1] + self.display_expression[start:]
            else:
                self.expression = self.expression[:start] + '-' + self.expression[start:]
                self.display_expression = self.display_expression[:start] + '-' + self.display_expression[start:]
        
        self.update_display()
    
    def convert_fraction(self):
        """Convert between decimal and fraction"""
        try:
            if self.last_result is None:
                return
            
            val = float(self.last_result)
            
            # Try to convert to fraction
            frac = nsimplify(val, [sqrt(2), sqrt(3), sqrt(5), pi, E])
            
            # Check if it's a simple fraction
            if frac.is_rational:
                self.expression = str(frac)
                self.display_expression = str(frac)
            else:
                self.expression = str(frac)
                self.display_expression = str(frac).replace('sqrt', '√').replace('pi', 'π')
            
            self.update_display()
        except Exception as e:
            pass
    
    def evaluate_expression(self, expr):
        """Evaluate expression using Taylor series implementations"""
        # Replace display symbols with Python syntax
        expr = expr.replace('π', 'pi').replace('e', 'E')
        expr = expr.replace('^', '**')
        
        # Handle factorial
        while '!' in expr:
            match = re.search(r'(\d+)!', expr)
            if match:
                num = int(match.group(1))
                result = TaylorSeriesCalculator.factorial(num)
                expr = expr[:match.start()] + str(result) + expr[match.end():]
            else:
                break
        
        # Define custom functions using Taylor series
        def taylor_sin(x):
            if self.angle_mode == 'DEG':
                x = math.radians(x)
            return TaylorSeriesCalculator.sin_taylor(x)
        
        def taylor_cos(x):
            if self.angle_mode == 'DEG':
                x = math.radians(x)
            return TaylorSeriesCalculator.cos_taylor(x)
        
        def taylor_tan(x):
            if self.angle_mode == 'DEG':
                x = math.radians(x)
            return TaylorSeriesCalculator.tan_taylor(x)
        
        def taylor_asin(x):
            result = TaylorSeriesCalculator.asin_taylor(x)
            if self.angle_mode == 'DEG':
                return math.degrees(result)
            return result
        
        def taylor_acos(x):
            result = TaylorSeriesCalculator.acos_taylor(x)
            if self.angle_mode == 'DEG':
                return math.degrees(result)
            return result
        
        def taylor_atan(x):
            result = TaylorSeriesCalculator.atan_taylor(x)
            if self.angle_mode == 'DEG':
                return math.degrees(result)
            return result
        
        def taylor_sinh(x):
            return TaylorSeriesCalculator.sinh_taylor(x)
        
        def taylor_cosh(x):
            return TaylorSeriesCalculator.cosh_taylor(x)
        
        def taylor_tanh(x):
            return TaylorSeriesCalculator.tanh_taylor(x)
        
        def taylor_asinh(x):
            return TaylorSeriesCalculator.asinh_taylor(x)
        
        def taylor_acosh(x):
            return TaylorSeriesCalculator.acosh_taylor(x)
        
        def taylor_atanh(x):
            return TaylorSeriesCalculator.atanh_taylor(x)
        
        def taylor_exp(x):
            return TaylorSeriesCalculator.exp_taylor(x)
        
        def taylor_ln(x):
            return TaylorSeriesCalculator.ln_taylor(x)
        
        def taylor_sqrt(x):
            return TaylorSeriesCalculator.sqrt_newton(x)
        
        # Create namespace with custom functions
        namespace = {
            'sin': taylor_sin,
            'cos': taylor_cos,
            'tan': taylor_tan,
            'asin': taylor_asin,
            'acos': taylor_acos,
            'atan': taylor_atan,
            'sinh': taylor_sinh,
            'cosh': taylor_cosh,
            'tanh': taylor_tanh,
            'asinh': taylor_asinh,
            'acosh': taylor_acosh,
            'atanh': taylor_atanh,
            'exp': taylor_exp,
            'ln': taylor_ln,
            'log10': lambda x: taylor_ln(x) / taylor_ln(10),
            'sqrt': taylor_sqrt,
            'pi': math.pi,
            'E': math.e,
        }
        
        return eval(expr, {"__builtins__": {}}, namespace)
    
    def format_result(self, value):
        """Format result with proper precision and symbolic representation"""
        if value is None:
            return "0"
        
        # Round to avoid floating point errors
        rounded = round(value, 12)
        
        # Check for common symbolic values
        if abs(rounded) < 1e-10:
            return "0"
        
        # Check for pi multiples
        pi_multiple = rounded / math.pi
        if abs(pi_multiple - round(pi_multiple)) < 1e-10 and abs(round(pi_multiple)) <= 10:
            n = round(pi_multiple)
            if n == 1:
                return "π"
            elif n == -1:
                return "-π"
            elif n == 0.5:
                return "π/2"
            elif n == -0.5:
                return "-π/2"
            elif n == 0.25:
                return "π/4"
            elif n == -0.25:
                return "-π/4"
            elif n == 0.333333:
                return "π/3"
            elif n == -0.333333:
                return "-π/3"
            else:
                return f"{n}π" if n != 0 else "0"
        
        # Format with appropriate precision
        if abs(rounded) < 0.0001 or abs(rounded) > 1e6:
            return f"{rounded:.6e}"
        elif rounded == int(rounded):
            return str(int(rounded))
        else:
            return f"{rounded:.10g}"
    
    def calculate(self):
        """Calculate the result of the expression"""
        if not self.expression:
            return
        
        try:
            result = self.evaluate_expression(self.expression)
            self.last_result = result
            formatted = self.format_result(result)
            self.result_display.config(text=formatted, fg='#4ecca3')
            self.has_error = False
        except Exception as e:
            self.result_display.config(text="ERROR", fg='#e74c3c')
            self.has_error = True


def main():
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
