// Main JavaScript file for Furniture System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle add to cart button clicks
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            const quantity = document.querySelector('#product-quantity') ? 
                             document.querySelector('#product-quantity').value : 1;
            
            // Add to cart animation
            this.innerHTML = '<i class="fas fa-check me-1"></i> Đã thêm';
            this.classList.remove('btn-primary');
            this.classList.add('btn-success');
            
            // Reset button after 2 seconds
            setTimeout(() => {
                this.innerHTML = '<i class="fas fa-shopping-cart me-1"></i> Thêm vào giỏ hàng';
                this.classList.remove('btn-success');
                this.classList.add('btn-primary');
            }, 2000);
            
            // Here you would normally call your backend API to add to cart
            // addToCart(productId, quantity);
        });
    });

    // Product image gallery
    const mainImage = document.querySelector('#main-product-image');
    const thumbnails = document.querySelectorAll('.product-thumbnail');
    
    if (mainImage && thumbnails.length > 0) {
        thumbnails.forEach(thumb => {
            thumb.addEventListener('click', function() {
                // Update main image
                mainImage.src = this.getAttribute('data-image');
                
                // Update active thumbnail
                thumbnails.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }

    // Quantity selector
    const quantityInput = document.querySelector('#product-quantity');
    const increaseBtn = document.querySelector('#increase-quantity');
    const decreaseBtn = document.querySelector('#decrease-quantity');
    
    if (quantityInput && increaseBtn && decreaseBtn) {
        increaseBtn.addEventListener('click', function() {
            let currentValue = parseInt(quantityInput.value);
            if (currentValue < 99) {
                quantityInput.value = currentValue + 1;
            }
        });
        
        decreaseBtn.addEventListener('click', function() {
            let currentValue = parseInt(quantityInput.value);
            if (currentValue > 1) {
                quantityInput.value = currentValue - 1;
            }
        });
        
        quantityInput.addEventListener('change', function() {
            let currentValue = parseInt(this.value);
            if (isNaN(currentValue) || currentValue < 1) {
                this.value = 1;
            } else if (currentValue > 99) {
                this.value = 99;
            }
        });
    }

    // Filter toggle on mobile
    const filterToggle = document.querySelector('#filter-toggle');
    const filterSidebar = document.querySelector('#filter-sidebar');
    
    if (filterToggle && filterSidebar) {
        filterToggle.addEventListener('click', function() {
            filterSidebar.classList.toggle('show-filter');
        });
    }
});
