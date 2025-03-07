// JavaScript para manipular o Lightbox
document.addEventListener('DOMContentLoaded', function() {
    const thumbnail = document.getElementById('thumbnail');
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const closeLightbox = document.getElementById('close-lightbox');

    if (thumbnail) {
        // Quando clicar na miniatura, mostra a imagem no lightbox
        thumbnail.addEventListener('click', function() {
            lightbox.style.display = 'flex';
            lightboxImg.src = this.src.replace('thumbnails/', ''); // Altera para a versão original da imagem
        });

        // Quando clicar no botão de fechar, oculta o lightbox
        closeLightbox.addEventListener('click', function() {
            lightbox.style.display = 'none';
        });

        // Quando clicar fora da imagem no lightbox, também oculta o lightbox
        lightbox.addEventListener('click', function(event) {
            if (event.target === lightbox) {
                lightbox.style.display = 'none';
            }
        });
    }
});
