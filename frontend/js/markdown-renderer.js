/**
 * BlueprintAI Markdown and JSON Renderer
 * Renders markdown via marked.js and formats BA JSON into rich card dashboards.
 * Handles both JSON (mock mode) and plain markdown (Ollama mode) for BA panel.
 */
class MarkdownRenderer {
    constructor() {
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                breaks: true,
                gfm: true
            });
        }
    }

    renderMarkdown(text) {
        if (!text || !text.trim()) return '';
        if (typeof marked === 'undefined') {
            return `<pre>${this.escapeHtml(text)}</pre>`;
        }
        const html = marked.parse(text);
        // Convert <code class="language-mermaid"> blocks → <div class="mermaid"> blocks
        // so Mermaid.js can pick them up and render as SVG diagrams
        return html.replace(
            /<pre><code class="language-mermaid">([\s\S]*?)<\/code><\/pre>/gi,
            (match, code) => {
                const decoded = code
                    .replace(/&amp;/g, '&')
                    .replace(/&lt;/g, '<')
                    .replace(/&gt;/g, '>')
                    .replace(/&quot;/g, '"')
                    .replace(/&#039;/g, "'");
                return `<div class="mermaid-wrapper"><div class="mermaid">${decoded}</div></div>`;
            }
        );
    }

    /**
     * Render markdown into a DOM element AND trigger Mermaid diagram rendering.
     * Call this instead of setting innerHTML manually when Mermaid diagrams may be present.
     */
    renderInto(element, text) {
        if (!element) return;
        element.innerHTML = this.renderMarkdown(text);
        this._renderMermaidInElement(element);
    }

    /**
     * Find all .mermaid divs inside a container and run Mermaid rendering on them.
     */
    async _renderMermaidInElement(container) {
        if (typeof mermaid === 'undefined') return;
        const diagrams = container.querySelectorAll('.mermaid');
        if (!diagrams.length) return;
        try {
            await mermaid.run({ nodes: diagrams });
        } catch (e) {
            console.warn('[Mermaid] Render error:', e);
        }
    }

    /**
     * Smart renderer for the Business Analyst panel.
     * Tries JSON card layout first, falls back to rich markdown.
     */
    renderBAOutput(text) {
        if (!text || !text.trim()) return '';
        
        // Try parsing as JSON first (mock mode)
        try {
            let cleaned = text.trim();
            if (cleaned.startsWith('```json')) {
                cleaned = cleaned.replace(/^```json\s*/, '').replace(/\s*```$/, '').trim();
            } else if (cleaned.startsWith('```')) {
                cleaned = cleaned.replace(/^```\s*/, '').replace(/\s*```$/, '').trim();
            }
            
            // Only attempt JSON parse if it looks like an object
            if (cleaned.startsWith('{')) {
                const data = JSON.parse(cleaned);
                // Validate required BA fields
                if (data.problem_statement && data.market_size) {
                    return this._renderBACards(data);
                }
            }
        } catch (e) {
            // Not JSON — fall through to markdown
        }

        // Fallback: render as rich markdown
        return this.renderMarkdown(text);
    }

    /**
     * Renders BA JSON data as a gorgeous card dashboard.
     */
    _renderBACards(data) {
        const ps = data.problem_statement || {};
        const ms = data.market_size || {};
        const metrics = Array.isArray(data.success_metrics) ? data.success_metrics : [];
        const competitors = Array.isArray(data.competitors) ? data.competitors : [];
        const rm = data.revenue_model || {};
        const assumptions = Array.isArray(data.key_assumptions) ? data.key_assumptions : [];

        // Parse market values
        const tamParts = this._parseMarketValue(ms.tam || '');
        const samParts = this._parseMarketValue(ms.sam || '');
        const somParts = this._parseMarketValue(ms.som || '');

        return `
<div class="ba-dashboard">
    <div class="ba-dashboard-title">Market &amp; Business Analysis</div>

    <!-- Problem Statement -->
    <div class="ba-card ba-card-accent">
        <h3>Core Problem &amp; Scope</h3>
        <p><strong>Pain Point:</strong> ${this.escapeHtml(ps.pain_point || '—')}</p>
        <p><strong>Target Audience:</strong> ${this.escapeHtml(ps.target_audience || '—')}</p>
        <p><strong>Current Workarounds:</strong> ${this.escapeHtml(ps.current_workarounds || '—')}</p>
    </div>

    <!-- Market Sizing -->
    <div class="ba-card">
        <h3>Market Sizing — TAM / SAM / SOM</h3>
        <div class="market-grid">
            <div class="market-stat tam">
                <div class="market-stat-label">TAM — Total Market</div>
                <div class="market-stat-value">${this.escapeHtml(tamParts.value)}</div>
                <div class="market-stat-sub">${this.escapeHtml(tamParts.desc)}</div>
            </div>
            <div class="market-stat sam">
                <div class="market-stat-label">SAM — Serviceable</div>
                <div class="market-stat-value">${this.escapeHtml(samParts.value)}</div>
                <div class="market-stat-sub">${this.escapeHtml(samParts.desc)}</div>
            </div>
            <div class="market-stat som">
                <div class="market-stat-label">SOM — Obtainable</div>
                <div class="market-stat-value">${this.escapeHtml(somParts.value)}</div>
                <div class="market-stat-sub">${this.escapeHtml(somParts.desc)}</div>
            </div>
        </div>
    </div>

    ${metrics.length > 0 ? `
    <!-- Success Metrics -->
    <div class="ba-card">
        <h3>Key Success Metrics (KPIs)</h3>
        <table class="kpi-table">
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Target</th>
                    <th>Justification</th>
                </tr>
            </thead>
            <tbody>
                ${metrics.map(m => `
                <tr>
                    <td>${this.escapeHtml(m.metric || '')}</td>
                    <td><span class="kpi-badge">${this.escapeHtml(m.target || '')}</span></td>
                    <td>${this.escapeHtml(m.justification || '')}</td>
                </tr>`).join('')}
            </tbody>
        </table>
    </div>` : ''}

    ${competitors.length > 0 ? `
    <!-- Competitor Landscape -->
    <div class="ba-card">
        <h3>Competitor Landscape</h3>
        <div class="competitor-grid">
            ${competitors.map(c => `
            <div class="competitor-card">
                <h4>${this.escapeHtml(c.name || 'Unknown')}</h4>
                ${Array.isArray(c.strengths) && c.strengths.length > 0 ? `
                <div class="strength-label">✓ Strengths</div>
                <div class="tag-list">${c.strengths.map(s => `<span class="tag strength">${this.escapeHtml(s)}</span>`).join('')}</div>` : ''}
                ${Array.isArray(c.weaknesses) && c.weaknesses.length > 0 ? `
                <div class="weakness-label">✗ Weaknesses</div>
                <div class="tag-list">${c.weaknesses.map(w => `<span class="tag weakness">${this.escapeHtml(w)}</span>`).join('')}</div>` : ''}
            </div>`).join('')}
        </div>
    </div>` : ''}

    <!-- Revenue Model & Assumptions -->
    <div class="bottom-grid">
        <div class="ba-card">
            <h3>Revenue Model</h3>
            <p><strong>Type:</strong> ${this.escapeHtml(rm.model_type || '—')}</p>
            <p style="margin-top: 8px; color: var(--color-text-muted); font-size: 13px;">${this.escapeHtml(rm.pricing_strategy || '')}</p>
        </div>
        ${assumptions.length > 0 ? `
        <div class="ba-card">
            <h3>Key Assumptions</h3>
            <ul style="padding-left: 18px; margin: 0;">
                ${assumptions.map(a => `<li style="color: rgba(255,255,255,0.6); font-size: 13px; margin-bottom: 6px; line-height: 1.6;">${this.escapeHtml(a)}</li>`).join('')}
            </ul>
        </div>` : ''}
    </div>
</div>`;
    }

    /**
     * Parse a market value string like "$4.5 Billion. Some description."
     * Returns { value: "$4.5B", desc: "description..." }
     */
    _parseMarketValue(str) {
        if (!str) return { value: '—', desc: '' };
        
        // First compact the number+unit, then find description after a period+space
        // Match pattern: optional $, digits, optional decimal, optional space, unit
        // e.g. "$4.5 Billion. Description" or "$4.5B description"
        let value = str.trim();
        let desc = '';
        
        // Look for a period followed by a space (sentence boundary), not decimal in number
        // Match: start + optional $ + number (with possible decimal) + optional unit word + . + rest
        const match = str.match(/^(\$[\d,]+(?:\.\d+)?\s*(?:Billion|Million|Trillion|B|M|T)?)\.\s*(.*)/i);
        if (match) {
            value = match[1].trim();
            desc = match[2].trim();
        } else {
            // Try splitting at first ". " (period + space) to find where description starts
            const dotSpaceIdx = str.indexOf('. ');
            if (dotSpaceIdx !== -1) {
                value = str.substring(0, dotSpaceIdx).trim();
                desc = str.substring(dotSpaceIdx + 2).trim();
            }
        }
        
        // Compact unit labels
        value = value.replace(/\$?([\d,]+(?:\.\d+)?)\s*Billion/i, '$$$1B');
        value = value.replace(/\$?([\d,]+(?:\.\d+)?)\s*Million/i, '$$$1M');
        value = value.replace(/\$?([\d,]+(?:\.\d+)?)\s*Trillion/i, '$$$1T');
        
        return { value, desc };
    }

    escapeHtml(text) {
        if (typeof text !== 'string') return String(text || '');
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

window.MarkdownRenderer = MarkdownRenderer;
