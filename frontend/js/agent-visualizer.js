/**
 * BlueprintAI Agent Pipeline Visualizer
 * Manages the visual state of each agent node (BA, PM, QA, Synthesis)
 * and animates progress transition lines.
 */
class AgentVisualizer {
    constructor() {
        this.nodes = {
            ba: document.getElementById('node-ba'),
            pm: document.getElementById('node-pm'),
            qa: document.getElementById('node-qa'),
            syn: document.getElementById('node-syn')
        };
        
        this.statuses = {
            ba: document.getElementById('status-ba'),
            pm: document.getElementById('status-pm'),
            qa: document.getElementById('status-qa'),
            syn: document.getElementById('status-syn')
        };
        
        this.progressBar = document.getElementById('pipeline-progress');
    }

    reset() {
        for (const key in this.nodes) {
            this.nodes[key].className = `pipeline-vertical-node ${key}`;
            this.statuses[key].textContent = 'Idle';
        }
        if (this.progressBar) {
            this.progressBar.style.height = '0%';
        }
    }

    setAgentState(agent, state) {
        // state can be: 'idle', 'active', 'done'
        const node = this.nodes[agent];
        const statusEl = this.statuses[agent];
        if (!node) return;
        
        // Remove existing state classes
        node.classList.remove('active', 'done');
        
        if (state === 'active') {
            node.classList.add('active');
            statusEl.textContent = 'Running...';
            this._updateProgressBar(agent, 'active');
        } else if (state === 'done') {
            node.classList.add('done');
            statusEl.textContent = 'Complete';
            this._updateProgressBar(agent, 'done');
        } else {
            statusEl.textContent = 'Idle';
        }
    }

    _updateProgressBar(agent, state) {
        if (!this.progressBar) return;
        
        let percentage = '0%';
        if (agent === 'ba') {
            percentage = state === 'active' ? '12.5%' : '25%';
        } else if (agent === 'pm') {
            percentage = state === 'active' ? '37.5%' : '50%';
        } else if (agent === 'qa') {
            percentage = state === 'active' ? '62.5%' : '75%';
        } else if (agent === 'syn') {
            percentage = state === 'active' ? '87.5%' : '100%';
        }
        
        this.progressBar.style.height = percentage;
    }
}

// Make it available on window
window.AgentVisualizer = AgentVisualizer;
