/**
 * BlueprintAI Landing Page — Interactions
 * Particle canvas background, scroll effects, stat counters
 */

// ── Particle Canvas ──────────────────────────────────────────
const canvas = document.getElementById('particle-canvas');
const ctx = canvas.getContext('2d');

let particles = [];
const PARTICLE_COUNT = 60;

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

function createParticle() {
    return {
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        size: Math.random() * 1.5 + 0.3,
        opacity: Math.random() * 0.4 + 0.05,
        decay: Math.random() * 0.003 + 0.001,
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

        if (p.opacity <= 0 || p.x < 0 || p.x > canvas.width || p.y < 0 || p.y > canvas.height) {
            particles[i] = createParticle();
            return;
        }

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${p.opacity})`;
        ctx.fill();
    });

    // Draw faint connection lines between close particles
    for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 120) {
                ctx.beginPath();
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                const alpha = (1 - dist / 120) * 0.06;
                ctx.strokeStyle = `rgba(255,255,255,${alpha})`;
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
    if (window.scrollY > 40) {
        nav.classList.add('scrolled');
    } else {
        nav.classList.remove('scrolled');
    }
}, { passive: true });

// ── Stat counter animation ───────────────────────────────────
function animateCounters() {
    document.querySelectorAll('.stat-number[data-target]').forEach(el => {
        const target = parseInt(el.dataset.target);
        const duration = 1200;
        const start = performance.now();

        function update(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            // Ease out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.floor(eased * target);
            if (progress < 1) requestAnimationFrame(update);
            else el.textContent = target;
        }
        requestAnimationFrame(update);
    });
}

// Trigger counter when hero section is visible
const heroObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            setTimeout(animateCounters, 800);
            heroObserver.disconnect();
        }
    });
}, { threshold: 0.3 });

const heroStats = document.querySelector('.hero-stats');
if (heroStats) heroObserver.observe(heroStats);

// ── Scroll-reveal for section elements ──────────────────────
const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            revealObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

document.querySelectorAll('.feature-card, .hiw-step, .agent-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    revealObserver.observe(el);
});

// Stagger agent cards and feature cards
document.querySelectorAll('.feature-card').forEach((el, i) => {
    el.style.transitionDelay = `${i * 0.08}s`;
});
document.querySelectorAll('.agent-card').forEach((el, i) => {
    el.style.transitionDelay = `${i * 0.1}s`;
});

// ── Button hover sound simulation via visual feedback ────────
document.querySelectorAll('.btn-primary').forEach(btn => {
    btn.addEventListener('mouseenter', () => {
        btn.style.letterSpacing = '0.3px';
    });
    btn.addEventListener('mouseleave', () => {
        btn.style.letterSpacing = '-0.2px';
    });
});

// ── Preview window animation: cycle active node ──────────────
const previewNodes = document.querySelectorAll('.preview-node');
let activeNodeIndex = 0;
const processingLabels = ['Processing...', 'Analyzing...', 'Drafting...', 'Synthesizing...'];

function cycleActiveNode() {
    previewNodes.forEach((node, i) => {
        node.classList.toggle('active-node', i === activeNodeIndex);
        const em = node.querySelector('em');
        if (em) {
            if (i === activeNodeIndex) {
                em.className = 'processing';
                em.textContent = processingLabels[i];
            } else if (i < activeNodeIndex) {
                em.className = '';
                em.textContent = 'Done ✓';
            } else {
                em.className = '';
                em.textContent = 'Waiting';
            }
        }
    });

    activeNodeIndex = (activeNodeIndex + 1) % previewNodes.length;
}

setInterval(cycleActiveNode, 2000);
