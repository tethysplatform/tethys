function prepareCarousel(carouselContainer) {
    let leftButton = carouselContainer.querySelector(".carousel-button-left");
    let rightButton = carouselContainer.querySelector(".carousel-button-right");

    let carousel = carouselContainer.querySelector(".carousel");
    // TODO Get all the cards in the carousel that are visible
    let cards = Array.from(carousel.querySelectorAll(".recipe-card"));

    let cardWidth = cards[0].getBoundingClientRect().width;
    let cardMargin = parseInt(getComputedStyle(cards[0]).marginRight);

    let extraCardsInLastSlide = cards.length % 4;
    
    let currentIndex = 5;
    let maxIndex = cards.length + 5;

    if (cards.length > 4) {
        // Clone the first and last 5 cards to the opposite end of the carousel to create the illusion of infinite scrolling
        let lastSlideClones = cards.slice(-5).map(card => card.cloneNode(true));
        let firstSlideClones = cards.slice(0, 4).map(card =>card.cloneNode(true));

        lastSlideClones.forEach(clone => carousel.insertBefore(clone, cards[0]));
        firstSlideClones.forEach(clone => carousel.appendChild(clone));
        
        setInitialPosition();

        leftButton.addEventListener("click", () => {
            updateCarousel(-4);
        });
        
        rightButton.addEventListener("click", () => {
            updateCarousel(4);
    });
    }
    
    function updateCarousel(offset) {
        let remainingCards = maxIndex - (currentIndex + offset);
        
        if (offset > 0 && remainingCards <= 4 && remainingCards > 0 && currentIndex < maxIndex) {
            currentIndex += remainingCards
        } else if (offset < 0 && currentIndex + offset < 5 && currentIndex > 5) {
            currentIndex = 5;
        } else {
            currentIndex += offset;
        }
        console.log("Post, Current index: ", currentIndex);
        let shift = -currentIndex * (cardWidth + cardMargin);
        carousel.style.transform = `translateX(${shift}px)`;
        checkBounds();
    }

    function checkBounds() {
        // Check if carousel is at either end of the slides, and if so, reset the position to the 
        // opposite end seamlessly without any transition to perform illusion of infinite scrolling
        if (currentIndex >= cards.length + 5) {
            setTimeout(() => {
                carousel.style.transition = "none"; 
                currentIndex = 5; //Reset to first slide
                let shift = -currentIndex * (cardWidth + cardMargin);
                carousel.style.transform = `translateX(${shift}px)`;
                
                setTimeout(() => carousel.style.transition = "transform 0.5s ease", 50); // Re-enable transition
            }, 500);
        } else if (currentIndex < 5) {
            setTimeout(() => {
                console.log("Pre, Current index: ", currentIndex);
                carousel.style.transition = "none";
                currentIndex = cards.length + 1; // Reset to last slide
                let shift = -currentIndex * (cardWidth + cardMargin);
                carousel.style.transform = `translateX(${shift}px)`;
                console.log("Post, Current index: ", currentIndex);
                setTimeout(() => carousel.style.transition = "transform 0.5s ease-in-out", 50); // Re-enable transition
            }, 500);
        }
    }
    
    function setInitialPosition() {
        carousel.style.transition = "none"; // Disable transition to avoid animation on initial load
        let shift = -currentIndex * (cardWidth + cardMargin);
        carousel.style.transform = `translateX(${shift}px)`;
        setTimeout(() => carousel.style.transition = "transform 0.5s ease-in-out", 50); // Re-enable transition
    }   
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