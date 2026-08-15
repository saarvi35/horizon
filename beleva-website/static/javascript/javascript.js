document.addEventListener("DOMContentLoaded", function () {
  const priceSlider = document.getElementById("price-slider");
  const minInput = document.getElementById("min_price");
  const maxInput = document.getElementById("max_price");
  const minDisplay = document.getElementById("min_price_display");
  const maxDisplay = document.getElementById("max_price_display");

  if (priceSlider && minInput && maxInput && minDisplay && maxDisplay) {
    const minValue = parseInt(minInput.value || 0);
    const maxValue = parseInt(maxInput.value || 10000);

    noUiSlider.create(priceSlider, {
      start: [minValue, maxValue],
      connect: true,
      step: 100,
      range: {
        min: 0,
        max: 10000,
      },
      format: {
        to: value => Math.round(value),
        from: value => Number(value)
      }
    });

    // Slider → Input
    priceSlider.noUiSlider.on("update", function (values) {
      const [minVal, maxVal] = values;
      minInput.value = minVal;
      maxInput.value = maxVal;
      minDisplay.value = minVal;
      maxDisplay.value = maxVal;
    });

    // Input → Slider (on blur or Enter)
    minDisplay.addEventListener("change", function () {
      let val = parseInt(this.value) || 0;
      let currentMax = parseInt(maxDisplay.value) || 10000;
      priceSlider.noUiSlider.set([val, currentMax]);
    });

    maxDisplay.addEventListener("change", function () {
      let val = parseInt(this.value) || 10000;
      let currentMin = parseInt(minDisplay.value) || 0;
      priceSlider.noUiSlider.set([currentMin, val]);
    });
  }
});




// product details

function changeImageByColor(imageUrl) {
        document.getElementById("mainImage").src = imageUrl;
    }

    function changeImage(event, imageUrl) {
        const mainImage = document.getElementById("mainImage");
        mainImage.src = imageUrl;

        document.querySelectorAll('.thumbnail').forEach(thumb => {
            thumb.classList.remove('border', 'border-success');
        });
        event.target.classList.add('border', 'border-success');
    }



// for deals scroll
const scrollContainer = document.getElementById('productScroll');
  const scrollLeftBtn = document.getElementById('scrollLeftBtn');
  const scrollRightBtn = document.getElementById('scrollRightBtn');

  // Show/hide buttons based on scroll position
  function updateButtonVisibility() {
    scrollLeftBtn.style.display = scrollContainer.scrollLeft > 0 ? 'flex' : 'none';
    const maxScrollLeft = scrollContainer.scrollWidth - scrollContainer.clientWidth;
    scrollRightBtn.style.display = scrollContainer.scrollLeft < maxScrollLeft ? 'flex' : 'none';
  }

  scrollLeftBtn.addEventListener('click', () => {
    scrollContainer.scrollBy({ left: -300, behavior: 'smooth' });
  });

  scrollRightBtn.addEventListener('click', () => {
    scrollContainer.scrollBy({ left: 300, behavior: 'smooth' });
  });

  scrollContainer.addEventListener('scroll', updateButtonVisibility);

  // Initialize button visibility
  window.addEventListener('load', updateButtonVisibility);


// for deals scroll
const scrollContainer1 = document.getElementById('productScroll1');
  const scrollLeftBtn1 = document.getElementById('scrollLeftBtn1');
  const scrollRightBtn1 = document.getElementById('scrollRightBtn1');

  // Show/hide buttons based on scroll position
  function updateButtonVisibility() {
    scrollLeftBtn1.style.display = scrollContainer1.scrollLeft > 0 ? 'flex' : 'none';
    const maxScrollLeft = scrollContainer1.scrollWidth - scrollContainer1.clientWidth;
    scrollRightBtn1.style.display = scrollContainer1.scrollLeft < maxScrollLeft ? 'flex' : 'none';
  }

  scrollLeftBtn1.addEventListener('click', () => {
    scrollContainer1.scrollBy({ left: -300, behavior: 'smooth' });
  });

  scrollRightBtn1.addEventListener('click', () => {
    scrollContainer1.scrollBy({ left: 300, behavior: 'smooth' });
  });

  scrollContainer1.addEventListener('scroll', updateButtonVisibility);

  // Initialize button visibility
  window.addEventListener('load', updateButtonVisibility);



// products wishlist
  function toggleWishlist(button) {
    const productId = button.getAttribute('data-product-id');

    fetch(`/add-to-wishlist/${productId}/`)
      .then(() => {
        const icon = button.querySelector('i');
        icon.classList.toggle('fas');
        icon.classList.toggle('far');
      })
      .catch(err => console.error('Wishlist toggle failed:', err));
  }

// home page message display

window.addEventListener("DOMContentLoaded", function () {
  const msg = document.getElementById("floating-message");
  if (msg) {
    setTimeout(() => {
      msg.style.opacity = "0";
      msg.style.transition = "opacity 0.5s ease";
      setTimeout(() => msg.remove(), 500);
    }, 3500);
  }
});


// deals timer
  const end = new Date("2025-11-15T23:59:59").getTime();
  const t = setInterval(() => {
    let d = end - Date.now();
    if (d <= 0) return document.getElementById("deal-timer").innerHTML="Deal Expired!", clearInterval(t);
    document.getElementById("days").innerText = Math.floor(d/864e5)+"d";
    document.getElementById("hours").innerText = Math.floor(d%(864e5)/36e5)+"h";
    document.getElementById("minutes").innerText = Math.floor(d%(36e5)/6e4)+"m";
    document.getElementById("seconds").innerText = Math.floor(d%(6e4)/1e3)+"s";
  },1000);