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
// --- LÓGICA DINÂMICA DE MINISTÉRIOS (PREPARAÇÃO PARA SUPABASE) ---

// 1. Simulação do Banco de Dados (Futuramente virá do Supabase)
const mockMinisterios = [
    {
        id: "sede",
        nome: "Ministério Redenção Sede",
        enderecoCurto: "Centro",
        enderecoCompleto: "Av. Principal, 1000 - Centro, Cidade - UF",
        pastor: "Pr. Marcos Silva e Pra. Helena",
        horarios: "Domingo às 18h | Quarta às 20h",
        descricao: "A igreja mãe do nosso ministério, onde tudo começou. Um ambiente espaçoso e acolhedor para toda a família.",
        imagem: "https://via.placeholder.com/800x600/2C5282/FFFFFF?text=Redencao+Sede"
    },
    {
        id: "cajuru",
        nome: "Ministério Redenção Cajuru",
        enderecoCurto: "Bairro Cajuru",
        enderecoCompleto: "Rua das Flores, 250 - Cajuru, Cidade - UF",
        pastor: "Pr. João Batista",
        horarios: "Domingo às 19h | Quinta às 20h",
        descricao: "Nossa congregação no coração do Cajuru. Uma igreja vibrante, com forte atuação na comunidade local e amor pelas pessoas.",
        imagem: "https://via.placeholder.com/800x600/1A365D/FFFFFF?text=Redencao+Cajuru"
    }
    // Adicione os outros 6 aqui com o mesmo padrão para testar
];

// Função que futuramente buscará do Supabase
async function getMinisterios() {
    // Exemplo futuro: 
    // const { data, error } = await supabase.from('ministerios').select('*');
    // return data;
    
    return mockMinisterios; // Retorno simulado atual
}

// 2. Renderizar a Lista (Página ministerios.html)
async function renderMinisteriosList() {
    const grid = document.getElementById('ministerios-grid');
    if (!grid) return; // Só executa se estiver na página da lista

    const ministerios = await getMinisterios();
    grid.innerHTML = ''; // Limpa o "Carregando..."

    ministerios.forEach(min => {
        const card = document.createElement('article');
        card.className = 'ministerio-card fade-in visible'; // Já deixo visível para não conflitar com o observer caso o DOM carregue rápido
        
        card.innerHTML = `
            <img src="${min.imagem}" alt="${min.nome}">
            <div class="ministerio-card-content">
                <h3>${min.nome}</h3>
                <p><i class="fas fa-map-marker-alt"></i> ${min.enderecoCurto}</p>
                <a href="ministerio_detalhe.html?id=${min.id}" class="btn-outline">Ver Detalhes</a>
            </div>
        `;
        grid.appendChild(card);
    });
}

// 3. Renderizar a Página de Detalhe Dinâmica (Página ministerio_detalhe.html)
async function renderMinisterioDetail() {
    // Pega o ID da URL (ex: ?id=cajuru)
    const urlParams = new URLSearchParams(window.location.search);
    const minId = urlParams.get('id');

    const nomeElement = document.getElementById('min-nome');
    if (!nomeElement) return; // Só executa se estiver na página de detalhe

    const ministerios = await getMinisterios();
    const minData = ministerios.find(m => m.id === minId);

    if (minData) {
        // Popula os dados no HTML
        document.getElementById('min-nome').innerText = minData.nome;
        document.getElementById('min-endereco-curto').innerText = minData.enderecoCurto;
        document.getElementById('min-descricao').innerText = minData.descricao;
        document.getElementById('min-endereco-completo').innerText = minData.enderecoCompleto;
        document.getElementById('min-pastor').innerText = minData.pastor;
        document.getElementById('min-horarios').innerText = minData.horarios;
        
        const imgEl = document.getElementById('min-imagem');
        imgEl.src = minData.imagem;
        imgEl.style.display = 'block';

        const heroBg = document.getElementById('min-hero-bg');
        heroBg.style.backgroundImage = `url('${minData.imagem}')`;
    } else {
        // Caso o ID não exista ou alguém digite URL errada
        nomeElement.innerText = "Ministério não encontrado";
        document.getElementById('min-endereco-curto').innerText = "Verifique o link acessado.";
    }
}

// Inicializa as funções dependendo da página em que o usuário está
document.addEventListener('DOMContentLoaded', () => {
    renderMinisteriosList();
    renderMinisterioDetail();
});