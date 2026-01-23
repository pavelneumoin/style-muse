// Плавное появление результата
window.addEventListener('DOMContentLoaded', function() {
    const result = document.getElementById('weatherResult');
    if (result && result.innerHTML.trim() !== '') {
        result.style.opacity = '0';
        result.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            result.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            result.style.opacity = '1';
            result.style.transform = 'translateY(0)';
        }, 100);
    }
});

// Валидация формы
const form = document.querySelector('.weather-form');
if (form) {
    form.addEventListener('submit', function(e) {
        const cityInput = form.querySelector('input[name="city"]');
        if (!cityInput.value.trim()) {
            e.preventDefault();
            alert('Пожалуйста, введите название города');
            return false;
        }
    });
}