const display = document.querySelector('#display');
const errorEl = document.querySelector('#error');
const buttons = document.querySelectorAll('.button');
const clearButton = document.querySelector('#clear');
const backspaceButton = document.querySelector('#backspace');
const equalsButton = document.querySelector('#equals');

function setDisplay(value) {
  display.value = value;
  errorEl.textContent = '';
}

function appendValue(value) {
  if (display.value === '0') {
    display.value = value;
    return;
  }
  display.value += value;
}

async function calculateExpression() {
  const expression = display.value.trim();
  if (!expression) {
    return;
  }

  try {
    const response = await fetch('/api/calc', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ expression }),
    });

    if (!response.ok) {
      let detail = 'Unable to calculate';
      try {
        const errData = await response.json();
        detail = errData.detail || detail;
      } catch {}
      throw new Error(detail);
    }

    const data = await response.json();
    setDisplay(String(data.result));
  } catch (err) {
    errorEl.textContent = err.message;
  }
}

buttons.forEach((button) => {
  const value = button.dataset.value;
  if (!value) return;

  button.addEventListener('click', () => {
    appendValue(value);
  });
});

clearButton.addEventListener('click', () => {
  setDisplay('');
});

backspaceButton.addEventListener('click', () => {
  setDisplay(display.value.slice(0, -1));
});

equalsButton.addEventListener('click', calculateExpression);

document.addEventListener('keydown', (event) => {
  const allowedKeys = '0123456789+-*/().';
  if (allowedKeys.includes(event.key)) {
    event.preventDefault();
    appendValue(event.key);
    return;
  }

  if (event.key === 'Enter') {
    event.preventDefault();
    calculateExpression();
    return;
  }

  if (event.key === 'Backspace') {
    event.preventDefault();
    setDisplay(display.value.slice(0, -1));
    return;
  }

  if (event.key === 'Escape') {
    event.preventDefault();
    setDisplay('');
  }
});
