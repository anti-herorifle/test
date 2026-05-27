let display = document.getElementById('display');
let secondaryDisplay = document.getElementById('secondary-display');
let currentExpression = '';
let isDegreeMode = true;
let lastResult = null;
let isError = false;

// Constants with high precision
const PI = Math.PI;
const E = Math.E;

// Helper function to check if a number is close to a rational multiple of pi
function findPiFraction(num) {
    if (Math.abs(num) < 1e-10) return { num: 0, den: 1 };
    
    const tolerance = 1e-9;
    const dividedByPi = num / PI;
    
    // Try to find a simple fraction for num/pi
    for (let den = 1; den <= 100; den++) {
        for (let numMult = -100; numMult <= 100; numMult++) {
            const candidate = numMult * PI / den;
            if (Math.abs(num - candidate) < tolerance) {
                return { num: numMult, den: den };
            }
        }
    }
    return null;
}

// Format result in terms of pi if possible
function formatWithPi(num) {
    if (Math.abs(num) < 1e-10) return '0';
    
    const piFraction = findPiFraction(num);
    if (piFraction && piFraction.num !== 0) {
        if (piFraction.den === 1) {
            if (piFraction.num === 1) return 'π';
            if (piFraction.num === -1) return '-π';
            return piFraction.num + 'π';
        } else {
            if (piFraction.num === 1) return 'π/' + piFraction.den;
            if (piFraction.num === -1) return '-π/' + piFraction.den;
            return piFraction.num + 'π/' + piFraction.den;
        }
    }
    return null;
}

// Simplify square roots and return as surd form if possible
function simplifySurd(num) {
    if (num < 0) return null;
    if (num === 0) return { coeff: 0, radicand: 1 };
    
    // Check for perfect squares up to 10000
    const sqrtNum = Math.sqrt(num);
    if (Math.abs(sqrtNum - Math.round(sqrtNum)) < 1e-10) {
        return { coeff: Math.round(sqrtNum), radicand: 1 };
    }
    
    // Try to factor out perfect squares
    let n = Math.floor(num);
    let coeff = 1;
    
    for (let i = 2; i * i <= n; i++) {
        while (n % (i * i) === 0) {
            coeff *= i;
            n /= (i * i);
        }
    }
    
    // Check if original was close to integer
    if (Math.abs(num - Math.round(num)) < 1e-10) {
        return { coeff: coeff, radicand: n };
    }
    
    return null;
}

// Format surd result
function formatSurd(coeff, radicand) {
    if (radicand === 1) return coeff.toString();
    if (coeff === 1) return '√' + radicand;
    if (coeff === -1) return '-√' + radicand;
    return coeff + '√' + radicand;
}

function appendNumber(num) {
    if (isError) {
        clearDisplay();
    }
    currentExpression += num;
    updateDisplay();
}

function appendOperator(operator) {
    if (isError) {
        clearDisplay();
    }
    const lastChar = currentExpression.slice(-1);
    if (currentExpression === '' && operator !== '-') {
        if (operator === '-') currentExpression = '0';
        else return;
    }
    if (['+', '-', '*', '/', '^'].includes(lastChar)) {
        currentExpression = currentExpression.slice(0, -1) + operator;
    } else {
        currentExpression += operator;
    }
    updateDisplay();
}

function appendFunction(func) {
    if (isError) {
        clearDisplay();
    }
    if (func === 'sqrt') {
        currentExpression += 'sqrt(';
    } else if (['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh', 'asinh', 'acosh', 'atanh', 'log', 'ln'].includes(func)) {
        currentExpression += func + '(';
    } else if (func === 'pi') {
        currentExpression += 'π';
    } else if (func === 'e') {
        currentExpression += 'e';
    }
    updateDisplay();
}

function toggleMode() {
    isDegreeMode = !isDegreeMode;
    const modeBtn = document.querySelector('button[onclick="toggleMode()"]');
    modeBtn.textContent = isDegreeMode ? 'DEG' : 'RAD';
    modeBtn.classList.toggle('mode-active', !isDegreeMode);
}

function clearDisplay() {
    currentExpression = '';
    lastResult = null;
    isError = false;
    secondaryDisplay.textContent = '';
    updateDisplay();
}

function deleteLast() {
    if (isError) {
        clearDisplay();
        return;
    }
    // Handle function names when deleting
    const functions = ['sqrt', 'asin', 'acos', 'atan', 'asinh', 'acosh', 'atanh', 'sinh', 'cosh', 'tanh', 'sin', 'cos', 'tan', 'log'];
    for (let func of functions) {
        if (currentExpression.endsWith(func + '(')) {
            currentExpression = currentExpression.slice(0, -(func.length + 1));
            updateDisplay();
            return;
        }
    }
    currentExpression = currentExpression.slice(0, -1);
    updateDisplay();
}

function toRadians(angle) {
    return isDegreeMode ? angle * Math.PI / 180 : angle;
}

function toDegrees(radians) {
    return isDegreeMode ? radians * 180 / Math.PI : radians;
}

// Helper function to round to significant digits to fix floating point imprecision
function roundToSignificantDigits(num, digits) {
    if (num === 0) return 0;
    if (!isFinite(num)) return num;
    const factor = Math.pow(10, digits - 1 - Math.floor(Math.log10(Math.abs(num))));
    return Math.round(num * factor) / factor;
}

function calculate() {
    try {
        if (currentExpression === '') return;

        let expr = currentExpression;
        
        // Store original expression for display
        const originalExpr = currentExpression;

        // Replace π with Math.PI and e with Math.E (but not in function names)
        expr = expr.replace(/π/g, 'Math.PI');
        // Replace standalone 'e' with Math.E (careful not to replace in numbers like 2.5e10)
        expr = expr.replace(/(?<![0-9])e(?![0-9])/g, 'Math.E');

        // Replace ^ with ** for exponentiation
        expr = expr.replace(/\^/g, '**');

        // Replace sqrt with Math.sqrt
        expr = expr.replace(/sqrt\(/g, 'Math.sqrt(');

        // Replace log with Math.log10 and ln with Math.log
        expr = expr.replace(/log\(/g, 'Math.log10(');
        expr = expr.replace(/ln\(/g, 'Math.log(');

        // Handle hyperbolic functions
        expr = expr.replace(/sinh\(/g, 'Math.sinh(');
        expr = expr.replace(/cosh\(/g, 'Math.cosh(');
        expr = expr.replace(/tanh\(/g, 'Math.tanh(');
        expr = expr.replace(/asinh\(/g, 'Math.asinh(');
        expr = expr.replace(/acosh\(/g, 'Math.acosh(');
        expr = expr.replace(/atanh\(/g, 'Math.atanh(');

        // Handle trigonometric functions based on mode
        // For degree mode, we need to properly wrap arguments
        if (isDegreeMode) {
            // For regular trig functions, wrap argument in toRadians
            expr = expr.replace(/sin\(/g, 'Math.sin(toRadians(');
            expr = expr.replace(/cos\(/g, 'Math.cos(toRadians(');
            expr = expr.replace(/tan\(/g, 'Math.tan(toRadians(');
            // For inverse functions, apply toDegrees to the result
            expr = expr.replace(/asin\(/g, 'toDegrees(Math.asin(');
            expr = expr.replace(/acos\(/g, 'toDegrees(Math.acos(');
            expr = expr.replace(/atan\(/g, 'toDegrees(Math.atan(');
        } else {
            // For radian mode, use direct Math functions
            expr = expr.replace(/sin\(/g, 'Math.sin(');
            expr = expr.replace(/cos\(/g, 'Math.cos(');
            expr = expr.replace(/tan\(/g, 'Math.tan(');
            expr = expr.replace(/asin\(/g, 'Math.asin(');
            expr = expr.replace(/acos\(/g, 'Math.acos(');
            expr = expr.replace(/atan\(/g, 'Math.atan(');
        }

        // Count parentheses and add closing ones if needed
        const openParens = (expr.match(/\(/g) || []).length;
        const closeParens = (expr.match(/\)/g) || []).length;
        if (openParens > closeParens) {
            expr += ')'.repeat(openParens - closeParens);
        }

        // Evaluate the expression safely
        const result = Function('toRadians', 'toDegrees', '"use strict";return (' + expr + ')')(toRadians, toDegrees);

        // Check for division by zero or invalid results
        if (!isFinite(result) || isNaN(result)) {
            currentExpression = 'Error';
            secondaryDisplay.textContent = '';
            isError = true;
        } else {
            // Try to format result in terms of pi for trig results
            let formattedResult = null;
            
            // Check if result can be expressed in terms of pi
            const piFormatted = formatWithPi(result);
            if (piFormatted) {
                formattedResult = piFormatted;
            }
            
            // Check if result is a square root (surd form)
            if (!formattedResult && Number.isInteger(Math.round(result * 1e10) / 1e10)) {
                const roundedResult = Math.round(result * 1e10) / 1e10;
                const surdFormatted = simplifySurd(roundedResult * roundedResult);
                if (surdFormatted && surdFormatted.radicand !== 1) {
                    // Only show surd if it's a clean simplification
                    const checkValue = surdFormatted.coeff * Math.sqrt(surdFormatted.radicand);
                    if (Math.abs(checkValue - Math.abs(result)) < 1e-9) {
                        formattedResult = formatSurd(surdFormatted.coeff, surdFormatted.radicand);
                    }
                }
            }
            
            // Use significant digits rounding for display
            const roundedResult = roundToSignificantDigits(result, 12);
            
            secondaryDisplay.textContent = originalExpr + ' =';
            
            // Show exact form if available, otherwise show decimal
            if (formattedResult) {
                currentExpression = formattedResult + ' (' + roundedResult.toString() + ')';
            } else {
                currentExpression = roundedResult.toString();
            }
            lastResult = roundedResult;
            isError = false;
        }
    } catch (error) {
        currentExpression = 'Error';
        secondaryDisplay.textContent = '';
        isError = true;
    }
    updateDisplay();
}

// Fraction conversion functions
function gcd(a, b) {
    a = Math.abs(a);
    b = Math.abs(b);
    while (b !== 0) {
        let t = b;
        b = a % b;
        a = t;
    }
    return a;
}

function decimalToFraction(decimal) {
    if (!isFinite(decimal)) return null;

    const tolerance = 1.0e-7;
    let h1 = 1, h2 = 0, k1 = 0, k2 = 1;
    let b = decimal;

    do {
        let a = Math.floor(b);
        let aux = h1;
        h1 = a * h1 + h2;
        h2 = aux;

        aux = k1;
        k1 = a * k1 + k2;
        k2 = aux;

        b = 1 / (b - a);
    } while (Math.abs(decimal - h1 / k1) > decimal * tolerance);

    return { numerator: h1, denominator: k1 };
}

function fractionToDecimal(numerator, denominator) {
    if (denominator === 0) return 'Error';
    return numerator / denominator;
}

function convertFraction() {
    try {
        if (currentExpression === '' || currentExpression === 'Error') return;

        const value = parseFloat(currentExpression);

        if (isNaN(value)) {
            // Try to parse as fraction (e.g., "1/2")
            const parts = currentExpression.split('/');
            if (parts.length === 2) {
                const num = parseFloat(parts[0]);
                const den = parseFloat(parts[1]);
                if (!isNaN(num) && !isNaN(den) && den !== 0) {
                    const result = fractionToDecimal(num, den);
                    secondaryDisplay.textContent = currentExpression + ' =';
                    currentExpression = result.toString();
                    updateDisplay();
                    return;
                }
            }
            return;
        }

        // Convert decimal to fraction
        const fraction = decimalToFraction(value);
        if (fraction) {
            // Simplify the fraction
            const commonDivisor = gcd(fraction.numerator, fraction.denominator);
            const simplifiedNum = fraction.numerator / commonDivisor;
            const simplifiedDen = fraction.denominator / commonDivisor;

            secondaryDisplay.textContent = value + ' ≈';
            currentExpression = `${simplifiedNum}/${simplifiedDen}`;
            updateDisplay();
        }
    } catch (error) {
        // Silently fail on conversion errors
    }
}

function updateDisplay() {
    // Replace * with × and other symbols for better visual display
    let displayValue = currentExpression
        .replace(/\*\*/g, '^')
        .replace(/\*/g, '×')
        .replace(/sqrt\(/g, '√(');
    display.value = displayValue;
}

// Add keyboard support
document.addEventListener('keydown', function(event) {
    const key = event.key;

    // Clear error state on any keyboard input
    if (isError) {
        clearDisplay();
    }

    if (/[0-9]/.test(key)) {
        appendNumber(key);
    } else if (key === '+') {
        appendOperator('+');
    } else if (key === '-') {
        appendOperator('-');
    } else if (key === '*') {
        appendOperator('*');
    } else if (key === '/') {
        appendOperator('/');
    } else if (key === '^') {
        appendOperator('^');
    } else if (key === '.') {
        appendNumber('.');
    } else if (key === '(' || key === ')') {
        appendNumber(key);
    } else if (key === 'Enter' || key === '=') {
        event.preventDefault();
        calculate();
    } else if (key === 'Backspace') {
        deleteLast();
    } else if (key === 'Escape' || key === 'c' || key === 'C') {
        clearDisplay();
    } else if (key.toLowerCase() === 'p') {
        appendFunction('pi');
    } else if (key.toLowerCase() === 'e' && !event.ctrlKey && !event.metaKey && !event.altKey) {
        // Only add e constant if not part of a modifier key combo
        appendFunction('e');
    }
});
