// Фильтрация вещей в гардеробе
function initFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const clothingCards = document.querySelectorAll('.clothing-card');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Удаляем активный класс у всех кнопок
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            // Добавляем активный класс к нажатой кнопке
            this.classList.add('active');
            
            const filter = this.getAttribute('data-filter');
            
            // Фильтруем карточки
            clothingCards.forEach(card => {
                const category = card.getAttribute('data-category');
                const seasons = card.getAttribute('data-seasons');
                
                if (filter === 'all' || 
                    category === filter || 
                    seasons.includes(filter)) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
}

// Плавное появление карточек при загрузке
function animateCards() {
    const cards = document.querySelectorAll('.clothing-card');
    
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initFilters();
    animateCards();
});