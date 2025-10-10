/**
 * Success Stories Carousel/Slider
 * Handles the carousel functionality for success stories
 */

let currentSlide = 0;
let totalSlides = 0;
let slidesToShow = 3;
let isTransitioning = false;

// Initialize carousel when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initCarousel();
    
    // Handle window resize
    window.addEventListener('resize', function() {
        updateSlidesToShow();
        initCarousel();
    });
    
    // Auto-scroll every 5 seconds
    setInterval(() => {
        if (!isTransitioning && totalSlides > slidesToShow) {
            moveCarousel(1);
        }
    }, 5000);
});

// Initialize the carousel
function initCarousel() {
    const track = document.getElementById('storiesTrack');
    const items = document.querySelectorAll('.story-item');
    
    if (!track || items.length === 0) {
        return;
    }
    
    totalSlides = items.length;
    updateSlidesToShow();
    
    // Reset current slide if it's beyond the available slides
    if (currentSlide >= totalSlides - slidesToShow + 1) {
        currentSlide = Math.max(0, totalSlides - slidesToShow);
    }
    
    updateCarousel();
    updateDots();
}

// Update number of slides to show based on screen size
function updateSlidesToShow() {
    const width = window.innerWidth;
    
    if (width < 768) {
        slidesToShow = 1; // Mobile
    } else if (width < 992) {
        slidesToShow = 2; // Tablet
    } else {
        slidesToShow = 3; // Desktop
    }
    
    // Update CSS custom property
    document.documentElement.style.setProperty('--slides-to-show', slidesToShow);
}

// Move carousel in specified direction
function moveCarousel(direction) {
    if (isTransitioning || totalSlides <= slidesToShow) {
        return;
    }
    
    isTransitioning = true;
    
    const maxSlide = totalSlides - slidesToShow;
    
    if (direction === 1) {
        // Move right
        currentSlide = currentSlide >= maxSlide ? 0 : currentSlide + 1;
    } else {
        // Move left
        currentSlide = currentSlide <= 0 ? maxSlide : currentSlide - 1;
    }
    
    updateCarousel();
    updateDots();
    
    // Reset transition flag after animation
    setTimeout(() => {
        isTransitioning = false;
    }, 500);
}

// Go to specific slide
function goToSlide(slideIndex) {
    if (isTransitioning || totalSlides <= slidesToShow) {
        return;
    }
    
    isTransitioning = true;
    currentSlide = slideIndex;
    
    updateCarousel();
    updateDots();
    
    // Reset transition flag after animation
    setTimeout(() => {
        isTransitioning = false;
    }, 500);
}

// Update carousel position
function updateCarousel() {
    const track = document.getElementById('storiesTrack');
    if (!track) return;
    
    const slideWidth = 100 / slidesToShow;
    const translateX = -(currentSlide * slideWidth);
    
    track.style.transform = `translateX(${translateX}%)`;
}

// Update dots indicator
function updateDots() {
    const dots = document.querySelectorAll('.dot');
    const maxSlide = Math.max(0, totalSlides - slidesToShow);
    
    dots.forEach((dot, index) => {
        dot.classList.remove('active');
        
        // Show active dot based on current slide
        if (index === currentSlide) {
            dot.classList.add('active');
        }
    });
    
    // Hide dots if there are not enough slides
    const dotsContainer = document.getElementById('carouselDots');
    if (dotsContainer) {
        dotsContainer.style.display = totalSlides > slidesToShow ? 'flex' : 'none';
    }
    
    // Hide navigation buttons if there are not enough slides
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    if (prevBtn && nextBtn) {
        const shouldShow = totalSlides > slidesToShow;
        prevBtn.style.display = shouldShow ? 'flex' : 'none';
        nextBtn.style.display = shouldShow ? 'flex' : 'none';
    }
}

// Touch/swipe support for mobile
let startX = 0;
let startY = 0;
let isDragging = false;

document.addEventListener('touchstart', function(e) {
    const carousel = document.getElementById('storiesCarousel');
    if (!carousel || !carousel.contains(e.target)) return;
    
    startX = e.touches[0].clientX;
    startY = e.touches[0].clientY;
    isDragging = true;
});

document.addEventListener('touchmove', function(e) {
    if (!isDragging) return;
    
    e.preventDefault();
}, { passive: false });

document.addEventListener('touchend', function(e) {
    if (!isDragging) return;
    
    const endX = e.changedTouches[0].clientX;
    const endY = e.changedTouches[0].clientY;
    const diffX = startX - endX;
    const diffY = startY - endY;
    
    // Only trigger swipe if horizontal movement is greater than vertical
    if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
        if (diffX > 0) {
            // Swipe left - move right
            moveCarousel(1);
        } else {
            // Swipe right - move left
            moveCarousel(-1);
        }
    }
    
    isDragging = false;
});

// Keyboard navigation
document.addEventListener('keydown', function(e) {
    const carousel = document.getElementById('storiesCarousel');
    if (!carousel || !carousel.contains(document.activeElement)) return;
    
    if (e.key === 'ArrowLeft') {
        e.preventDefault();
        moveCarousel(-1);
    } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        moveCarousel(1);
    }
});

// Pause auto-scroll on hover
document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.getElementById('storiesCarousel');
    if (carousel) {
        carousel.addEventListener('mouseenter', function() {
            // Pause auto-scroll (this would need to be implemented with a global variable)
            window.carouselPaused = true;
        });
        
        carousel.addEventListener('mouseleave', function() {
            // Resume auto-scroll
            window.carouselPaused = false;
        });
    }
});

