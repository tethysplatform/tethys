document.addEventListener("DOMContentLoaded", () => {
    const carousels = document.querySelectorAll(".recipe-gallery.carousel");

    carousels.forEach(carousel => {
        const cards = carousel.querySelectorAll(".recipe-card");
        const leftButton = carousel.querySelector(".carousel-button-left");
        const rightButton = carousel.querySelector(".carousel-button-right");

        let currentPageIndex = 0;
        let maxPageIndex = Math.ceil(cards.length / 4) - 1;
        let carouselWidth = carousel.offsetWidth;

        leftButton.addEventListener("click", () => {
            updateCarousel(-1);
        });

        rightButton.addEventListener("click", () => {
            updateCarousel(1);
        });
        
        const updateCarousel = (offset) => {
            const containerWidth = cards[0].parentElement.offsetWidth;

            currentPageIndex += offset;
            console.log(currentPageIndex, maxPageIndex);
            cards.forEach(function(card) {
                card.style.transform = `translateX(${currentPageIndex * -containerWidth}px)`;

            });
            if (currentPageIndex === 0) {
                leftButton.classList.add("hidden");
            } else {
                leftButton.classList.remove("hidden");
            }
            if (currentPageIndex === maxPageIndex) {
                rightButton.classList.add("hidden");
            } else {
                rightButton.classList.remove("hidden");
            }
        };

    });
});