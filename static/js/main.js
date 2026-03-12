document.addEventListener('DOMContentLoaded', () => {

    // === Kids Interactive Dressing Logic ===
    const clothingOrder = {
        'top': 1, 'bottom': 1, 'dress': 1,
        'shoes': 2,
        'coat': 3,
        'scarf': 4,
        'hat': 5, 'gloves': 5,
        'umbrella': 6, 'sunglasses': 6
    };

    const dressingMessages = {
        'top': 'Сначала надеваем кофточку!',
        'bottom': 'Теперь штанишки - грей ножки!',
        'dress': 'Надеваем красивое платье!',
        'shoes': 'Обуваем ботинки для прогулки!',
        'coat': 'Куртка согреет от ветра!',
        'scarf': 'Шарфик бережет горло!',
        'hat': 'Шапка прячет ушки от холода!',
        'gloves': 'Перчатки греют ручки!',
        'umbrella': 'Берем зонт от дождя!',
        'sunglasses': 'Очки от яркого солнышка!'
    };

    // Hide all clothing initially
    const allClothingItems = document.querySelectorAll('.clothing-item');
    allClothingItems.forEach(el => el.classList.add('hidden-clothing'));

    window.startDressing = function (gender) {
        const avatarContainer = document.getElementById(`${gender}-avatar`);
        if (!avatarContainer) return;

        const btn = document.querySelector(`#${gender}-avatar-card .dress-up-btn`);
        if (btn) {
            btn.style.transform = 'scale(0)';
            setTimeout(() => btn.style.display = 'none', 300);
        }

        const bubble = document.getElementById(`${gender}-bubble`);

        const items = Array.from(avatarContainer.querySelectorAll('.hidden-clothing'));

        const layers = {};
        items.forEach(item => {
            const type = item.dataset.item;
            const layerNum = clothingOrder[type] || 99;
            if (!layers[layerNum]) layers[layerNum] = [];
            layers[layerNum].push(item);
        });

        const sortedLayers = Object.keys(layers).sort((a, b) => a - b);
        let currentStep = 0;

        function showNextLayer() {
            if (currentStep >= sortedLayers.length) {
                if (bubble) {
                    bubble.textContent = 'Готово! Мы оделись! 🎉';
                    setTimeout(() => bubble.classList.remove('show'), 3000);
                }
                return;
            }

            const layerIdx = sortedLayers[currentStep];
            const currentItems = layers[layerIdx];

            let typeName = '';
            currentItems.forEach(el => {
                el.classList.remove('hidden-clothing');
                el.classList.add('show-clothing');
                if (!typeName) typeName = el.dataset.item;
            });

            if (bubble && typeName) {
                bubble.textContent = dressingMessages[typeName] || 'Надеваем это!';
                bubble.classList.add('show');
            }

            currentStep++;
            setTimeout(showNextLayer, 1800);
        }

        showNextLayer();
    };

    // Jiggle on click
    allClothingItems.forEach(item => {
        item.addEventListener('mousedown', function (e) {
            if (this.classList.contains('show-clothing') || !this.classList.contains('hidden-clothing')) {
                this.classList.add('jiggling');
                setTimeout(() => this.classList.remove('jiggling'), 500);

                const typeName = this.dataset.item;
                const gender = this.dataset.gender;
                const bubble = document.getElementById(`${gender}-bubble`);
                if (bubble && typeName) {
                    bubble.textContent = dressingMessages[typeName] || 'Ой, щекотно! 😄';
                    bubble.classList.add('show');
                    setTimeout(() => bubble.classList.remove('show'), 2000);
                }
            }
        });
    });

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
            const mascot = document.getElementById('mascot');
            if (mascot) mascot.classList.add('mascot-thinking');

            try {
                const response = await fetch('/api/explain_term', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ term: topic })
                });

                const data = await response.json();

                if (data.explanation) {
                    showAiModal('🎓 Интересно!', data.explanation);
                    playTTS(data.explanation);
                } else {
                    showAiModal('😅 Упс', 'Не удалось получить ответ. Попробуй ещё раз!');
                }
            } catch (e) {
                showAiModal('❌ Ошибка', 'Проблема с подключением. Проверь интернет!');
            } finally {
                if (mascot) mascot.classList.remove('mascot-thinking');
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

    // === TTS Playback ===
    async function playTTS(text) {
        try {
            const response = await fetch('/api/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            });
            const data = await response.json();
            if (data.audio_base64) {
                const audio = new Audio("data:audio/mp3;base64," + data.audio_base64);
                audio.play();
            }
        } catch (e) {
            console.error("TTS playback failed:", e);
        }
    }

    const playAdviceBtn = document.getElementById('play-advice-btn');
    const mainAdviceText = document.getElementById('main-advice-text');
    if (playAdviceBtn && mainAdviceText) {
        playAdviceBtn.addEventListener('click', () => {
            playTTS(mainAdviceText.textContent);
        });
    }

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
            if (mascot) mascot.classList.add('mascot-thinking');

            try {
                const response = await fetch('/api/explain_term', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ term: topic })
                });

                const data = await response.json();

                if (data.explanation) {
                    showAiModal('🎓 Пушок говорит:', data.explanation);
                    playTTS(data.explanation);
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
            } finally {
                if (mascot) mascot.classList.remove('mascot-thinking');
            }
        });
    });

    // Восстанавливаем CSS анимацию маскота
    if (mascot) {
        mascot.addEventListener('animationend', (e) => {
            if (e.animationName === 'bounce') {
                mascot.style.animation = ''; // Убираем инлайновый стиль, чтобы работали классы
            }
        });
    }

    // === STT / Mic Logic ===
    const micBtn = document.getElementById('mic-btn');
    const micStatus = document.getElementById('mic-status');
    const micResult = document.getElementById('mic-result');
    let mediaRecorder = null;
    let audioChunks = [];

    if (micBtn) {
        micBtn.addEventListener('mousedown', startRecording);
        micBtn.addEventListener('mouseup', stopRecording);
        micBtn.addEventListener('mouseleave', stopRecording);

        micBtn.addEventListener('touchstart', (e) => { e.preventDefault(); startRecording(); });
        micBtn.addEventListener('touchend', stopRecording);
        micBtn.addEventListener('touchcancel', stopRecording);
    }

    async function startRecording() {
        if (mediaRecorder && mediaRecorder.state === 'recording') return;
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = event => {
                if (event.data.size > 0) audioChunks.push(event.data);
            };

            mediaRecorder.start();
            if (micStatus) {
                micStatus.textContent = 'Слушаю... Говори! 🔴';
                micStatus.style.display = 'block';
            }
            if (micResult) micResult.style.display = 'none';
            micBtn.style.transform = 'scale(1.1)';
            micBtn.style.boxShadow = '0 0 20px rgba(255, 0, 0, 0.6)';
        } catch (err) {
            console.error("Mic access error:", err);
            alert("Нет доступа к микрофону! Проверьте разрешения браузера.");
        }
    }

    async function stopRecording() {
        if (!mediaRecorder || mediaRecorder.state === 'inactive') return;

        mediaRecorder.onstop = async () => {
            if (micStatus) {
                micStatus.textContent = 'Распознаю... ⏳';
            }
            micBtn.style.transform = 'scale(1)';
            micBtn.style.boxShadow = '0 4px 15px rgba(255,105,180,0.3)';

            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });

            const formData = new FormData();
            formData.append('audio', audioBlob, 'speech.webm');

            try {
                const resp = await fetch('/api/stt', {
                    method: 'POST',
                    body: formData
                });
                const data = await resp.json();
                if (micStatus) micStatus.style.display = 'none';

                if (data.text) {
                    if (micResult) {
                        micResult.textContent = '🗣️ "' + data.text + '"';
                        micResult.style.display = 'block';
                        setTimeout(() => micResult.style.display = 'none', 5000);
                    }
                    askMascotVoice(data.text);
                } else {
                    if (micResult) {
                        micResult.textContent = 'Ничего не расслышал 😔';
                        micResult.style.display = 'block';
                        setTimeout(() => micResult.style.display = 'none', 3000);
                    }
                }
            } catch (e) {
                console.error(e);
                if (micStatus) micStatus.style.display = 'none';
            }

            mediaRecorder.stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.stop();
    }

    function askMascotVoice(questionText) {
        if (mascotSpeech) {
            mascotSpeech.textContent = 'Думаю над вопросом... 🤔';
        }
        if (mascot) mascot.classList.add('mascot-thinking');

        showAiModal('☁️ Пушок думает...', 'Секунду, спрашиваю у умной нейросети: "' + questionText + '"');

        const mascotPrompt = "Очень коротко ответь на вопрос ребенка (1-2 предложения, просто и весело): " + questionText;

        fetch('/api/explain_term', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ term: mascotPrompt })
        })
            .then(r => r.json())
            .then(data => {
                if (data.explanation) {
                    showAiModal('🎓 Пушок говорит:', data.explanation);
                    playTTS(data.explanation);
                    if (mascotSpeech) {
                        mascotSpeech.textContent = 'Вот что я узнал! 🎉';
                    }
                } else {
                    showAiModal('😅 Упс', 'Не удалось получить ответ. Попробуй ещё раз!');
                    if (mascotSpeech) {
                        mascotSpeech.textContent = 'Что-то пошло не так... 😕';
                    }
                }
            })
            .catch(err => {
                showAiModal('❌ Ошибка', 'Проблема с подключением.');
                console.error(err);
            })
            .finally(() => {
                if (mascot) mascot.classList.remove('mascot-thinking');
            });
    }

    // Listeners for coloring button
    const makeColoringBtn = document.getElementById('make-coloring-btn');
    const coloringResult = document.getElementById('coloring-result');
    const coloringImg = document.getElementById('coloring-img');

    if (makeColoringBtn) {
        makeColoringBtn.addEventListener('click', async () => {
            const outfit = makeColoringBtn.dataset.outfit || '';

            makeColoringBtn.disabled = true;
            makeColoringBtn.innerHTML = '⏳ Рисую контуры...';

            try {
                const resp = await fetch('/api/generate_coloring', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ outfit: outfit })
                });
                const data = await resp.json();

                if (data.image_base64) {
                    makeColoringBtn.style.display = 'none';
                    coloringImg.src = "data:image/jpeg;base64," + data.image_base64;
                    coloringResult.style.display = 'block';
                } else {
                    alert('Не удалось создать раскраску 😢');
                    makeColoringBtn.disabled = false;
                    makeColoringBtn.innerHTML = '🖍️ Сделать раскраску';
                }
            } catch (e) {
                console.error(e);
                alert('Ошибка сети');
                makeColoringBtn.disabled = false;
                makeColoringBtn.innerHTML = '🖍️ Сделать раскраску';
            }
        });
    }

});