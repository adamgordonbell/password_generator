document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('password-input');
    const strengthScore = document.getElementById('strength-score');
    const conditions = document.getElementById('conditions');
    const hintPopup = document.getElementById('hint-popup');

    // Initialize conditions
    fetch('/check_password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({password: ''}),
    })
    .then(response => response.json())
    .then(data => updateUI(data));

    passwordInput.addEventListener('input', function() {
        fetch('/check_password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({password: this.value}),
        })
        .then(response => response.json())
        .then(data => updateUI(data));
    });

    function updateUI(data) {
        strengthScore.textContent = `Strength: ${data.strength.score}`;
        strengthScore.className = `text-xl font-semibold mb-4 ${getStrengthColor(data.strength.score)}`;
        
        conditions.innerHTML = '';
        
        data.conditions.forEach(condition => {
            const div = document.createElement('div');
            div.className = 'flex items-center space-x-2 p-2 rounded';
            
            const checkbox = document.createElement('span');
            checkbox.className = 'h-6 w-16 inline-flex items-center justify-center border border-gray-300 rounded mr-2 px-1';
            if (condition.met === 0) {
                checkbox.textContent = 'X';
                checkbox.className += ' bg-red-500 text-white';
            } else {
                checkbox.innerHTML = '✓'.repeat(condition.met).split('').join(' '); // Unicode checkmark with spaces
                checkbox.className += ' bg-green-500 text-white';
            }
            
            const text = document.createElement('span');
            text.textContent = condition.message;
            
            const infoIcon = document.createElement('span');
            infoIcon.innerHTML = '&#9432;'; // Info icon
            infoIcon.className = 'text-blue-500 cursor-pointer ml-2';
            infoIcon.addEventListener('mouseover', (e) => showHint(e, condition.hint));
            infoIcon.addEventListener('mouseout', hideHint);
            
            div.appendChild(checkbox);
            div.appendChild(text);
            div.appendChild(infoIcon);
            conditions.appendChild(div);
        });
    }

    function showHint(event, hint) {
        hintPopup.textContent = hint;
        hintPopup.style.left = `${event.pageX + 10}px`;
        hintPopup.style.top = `${event.pageY + 10}px`;
        hintPopup.classList.remove('hidden');
    }

    function hideHint() {
        hintPopup.classList.add('hidden');
    }

    function getStrengthColor(score) {
        if (score <= 0) return 'text-red-500';
        if (score <= 2) return 'text-yellow-500';
        if (score <= 4) return 'text-green-500';
        return 'text-blue-500';
    }
});
