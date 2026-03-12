// Фильтрация вещей в гардеробе
function initFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const clothingCards = document.querySelectorAll('.clothing-card');

    filterButtons.forEach(button => {
        button.addEventListener('click', function () {
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
document.addEventListener('DOMContentLoaded', function () {
    initFilters();
    animateCards();
    initFittingRoom();
});

function initFittingRoom() {
    const toggleBtn = document.getElementById('toggle-fitting-room-btn');
    const fittingRoom = document.getElementById('fitting-room-section');

    if (!toggleBtn || !fittingRoom) return;

    toggleBtn.addEventListener('click', () => {
        if (fittingRoom.style.display === 'none') {
            fittingRoom.style.display = 'block';
            toggleBtn.textContent = '❌ Закрыть примерочную';
            fittingRoom.scrollIntoView({ behavior: 'smooth' });
        } else {
            fittingRoom.style.display = 'none';
            toggleBtn.textContent = '👕 Примерочная';
        }
    });

    // Drag and drop logic
    const cards = document.querySelectorAll('.clothing-card[draggable="true"]');
    const dropZones = document.querySelectorAll('.drop-zone');

    cards.forEach(card => {
        card.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', JSON.stringify({
                id: card.dataset.id,
                name: card.dataset.name,
                category: card.dataset.category,
                colorHTML: card.querySelector('.card-color-indicator').outerHTML
            }));
            card.style.opacity = '0.5';
        });

        card.addEventListener('dragend', () => {
            card.style.opacity = '1';
        });
    });

    dropZones.forEach(zone => {
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.style.borderColor = 'var(--pink)';
            zone.style.background = '#fbcfe8';
        });

        zone.addEventListener('dragleave', (e) => {
            zone.style.borderColor = '#cbd5e1';
            zone.style.background = '#f8fafc';
        });

        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.style.borderColor = '#cbd5e1';
            zone.style.background = '#f8fafc';

            const dataStr = e.dataTransfer.getData('text/plain');
            if (!dataStr) return;

            try {
                const data = JSON.parse(dataStr);

                zone.innerHTML = `
                    <div style="font-size: 0.8rem; line-height: 1.2;">
                        ${data.colorHTML}
                        <br><b>${data.name}</b>
                    </div>
                `;
                zone.dataset.itemId = data.id;
                zone.dataset.itemName = data.name;
                zone.style.borderStyle = 'solid';
                zone.style.borderColor = 'var(--purple)';

            } catch (err) {
                console.error(err);
            }
        });

        zone.addEventListener('click', () => {
            if (zone.dataset.itemId) {
                delete zone.dataset.itemId;
                delete zone.dataset.itemName;
                const slotNames = {
                    'head': 'Шапка',
                    'body': 'Верх / Платье',
                    'legs': 'Низ',
                    'feet': 'Обувь'
                };
                zone.innerHTML = `${slotNames[zone.dataset.slot]}<br>(Перетащи)`;
                zone.style.borderStyle = 'dashed';
                zone.style.borderColor = '#cbd5e1';
            }
        });
    });

    // Evaluate Outfit
    const evalBtn = document.getElementById('evaluate-outfit-btn');
    const evalWeather = document.getElementById('fitting-weather-input');
    const evalResult = document.getElementById('evaluate-result');
    const evalText = document.getElementById('evaluate-text');

    if (evalBtn) {
        evalBtn.addEventListener('click', async () => {
            const outfit = [];
            dropZones.forEach(z => {
                if (z.dataset.itemName) {
                    outfit.push(z.dataset.itemName);
                }
            });

            if (outfit.length === 0) {
                alert("Сначала одень манекен! Перетащи вещи на силуэт.");
                return;
            }

            const weather = evalWeather.value.trim() || 'неизвестно';

            evalBtn.disabled = true;
            evalBtn.innerHTML = '⏳ Думаю...';
            evalResult.style.display = 'none';

            try {
                const resp = await fetch('/api/evaluate_outfit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        weather: weather,
                        outfit: outfit
                    })
                });
                const result = await resp.json();

                if (result.feedback) {
                    evalText.textContent = result.feedback;
                    evalResult.style.display = 'block';
                } else {
                    alert("Ошибка: " + (result.error || "Неизвестная ошибка"));
                }
            } catch (e) {
                console.error(e);
                alert("Ошибка сети при оценке наряда.");
            } finally {
                evalBtn.disabled = false;
                evalBtn.innerHTML = '<span>✨</span> Оценить наряд Пушком';
            }
        });
    }
}