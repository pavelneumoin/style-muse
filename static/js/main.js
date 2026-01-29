document.addEventListener('DOMContentLoaded', () => {

    // === State ===
    let selectedItem = null;
    let selectedGender = null;

    const itemNames = {
        'coat': 'Пальто',
        'top': 'Верх',
        'bottom': 'Низ',
        'dress': 'Платье',
        'shoes': 'Обувь',
        'hat': 'Шапка',
        'scarf': 'Шарф',
        'gloves': 'Перчатки',
        'umbrella': 'Зонт',
        'sunglasses': 'Очки'
    };

    // === Color Modal ===
    const colorModal = document.getElementById('color-modal');
    const colorModalOverlay = document.getElementById('color-modal-overlay');
    const closeColorsBtn = document.getElementById('close-colors');
    const openColorsBtn = document.getElementById('open-colors');
    const colorBtns = document.querySelectorAll('.color-btn');
    const selectedHint = document.getElementById('selected-item-hint');
    const selectedName = document.getElementById('selected-element-name');

    function openColorModal() {
        if (!selectedItem) {
            if (selectedHint) selectedHint.style.display = 'block';
            return;
        }
        if (colorModal && colorModalOverlay) {
            colorModal.classList.add('show');
            colorModalOverlay.classList.add('show');
        }
    }

    function closeColorModal() {
        if (colorModal && colorModalOverlay) {
            colorModal.classList.remove('show');
            colorModalOverlay.classList.remove('show');
        }
    }

    if (openColorsBtn) openColorsBtn.addEventListener('click', openColorModal);
    if (closeColorsBtn) closeColorsBtn.addEventListener('click', closeColorModal);
    if (colorModalOverlay) colorModalOverlay.addEventListener('click', closeColorModal);

    // === Clothing Item Selection ===
    const clothingItems = document.querySelectorAll('.clothing-item');

    clothingItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.stopPropagation();

            // Deselect all
            clothingItems.forEach(i => i.classList.remove('selected'));

            // Select this one (all matching items of same type and gender)
            const itemType = item.dataset.item;
            const gender = item.dataset.gender;

            document.querySelectorAll(`.clothing-item[data-item="${itemType}"][data-gender="${gender}"]`)
                .forEach(el => el.classList.add('selected'));

            selectedItem = itemType;
            selectedGender = gender;

            // Update hint
            if (selectedHint) selectedHint.style.display = 'none';
            if (selectedName) selectedName.textContent = itemNames[itemType] || itemType;

            // Open color modal
            openColorModal();
        });
    });

    // === Apply Color ===
    colorBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const color = btn.dataset.color;
            if (!color || !selectedItem || !selectedGender) return;

            // Apply color to all selected items
            document.querySelectorAll(`.clothing-item[data-item="${selectedItem}"][data-gender="${selectedGender}"]`)
                .forEach(el => {
                    el.setAttribute('fill', color);
                    el.style.fill = color;
                    if (el.tagName === 'line' || el.tagName === 'path') {
                        if (el.getAttribute('stroke')) {
                            el.setAttribute('stroke', color);
                        }
                    }
                });

            // Flash animation
            btn.style.transform = 'scale(1.3)';
            setTimeout(() => btn.style.transform = '', 200);

            closeColorModal();
        });
    });

    // === AI Modal ===
    const aiModal = document.getElementById('ai-modal');
    const aiModalOverlay = document.getElementById('ai-modal-overlay');
    const aiModalTitle = document.getElementById('ai-modal-title');
    const aiModalContent = document.getElementById('ai-modal-content');
    const closeAiModal = document.getElementById('close-ai-modal');

    function showAiModal(title, content) {
        if (aiModal && aiModalOverlay) {
            aiModalTitle.textContent = title;
            aiModalContent.textContent = content;
            aiModal.classList.add('show');
            aiModalOverlay.classList.add('show');
        }
    }

    function hideAiModal() {
        if (aiModal && aiModalOverlay) {
            aiModal.classList.remove('show');
            aiModalOverlay.classList.remove('show');
        }
    }

    if (closeAiModal) closeAiModal.addEventListener('click', hideAiModal);
    if (aiModalOverlay) aiModalOverlay.addEventListener('click', hideAiModal);

    // === Clickable AI Elements ===
    const clickableAiElements = document.querySelectorAll('.clickable-ai');
    let aiCooldown = false;
    const COOLDOWN_TIME = 10000; // 10 секунд кулдаун

    clickableAiElements.forEach(el => {
        el.addEventListener('click', async () => {
            const topic = el.dataset.topic;
            if (!topic) return;

            // Проверяем кулдаун
            if (aiCooldown) {
                showAiModal('⏳ Подожди!', 'Нейросеть отдыхает. Попробуй через несколько секунд! 😊');
                return;
            }

            // Устанавливаем кулдаун
            aiCooldown = true;

            // Добавляем визуальный индикатор кулдауна
            clickableAiElements.forEach(elem => {
                elem.style.opacity = '0.5';
                elem.style.cursor = 'not-allowed';
            });

            // Снимаем кулдаун через COOLDOWN_TIME
            setTimeout(() => {
                aiCooldown = false;
                clickableAiElements.forEach(elem => {
                    elem.style.opacity = '1';
                    elem.style.cursor = 'pointer';
                });
            }, COOLDOWN_TIME);

            showAiModal('🤖 Загружаю...', 'Секунду, спрашиваю у умной нейросети...');

            try {
                const response = await fetch('/api/explain_term', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ term: topic })
                });

                const data = await response.json();

                if (data.explanation) {
                    showAiModal('🎓 Интересно!', data.explanation);
                } else {
                    showAiModal('😅 Упс', 'Не удалось получить ответ. Попробуй ещё раз!');
                }
            } catch (e) {
                showAiModal('❌ Ошибка', 'Проблема с подключением. Проверь интернет!');
            }
        });
    });

    // === Click outside to deselect ===
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.clothing-item') && !e.target.closest('.modal')) {
            clothingItems.forEach(i => i.classList.remove('selected'));
            selectedItem = null;
            selectedGender = null;
        }
    });

    // === AI Question Buttons ===
    const aiQuestionBtns = document.querySelectorAll('.ai-question-btn');
    const mascot = document.getElementById('mascot');
    const mascotSpeech = document.getElementById('mascot-speech');

    const mascotPhrases = [
        'Сейчас узнаю! 🔍',
        'Отличный вопрос! ✨',
        'Думаю... 🤔',
        'Секундочку! ⏳',
        'Ого, интересно! 🌟'
    ];

    aiQuestionBtns.forEach(btn => {
        btn.addEventListener('click', async () => {
            const topic = btn.dataset.topic;
            if (!topic) return;

            // Проверяем кулдаун
            if (aiCooldown) {
                if (mascotSpeech) {
                    mascotSpeech.textContent = 'Подожди немножко! Я отдыхаю 😴';
                }
                showAiModal('⏳ Подожди!', 'Пушок устал и отдыхает. Попробуй через несколько секунд! 😊');
                return;
            }

            // Анимация маскота
            if (mascot) {
                mascot.style.animation = 'none';
                mascot.offsetHeight; // Trigger reflow
                mascot.style.animation = 'bounce 0.5s ease';
            }

            // Случайная фраза маскота
            if (mascotSpeech) {
                mascotSpeech.textContent = mascotPhrases[Math.floor(Math.random() * mascotPhrases.length)];
            }

            // Устанавливаем кулдаун
            aiCooldown = true;
            aiQuestionBtns.forEach(b => {
                b.style.opacity = '0.5';
                b.style.pointerEvents = 'none';
            });

            setTimeout(() => {
                aiCooldown = false;
                aiQuestionBtns.forEach(b => {
                    b.style.opacity = '1';
                    b.style.pointerEvents = 'auto';
                });
                if (mascotSpeech) {
                    mascotSpeech.textContent = 'Спроси меня ещё! 🌈';
                }
            }, COOLDOWN_TIME);

            showAiModal('☁️ Пушок думает...', 'Секунду, спрашиваю у умной нейросети...');

            try {
                const response = await fetch('/api/explain_term', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ term: topic })
                });

                const data = await response.json();

                if (data.explanation) {
                    showAiModal('🎓 Пушок говорит:', data.explanation);
                    if (mascotSpeech) {
                        mascotSpeech.textContent = 'Вот что я узнал! 🎉';
                    }
                } else {
                    showAiModal('😅 Упс', 'Не удалось получить ответ. Попробуй ещё раз!');
                    if (mascotSpeech) {
                        mascotSpeech.textContent = 'Что-то пошло не так... 😕';
                    }
                }
            } catch (e) {
                showAiModal('❌ Ошибка', 'Проблема с подключением. Проверь интернет!');
                if (mascotSpeech) {
                    mascotSpeech.textContent = 'Нет связи с интернетом 📡';
                }
            }
        });
    });

    // Восстанавливаем анимацию маскота
    if (mascot) {
        mascot.addEventListener('animationend', () => {
            mascot.style.animation = 'float 3s ease-in-out infinite';
        });
    }
});