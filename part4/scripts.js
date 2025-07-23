document.addEventListener('DOMContentLoaded', () => {
  const page = document.body.dataset.page;

  switch (page) {
    case 'login':
      handleLoginPage();
      break;
    case 'index':
      handleIndexPage();
      break;
    case 'place':
      handlePlaceDetails();
      break;
    case 'add_review':
      handleReviewSubmission();
      break;
  }
});

function handleLoginPage() {
  const form = document.getElementById('login-form');
  form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!form.checkValidity()) return form.reportValidity();

    const email = form.email.value;
    const password = form.password.value;

    const res = await fetch('http://localhost:5000/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (res.ok) {
      const { access_token } = await res.json();
      document.cookie = `token=${access_token}; path=/`;
      window.location.href = 'index.html';
    } else {
      alert('Login failed.');
    }
  });
}

function handleIndexPage() {
  const token = getToken();
  if (!token) window.location.href = 'login.html';

  fetch('http://localhost:5000/api/v1/places', {
    headers: { 'Authorization': `Bearer ${token}` }
  })
    .then(res => res.json())
    .then(displayPlaces);

  const filter = document.getElementById('price-filter');
  if (filter) {
    filter.innerHTML = `<option value="">All</option><option>50</option><option>100</option><option>150</option>`;
    filter.addEventListener('change', () => {
      const max = parseFloat(filter.value);
      document.querySelectorAll('.place-card').forEach(card => {
        const price = parseFloat(card.dataset.price);
        card.style.display = (!filter.value || price <= max) ? 'block' : 'none';
      });
    });
  }
}

function displayPlaces(places) {
  const list = document.getElementById('places-list');
  if (!list) return;
  list.innerHTML = '';

  places.forEach(place => {
    const card = document.createElement('div');
    card.className = 'place-card';
    card.dataset.price = place.price;
    card.innerHTML = `
      <h3>${place.name}</h3>
      <p>${place.description}</p>
      <p>Location: ${place.location}</p>
      <p>Price: $${place.price}</p>
      <a href="place.html?id=${place.id}" class="details-button">View Details</a>
    `;
    list.appendChild(card);
  });
}

function handlePlaceDetails() {
  const token = getToken();
  const id = getParam('id');
  if (!token || !id) return;

  fetch(`http://localhost:5000/api/v1/places/${id}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
    .then(res => res.json())
    .then(data => {
      showPlaceDetails(data);
      showReviews(data.reviews);
    });
}

function showPlaceDetails(place) {
  const container = document.getElementById('place-details');
  if (!container) return;
  container.innerHTML = `
    <h3>${place.name}</h3>
    <p>${place.description}</p>
    <p>${place.location}</p>
    <p>Price: $${place.price}</p>
    <div class="amenities">
      ${place.amenities.includes('bed') ? '<img src="icon_bed.png" alt="Bed">' : ''}
      ${place.amenities.includes('bath') ? '<img src="icon_bath.png" alt="Bath">' : ''}
      ${place.amenities.includes('wifi') ? '<img src="icon_wifi.png" alt="WiFi">' : ''}
    </div>
  `;
}

function showReviews(reviews = []) {
  const container = document.getElementById('reviews');
  if (!container) return;
  container.innerHTML = '';

  reviews.forEach(r => {
    const div = document.createElement('div');
    div.className = 'review-card';
    div.innerHTML = `
      <p>${r.comment}</p>
      <small>by ${r.user}</small>
      <span>${'⭐️'.repeat(r.rating)}</span>
    `;
    container.appendChild(div);
  });
}

function handleReviewSubmission() {
  const form = document.getElementById('review-form');
  if (!form) return;
  const token = getToken();
  const id = getParam('id');
  if (!token || !id) return window.location.href = 'login.html';

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const review = form.review.value;
    const rating = form.rating.value;

    const res = await fetch(`http://localhost:5000/api/v1/places/${id}/reviews`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ comment: review, rating: Number(rating) })
    });

    if (res.ok) {
      alert('Review submitted!');
      window.location.href = `place.html?id=${id}`;
    } else {
      alert('Failed to submit review.');
    }
  });
}

function getToken() {
  const match = document.cookie.match(/(?:^|; )token=([^;]*)/);
  return match ? match[1] : null;
}

function getParam(key) {
  return new URLSearchParams(window.location.search).get(key);
}