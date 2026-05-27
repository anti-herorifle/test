import tkinter as tk
from tkinter import ttk, messagebox
import math
import re
from fractions import Fraction

class TaylorMath:
    """
    Custom mathematical engine using Taylor Series approximations.
    Includes range reduction for better convergence and accuracy.
    """
    
    PI = 3.141592653589793238462643383279502884197
    E = 2.718281828459045235360287471352662497757

    @staticmethod
    def factorial(n):
        if n == 0 or n == 1:
            return 1
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

    @staticmethod
    def normalize_angle_rad(x):
        """Reduce angle to [-PI, PI] for better convergence."""
        two_pi = 2 * TaylorMath.PI
        x = x % two_pi
        if x > TaylorMath.PI:
            x -= two_pi
        elif x < -TaylorMath.PI:
            x += two_pi
        return x

    @staticmethod
    def sin_taylor(x, terms=20):
        """Calculate sin(x) using Taylor Series: x - x^3/3! + x^5/5! - ..."""
        x = TaylorMath.normalize_angle_rad(x)
        result = 0.0
        for n in range(terms):
            sign = (-1) ** n
            power = 2 * n + 1
            term = (sign * (x ** power)) / TaylorMath.factorial(power)
            result += term
        return result

    @staticmethod
    def cos_taylor(x, terms=20):
        """Calculate cos(x) using Taylor Series: 1 - x^2/2! + x^4/4! - ..."""
        x = TaylorMath.normalize_angle_rad(x)
        result = 0.0
        for n in range(terms):
            sign = (-1) ** n
            power = 2 * n
            term = (sign * (x ** power)) / TaylorMath.factorial(power)
            result += term
        return result

    @staticmethod
    def exp_taylor(x, terms=30):
        """Calculate e^x using Taylor Series: 1 + x + x^2/2! + ..."""
        # Range reduction: e^x = (e^(x/k))^k to keep x small
        k = 1
        while abs(x) > 1:
            x /= 2
            k *= 2
        
        result = 1.0
        term = 1.0
        for n in range(1, terms):
            term *= x / n
            result += term
            if abs(term) < 1e-15:
                break
        
        return result ** k

    @staticmethod
    def atan_taylor(x, terms=100):
        """Calculate atan(x) using Taylor Series: x - x^3/3 + x^5/5 - ..."""
        # Convergence only for |x| <= 1. Use identity for |x| > 1
        if abs(x) > 1:
            return (TaylorMath.PI / 2 * (1 if x > 0 else -1)) - TaylorMath.atan_taylor(1/x, terms)
        
        result = 0.0
        x_sq = x * x
        for n in range(terms):
            sign = (-1) ** n
            power = 2 * n + 1
            term = (sign * (x ** power)) / power
            result += term
            if abs(term) < 1e-15:
                break
        return result

    @staticmethod
    def tan_taylor(x, terms=20):
        s = TaylorMath.sin_taylor(x, terms)
        c = TaylorMath.cos_taylor(x, terms)
        if abs(c) < 1e-10:
            raise ValueError("Undefined")
        return s / c

    @staticmethod
    def sinh_taylor(x, terms=30):
        """sinh(x) = (e^x - e^-x) / 2"""
        return (TaylorMath.exp_taylor(x, terms) - TaylorMath.exp_taylor(-x, terms)) / 2

    @staticmethod
    def cosh_taylor(x, terms=30):
        """cosh(x) = (e^x + e^-x) / 2"""
        return (TaylorMath.exp_taylor(x, terms) + TaylorMath.exp_taylor(-x, terms)) / 2

    @staticmethod
    def tanh_taylor(x, terms=30):
        s = TaylorMath.sinh_taylor(x, terms)
        c = TaylorMath.cosh_taylor(x, terms)
        return s / c

    @staticmethod
    def ln_taylor(x, terms=100):
        """Calculate ln(x) using series for ln((1+y)/(1-y)) where y = (x-1)/(x+1)"""
        if x <= 0:
            raise ValueError("Logarithm undefined for non-positive values")
        
        # Reduce range: ln(x * 2^n) = ln(x) + n*ln(2)
        n = 0
        while x > 2:
            x /= 2
            n += 1
        while x < 0.5:
            x *= 2
            n -= 1
            
        y = (x - 1) / (x + 1)
        y_sq = y * y
        result = 0.0
        for k in range(terms):
            term = (y ** (2 * k + 1)) / (2 * k + 1)
            result += term
            if abs(term) < 1e-15:
                break
        
        ln2 = 0.6931471805599453
        return 2 * result + n * ln2

    @staticmethod
    def asin_taylor(x, terms=50):
        """asin(x) using integral of 1/sqrt(1-t^2) series or atan identity"""
        if abs(x) > 1:
            raise ValueError("Domain error")
        if abs(x) == 1:
            return TaylorMath.PI / 2 * (1 if x > 0 else -1)
        # asin(x) = atan(x / sqrt(1-x^2))
        try:
            val = x / math.sqrt(1 - x*x)
            return TaylorMath.atan_taylor(val, terms)
        except:
            return TaylorMath.PI / 2 * (1 if x > 0 else -1)

    @staticmethod
    def acos_taylor(x, terms=50):
        """acos(x) = PI/2 - asin(x)"""
        return TaylorMath.PI / 2 - TaylorMath.asin_taylor(x, terms)

    @staticmethod
    def atan_taylor_wrapper(x, terms=50):
        return TaylorMath.atan_taylor(x, terms)

    @staticmethod
    def asinh_taylor(x, terms=30):
        """asinh(x) = ln(x + sqrt(x^2 + 1))"""
        return TaylorMath.ln_taylor(x + math.sqrt(x*x + 1), terms)

    @staticmethod
    def acosh_taylor(x, terms=30):
        """acosh(x) = ln(x + sqrt(x^2 - 1))"""
        if x < 1:
            raise ValueError("Domain error")
        return TaylorMath.ln_taylor(x + math.sqrt(x*x - 1), terms)

    @staticmethod
    def atanh_taylor(x, terms=50):
        """atanh(x) = 0.5 * ln((1+x)/(1-x))"""
        if abs(x) >= 1:
            raise ValueError("Domain error")
        return 0.5 * TaylorMath.ln_taylor((1+x)/(1-x), terms)

    @staticmethod
    def sqrt_newton(x, iterations=20):
        if x < 0:
            raise ValueError("Square root of negative number")
        if x == 0:
            return 0
        guess = x / 2.0
        for _ in range(iterations):
            guess = (guess + x / guess) / 2
        return guess


class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Scientific Calculator (Taylor Series)")
        self.root.geometry("500x650")
        self.root.configure(bg="#2b2b2b")
        
        self.math_engine = TaylorMath()
        self.is_degree = True
        self.current_expression = ""
        self.last_result = None
        self.has_error = False

        # Display Frame
        self.display_frame = tk.Frame(root, bg="#1e1e1e", pady=20)
        self.display_frame.pack(fill=tk.X, padx=10, pady=10)

        self.expression_label = tk.Label(
            self.display_frame, text="", font=("Consolas", 12), 
            fg="#aaaaaa", bg="#1e1e1e", anchor="e"
        )
        self.expression_label.pack(fill=tk.X, padx=10)

        self.result_label = tk.Label(
            self.display_frame, text="0", font=("Consolas", 28, "bold"), 
            fg="#ffffff", bg="#1e1e1e", anchor="e"
        )
        self.result_label.pack(fill=tk.X, padx=10)

        # Buttons Frame
        self.buttons_frame = tk.Frame(root, bg="#2b2b2b")
        self.buttons_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.create_buttons()

        # Keyboard Binding
        self.root.bind("<Key>", self.on_key_press)

    def create_buttons(self):
        button_config = [
            # Row 0
            ("deg/rad", self.toggle_mode, "#4a4a4a", "#ffffff"),
            ("(", lambda: self.append_char("("), "#4a4a4a", "#ffffff"),
            (")", lambda: self.append_char(")"), "#4a4a4a", "#ffffff"),
            ("C", self.clear_all, "#d32f2f", "#ffffff"),
            ("⌫", self.backspace, "#d32f2f", "#ffffff"),
            ("÷", lambda: self.append_char("/"), "#ff9800", "#ffffff"),
            
            # Row 1
            ("sin", lambda: self.append_func("sin"), "#6a1b9a", "#ffffff"),
            ("cos", lambda: self.append_func("cos"), "#6a1b9a", "#ffffff"),
            ("tan", lambda: self.append_func("tan"), "#6a1b9a", "#ffffff"),
            ("7", lambda: self.append_char("7"), "#333333", "#ffffff"),
            ("8", lambda: self.append_char("8"), "#333333", "#ffffff"),
            ("9", lambda: self.append_char("9"), "#333333", "#ffffff"),
            ("×", lambda: self.append_char("*"), "#ff9800", "#ffffff"),

            # Row 2
            ("asin", lambda: self.append_func("asin"), "#6a1b9a", "#ffffff"),
            ("acos", lambda: self.append_func("acos"), "#6a1b9a", "#ffffff"),
            ("atan", lambda: self.append_func("atan"), "#6a1b9a", "#ffffff"),
            ("4", lambda: self.append_char("4"), "#333333", "#ffffff"),
            ("5", lambda: self.append_char("5"), "#333333", "#ffffff"),
            ("6", lambda: self.append_char("6"), "#333333", "#ffffff"),
            ("-", lambda: self.append_char("-"), "#ff9800", "#ffffff"),

            # Row 3
            ("sinh", lambda: self.append_func("sinh"), "#4a148c", "#ffffff"),
            ("cosh", lambda: self.append_func("cosh"), "#4a148c", "#ffffff"),
            ("tanh", lambda: self.append_func("tanh"), "#4a148c", "#ffffff"),
            ("1", lambda: self.append_char("1"), "#333333", "#ffffff"),
            ("2", lambda: self.append_char("2"), "#333333", "#ffffff"),
            ("3", lambda: self.append_char("3"), "#333333", "#ffffff"),
            ("+", lambda: self.append_char("+"), "#ff9800", "#ffffff"),

            # Row 4
            ("asinh", lambda: self.append_func("asinh"), "#4a148c", "#ffffff"),
            ("acosh", lambda: self.append_func("acosh"), "#4a148c", "#ffffff"),
            ("atanh", lambda: self.append_func("atanh"), "#4a148c", "#ffffff"),
            ("π", lambda: self.append_char("pi"), "#00897b", "#ffffff"),
            ("e", lambda: self.append_char("e"), "#00897b", "#ffffff"),
            ("0", lambda: self.append_char("0"), "#333333", "#ffffff"),
            (".", lambda: self.append_char("."), "#333333", "#ffffff"),
            
            # Row 5
            ("x^y", lambda: self.append_char("**"), "#6a1b9a", "#ffffff"),
            ("√", lambda: self.append_func("sqrt"), "#6a1b9a", "#ffffff"),
            ("log", lambda: self.append_func("log"), "#6a1b9a", "#ffffff"),
            ("ln", lambda: self.append_func("ln"), "#6a1b9a", "#ffffff"),
            ("a/b↔d", self.toggle_fraction, "#00897b", "#ffffff"),
            ("=", self.calculate, "#4caf50", "#ffffff"),
        ]

        row = 0
        col = 0
        # Grid configuration
        for i in range(7):
            self.buttons_frame.grid_columnconfigure(i, weight=1)
        for i in range(6):
            self.buttons_frame.grid_rowconfigure(i, weight=1)

        for text, command, bg, fg in button_config:
            btn = tk.Button(
                self.buttons_frame, text=text, command=command,
                bg=bg, fg=fg, font=("Consolas", 11, "bold"),
                relief=tk.FLAT, activebackground="#555555", activeforeground="#ffffff",
                height=2, width=5
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
            col += 1
            if col > 6:
                col = 0
                row += 1

    def toggle_mode(self):
        self.is_degree = not self.is_degree
        mode_str = "DEG" if self.is_degree else "RAD"
        self.expression_label.config(text=f"Mode: {mode_str}")
        if not self.current_expression:
            self.result_label.config(text=mode_str)

    def append_char(self, char):
        if self.has_error:
            self.clear_all()
        self.current_expression += str(char)
        self.update_display()

    def append_func(self, func_name):
        if self.has_error:
            self.clear_all()
        self.current_expression += f"{func_name}("
        self.update_display()

    def backspace(self):
        if self.has_error:
            self.clear_all()
            return
        self.current_expression = self.current_expression[:-1]
        self.update_display()

    def clear_all(self):
        self.current_expression = ""
        self.last_result = None
        self.has_error = False
        self.expression_label.config(text="")
        self.result_label.config(text="0")

    def update_display(self):
        self.result_label.config(text=self.current_expression if self.current_expression else "0")

    def evaluate_expression(self, expr):
        # Replace visual symbols with python operators
        expr = expr.replace("×", "*").replace("÷", "/").replace("π", "math.pi")
        
        # Define available functions using our Taylor Engine
        # We wrap them to handle degree conversion automatically
        def safe_sin(x):
            rad = x if not self.is_degree else math.radians(x)
            return self.math_engine.sin_taylor(rad)
        
        def safe_cos(x):
            rad = x if not self.is_degree else math.radians(x)
            return self.math_engine.cos_taylor(rad)
        
        def safe_tan(x):
            rad = x if not self.is_degree else math.radians(x)
            return self.math_engine.tan_taylor(rad)
        
        def safe_asin(x):
            res = self.math_engine.asin_taylor(x)
            return math.degrees(res) if self.is_degree else res
        
        def safe_acos(x):
            res = self.math_engine.acos_taylor(x)
            return math.degrees(res) if self.is_degree else res
        
        def safe_atan(x):
            res = self.math_engine.atan_taylor_wrapper(x)
            return math.degrees(res) if self.is_degree else res

        def safe_sinh(x): return self.math_engine.sinh_taylor(x)
        def safe_cosh(x): return self.math_engine.cosh_taylor(x)
        def safe_tanh(x): return self.math_engine.tanh_taylor(x)
        
        def safe_asinh(x): return self.math_engine.asinh_taylor(x)
        def safe_acosh(x): return self.math_engine.acosh_taylor(x)
        def safe_atanh(x): return self.math_engine.atanh_taylor(x)

        def safe_sqrt(x): return self.math_engine.sqrt_newton(x)
        def safe_log(x): return self.math_engine.ln_taylor(x) / self.math_engine.ln_taylor(10) # log10
        def safe_ln(x): return self.math_engine.ln_taylor(x)
        def safe_exp(x): return self.math_engine.exp_taylor(x)

        # Create local scope for eval
        local_scope = {
            "sin": safe_sin, "cos": safe_cos, "tan": safe_tan,
            "asin": safe_asin, "acos": safe_acos, "atan": safe_atan,
            "sinh": safe_sinh, "cosh": safe_cosh, "tanh": safe_tanh,
            "asinh": safe_asinh, "acosh": safe_acosh, "atanh": safe_atanh,
            "sqrt": safe_sqrt, "log": safe_log, "ln": safe_ln, "exp": safe_exp,
            "pi": self.math_engine.PI, "e": self.math_engine.E,
            "abs": abs
        }
        
        try:
            result = eval(expr, {"__builtins__": {}}, local_scope)
            return result
        except Exception as ex:
            raise ValueError(str(ex))

    def format_result(self, value):
        if isinstance(value, complex):
            return "Complex Result"
        
        # Round to avoid floating point artifacts
        rounded = round(value, 10)
        if abs(rounded) < 1e-10:
            return "0"
            
        # Check for Pi multiples
        if self.is_degree:
             return str(rounded)
        
        pi_ratio = rounded / self.math_engine.PI
        close_int = round(pi_ratio)
        if abs(pi_ratio - close_int) < 1e-9:
            if close_int == 1: return "π"
            if close_int == -1: return "-π"
            return f"{close_int}π"
        
        # Check for simple fractions of Pi
        for denom in [2, 3, 4, 6]:
            ratio = pi_ratio * denom
            close_int = round(ratio)
            if abs(ratio - close_int) < 1e-9:
                return f"{close_int}π/{denom}"

        return str(rounded)

    def calculate(self):
        if not self.current_expression:
            return
        
        try:
            raw_result = self.evaluate_expression(self.current_expression)
            self.last_result = raw_result
            
            formatted = self.format_result(raw_result)
            self.expression_label.config(text=self.current_expression + " =")
            self.result_label.config(text=formatted)
            self.current_expression = str(raw_result) # Continue calculation with result
            self.has_error = False
        except Exception as e:
            self.result_label.config(text="ERROR")
            self.expression_label.config(text=str(e))
            self.has_error = True
            self.current_expression = ""

    def toggle_fraction(self):
        if self.last_result is None and not self.current_expression:
            return
        
        try:
            val = float(self.last_result) if self.last_result is not None else float(eval(self.current_expression))
            fraction = Fraction(val).limit_denominator(10000)
            
            if fraction.denominator == 1:
                res_str = str(fraction.numerator)
            else:
                res_str = f"{fraction.numerator}/{fraction.denominator}"
            
            self.expression_label.config(text=f"{val} →")
            self.result_label.config(text=res_str)
            self.current_expression = str(val) # Keep decimal for further calc
        except:
            pass

    def on_key_press(self, event):
        if self.has_error:
            self.clear_all()
            
        key = event.char
        if key.isdigit() or key in "+-*/().^":
            self.append_char(key)
        elif key.lower() == 'p':
            self.append_char("pi")
        elif key.lower() == 'e':
            self.append_char("e")
        elif event.keysym == 'Return':
            self.calculate()
        elif event.keysym == 'Escape':
            self.clear_all()
        elif event.keysym == 'BackSpace':
            self.backspace()

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()
