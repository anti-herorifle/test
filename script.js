let display = document.getElementById('display');
let secondaryDisplay = document.getElementById('secondary-display');
let currentExpression = '';
let isDegreeMode = true;
let lastResult = null;

function appendNumber(num) {
    currentExpression += num;
    updateDisplay();
}

function appendOperator(operator) {
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
    if (func === 'sqrt') {
        currentExpression += 'sqrt(';
    } else if (['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'log', 'ln'].includes(func)) {
        currentExpression += func + '(';
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
    secondaryDisplay.textContent = '';
    updateDisplay();
}

function deleteLast() {
    // Handle function names when deleting
    const functions = ['sqrt', 'asin', 'acos', 'atan', 'sin', 'cos', 'tan', 'log'];
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

        // Replace ^ with ** for exponentiation
        expr = expr.replace(/\^/g, '**');

        // Replace sqrt with Math.sqrt
        expr = expr.replace(/sqrt\(/g, 'Math.sqrt(');

        // Replace log with Math.log10 and ln with Math.log
        expr = expr.replace(/log\(/g, 'Math.log10(');
        expr = expr.replace(/ln\(/g, 'Math.log(');

        // Handle trigonometric functions based on mode
        if (isDegreeMode) {
            // For degree mode, wrap the argument in toRadians
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
        } else {
            // Use a more robust rounding approach to handle floating point imprecision
            // Round to 10 significant digits for display
            const roundedResult = roundToSignificantDigits(result, 10);
            secondaryDisplay.textContent = currentExpression + ' =';
            currentExpression = roundedResult.toString();
            lastResult = roundedResult;
        }
    } catch (error) {
        currentExpression = 'Error';
        secondaryDisplay.textContent = '';
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
    }
});
