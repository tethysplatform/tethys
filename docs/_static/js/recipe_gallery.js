function prepareCarousel(carouselContainer) {
    let leftButton = carouselContainer.querySelector(".carousel-button-left");
    let rightButton = carouselContainer.querySelector(".carousel-button-right");
    let carousel = carouselContainer.querySelector(".carousel");

    function getCards() {
        // Function to get all visible cards in the carousel that are not cloned
        return Array.from(carousel.querySelectorAll(".recipe-card")).filter(card => !card.classList.contains("recipe-hidden") && !card.classList.contains("cloned"));
    }

    function getNumOfCards() {
        return getCards().length;
    }

    function getMaxIndex() {
        // Function to get the maximum index of the carousel accounting for the cloned cards at the beginning
        return getCards().length + 4;
    }

    let cards = getCards();

    let cardWidth;
    let cardMargin;
    let extraCardsInLastSlide;

    if(getNumOfCards() > 0) {
        cardWidth = cards[0].getBoundingClientRect().width;
        cardMargin = parseInt(getComputedStyle(cards[0]).marginRight);
        extraCardsInLastSlide = getNumOfCards() % 3;
    }
    
    // Set the initial index to 5 to account for cloned cards at the beginning
    let currentIndex = 4;

    // Only show and prepare buttons if there are more than 4 cards
    if (getNumOfCards() > 3) {
        leftButton.classList.remove("recipe-hidden");
        rightButton.classList.remove("recipe-hidden");

        // Clone the first and last 5 cards to the opposite end of the carousel to create the illusion of infinite scrolling
        let lastSlideClones = cards.slice(-4).map(card => { 
            let clone = card.cloneNode(true);
            clone.classList.add("cloned");
            return clone;
        });
        let firstSlideClones = cards.slice(0, 3).map(card => {
            let clone = card.cloneNode(true);
            clone.classList.add("cloned");
            return clone;
        });
        lastSlideClones.forEach(clone => carousel.insertBefore(clone, cards[0]));
        firstSlideClones.forEach(clone => carousel.appendChild(clone));
        
        setInitialPosition();

        leftButton.addEventListener("click", () => {
            updateCarousel(-3);
        });
        
        rightButton.addEventListener("click", () => {
            updateCarousel(3);
        }); 
    } else {
        leftButton.classList.add("recipe-hidden");
        rightButton.classList.add("recipe-hidden");
        setTimeout(() => {
            carousel.style.transition = "none";
            carousel.style.transform = `translateX(${0}px)`;
            setTimeout(() => carousel.style.transition = "transform 0.5s ease", 50); // Re-enable transition
        }, 500);
    }
    
    function updateCarousel(offset) {
        // Function to update the carousel position by the given offset
        cards = getCards();
        let maxIndex = getMaxIndex();
        let remainingCards = maxIndex - (currentIndex + offset);
        
        // Check if there is less than 4 cards remaining in the carousel, and if so, move that many remaining cards to the right.
        if (offset > 0 && remainingCards <= 3 && remainingCards > 0 && currentIndex < maxIndex) {
            currentIndex += remainingCards
        // Check if returning to the first slide with less than 4 cards to reach the beginning of the carousel, if so, move that many cards to the left.
        } else if (offset < 0 && currentIndex + offset < 4 && currentIndex > 4) {
            currentIndex = 4;
        } else {
            currentIndex += offset;
        }
        // Calculate the new position of the carousel
        let shift = -currentIndex * (cardWidth + cardMargin);
        carousel.style.transform = `translateX(${shift}px)`;
        checkBounds();
    }

    function checkBounds() {
        // Check if carousel is at either end of the slides, and if so, reset the position to the 
        // opposite end seamlessly without any transition to create an illusion of infinite scrolling
        let numOfCards = getNumOfCards();
        let isAtFirstSlide = currentIndex >= numOfCards + 4;
        let isAtLastSlide = currentIndex < 4;

        if (isAtLastSlide || isAtFirstSlide) {
            setTimeout(() => {
                carousel.style.transition = "none"; // Disable transition
                if (isAtFirstSlide) {
                    currentIndex = 4;
                }
                if (isAtLastSlide) {
                    currentIndex = numOfCards + 1;
                }

                let shift = -currentIndex * (cardWidth + cardMargin);
                carousel.style.transform = `translateX(${shift}px)`;
                setTimeout(() => carousel.style.transition = "transform 0.5s ease", 50); // Re-enable transition
            }, 500);
        }
    }
    
    function setInitialPosition() {
        // Set the initial position of the carousel to the first slide
        carousel.style.transition = "none"; // Disable transition to avoid animation on initial load
        let shift = -currentIndex * (cardWidth + cardMargin);
        carousel.style.transform = `translateX(${shift}px)`;
        setTimeout(() => carousel.style.transition = "transform 0.5s ease-in-out", 50); // Re-enable transition
    }   
}

document.addEventListener("DOMContentLoaded", () => {
    let carouselContainers = document.querySelectorAll(".carousel-container");

    // Initialize all carousel containers
    carouselContainers.forEach(carouselContainer => {
        prepareCarousel(carouselContainer);
    });

    // Add event listener to search bar to filter recipes by tags
    var searchBar = document.querySelector("#recipe-tag-search-bar");
    if (searchBar) {
        searchBar.addEventListener("input", () => {
            let searchValue = searchBar.value.toLowerCase();

            // Hide all cards without tags that match the search terms
            let cards = document.querySelectorAll(".recipe-card");
            cards.forEach(card => {
                // Check if the tags of the card contain the search value
                let tags = card.querySelector(".recipe-tags").textContent.toLowerCase();
                let title = card.querySelector(".recipe-title").textContent.toLowerCase();
                if (tags.includes(searchValue) || title.includes(searchValue)) {
                    card.classList.remove("hidden");
                } else {
                    card.classList.add("hidden");
                }
            });

            carouselContainers.forEach(carouselContainer => {
                let carousel = carouselContainer.querySelector(".carousel");

                // Remove all cloned cards in preparation to re-initialize the carousel
                let clonedCards = carousel.querySelectorAll(".recipe-card.cloned");
                clonedCards.forEach(clone => clone.remove());

                // Re-initialize the carousel container
                prepareCarousel(carouselContainer);
            });
        });
    }
});