/**
 * Script Principal - Ministério Redenção (Home Institucional)
 */

document.addEventListener('DOMContentLoaded', () => {

    // 1. ANIMAÇÃO ON SCROLL (Intersection Observer)
    const fadeElements = document.querySelectorAll('.fade-in');

    const appearOptions = {
        threshold: 0.15, // Aciona quando 15% do elemento estiver na tela
        rootMargin: "0px 0px -50px 0px"
    };

    const appearOnScroll = new IntersectionObserver(function(entries, observer) {
        entries.forEach(entry => {
            if (!entry.isIntersecting) {
                return;
            } else {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target); // Otimização: para de observar após animar
            }
        });
    }, appearOptions);

    fadeElements.forEach(element => {
        appearOnScroll.observe(element);
    });

    // 2. MENU MOBILE
    const mobileBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');

    if (mobileBtn && navLinks) {
        mobileBtn.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            
            // Adicionando via JS para evitar poluir o CSS caso o JS falhe
            if (navLinks.classList.contains('active')) {
                navLinks.style.display = 'flex';
                navLinks.style.flexDirection = 'column';
                navLinks.style.position = 'absolute';
                navLinks.style.top = '70px';
                navLinks.style.left = '0';
                navLinks.style.width = '100%';
                navLinks.style.backgroundColor = '#FFFFFF';
                navLinks.style.padding = '20px';
                navLinks.style.boxShadow = '0 10px 20px rgba(0,0,0,0.1)';
                navLinks.style.borderTop = '1px solid #f0f0f0';
            } else {
                navLinks.style.display = 'none';
            }
        });

        // Fechar menu ao clicar em um link
        const links = navLinks.querySelectorAll('a');
        links.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth < 768) {
                    navLinks.classList.remove('active');
                    navLinks.style.display = 'none';
                }
            });
        });
    }
});