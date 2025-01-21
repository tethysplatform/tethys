function prepareCarousel(carouselContainer) {
    let carousel = carouselContainer.querySelector(".carousel");
    let cards = carousel.querySelectorAll(".recipe-card");
    let cardTransformations = Array.from(cards).map(() => 0);

    
    let containerWidth = carouselContainer.getBoundingClientRect().width;
    let cardWidth = containerWidth * 0.20 - 10;
    let buttonWidth = containerWidth * 0.10 - 10;
    
    const setInitialPosition = () => {
        carousel.style.transform = `translateX(${buttonWidth}px)`;
    };

    const leftButton = carouselContainer.querySelector(".carousel-button-left");
    const rightButton = carouselContainer.querySelector(".carousel-button-right");

    setInitialPosition();
    leftButton.classList.add("hidden");

    let currentIndex = 0;
    let maxIndex = Math.ceil(cards.length / 4) - 1;
    let cardsInLastSlide = cards.length % 4;
    
    function updateCarousel(offset) {

        carousel.style.transform = `translateX(${offset * (cardWidth * 4)}px)`;
    }

    leftButton.addEventListener("click", () => {
        updateCarousel(1);
    });
    
    rightButton.addEventListener("click", () => {
        updateCarousel(-1);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const carouselContainers = document.querySelectorAll(".carousel-container");
    const carousels = document.querySelectorAll(".carousel");
    carouselContainers.forEach(carouselContainer => {
        prepareCarousel(carouselContainer);
    });

    var searchBar = document.querySelector("#recipe-tag-search-bar");
    if (searchBar) {
        searchBar.addEventListener("input", () => {
            let searchValue = searchBar.value.toLowerCase();
            let cards = document.querySelectorAll(".recipe-card");
            cards.forEach(card => {
                const tags = card.querySelector(".recipe-tags").textContent.toLowerCase();
                if (tags.includes(searchValue)) {
                    card.classList.remove("hidden");
                } else {
                    card.classList.add("hidden");
                }
            });
        });
    }
});