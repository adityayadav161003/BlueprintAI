/**
 * RequireAI Markdown and JSON Renderer
 * Formats Markdown using marked.js and formats raw JSON business analyses
 * into gorgeous HTML dashboards.
 */
class MarkdownRenderer {
    constructor() {
        // Set marked options if marked is available
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                breaks: true,
                gfm: true
            });
        }
    }

    renderMarkdown(text) {
        if (typeof marked === 'undefined') {
            return `<pre>${this.escapeHtml(text)}</pre>`;
        }
        return marked.parse(text);
    }

    renderBAJson(jsonText) {
        try {
            // Trim and clean potential markdown code block wraps (like ```json ... ```)
            let cleaned = jsonText.trim();
            if (cleaned.startsWith('```json')) {
                cleaned = cleaned.replace(/^```json/, '').replace(/```$/, '').trim();
            } else if (cleaned.startsWith('```')) {
                cleaned = cleaned.replace(/^```/, '').replace(/```$/, '').trim();
            }

            const data = JSON.parse(cleaned);
            
            // Build a gorgeous dashboard layout
            let html = `
                <div class="ba-dashboard">
                    <h2 style="margin-top:0; border-bottom: 2px solid var(--color-ba); padding-bottom: 8px;">Market & Business Analysis</h2>
                    
                    <!-- Problem Statement Card -->
                    <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-left: 4px solid var(--color-ba); border-radius: 8px; padding: 20px; margin: 20px 0;">
                        <h3 style="color: var(--color-ba); margin-bottom: 8px;">Core Problem & Scope</h3>
                        <p><strong>Pain Point:</strong> ${data.problem_statement.pain_point}</p>
                        <p style="margin-top: 8px;"><strong>Target Audience:</strong> ${data.problem_statement.target_audience}</p>
                        <p style="margin-top: 8px;"><strong>Current Workarounds:</strong> ${data.problem_statement.current_workarounds}</p>
                    </div>

                    <!-- Market Sizes Grid -->
                    <h3 style="margin-top: 24px; margin-bottom: 12px;">Market sizing (TAM / SAM / SOM)</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 24px;">
                        <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; text-align: center;">
                            <div style="font-size: 11px; font-weight: 700; color: var(--color-text-muted); text-transform: uppercase;">TAM (Total Market)</div>
                            <div style="font-size: 20px; font-weight: 800; color: #fff; margin: 8px 0;">${data.market_size.tam.split('.')[0]}</div>
                            <div style="font-size: 11px; color: var(--color-text-muted);">${data.market_size.tam.includes('.') ? data.market_size.tam.substring(data.market_size.tam.indexOf('.')+1).trim() : ''}</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; text-align: center;">
                            <div style="font-size: 11px; font-weight: 700; color: var(--color-text-muted); text-transform: uppercase;">SAM (Serviceable Market)</div>
                            <div style="font-size: 20px; font-weight: 800; color: #fff; margin: 8px 0;">${data.market_size.sam.split('.')[0]}</div>
                            <div style="font-size: 11px; color: var(--color-text-muted);">${data.market_size.sam.includes('.') ? data.market_size.sam.substring(data.market_size.sam.indexOf('.')+1).trim() : ''}</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; text-align: center;">
                            <div style="font-size: 11px; font-weight: 700; color: var(--color-text-muted); text-transform: uppercase;">SOM (Obtainable Market)</div>
                            <div style="font-size: 20px; font-weight: 800; color: #fff; margin: 8px 0;">${data.market_size.som.split('.')[0]}</div>
                            <div style="font-size: 11px; color: var(--color-text-muted);">${data.market_size.som.includes('.') ? data.market_size.som.substring(data.market_size.som.indexOf('.')+1).trim() : ''}</div>
                        </div>
                    </div>

                    <!-- Success Metrics -->
                    <h3 style="margin-top: 24px; margin-bottom: 12px;">Key Success Metrics (KPIs)</h3>
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 24px;">
                        <thead>
                            <tr style="background: rgba(255,255,255,0.03);">
                                <th style="border: 1px solid var(--border-color); padding: 10px; text-align:left;">Metric</th>
                                <th style="border: 1px solid var(--border-color); padding: 10px; text-align:left;">Target</th>
                                <th style="border: 1px solid var(--border-color); padding: 10px; text-align:left;">Justification</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.success_metrics.map(m => `
                                <tr>
                                    <td style="border: 1px solid var(--border-color); padding: 10px; font-weight: 700;">${m.metric}</td>
                                    <td style="border: 1px solid var(--border-color); padding: 10px; color: var(--color-ba); font-weight:700;">${m.target}</td>
                                    <td style="border: 1px solid var(--border-color); padding: 10px;">${m.justification}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>

                    <!-- Competitor Matrix -->
                    <h3 style="margin-top: 24px; margin-bottom: 12px;">Competitor Landscape</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; margin-bottom: 24px;">
                        ${data.competitors.map(c => `
                            <div style="background: rgba(255,255,255,0.01); border: 1px solid var(--border-color); border-radius: 8px; padding: 16px;">
                                <h4 style="color: #fff; margin-bottom: 10px; font-size: 15px;">${c.name}</h4>
                                <div style="margin-bottom: 8px;">
                                    <div style="font-size: 11px; color: var(--color-ba); font-weight: 700; text-transform: uppercase;">Strengths:</div>
                                    <ul style="padding-left: 18px; margin: 4px 0; font-size:13px;">
                                        ${c.strengths.map(s => `<li>${s}</li>`).join('')}
                                    </ul>
                                </div>
                                <div>
                                    <div style="font-size: 11px; color: var(--color-qa); font-weight: 700; text-transform: uppercase;">Weaknesses:</div>
                                    <ul style="padding-left: 18px; margin: 4px 0; font-size:13px;">
                                        ${c.weaknesses.map(w => `<li>${w}</li>`).join('')}
                                    </ul>
                                </div>
                            </div>
                        `).join('')}
                    </div>

                    <!-- Revenue Model & Assumptions -->
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px;">
                        <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 8px; padding: 16px;">
                            <h4 style="color: #fff; margin-bottom: 8px; font-size: 15px;">Revenue Model</h4>
                            <p><strong>Type:</strong> ${data.revenue_model.model_type}</p>
                            <p style="margin-top: 6px; font-size: 13px; color: var(--color-text-muted);">${data.revenue_model.pricing_strategy}</p>
                        </div>
                        <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 8px; padding: 16px;">
                            <h4 style="color: #fff; margin-bottom: 8px; font-size: 15px;">Key Assumptions</h4>
                            <ul style="padding-left: 18px; font-size: 13px; color: var(--color-text-muted);">
                                ${data.key_assumptions.map(a => `<li>${a}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            `;
            return html;
        } catch (e) {
            // Fallback to raw text rendered inside pre code in case of error
            return `
                <div class="ba-raw">
                    <h2 style="margin-top:0; border-bottom: 2px solid var(--color-ba); padding-bottom: 8px;">Market Analysis (Raw Data)</h2>
                    <pre style="margin-top:16px;"><code>${this.escapeHtml(jsonText)}</code></pre>
                </div>
            `;
        }
    }

    escapeHtml(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

window.MarkdownRenderer = MarkdownRenderer;
