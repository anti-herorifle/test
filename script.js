let display = document.getElementById('display');
let currentExpression = '';

function appendNumber(num) {
    currentExpression += num;
    updateDisplay();
}

function appendOperator(operator) {
    const lastChar = currentExpression.slice(-1);
    if (currentExpression === '' && operator !== '-') return;
    if (['+', '-', '*', '/'].includes(lastChar)) {
        currentExpression = currentExpression.slice(0, -1) + operator;
    } else {
        currentExpression += operator;
    }
    updateDisplay();
}

function clearDisplay() {
    currentExpression = '';
    updateDisplay();
}

function deleteLast() {
    currentExpression = currentExpression.slice(0, -1);
    updateDisplay();
}

function calculate() {
    try {
        if (currentExpression === '') return;
        
        // Evaluate the expression safely
        const result = Function('"use strict";return (' + currentExpression + ')')();
        
        // Check for division by zero or invalid results
        if (!isFinite(result)) {
            currentExpression = 'Error';
        } else {
            currentExpression = result.toString();
        }
    } catch (error) {
        currentExpression = 'Error';
    }
    updateDisplay();
}

function updateDisplay() {
    // Replace * with × for better visual display
    let displayValue = currentExpression.replace(/\*/g, '×');
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
    } else if (key === '.') {
        appendNumber('.');
    } else if (key === 'Enter' || key === '=') {
        event.preventDefault();
        calculate();
    } else if (key === 'Backspace') {
        deleteLast();
    } else if (key === 'Escape' || key === 'c' || key === 'C') {
        clearDisplay();
    }
});
