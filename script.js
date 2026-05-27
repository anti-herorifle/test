// Calculator with advanced functions

let currentInput = '';
let previousInput = '';
let operator = null;
let shouldResetDisplay = false;
let isDegreeMode = true; // Default to degrees
let isError = false;

const display = document.getElementById('display');
const expressionDisplay = document.getElementById('expression-display');
const modeButton = document.getElementById('mode-btn');

// Update display
function updateDisplay() {
    if (isError) {
        display.value = 'ERROR';
    } else {
        display.value = currentInput || '0';
    }
    expressionDisplay.textContent = previousInput + (operator || '');
}

// Format number to avoid floating point errors
function formatNumber(num) {
    if (!isFinite(num)) return 'ERROR';
    
    // Handle very small numbers that should be zero
    if (Math.abs(num) < 1e-12) return '0';
    
    // Round to 12 significant digits
    const rounded = parseFloat(num.toPrecision(12));
    
    // Check if it's a nice fraction of pi
    if (Math.abs(num) > 1e-10) {
        const piMultiple = num / Math.PI;
        const roundedPiMultiple = parseFloat(piMultiple.toPrecision(12));
        
        // Common pi fractions
        const fractions = [
            { val: 0, text: '0' },
            { val: 1/6, text: '\u03C0/6' },
            { val: 1/4, text: '\u03C0/4' },
            { val: 1/3, text: '\u03C0/3' },
            { val: 1/2, text: '\u03C0/2' },
            { val: 2/3, text: '2\u03C0/3' },
            { val: 3/4, text: '3\u03C0/4' },
            { val: 5/6, text: '5\u03C0/6' },
            { val: 1, text: '\u03C0' },
            { val: 7/6, text: '7\u03C0/6' },
            { val: 5/4, text: '5\u03C0/4' },
            { val: 4/3, text: '4\u03C0/3' },
            { val: 3/2, text: '3\u03C0/2' },
            { val: 5/3, text: '5\u03C0/3' },
            { val: 7/4, text: '7\u03C0/4' },
            { val: 11/6, text: '11\u03C0/6' },
            { val: 2, text: '2\u03C0' }
        ];
        
        for (const frac of fractions) {
            if (Math.abs(roundedPiMultiple - frac.val) < 1e-10) {
                return frac.text;
            }
            if (Math.abs(roundedPiMultiple + frac.val) < 1e-10) {
                return '-' + frac.text;
            }
        }
    }
    
    // Convert to string and clean up
    let str = rounded.toString();
    
    // Remove trailing zeros after decimal point
    if (str.includes('.') && !str.includes('e')) {
        str = str.replace(/\.?0+$/, '');
    }
    
    return str;
}

// Simplify square roots to surd form
function simplifySurd(num) {
    if (num < 0) return null;
    if (num === 0) return '0';
    
    // Check for perfect squares
    const sqrt = Math.sqrt(num);
    if (Number.isInteger(sqrt)) return sqrt.toString();
    
    // Try to factor out perfect squares
    for (let i = Math.floor(sqrt); i >= 2; i--) {
        const square = i * i;
        if (num % square === 0) {
            const remaining = num / square;
            if (remaining === 1) return i.toString();
            return i + '\u221A' + remaining;
        }
    }
    
    return '\u221A' + num;
}

// Safe evaluation of mathematical expressions
function safeEvaluate(expr) {
    try {
        // Replace mathematical constants
        expr = expr.replace(/\u03C0/g, 'Math.PI');
        expr = expr.replace(/e(?![x])/g, 'Math.E');
        
        // Replace mathematical functions
        expr = expr.replace(/sin\(/g, 'sin(');
        expr = expr.replace(/cos\(/g, 'cos(');
        expr = expr.replace(/tan\(/g, 'tan(');
        expr = expr.replace(/asin\(/g, 'asin(');
        expr = expr.replace(/acos\(/g, 'acos(');
        expr = expr.replace(/atan\(/g, 'atan(');
        expr = expr.replace(/sinh\(/g, 'sinh(');
        expr = expr.replace(/cosh\(/g, 'cosh(');
        expr = expr.replace(/tanh\(/g, 'tanh(');
        expr = expr.replace(/asinh\(/g, 'asinh(');
        expr = expr.replace(/acosh\(/g, 'acosh(');
        expr = expr.replace(/atanh\(/g, 'atanh(');
        expr = expr.replace(/log\(/g, 'Math.log10(');
        expr = expr.replace(/ln\(/g, 'Math.log(');
        expr = expr.replace(/\u221A\(/g, 'Math.sqrt(');
        expr = expr.replace(/\^/g, '**');
        
        // Define trigonometric functions with degree/radian support
        const sin = function(x) { return Math.sin(isDegreeMode ? x * Math.PI / 180 : x); };
        const cos = function(x) { return Math.cos(isDegreeMode ? x * Math.PI / 180 : x); };
        const tan = function(x) { return Math.tan(isDegreeMode ? x * Math.PI / 180 : x); };
        
        // Inverse trigonometric functions - return in degrees or radians
        const asin = function(x) {
            var result = Math.asin(x);
            return isDegreeMode ? result * 180 / Math.PI : result;
        };
        
        const acos = function(x) {
            var result = Math.acos(x);
            return isDegreeMode ? result * 180 / Math.PI : result;
        };
        
        const atan = function(x) {
            var result = Math.atan(x);
            return isDegreeMode ? result * 180 / Math.PI : result;
        };
        
        // Hyperbolic functions
        const sinh = function(x) { return Math.sinh(x); };
        const cosh = function(x) { return Math.cosh(x); };
        const tanh = function(x) { return Math.tanh(x); };
        
        // Inverse hyperbolic functions using logarithm formulas
        const asinh = function(x) { return Math.log(x + Math.sqrt(x * x + 1)); };
        const acosh = function(x) {
            if (x < 1) throw new Error('Invalid input');
            return Math.log(x + Math.sqrt(x * x - 1));
        };
        const atanh = function(x) {
            if (Math.abs(x) >= 1) throw new Error('Invalid input');
            return 0.5 * Math.log((1 + x) / (1 - x));
        };
        
        // Evaluate the expression
        const result = eval(expr);
        return result;
    } catch (error) {
        throw error;
    }
}

// Calculate result
function calculate() {
    if (isError) {
        clear();
        return;
    }
    
    if (!currentInput) return;
    
    try {
        let expr = currentInput;
        
        // Handle implicit multiplication (e.g., 2π -> 2*π)
        expr = expr.replace(/(\d)([\u03C0e])/g, '$1*$2');
        expr = expr.replace(/([\u03C0e])(\d)/g, '$1*$2');
        expr = expr.replace(/(\))(\d)/g, '$1*$2');
        expr = expr.replace(/(\d)(\()/g, '$1*$2');
        expr = expr.replace(/(\))(\()/g, '$1*$2');
        expr = expr.replace(/([\u03C0e])(\()/g, '$1*$2');
        expr = expr.replace(/(\))([\u03C0e])/g, '$1*$2');
        
        const result = safeEvaluate(expr);
        
        // Format the result
        let formattedResult;
        
        // Check for surd form if result is from a square root operation
        if (currentInput.includes('\u221A')) {
            const numericResult = parseFloat(result.toPrecision(12));
            if (numericResult >= 0 && Number.isInteger(numericResult * numericResult)) {
                formattedResult = simplifySurd(numericResult * numericResult);
            } else {
                formattedResult = formatNumber(result);
            }
        } else {
            formattedResult = formatNumber(result);
        }
        
        previousInput = currentInput + ' = ';
        currentInput = formattedResult;
        operator = null;
        shouldResetDisplay = true;
        isError = false;
        updateDisplay();
    } catch (error) {
        currentInput = '';
        isError = true;
        updateDisplay();
    }
}

// Add to display
function appendToDisplay(value) {
    if (isError) {
        clear();
    }
    
    if (shouldResetDisplay && !isNaN(value)) {
        currentInput = value;
        shouldResetDisplay = false;
    } else {
        currentInput += value;
        shouldResetDisplay = false;
    }
    updateDisplay();
}

// Clear all
function clear() {
    currentInput = '';
    previousInput = '';
    operator = null;
    isError = false;
    shouldResetDisplay = false;
    updateDisplay();
}

// Backspace
function backspace() {
    if (isError) {
        clear();
        return;
    }
    
    if (shouldResetDisplay) {
        clear();
        return;
    }
    
    currentInput = currentInput.slice(0, -1);
    updateDisplay();
}

// Toggle degree/radian mode
function toggleMode() {
    isDegreeMode = !isDegreeMode;
    modeButton.textContent = isDegreeMode ? 'DEG' : 'RAD';
}

// Convert between fraction and decimal
function convertFraction() {
    if (isError) {
        clear();
        return;
    }
    
    if (!currentInput) return;
    
    try {
        const value = parseFloat(safeEvaluate(currentInput));
        
        if (isNaN(value) || !isFinite(value)) {
            return;
        }
        
        // Check if it looks like a fraction input (contains /)
        if (currentInput.includes('/')) {
            // Convert fraction to decimal
            const parts = currentInput.split('/');
            if (parts.length === 2) {
                const numerator = parseFloat(parts[0]);
                const denominator = parseFloat(parts[1]);
                if (!isNaN(numerator) && !isNaN(denominator) && denominator !== 0) {
                    currentInput = formatNumber(numerator / denominator);
                    shouldResetDisplay = true;
                    updateDisplay();
                }
            }
        } else {
            // Convert decimal to fraction
            const decimal = value;
            
            // Handle negative numbers
            const sign = decimal < 0 ? '-' : '';
            const absDecimal = Math.abs(decimal);
            
            // Try to find a simple fraction
            const maxDenominator = 1000;
            let bestNumerator = 0;
            let bestDenominator = 1;
            let bestError = Infinity;
            
            for (let denom = 1; denom <= maxDenominator; denom++) {
                const numer = Math.round(absDecimal * denom);
                const error = Math.abs(absDecimal - numer / denom);
                
                if (error < bestError) {
                    bestError = error;
                    bestNumerator = numer;
                    bestDenominator = denom;
                    
                    // If we found an exact match, stop
                    if (error < 1e-12) break;
                }
            }
            
            // Only show fraction if it's a good approximation
            if (bestError < 1e-6) {
                if (bestDenominator === 1) {
                    currentInput = sign + bestNumerator.toString();
                } else {
                    currentInput = sign + bestNumerator + '/' + bestDenominator;
                }
                shouldResetDisplay = true;
                updateDisplay();
            }
        }
    } catch (error) {
        // Ignore conversion errors
    }
}

// Add function to display
function addFunction(funcName) {
    if (isError) {
        clear();
    }
    
    if (shouldResetDisplay) {
        currentInput = funcName + '(';
        shouldResetDisplay = false;
    } else {
        currentInput += funcName + '(';
    }
    updateDisplay();
}

// Keyboard support
document.addEventListener('keydown', function(event) {
    if (isError && event.key !== 'Escape') {
        clear();
    }
    
    const key = event.key;
    
    if (!isNaN(key) || key === '.') {
        appendToDisplay(key);
    } else if (key === '+') {
        appendToDisplay('+');
    } else if (key === '-') {
        appendToDisplay('-');
    } else if (key === '*') {
        appendToDisplay('*');
    } else if (key === '/') {
        event.preventDefault();
        appendToDisplay('/');
    } else if (key === '^') {
        appendToDisplay('^');
    } else if (key === '(' || key === ')') {
        appendToDisplay(key);
    } else if (key === 'Enter' || key === '=') {
        event.preventDefault();
        calculate();
    } else if (key === 'Backspace') {
        backspace();
    } else if (key === 'Escape') {
        clear();
    } else if (key.toLowerCase() === 'p') {
        appendToDisplay('\u03C0');
    } else if (key.toLowerCase() === 'e') {
        appendToDisplay('e');
    } else if (key.toLowerCase() === 's' && event.shiftKey) {
        addFunction('asin');
    } else if (key.toLowerCase() === 'c' && event.shiftKey) {
        addFunction('acos');
    } else if (key.toLowerCase() === 't' && event.shiftKey) {
        addFunction('atan');
    }
});

// Initialize display
updateDisplay();
