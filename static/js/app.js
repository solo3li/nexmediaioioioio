/**
 * NEXMEDIA.AI - Interactive UI Logic
 * Vanilla JavaScript for Audio Visualizer, 4K Cinema Player,
 * Before/After Visual Slider, and Real-time SSE Pipeline Simulator.
 */

document.addEventListener('DOMContentLoaded', () => {
    initCelestialParticles();
    initAudioVisualizer();
    initVideoTimeline();
    initComparisonSlider();
    initPlaygroundStudio();
    initShowcaseGalleryAndModal();
    initPipelineSimulator();
    initCreditsCalculator();
    initLanguageSwitcher();
    initHeaderScroll();
    init3DParallaxTilt();
    initSoundFX();
    initMobileDrawer();
    initHeroNeuralPlayer();
});

/* --------------------------------------------------------------------------
   0. 3D Parallax Tilt & Specular Glare Reflection
-------------------------------------------------------------------------- */
function init3DParallaxTilt() {
    const cards = document.querySelectorAll('.portal-card, .pillar-card');
    
    cards.forEach(card => {
        if (!card.querySelector('.card-glare-effect')) {
            const glare = document.createElement('div');
            glare.className = 'card-glare-effect';
            card.appendChild(glare);
        }

        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = ((y - centerY) / centerY) * -6;
            const rotateY = ((x - centerX) / centerX) * 6;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
            card.style.setProperty('--mouse-x', `${(x / rect.width) * 100}%`);
            card.style.setProperty('--mouse-y', `${(y / rect.height) * 100}%`);
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });
}

/* --------------------------------------------------------------------------
   1. Audio Waveform & Astrolabe Visualizer
-------------------------------------------------------------------------- */
function initAudioVisualizer() {
    const canvas = document.getElementById('waveform-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const playBtn = document.getElementById('audio-play-toggle');
    const needle = document.getElementById('astrolabe-needle');
    const timecode = document.getElementById('audio-timecode');
    const iconPlay = playBtn ? playBtn.querySelector('.icon-play') : null;
    const iconPause = playBtn ? playBtn.querySelector('.icon-pause') : null;

    let isPlaying = false;
    let animationId = null;
    let phase = 0;
    let seconds = 14;

    function drawWaveform() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const width = canvas.width;
        const height = canvas.height;
        const centerY = height / 2;
        const barsCount = 38;
        const barWidth = 4;
        const gap = 3;

        for (let i = 0; i < barsCount; i++) {
            const x = i * (barWidth + gap) + 8;
            
            // Dynamic sine height based on playing state
            let amplitude = 6;
            if (isPlaying) {
                amplitude = Math.sin(phase + i * 0.35) * 18 + Math.cos(phase * 1.5 + i * 0.2) * 10;
                amplitude = Math.max(Math.abs(amplitude), 4);
            } else {
                amplitude = Math.sin(i * 0.4) * 8 + 6;
            }

            // Dual tone: Forest Green and Gold accent
            const isGold = i % 4 === 0;
            ctx.fillStyle = isGold ? '#D4AF37' : '#2ECC71';
            
            // Center-aligned vertical bar
            ctx.beginPath();
            ctx.roundRect(x, centerY - amplitude / 2, barWidth, amplitude, 2);
            ctx.fill();
        }

        if (isPlaying) {
            phase += 0.08;
            // Oscillate astrolabe needle
            if (needle) {
                const angle = Math.sin(phase * 0.8) * 35;
                needle.style.transform = `rotate(${angle}deg)`;
            }
            animationId = requestAnimationFrame(drawWaveform);
        }
    }

    // Initial static draw
    drawWaveform();

    if (playBtn) {
        playBtn.addEventListener('click', () => {
            isPlaying = !isPlaying;

            if (isPlaying) {
                if (iconPlay) iconPlay.style.display = 'none';
                if (iconPause) iconPause.style.display = 'block';
                playBtn.querySelector('span').textContent = 'إيقاف الموجة مؤقتاً';
                playBtn.style.backgroundColor = '#16532D';
                drawWaveform();
            } else {
                if (iconPlay) iconPlay.style.display = 'block';
                if (iconPause) iconPause.style.display = 'none';
                playBtn.querySelector('span').textContent = 'تجربة الموجة الصوتية الحية';
                playBtn.style.backgroundColor = '';
                cancelAnimationFrame(animationId);
                drawWaveform();
            }
        });
    }
}

/* --------------------------------------------------------------------------
   2. Interactive 4K Cinema Timeline
-------------------------------------------------------------------------- */
function initVideoTimeline() {
    const playBtn = document.getElementById('cinema-play-btn');
    const progressBar = document.getElementById('cinema-progress');
    const thumb = document.getElementById('cinema-thumb');
    let isPlaying = false;
    let progress = 45;
    let interval = null;

    if (playBtn && progressBar) {
        playBtn.addEventListener('click', () => {
            isPlaying = !isPlaying;
            if (isPlaying) {
                playBtn.querySelector('.play-text').textContent = 'المعاينة قيد التشغيل...';
                interval = setInterval(() => {
                    progress = (progress + 1) % 100;
                    progressBar.style.width = progress + '%';
                    if (thumb) thumb.style.left = progress + '%';
                }, 80);
            } else {
                playBtn.querySelector('.play-text').textContent = 'مشاهدة المعاينة السينمائية';
                clearInterval(interval);
            }
        });
    }
}

/* --------------------------------------------------------------------------
   3. Interactive Before/After Visual Comparison Slider
-------------------------------------------------------------------------- */
function initComparisonSlider() {
    const box = document.getElementById('comparison-slider');
    const beforeLayer = document.getElementById('before-layer');
    const handle = document.getElementById('slider-handle');

    if (!box || !beforeLayer || !handle) return;

    let isDragging = false;

    function updateSlider(xPos) {
        const rect = box.getBoundingClientRect();
        let offsetX = xPos - rect.left;
        offsetX = Math.max(0, Math.min(offsetX, rect.width));
        const percentage = (offsetX / rect.width) * 100;

        beforeLayer.style.width = percentage + '%';
        handle.style.left = percentage + '%';
    }

    box.addEventListener('mousedown', (e) => {
        isDragging = true;
        updateSlider(e.clientX);
    });

    window.addEventListener('mouseup', () => {
        isDragging = false;
    });

    window.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        updateSlider(e.clientX);
    });

    // Touch support for mobile devices
    box.addEventListener('touchmove', (e) => {
        if (e.touches.length > 0) {
            updateSlider(e.touches[0].clientX);
        }
    }, { passive: true });
}

/* --------------------------------------------------------------------------
   4. Real-time Pipeline Simulator (SSE + django-q2 Demonstration)
-------------------------------------------------------------------------- */
function initPipelineSimulator() {
    const startBtn = document.getElementById('btn-start-simulation');
    const fillCircle = document.getElementById('gauge-circle-fill');
    const percentEl = document.getElementById('sim-percentage');
    const statusEl = document.getElementById('sim-task-status');
    const badgeEl = document.getElementById('sim-status-badge');
    const logBox = document.getElementById('terminal-logs');
    const taskIdEl = document.getElementById('sim-task-id');

    if (!startBtn || !fillCircle || !percentEl) return;

    // Circumference of r=50 circle: 2 * pi * 50 = 314
    const totalCircumference = 314;

    function setGauge(percentage) {
        const offset = totalCircumference - (percentage / 100) * totalCircumference;
        fillCircle.style.strokeDashoffset = offset;
        percentEl.textContent = Math.round(percentage) + '%';
    }

    function addLog(text, isGold = false) {
        if (!logBox) return;
        const line = document.createElement('div');
        line.className = isGold ? 'log-line text-gold' : 'log-line';
        const now = new Date();
        const timeStr = now.toTimeString().split(' ')[0] + '.' + String(now.getMilliseconds()).padStart(3, '0');
        line.textContent = `[${timeStr}] ${text}`;
        logBox.appendChild(line);
        logBox.scrollTop = logBox.scrollHeight;
    }

    startBtn.addEventListener('click', () => {
        startBtn.disabled = true;
        startBtn.style.opacity = '0.6';

        // Generate dynamic UUID
        const randId = Math.random().toString(16).substring(2, 6) + '-' + 
                       Math.random().toString(16).substring(2, 6) + '-' + 
                       Math.random().toString(16).substring(2, 6);
        if (taskIdEl) taskIdEl.textContent = randId;

        // Reset state
        setGauge(0);
        if (statusEl) statusEl.textContent = 'استلام طلب التوليد (PROMPT QUEUED)';
        if (badgeEl) {
            badgeEl.textContent = 'معالجة مباشرة • Live Rendering';
            badgeEl.style.color = '#4ADE80';
        }

        // Highlight Step 1
        setStepActive('step-queue');
        addLog(`[طلب التوليد] تم استلام تفاصيل المشهد والتحقق من الحصة الائتمانية بالمعرف: ${randId}`);

        setTimeout(() => {
            setGauge(25);
            setStepActive('step-worker');
            if (statusEl) statusEl.textContent = 'المعالجة العصبية (PROCESSING)';
            addLog(`[تحليل المشهد] توزيع زوايا الكاميرا ومسارات الإضاءة والعمق البصري.`);
            addLog(`[محرك التوليد] بدء رندرة الإطارات الأولية بدقة عالية.`);
        }, 800);

        setTimeout(() => {
            setGauge(60);
            setStepActive('step-stream');
            if (statusEl) statusEl.textContent = 'الرندرة السينمائية 4K... 60%';
            addLog(`[المعالجة البصرية] استكمال سلاسة الحركة وتوليد الإطارات الفائقة (60 FPS).`);
            addLog(`[المعالجة الصوتية] دمج وهندسة المؤثرات الصوتية بتردد 48kHz: 60%`);
        }, 1800);

        setTimeout(() => {
            setGauge(88);
            setStepActive('step-storage');
            if (statusEl) statusEl.textContent = 'اللمسات النهائية والتصدير... 88%';
            addLog(`[تصحيح الألوان] تطبيق التدرج اللوني السينمائي وتجهيز ملف الفيديو فائق الجودة.`);
        }, 2800);

        setTimeout(() => {
            setGauge(100);
            if (statusEl) statusEl.textContent = 'جاهز للتنزيل (COMPLETED)';
            if (badgeEl) {
                badgeEl.textContent = 'تم الإنتاج 100% • READY';
                badgeEl.style.color = '#D4AF37';
            }
            addLog(`[اكتمل الإنتاج] تم إنتاج العمل بنجاح! رابط المعاينة والتحميل بدقة 4K متاح الآن.`, true);
            startBtn.disabled = false;
            startBtn.style.opacity = '1';
        }, 3800);
    });

    function setStepActive(stepId) {
        document.querySelectorAll('.sim-step-item').forEach(el => el.classList.remove('active'));
        const target = document.getElementById(stepId);
        if (target) target.classList.add('active');
    }
}

/* --------------------------------------------------------------------------
   5. Header Scroll Shadows (Disabled for seamless hero integration)
-------------------------------------------------------------------------- */
function initHeaderScroll() {
    // Seamless zero-border hero header - no shadow or background injection
    return;
}

/* --------------------------------------------------------------------------
   6. Celestial Particles & Star Dust Engine
-------------------------------------------------------------------------- */
function initCelestialParticles() {
    const canvas = document.getElementById('celestial-canvas');
    if (!canvas || !canvas.parentElement) return;

    const ctx = canvas.getContext('2d');
    let width = canvas.width = canvas.parentElement.offsetWidth;
    let height = canvas.height = canvas.parentElement.offsetHeight;

    window.addEventListener('resize', () => {
        if (!canvas.parentElement) return;
        width = canvas.width = canvas.parentElement.offsetWidth;
        height = canvas.height = canvas.parentElement.offsetHeight;
    });

    const particlesCount = Math.min(Math.floor((width * height) / 16000), 65);
    const particles = [];
    const mouse = { x: -1000, y: -1000, active: false };

    for (let i = 0; i < particlesCount; i++) {
        particles.push({
            x: Math.random() * width,
            y: Math.random() * height,
            vx: (Math.random() - 0.5) * 0.45,
            vy: (Math.random() - 0.5) * 0.45,
            radius: Math.random() * 2 + 1,
            goldHue: Math.random() > 0.4 ? '#C5A059' : '#D4AF37',
            alpha: Math.random() * 0.6 + 0.2
        });
    }

    const heroSection = document.querySelector('.royal-hero-section');
    if (heroSection) {
        heroSection.addEventListener('mousemove', (e) => {
            const rect = heroSection.getBoundingClientRect();
            mouse.x = e.clientX - rect.left;
            mouse.y = e.clientY - rect.top;
            mouse.active = true;
        });

        heroSection.addEventListener('mouseleave', () => {
            mouse.active = false;
        });
    }

    function render() {
        ctx.clearRect(0, 0, width, height);

        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];

            p.x += p.vx;
            p.y += p.vy;

            if (p.x < 0 || p.x > width) p.vx *= -1;
            if (p.y < 0 || p.y > height) p.vy *= -1;

            if (mouse.active) {
                const dx = mouse.x - p.x;
                const dy = mouse.y - p.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 130) {
                    p.x += dx * 0.015;
                    p.y += dy * 0.015;
                }
            }

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = p.goldHue;
            ctx.globalAlpha = p.alpha;
            ctx.fill();

            for (let j = i + 1; j < particles.length; j++) {
                const p2 = particles[j];
                const dx = p.x - p2.x;
                const dy = p.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 100) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = '#C5A059';
                    ctx.globalAlpha = (1 - dist / 100) * 0.18;
                    ctx.lineWidth = 0.8;
                    ctx.stroke();
                }
            }
        }

        ctx.globalAlpha = 1.0;
        requestAnimationFrame(render);
    }

    render();
}

/* --------------------------------------------------------------------------
   7. Neural Style Playground Studio
-------------------------------------------------------------------------- */
function initPlaygroundStudio() {
    const presetBtns = document.querySelectorAll('.btn-preset');
    const styleChips = document.querySelectorAll('.style-chip');
    const promptInput = document.getElementById('playground-prompt-input');
    const generateBtn = document.getElementById('playground-generate-btn');
    const loader = document.getElementById('playground-loader');
    const visualArt = document.getElementById('playground-visual-art');
    const styleTag = document.getElementById('playground-style-tag');
    const artTitle = document.getElementById('playground-art-title');
    const artDesc = document.getElementById('playground-art-desc');
    const latencyEl = document.getElementById('playground-latency');

    const styleMeta = {
        andalusian: {
            tag: 'طراز سينمائي واقعي 8K',
            title: 'بورتريه فوتوغرافي واقعي',
            desc: 'تم التوليد بنموذج فوتوغرافي متقدم مع إضاءة درامية وعمق ميدان احترافي بدقة 8K.',
            className: 'style-andalusian'
        },
        cinema4k: {
            tag: 'سينمائي 4K UHD',
            title: 'مشهد إعلاني سينمائي فاخر',
            desc: 'تجسيد فوتوغرافي واقعي فائق الوضوح 4K مع تدرجات إضاءة الشفق الذهبي والظلال الناعمة.',
            className: 'style-cinema4k'
        },
        gilded: {
            tag: 'طراز فني وتصميم إعلاني',
            title: 'تصميم إعلاني ثلاثي الأبعاد',
            desc: 'توليد تشكيلي إعلاني معاصر بإضاءة استوديو متقنة وتفاصيل فائقة الجودة.',
            className: 'style-gilded'
        }
    };

    function setStyle(styleKey) {
        styleChips.forEach(chip => {
            chip.classList.toggle('active', chip.dataset.style === styleKey);
        });

        if (visualArt && styleMeta[styleKey]) {
            visualArt.className = `preview-art-display ${styleMeta[styleKey].className}`;
            if (styleTag) styleTag.textContent = styleMeta[styleKey].tag;
            if (artTitle) artTitle.textContent = styleMeta[styleKey].title;
            if (artDesc) artDesc.textContent = styleMeta[styleKey].desc;
        }
    }

    presetBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            presetBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            if (promptInput) promptInput.value = btn.dataset.prompt;
            setStyle(btn.dataset.style);
        });
    });

    styleChips.forEach(chip => {
        chip.addEventListener('click', () => {
            setStyle(chip.dataset.style);
        });
    });

    if (generateBtn && loader) {
        generateBtn.addEventListener('click', () => {
            generateBtn.disabled = true;
            loader.style.display = 'flex';

            setTimeout(() => {
                loader.style.display = 'none';
                generateBtn.disabled = false;

                if (artTitle && promptInput && promptInput.value.trim()) {
                    artTitle.textContent = promptInput.value.trim().substring(0, 36) + '...';
                }

                if (latencyEl) {
                    const rnd = (Math.random() * 0.4 + 0.6).toFixed(2);
                    latencyEl.textContent = `${rnd} ثانية`;
                }

                if (visualArt) {
                    visualArt.style.transform = 'scale(0.98)';
                    setTimeout(() => {
                        visualArt.style.transform = 'scale(1)';
                    }, 180);
                }
            }, 750);
        });
    }
}

/* --------------------------------------------------------------------------
   8. Curated Showcase Gallery & Cinematic Modal
-------------------------------------------------------------------------- */
function initShowcaseGalleryAndModal() {
    const filterTabs = document.querySelectorAll('.filter-tab');
    const cards = document.querySelectorAll('.showcase-item-card');
    const modal = document.getElementById('showcase-modal');
    const closeBtn = document.getElementById('modal-close-btn');
    const modalTag = document.getElementById('modal-tag');
    const modalTitle = document.getElementById('modal-title');
    const modalViewport = document.getElementById('modal-viewport');

    filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            filterTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const filter = tab.dataset.filter;

            cards.forEach(card => {
                if (filter === 'all' || card.dataset.category === filter) {
                    card.style.display = 'flex';
                    card.style.opacity = '1';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });

    function openModalForCard(card) {
        if (!modal) return;
        const title = card.dataset.title || 'معاينة العمل';
        const badge = card.dataset.badge || 'عمل معالج بالذكاء الاصطناعي';
        const category = card.dataset.category;

        if (modalTitle) modalTitle.textContent = title;
        if (modalTag) modalTag.textContent = badge;

        if (modalViewport) {
            if (category === 'cinema') {
                modalViewport.innerHTML = `
                    <div class="modal-viewport-scene" style="background: radial-gradient(circle, rgba(212,175,55,0.2), #0B0705);">
                        <div style="font-size: 3rem; color: #D4AF37;">🎬</div>
                        <h4 style="font-size: 1.25rem; color: #FAF7F0;">معاينة البث السينمائي 4K UHD</h4>
                        <p style="font-size: 0.85rem; color: rgba(255,255,255,0.7); max-width: 480px;">
                            يتم سحب تدفق الفيديو من مستودع MinIO S3 المشفر بمعدل نقل 48 Mbps وبترميز HEVC / H.265.
                        </p>
                        <div style="width: 80%; height: 6px; background: rgba(255,255,255,0.15); border-radius: 3px; position: relative; margin-top: 10px;">
                            <div style="width: 65%; height: 100%; background: #D4AF37; border-radius: 3px;"></div>
                        </div>
                    </div>
                `;
            } else if (category === 'audio') {
                modalViewport.innerHTML = `
                    <div class="modal-viewport-scene" style="background: radial-gradient(circle, rgba(46,204,113,0.2), #0B0705);">
                        <div style="font-size: 3rem; color: #4ADE80;">🎙️</div>
                        <h4 style="font-size: 1.25rem; color: #FAF7F0;">مشغل الأكوستيك والصوتيات النقي</h4>
                        <div class="audio-mini-bars" style="position: static; height: 36px; gap: 6px; margin: 8px 0;">
                            <span style="width: 5px; height: 70%;"></span>
                            <span style="width: 5px; height: 100%;"></span>
                            <span style="width: 5px; height: 50%;"></span>
                            <span style="width: 5px; height: 90%;"></span>
                            <span style="width: 5px; height: 40%;"></span>
                            <span style="width: 5px; height: 80%;"></span>
                            <span style="width: 5px; height: 60%;"></span>
                        </div>
                        <p style="font-size: 0.85rem; color: #C5A059;">48kHz • 24-bit Lossless Studio Master</p>
                    </div>
                `;
            } else {
                modalViewport.innerHTML = `
                    <div class="modal-viewport-scene" style="background: radial-gradient(circle, rgba(197,160,89,0.3), #0B0705);">
                        <div style="font-size: 3rem; color: #C5A059;">۞</div>
                        <h4 style="font-size: 1.25rem; color: #FAF7F0;">التشكيل البصري عالي الدقة</h4>
                        <p style="font-size: 0.85rem; color: rgba(255,255,255,0.7); max-width: 480px;">
                            دقة 3840×2160 معززة بنموذج استكمال التفاصيل الدقيقة وحفظ ألوان ورق البردي والذهب.
                        </p>
                    </div>
                `;
            }
        }

        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    cards.forEach(card => {
        const trigger = card.querySelector('.btn-preview-trigger');
        if (trigger) {
            trigger.addEventListener('click', (e) => {
                e.stopPropagation();
                openModalForCard(card);
            });
        }
        card.addEventListener('click', () => {
            openModalForCard(card);
        });
    });

    function closeModal() {
        if (!modal) return;
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (closeBtn) closeBtn.addEventListener('click', closeModal);

    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });
    }

    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal && modal.classList.contains('active')) {
            closeModal();
        }
    });
}

/* --------------------------------------------------------------------------
   9. Credits & Pricing Calculator Engine
-------------------------------------------------------------------------- */
function initCreditsCalculator() {
    const sliderVideo = document.getElementById('slider-video');
    const sliderAudio = document.getElementById('slider-audio');
    const sliderImage = document.getElementById('slider-image');

    const numVideo = document.getElementById('val-video-num');
    const numAudio = document.getElementById('val-audio-num');
    const numImage = document.getElementById('val-image-num');

    const totalCreditsEl = document.getElementById('calc-total-credits');
    const tierNameEl = document.getElementById('calc-tier-name');
    const priceUsdEl = document.getElementById('calc-price-usd');
    const priceSarEl = document.getElementById('calc-price-sar');

    if (!sliderVideo || !sliderAudio || !sliderImage) return;

    function recalculate() {
        const videoMin = parseInt(sliderVideo.value, 10);
        const audioHours = parseInt(sliderAudio.value, 10);
        const images = parseInt(sliderImage.value, 10);

        if (numVideo) numVideo.textContent = videoMin;
        if (numAudio) numAudio.textContent = audioHours;
        if (numImage) numImage.textContent = images;

        const totalCredits = (videoMin * 35) + (audioHours * 15) + (images * 1);

        if (totalCreditsEl) {
            totalCreditsEl.textContent = totalCredits.toLocaleString();
        }

        let tierName = 'باقة الحكمة (Starter)';
        let priceUsd = 29;
        let priceSar = 109;

        if (totalCredits > 2200) {
            tierName = 'باقة السيادة (Enterprise AI)';
            priceUsd = 149;
            priceSar = 559;
        } else if (totalCredits > 700) {
            tierName = 'باقة الأندلس (Studio Pro)';
            priceUsd = 69;
            priceSar = 259;
        }

        if (tierNameEl) tierNameEl.textContent = tierName;
        if (priceUsdEl) priceUsdEl.textContent = priceUsd;
        if (priceSarEl) priceSarEl.textContent = `~ ${priceSar} ريال سعودي`;
    }

    sliderVideo.addEventListener('input', recalculate);
    sliderAudio.addEventListener('input', recalculate);
    sliderImage.addEventListener('input', recalculate);

    recalculate();
}

/* --------------------------------------------------------------------------
   10. Instant Bilingual Language Switcher (AR/EN)
-------------------------------------------------------------------------- */
function initLanguageSwitcher() {
    const langBtn = document.getElementById('lang-toggle-btn');
    if (!langBtn) return;

    let currentLang = 'ar';

    const translations = {
        ar: {
            title: 'إِشْرَاقُ البَصَرِيَّاتِ وَالصَّوْتِيَّاتِ',
            desc: 'المنصة السيادية الأولى لتوحيد وتطوير نماذج الصوتيات والفيديو والصور فائقة الدقة، مستلهمة من عراقة بيت الحكمة وعلوم ابن الهيثم في البصريات والفارابي في الأكوستيك.',
            btnCta: 'ابدأ رحلتك مجاناً',
            btnExplore: 'استكشف البوابات الثلاث'
        },
        en: {
            title: 'THE ALCHEMY OF SIGHT, SOUND & CINEMA',
            desc: 'The premier sovereign studio unifying cutting-edge generative neural models for 4K video, lossless acoustic engineering, and fine visual synthesis.',
            btnCta: 'Start Sovereign Trial',
            btnExplore: 'Explore 3 Portals'
        }
    };

    langBtn.addEventListener('click', () => {
        currentLang = currentLang === 'ar' ? 'en' : 'ar';

        document.documentElement.lang = currentLang;
        document.documentElement.dir = currentLang === 'ar' ? 'rtl' : 'ltr';

        langBtn.querySelectorAll('.lang-badge').forEach(badge => {
            badge.classList.toggle('active', badge.dataset.lang === currentLang);
        });

        const calligraphyTitle = document.querySelector('.hero-arabic-calligraphy');
        const heroDesc = document.querySelector('.hero-description');
        const mainCta = document.getElementById('hero-main-cta');
        const exploreBtn = document.getElementById('hero-explore-btn');

        if (calligraphyTitle) calligraphyTitle.textContent = translations[currentLang].title;
        if (heroDesc) heroDesc.textContent = translations[currentLang].desc;
        if (mainCta && mainCta.querySelector('span')) mainCta.querySelector('span').textContent = translations[currentLang].btnCta;
        if (exploreBtn && exploreBtn.querySelector('span')) exploreBtn.querySelector('span').textContent = translations[currentLang].btnExplore;
    });
}

/* --------------------------------------------------------------------------
   11. Synthesized Web Audio Haptic Sound Effects (Golden Chimes)
-------------------------------------------------------------------------- */
let audioCtx = null;
let soundFXEnabled = false;

function playGoldenChime(freq = 587.33, duration = 0.35, type = 'sine') {
    if (!soundFXEnabled) return;
    try {
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        if (!AudioContextClass) return;

        if (!audioCtx) {
            audioCtx = new AudioContextClass();
        }
        if (audioCtx.state === 'suspended') {
            audioCtx.resume();
        }

        const now = audioCtx.currentTime;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();

        osc.type = type;
        osc.frequency.setValueAtTime(freq, now);
        osc.frequency.exponentialRampToValueAtTime(freq * 0.98, now + duration);

        gain.gain.setValueAtTime(0.001, now);
        gain.gain.linearRampToValueAtTime(0.12, now + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);

        osc.connect(gain);
        gain.connect(audioCtx.destination);

        osc.start(now);
        osc.stop(now + duration);
    } catch (e) {
        // Fallback gracefully if Web Audio is unsupported or blocked
    }
}

function initSoundFX() {
    const toggleBtn = document.getElementById('sound-fx-toggle');
    if (!toggleBtn) return;

    const iconOff = toggleBtn.querySelector('.icon-sound-off');
    const iconOn = toggleBtn.querySelector('.icon-sound-on');
    const label = document.getElementById('sound-toggle-label');

    toggleBtn.addEventListener('click', () => {
        soundFXEnabled = !soundFXEnabled;
        toggleBtn.classList.toggle('active', soundFXEnabled);

        if (iconOff) iconOff.style.display = soundFXEnabled ? 'none' : 'inline-block';
        if (iconOn) iconOn.style.display = soundFXEnabled ? 'inline-block' : 'none';
        if (label) label.textContent = soundFXEnabled ? 'النغمات: نشطة' : 'النغمات: مكتومة';

        if (soundFXEnabled) {
            playGoldenChime(659.25, 0.4, 'triangle'); // E5 chime
            setTimeout(() => playGoldenChime(880, 0.35, 'sine'), 120); // A5 harmonic
        }
    });

    // Attach soft micro-interactions to key buttons and chips
    const interactiveSelectors = [
        '.btn-royal-forest',
        '.btn-royal-outline',
        '.style-chip',
        '.playground-tab',
        '.btn-ghost',
        '#pipeline-start-btn',
        '#audio-play-toggle',
        '.gallery-item',
        '.studio-badge-item'
    ];

    document.querySelectorAll(interactiveSelectors.join(', ')).forEach(el => {
        el.addEventListener('click', () => {
            if (soundFXEnabled) {
                playGoldenChime(523.25, 0.25, 'sine'); // C5 tone
            }
        });
    });

    // Slider audio micro-feedback
    const sliders = [
        document.getElementById('slider-video'), 
        document.getElementById('slider-audio'), 
        document.getElementById('slider-image')
    ];
    sliders.forEach(slider => {
        if (slider) {
            slider.addEventListener('input', () => {
                if (soundFXEnabled && Math.random() > 0.6) {
                    playGoldenChime(784, 0.08, 'sine'); // G5 subtle blip
                }
            });
        }
    });
}

/* --------------------------------------------------------------------------
   12. Mobile Drawer Navigation
-------------------------------------------------------------------------- */
function initMobileDrawer() {
    const mobileBtn = document.getElementById('mobile-menu-btn');
    const drawer = document.getElementById('mobile-drawer');
    const closeBtn = document.getElementById('drawer-close-btn');
    if (!mobileBtn || !drawer) return;

    function openDrawer() {
        drawer.classList.add('open');
        drawer.setAttribute('aria-hidden', 'false');
    }

    function closeDrawer() {
        drawer.classList.remove('open');
        drawer.setAttribute('aria-hidden', 'true');
    }

    mobileBtn.addEventListener('click', openDrawer);
    if (closeBtn) closeBtn.addEventListener('click', closeDrawer);

    // Close when clicking nav items inside drawer
    drawer.querySelectorAll('.drawer-nav-item').forEach(item => {
        item.addEventListener('click', closeDrawer);
    });
}

/* --------------------------------------------------------------------------
   13. Hero Neural Waveform & Cinema Player Animation
-------------------------------------------------------------------------- */
function initHeroNeuralPlayer() {
    const canvas = document.getElementById('hero-neural-waveform');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const playBtn = document.getElementById('hero-player-play-btn');
    const iconPlay = playBtn ? playBtn.querySelector('.icon-play-hero') : null;
    const iconPause = playBtn ? playBtn.querySelector('.icon-pause-hero') : null;

    let isPlaying = true;
    let phase = 0;
    let animId = null;

    function renderWaveform() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const width = canvas.width;
        const height = canvas.height;
        const centerY = height / 2;
        const barsCount = 56;
        const barWidth = 4;
        const gap = (width - 24) / barsCount;

        for (let i = 0; i < barsCount; i++) {
            const x = 12 + i * gap;
            
            // Harmonic multi-frequency oscillation
            let amp = 8;
            if (isPlaying) {
                const s1 = Math.sin(phase + i * 0.3) * 26;
                const s2 = Math.cos(phase * 1.4 + i * 0.18) * 16;
                const s3 = Math.sin(phase * 0.8 - i * 0.45) * 10;
                amp = Math.max(Math.abs(s1 + s2 + s3), 6);
            } else {
                amp = Math.sin(i * 0.28) * 12 + 6;
            }

            // Tri-color gradient matching the generated mockup: Emerald Green -> Gold -> Cyan
            let barColor = '#2ECC71';
            if (i < 18) {
                barColor = '#2ECC71'; // Forest Emerald
            } else if (i < 38) {
                barColor = '#D4AF37'; // Andalusian Gold
            } else {
                barColor = '#3498DB'; // Sapphire Azure
            }

            ctx.fillStyle = barColor;
            ctx.shadowBlur = isPlaying ? 8 : 2;
            ctx.shadowColor = barColor;

            ctx.beginPath();
            ctx.roundRect(x, centerY - amp / 2, barWidth, amp, 2);
            ctx.fill();
        }

        if (isPlaying) {
            phase += 0.055;
            animId = requestAnimationFrame(renderWaveform);
        }
    }

    renderWaveform();

    if (playBtn) {
        playBtn.addEventListener('click', () => {
            isPlaying = !isPlaying;
            if (iconPlay) iconPlay.style.display = isPlaying ? 'none' : 'inline-block';
            if (iconPause) iconPause.style.display = isPlaying ? 'inline-block' : 'none';

            if (isPlaying) {
                renderWaveform();
            }
        });
    }
}



