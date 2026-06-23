/**
 * BlueprintAI Landing Page v2 — Premium Interactions
 * Particles · Scroll reveal · Stat counters · Pipeline animator
 */

// ── Particle Canvas (subtle, blue-tinted) ────────────────────
const canvas = document.getElementById('particle-canvas');
const ctx = canvas.getContext('2d');
let particles = [];
const PARTICLE_COUNT = 55;

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

function randomColor() {
    const palette = [
        [124, 157, 255],  // blue
        [167, 139, 250],  // purple
        [52,  211, 153],  // green
        [255, 255, 255],  // white
    ];
    return palette[Math.floor(Math.random() * palette.length)];
}

function createParticle() {
    const [r, g, b] = randomColor();
    return {
        x:  Math.random() * canvas.width,
        y:  Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.25,
        vy: (Math.random() - 0.5) * 0.25,
        size: Math.random() * 1.2 + 0.3,
        opacity: Math.random() * 0.35 + 0.05,
        decay: Math.random() * 0.002 + 0.0008,
        r, g, b,
    };
}

function initParticles() {
    particles = Array.from({ length: PARTICLE_COUNT }, createParticle);
}

function drawParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach((p, i) => {
        p.x += p.vx;
        p.y += p.vy;
        p.opacity -= p.decay;

        if (p.opacity <= 0 || p.x < -10 || p.x > canvas.width + 10 || p.y < -10 || p.y > canvas.height + 10) {
            particles[i] = createParticle();
            return;
        }

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${p.r}, ${p.g}, ${p.b}, ${p.opacity})`;
        ctx.fill();
    });

    // Faint connection lines between close particles
    for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 100) {
                ctx.beginPath();
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                const alpha = (1 - dist / 100) * 0.04;
                ctx.strokeStyle = `rgba(124, 157, 255, ${alpha})`;
                ctx.lineWidth = 0.5;
                ctx.stroke();
            }
        }
    }

    requestAnimationFrame(drawParticles);
}

resizeCanvas();
initParticles();
drawParticles();
window.addEventListener('resize', () => { resizeCanvas(); initParticles(); });

// ── Navbar scroll effect ──────────────────────────────────────
const nav = document.getElementById('landing-nav');
window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 40);
}, { passive: true });

// ── Stat counter animation ────────────────────────────────────
function animateCounters() {
    document.querySelectorAll('.stat-number[data-target]').forEach(el => {
        const target = parseInt(el.dataset.target);
        const duration = 1400;
        const start = performance.now();
        function update(now) {
            const t = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - t, 4); // ease-out-quart
            el.textContent = Math.floor(eased * target);
            if (t < 1) requestAnimationFrame(update);
            else el.textContent = target;
        }
        requestAnimationFrame(update);
    });
}

// Trigger counters when stats bar enters view
const statsEl = document.querySelector('.hero-stats');
if (statsEl) {
    const statsObs = new IntersectionObserver(entries => {
        entries.forEach(e => {
            if (e.isIntersecting) { setTimeout(animateCounters, 600); statsObs.disconnect(); }
        });
    }, { threshold: 0.5 });
    statsObs.observe(statsEl);
}

// ── Scroll-reveal with IntersectionObserver ───────────────────
const revealObs = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            revealObs.unobserve(entry.target);
        }
    });
}, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

document.querySelectorAll('.reveal').forEach(el => revealObs.observe(el));

// ── Preview window: animated pipeline cycling ─────────────────
const agents = [
    { label: 'BA',  name: 'Business Analyst',  doneText: '✓ Complete',  activeText: 'Analyzing...',  doneClass: 'p-done',  activeClass: 'p-active', waitClass: 'p-wait' },
    { label: 'PM',  name: 'Product Manager',    doneText: '✓ Complete',  activeText: 'Writing PRD...', doneClass: 'p-done', activeClass: 'p-active', waitClass: 'p-wait' },
    { label: 'QA',  name: 'QA Critic',          doneText: '✓ Complete',  activeText: 'Reviewing...',  doneClass: 'p-done',  activeClass: 'p-active', waitClass: 'p-wait' },
    { label: 'SYN', name: 'Synthesis CPO',       doneText: '✓ Complete',  activeText: 'Synthesizing...', doneClass: 'p-done', activeClass: 'p-active', waitClass: 'p-wait' },
];

const previewSidebar = document.querySelector('.preview-sidebar');
let activeAgent = 1; // start at PM (index 1)

function renderPipelineNodes() {
    if (!previewSidebar) return;
    previewSidebar.innerHTML = agents.map((agent, i) => {
        let cls = agent.waitClass;
        let status = 'Waiting';
        if (i < activeAgent)  { cls = agent.doneClass;   status = agent.doneText; }
        if (i === activeAgent){ cls = agent.activeClass;  status = agent.activeText; }

        return `
        <div class="preview-node ${cls}">
            <div class="pnode-icon">${agent.label}</div>
            <div class="pnode-text">
                <span>${agent.name}</span>
                <em>${status}</em>
            </div>
        </div>`;
    }).join('');
}

renderPipelineNodes();

setInterval(() => {
    activeAgent = (activeAgent + 1) % agents.length;
    renderPipelineNodes();
}, 2200);

// ── Pipeline section animation ────────────────────────────────
// Cycle the spv-node states to animate the pipeline demo
const spvNodes  = document.querySelectorAll('.spv-node');
const spvLines  = document.querySelectorAll('.spv-line');
let spvActive   = 1;

function updateSpvPipeline() {
    spvNodes.forEach((node, i) => {
        node.classList.remove('done', 'active');
        if (i < spvActive)  node.classList.add('done');
        if (i === spvActive) node.classList.add('active');
    });
    spvLines.forEach((line, i) => {
        line.classList.remove('done');
        if (i < spvActive) line.classList.add('done');
    });
    spvActive = (spvActive + 1) % spvNodes.length;
}

setInterval(updateSpvPipeline, 2200);

// ── Mouse parallax for hero orbs ──────────────────────────────
const orb1 = document.querySelector('.orb-1');
const orb2 = document.querySelector('.orb-2');
const orb3 = document.querySelector('.orb-3');

window.addEventListener('mousemove', (e) => {
    const mx = (e.clientX / window.innerWidth - 0.5) * 2;  // -1 to 1
    const my = (e.clientY / window.innerHeight - 0.5) * 2;

    if (orb1) orb1.style.transform = `translate(${mx * 20}px, ${my * 15}px) scale(1)`;
    if (orb2) orb2.style.transform = `translate(${mx * -15}px, ${my * -10}px) scale(1)`;
    if (orb3) orb3.style.transform = `translate(${mx * 12}px, ${my * 18}px) scale(1)`;
}, { passive: true });

// ── Smooth anchor scrolling ───────────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', e => {
        const target = document.querySelector(anchor.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});
