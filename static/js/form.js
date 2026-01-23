// Валидация формы добавления/редактирования вещи
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('clothingForm');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            const name = form.querySelector('#name').value.trim();
            const category = form.querySelector('#category').value;
            
            if (!name) {
                alert('Пожалуйста, введите название вещи');
                e.preventDefault();
                return false;
            }
            
            if (!category) {
                alert('Пожалуйста, выберите категорию');
                e.preventDefault();
                return false;
            }
            
            // Показываем сообщение об успешном сохранении
            if (confirm('Вещь успешно сохранена!')) {
                return true;
            } else {
                e.preventDefault();
                return false;
            }
        });
        
        // Автофокус на поле названия
        const nameInput = form.querySelector('#name');
        if (nameInput) {
            nameInput.focus();
        }
    }
});