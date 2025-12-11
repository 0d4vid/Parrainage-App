document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const importBtn = document.getElementById('import-btn');
    const resetBtn = document.getElementById('reset-btn');
    const undoBtn = document.getElementById('undo-btn');
    const drawBtn = document.getElementById('draw-btn');
    
    const parrainCard = document.getElementById('parrain-card');
    const filleulCard = document.getElementById('filleul-card');
    const parrainInfo = document.getElementById('parrain-info');
    const filleulInfo = document.getElementById('filleul-info');

    const parrainsCountSpan = document.getElementById('parrains-count');
    const filleulsCountSpan = document.getElementById('filleuls-count');

    // --- API Configuration ---
    const API_BASE_URL = 'http://127.0.0.1:5000/api';

    // --- State ---
    let particlesContainer;

    // --- Functions ---

    async function updateStats() {
        try {
            const response = await fetch(`${API_BASE_URL}/stats`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            parrainsCountSpan.textContent = data.available_parrains ?? '--';
            filleulsCountSpan.textContent = data.remaining_filleuls ?? '--';

            drawBtn.disabled = data.remaining_filleuls === 0;
        } catch (error) {
            console.error('Failed to fetch stats:', error);
            parrainsCountSpan.textContent = 'Erreur';
            filleulsCountSpan.textContent = 'Erreur';
        }
    }

    async function handleApiPost(url, confirmMessage) {
        if (!confirm(confirmMessage)) return;
        
        try {
            const response = await fetch(url, { method: 'POST' });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'Request failed');
            
            alert(result.message);
            parrainInfo.innerHTML = '';
            filleulInfo.innerHTML = '';
            await updateStats();
        } catch (error) {
            console.error('API POST Error:', error);
            alert(`Erreur : ${error.message}`);
        }
    }

    const handleImport = () => handleApiPost(`${API_BASE_URL}/import`, "Voulez-vous vraiment importer les données ? Cela écrasera les données actuelles.");
    const handleReset = () => handleApiPost(`${API_BASE_URL}/reset`, "Voulez-vous vraiment réinitialiser le parrainage ? Toutes les paires seront effacées.");
    const handleUndo = () => handleApiPost(`${API_BASE_URL}/undo`, "Voulez-vous vraiment annuler le dernier tirage ?");

    async function handleDraw() {
        drawBtn.disabled = true;
        parrainInfo.textContent = '...';
        filleulInfo.textContent = '...';
        try {
            const response = await fetch(`${API_BASE_URL}/draw`);
            const result = await response.json();

            if (!response.ok) {
                if(response.status === 404) {
                    alert(result.message || 'Action impossible.');
                    parrainInfo.innerHTML = '';
                    filleulInfo.innerHTML = '';
                } else {
                    throw new Error(result.error || 'Failed to draw a pair');
                }
            } else {
                displayPair(result);
                triggerAnimation();
            }
            
            await updateStats();
        } catch (error) {
            console.error('Draw failed:', error);
            alert(`Erreur lors du tirage : ${error.message}`);
        } finally {
            // The button's state is managed by updateStats()
        }
    }

    function displayPair(pair) {
        parrainInfo.innerHTML = `<span>${pair.parrain.prenom} ${pair.parrain.nom}</span><small>${pair.parrain.promotion}</small>`;
        filleulInfo.innerHTML = `<span>${pair.filleul.prenom} ${pair.filleul.nom}</span><small>${pair.filleul.promotion}</small>`;
    }

    function triggerAnimation() {
        if (!particlesContainer) return;

        const parrainRect = parrainCard.getBoundingClientRect();
        const filleulRect = filleulCard.getBoundingClientRect();

        const emitterOptions = {
            life: {
                duration: 0.2,
                count: 1
            },
            particles: {
                move: {
                    speed: {min: 5, max: 10}
                }
            }
        };

        particlesContainer.addEmitter({
            ...emitterOptions,
            position: {
                x: ((parrainRect.left + parrainRect.right) / 2) * 100 / window.innerWidth,
                y: ((parrainRect.top + parrainRect.bottom) / 2) * 100 / window.innerHeight,
            }
        });
        
        particlesContainer.addEmitter({
            ...emitterOptions,
            position: {
                x: ((filleulRect.left + filleulRect.right) / 2) * 100 / window.innerWidth,
                y: ((filleulRect.top + filleulRect.bottom) / 2) * 100 / window.innerHeight,
            }
        });
    }

    async function initParticles() {
        if(window.tsParticles) {
            particlesContainer = await tsParticles.load({
                id: "particles-js",
                options: {
                    background: { color: { value: "transparent" } },
                    fpsLimit: 60,
                    particles: {
                        number: { value: 50, density: { enable: true, area: 800 } },
                        color: { value: "#FF851B" },
                        shape: { type: "circle" },
                        opacity: { value: { min: 0.1, max: 0.5 } },
                        size: { value: { min: 1, max: 3 } },
                        move: {
                            enable: true,
                            speed: 1,
                            direction: "none",
                            outModes: "out"
                        }
                    },
                    interactivity: {
                        events: { onHover: { enable: true, mode: "repulse" } },
                        modes: { repulse: { distance: 100 } }
                    },
                    detectRetina: true
                }
            });
        }
    }

    // --- Event Listeners ---
    importBtn.addEventListener('click', handleImport);
    resetBtn.addEventListener('click', handleReset);
    undoBtn.addEventListener('click', handleUndo);
    drawBtn.addEventListener('click', handleDraw);

    // --- Initial Load ---
    updateStats();
    initParticles();
});
