/**
 * BlueprintAI Application Controller
 * Hooks UI elements, manages tabs, performs async POST SSE streams,
 * and communicates with history endpoints.
 */
document.addEventListener('DOMContentLoaded', () => {
    // Instantiate helpers
    const visualizer = new window.AgentVisualizer();
    const renderer = new window.MarkdownRenderer();

    // DOM Elements
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const historyList = document.getElementById('history-list');
    
    const promptInput = document.getElementById('prompt-input');
    const industrySelect = document.getElementById('industry-select');
    const generateBtn = document.getElementById('generate-btn');
    
    const statusBanner = document.getElementById('status-banner');
    const statusText = document.getElementById('pipeline-status-text');
    const statusSpinner = document.getElementById('status-spinner');
    
    const exportActions = document.getElementById('export-actions');
    const exportMdBtn = document.getElementById('export-md-btn');
    const exportPdfBtn = document.getElementById('export-pdf-btn');
    
    const tabBtns = document.querySelectorAll('.tab-btn');
    const panels = {
        'panel-ba': document.getElementById('panel-ba'),
        'panel-pm': document.getElementById('panel-pm'),
        'panel-qa': document.getElementById('panel-qa'),
        'panel-final': document.getElementById('panel-final')
    };

    // State Variables
    let activeGeneration = {
        ba: "",
        pm: "",
        qa: "",
        final: ""
    };
    let activeProjectId = null;
    let isGenerating = false;

    // 1. Sidebar Toggle Action
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });

    const collapsedIndicator = document.getElementById('sidebar-collapsed-indicator');
    if (collapsedIndicator) {
        collapsedIndicator.addEventListener('click', () => {
            sidebar.classList.remove('collapsed');
        });
    }


    // 2. Tab Switching Action
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.getAttribute('data-target');
            
            // Toggle active tabs
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Toggle active panels
            for (const key in panels) {
                panels[key].classList.remove('active');
            }
            if (panels[target]) {
                panels[target].classList.add('active');
            }
        });
    });

    // Helper to switch active panel programmatically
    function switchTab(targetPanelId) {
        const targetBtn = Array.from(tabBtns).find(btn => btn.getAttribute('data-target') === targetPanelId);
        if (targetBtn) {
            targetBtn.click();
        }
    }

    // 3. Load Session History
    async function loadHistory() {
        try {
            const response = await fetch('/api/history');
            if (!response.ok) throw new Error("Failed to load history");
            
            const history = await response.json();
            historyList.innerHTML = "";
            
            if (history.length === 0) {
                historyList.innerHTML = `
                    <div style="color: var(--color-text-muted); font-size: 13px; text-align: center; padding: 20px;">
                        No history found
                    </div>
                `;
                return;
            }
            
            history.forEach(item => {
                const date = new Date(item.timestamp * 1000).toLocaleDateString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                
                const itemEl = document.createElement('div');
                itemEl.className = `history-item ${activeProjectId === item.project_id ? 'active' : ''}`;
                itemEl.innerHTML = `
                    <div class="history-item-prompt" title="${item.prompt}">${item.prompt}</div>
                    <div class="history-item-meta">
                        <span>${item.industry}</span>
                        <span>${date}</span>
                    </div>
                `;
                
                itemEl.addEventListener('click', () => loadHistoryDetail(item.project_id));
                historyList.appendChild(itemEl);
            });
        } catch (e) {
            console.error("Error loading history:", e);
        }
    }

    // 4. Load Specific Generation Detail
    async function loadHistoryDetail(projectId) {
        if (isGenerating) return;
        
        activeProjectId = projectId;
        
        // Highlight active sidebar item
        document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));
        
        try {
            const response = await fetch(`/api/history/${projectId}`);
            if (!response.ok) throw new Error("Failed to load history details");
            
            const data = await response.json();
            
            // Set active states
            activeGeneration.ba = data.ba;
            activeGeneration.pm = data.pm;
            activeGeneration.qa = data.qa;
            activeGeneration.final = data.final;
            
            // Render all panels
            panels['panel-ba'].innerHTML = renderer.renderBAJson(data.ba);
            panels['panel-pm'].innerHTML = renderer.renderMarkdown(data.pm);
            panels['panel-qa'].innerHTML = renderer.renderMarkdown(data.qa);
            panels['panel-final'].innerHTML = renderer.renderMarkdown(data.final);
            
            // Set all nodes to complete
            visualizer.reset();
            visualizer.setAgentState('ba', 'done');
            visualizer.setAgentState('pm', 'done');
            visualizer.setAgentState('qa', 'done');
            visualizer.setAgentState('syn', 'done');
            
            // Show status completed
            statusBanner.style.display = 'flex';
            statusText.textContent = "Loaded from history database.";
            statusSpinner.style.display = 'none';
            exportActions.style.display = 'flex';
            
            // Set inputs
            promptInput.value = data.prompt;
            industrySelect.value = data.industry;
            
            // Go to final document tab
            switchTab('panel-final');
            
            // Reload history to refresh active tags
            loadHistory();
            
        } catch (e) {
            alert("Error loading details: " + e.message);
        }
    }

    // 5. Trigger Multi-Agent Pipeline (SSE)
    async function generatePRD() {
        const prompt = promptInput.value.trim();
        const industry = industrySelect.value;
        
        if (!prompt) {
            alert("Please describe your product idea first!");
            return;
        }

        // Lock UI controls
        isGenerating = true;
        generateBtn.disabled = true;
        visualizer.reset();
        activeProjectId = null;
        
        activeGeneration.ba = "";
        activeGeneration.pm = "";
        activeGeneration.qa = "";
        activeGeneration.final = "";
        
        panels['panel-ba'].innerHTML = `<div style="padding: 10px; color: var(--color-ba);">Preparing Business Analyst environment...</div>`;
        panels['panel-pm'].innerHTML = `<div style="padding: 10px; color: var(--color-pm);">Waiting for Business Analyst stage completion...</div>`;
        panels['panel-qa'].innerHTML = `<div style="padding: 10px; color: var(--color-qa);">Waiting for Product Manager stage completion...</div>`;
        panels['panel-final'].innerHTML = `<div style="padding: 10px; color: var(--color-primary);">Waiting for Pipeline Synthesis...</div>`;
        
        statusBanner.style.display = 'flex';
        statusText.textContent = "Initializing multi-agent pipeline...";
        statusSpinner.style.display = 'block';
        exportActions.style.display = 'none';
        
        switchTab('panel-ba');

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt, industry })
            });

            if (!response.ok) {
                throw new Error("HTTP error starting generation. Make sure server is running.");
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n");
                buffer = lines.pop(); // Keep partial line in buffer

                for (const line of lines) {
                    const trimmedLine = line.trim();
                    if (!trimmedLine.startsWith("data: ")) continue;
                    
                    const dataStr = trimmedLine.slice(6).trim();
                    if (!dataStr) continue;

                    try {
                        const eventData = JSON.parse(dataStr);
                        processSSEEvent(eventData);
                    } catch (e) {
                        console.error("SSE parse error", e, dataStr);
                    }
                }
            }

        } catch (e) {
            statusText.textContent = `Error: ${e.message}`;
            statusSpinner.style.display = 'none';
            isGenerating = false;
            generateBtn.disabled = false;
        }
    }

    // 6. Handle SSE events
    function processSSEEvent(data) {
        const { event, text, project_id } = data;
        
        switch (event) {
            case 'status':
                statusText.textContent = text;
                break;
                
            case 'ba_start':
                visualizer.setAgentState('ba', 'active');
                panels['panel-ba'].innerHTML = "";
                switchTab('panel-ba');
                break;
                
            case 'ba_chunk':
                activeGeneration.ba += text;
                panels['panel-ba'].textContent = activeGeneration.ba; // Keep simple text while streaming
                break;
                
            case 'ba_done':
                visualizer.setAgentState('ba', 'done');
                activeGeneration.ba = text;
                panels['panel-ba'].innerHTML = renderer.renderBAJson(text); // Beautiful formatting when done
                break;
                
            case 'pm_start':
                visualizer.setAgentState('pm', 'active');
                panels['panel-pm'].innerHTML = "";
                switchTab('panel-pm');
                break;
                
            case 'pm_chunk':
                activeGeneration.pm += text;
                panels['panel-pm'].innerHTML = renderer.renderMarkdown(activeGeneration.pm);
                break;
                
            case 'pm_done':
                visualizer.setAgentState('pm', 'done');
                activeGeneration.pm = text;
                panels['panel-pm'].innerHTML = renderer.renderMarkdown(text);
                break;
                
            case 'qa_start':
                visualizer.setAgentState('qa', 'active');
                panels['panel-qa'].innerHTML = "";
                switchTab('panel-qa');
                break;
                
            case 'qa_chunk':
                activeGeneration.qa += text;
                panels['panel-qa'].innerHTML = renderer.renderMarkdown(activeGeneration.qa);
                break;
                
            case 'qa_done':
                visualizer.setAgentState('qa', 'done');
                activeGeneration.qa = text;
                panels['panel-qa'].innerHTML = renderer.renderMarkdown(text);
                break;
                
            case 'syn_start':
                visualizer.setAgentState('syn', 'active');
                panels['panel-final'].innerHTML = "";
                switchTab('panel-final');
                break;
                
            case 'syn_chunk':
                activeGeneration.final += text;
                panels['panel-final'].innerHTML = renderer.renderMarkdown(activeGeneration.final);
                break;
                
            case 'syn_done':
                visualizer.setAgentState('syn', 'done');
                activeGeneration.final = text;
                panels['panel-final'].innerHTML = renderer.renderMarkdown(text);
                break;
                
            case 'done':
                isGenerating = false;
                generateBtn.disabled = false;
                statusSpinner.style.display = 'none';
                statusText.textContent = "Pipeline execution completed successfully.";
                exportActions.style.display = 'flex';
                activeProjectId = project_id;
                loadHistory();
                break;
                
            case 'error':
                statusText.textContent = `Error: ${text}`;
                statusSpinner.style.display = 'none';
                isGenerating = false;
                generateBtn.disabled = false;
                break;
        }
    }

    // 7. Button Listeners
    generateBtn.addEventListener('click', generatePRD);
    
    exportMdBtn.addEventListener('click', () => {
        const safeName = (promptInput.value.trim() || 'product').toLowerCase().replace(/[^a-z0-9]+/g, '_');
        window.ExportHandler.downloadMarkdown(`${safeName}_prd.md`, activeGeneration.final);
    });
    
    exportPdfBtn.addEventListener('click', () => {
        window.ExportHandler.exportPDF();
    });

    // 8. Init calls
    loadHistory();
});
