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
    let tsParticles;

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

    async function handleImport() {
        if (!confirm("Voulez-vous vraiment importer les données ? Cela écrasera les données actuelles.")) return;
        
        try {
            const response = await fetch(`${API_BASE_URL}/import`, { method: 'POST' });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'Failed to import data');
            
            alert(result.message);
            await updateStats();
        } catch (error) {
            console.error('Import failed:', error);
            alert(`Erreur lors de l'import : ${error.message}`);
        }
    }

    async function handleReset() {
        if (!confirm("Voulez-vous vraiment réinitialiser le parrainage ? Toutes les paires seront effacées.")) return;
        
        try {
            const response = await fetch(`${API_BASE_URL}/reset`, { method: 'POST' });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'Failed to reset');

            alert(result.message);
            parrainInfo.innerHTML = '';
            filleulInfo.innerHTML = '';
            await updateStats();
        } catch (error) {
            console.error('Reset failed:', error);
            alert(`Erreur lors de la réinitialisation : ${error.message}`);
        }
    }

    async function handleUndo() {
        if (!confirm("Voulez-vous vraiment annuler le dernier tirage ?")) return;
        
        try {
            const response = await fetch(`${API_BASE_URL}/undo`, { method: 'POST' });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'Failed to undo');
            
            alert(result.message);
            parrainInfo.innerHTML = '';
            filleulInfo.innerHTML = '';
            await updateStats();
        } catch (error) {
            console.error('Undo failed:', error);
            alert(`Erreur lors de l'annulation : ${error.message}`);
        }
    }
    
    async function handleDraw() {
        drawBtn.disabled = true;
        parrainInfo.textContent = '...';
        filleulInfo.textContent = '...';
        try {
            const response = await fetch(`${API_BASE_URL}/draw`);
            const result = await response.json();

            if (!response.ok) {
                // Handle "no more students" message gracefully
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
            // The button will be re-enabled by updateStats if applicable
        }
    }

    function displayPair(pair) {
        parrainInfo.innerHTML = `<span>${pair.parrain.prenom} ${pair.parrain.nom}</span><small>${pair.parrain.promotion}</small>`;
        filleulInfo.innerHTML = `<span>${pair.filleul.prenom} ${pair.filleul.nom}</span><small>${pair.filleul.promotion}</small>`;
    }

    function triggerAnimation() {
        const parrainRect = parrainCard.getBoundingClientRect();
        const filleulRect = filleulCard.getBoundingClientRect();

        const burstOptions = {
            count: 20,
            spread: 40,
            startVelocity: 30,
            angle: 90
        };
        
        // Emitter for Parrain
        tsParticles.addEmitter({
            position: {
                x: ((parrainRect.left + parrainRect.right) / 2) * 100 / window.innerWidth,
                y: ((parrainRect.top + parrainRect.bottom) / 2) * 100 / window.innerHeight,
            },
            size: {
                width: 10,
                height: 10
            },
            life: {
                duration: 0.2,
                count: 1
            },
            particles: {
                move: {
                    speed: {min: 5, max: 10}
                }
            }
        });
        
        // Emitter for Filleul
        tsParticles.addEmitter({
            position: {
                x: ((filleulRect.left + filleulRect.right) / 2) * 100 / window.innerWidth,
                y: ((filleulRect.top + filleulRect.bottom) / 2) * 100 / window.innerHeight,
            },
            size: {
                width: 10,
                height: 10
            },
            life: {
                duration: 0.2,
                count: 1
            },
            particles: {
                move: {
                    speed: {min: 5, max: 10}
                }
            }
        });
    }

    async function initParticles() {
        if(window.tsParticles) {
            await tsParticles.load({
                id: "particles-js",
                options: { /* ... existing particle options ... */ }
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