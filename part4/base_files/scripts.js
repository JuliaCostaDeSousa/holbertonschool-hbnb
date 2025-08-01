/* 
  This is a SAMPLE FILE to get you started.
  Please, follow the project instructions to complete the tasks.
*/

const { get } = require("mermaid/dist/diagrams/state/id-cache.js");
const { card } = require("mermaid/dist/rendering-util/rendering-elements/shapes/card.js");
const { interpolateToCurve } = require("mermaid/dist/utils.js");

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const placeDetailsSection = document.getElementById('place-details');
    const priceFilter = document.getElementById('price-filter');
    const reviewForm = document.getElementById('review-form');
    const token = checkAuthentication();
    const placeId = getPlaceIdFromURL();

    let option_values = ['10', '50', '100', 'All']
    for (const option_value of option_values) {
        const option = document.createElement('option');
        option.value = option_value
        option.textContent = option_value
        priceFilter.appendChild(option)
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const email = document.getElementById('email').value
            const password = document.getElementById('password').value
            await loginUser(email, password)
        });
    }

    if (placeDetailsSection) {
        const token = getCookie("token")
        const placeId = getPlaceIdFromURL()
        if (!placeId) {
            alert("Invalid place ID in URL.");
            return;
        }
        const url = "http://127.0.0.1:5000/api/places/" + placeId
        fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            }
        })
        .then(response => {
            if (response.ok) {
                return response.json()
            } else {
                alert("Error fetching place details: " + response.statusText);
            }
        })
        .then(data => {
            if (data) {
                displayPlaceDetails(data)
            }
        })
        .catch(error => {
            alert('Network error: ' + error);
        })
    }

    if (priceFilter){
        priceFilter.addEventListener('change', (event) => {
        let selectedValue = event.target.value;
        const cards = document.getElementsByClassName('place-card');
        
        if (selectedValue == 'All') {
            for (card of cards){
                card.style.display =''
            }
        } else {
            const maxPrice = parseInt(selectedValue)

            for (card of cards){
                const priceP = card.getElementsByTagName('p')[0]
                const priceText = priceP.textContent;
                const price = parseInt(priceText.replace('Price per night: ', ''));
    
                if (price <= maxPrice) {
                    card.style.display =''
                } else {
                    card.style.display ='none'
                }
            }
        }
    })}

    if (reviewForm) {
        reviewForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const comment = document.getElementById('review-text').value;
            const rating = document.getElementById('rating').value;
            submitReview(token, placeId, comment, rating)
        });
    }
});

async function submitReview(token, placeId, comment, rating) {
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/reviews`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            },
            body: JSON.stringify({
                place_id: placeId,
                comment: comment,
                rating: parseInt(rating)
            })
        });

        if (response.ok) {
            alert('Review submitted successfully!');
            document.getElementById('review-form').reset();
        } else {
            alert('Failed to submit review');
        }
    } catch (error) {
        alert('Network error: ' + error);
    }
}

async function loginUser(email, password) {
    try {
        const response = await fetch('http://127.0.0.1:5000/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
    });
    if (response.ok) {
        const data = await response.json();
        document.cookie = `token=${data.access_token}; path=/`;
        window.location.href = 'index.html';
    } else {
        alert('Login failed: ' + response.statusText);
    }
    } catch (error) {
        alert('Network error: ' + error);
    }
}

function checkAuthentication() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');
    const addReviewSection = document.getElementById('add-review');
    const currentPage = window.location.pathname;

    if (loginLink) {
        loginLink.style.display = token ? 'none' : 'block';
    }

    if (currentPage.endsWith('index.html')) {
        if (token) {
            fetchPlaces(token);
        }
    } else if (currentPage.endsWith('place.html')) {
        const placeId = getPlaceIdFromURL();

        if (addReviewSection) {
            addReviewSection.style.display = token ? 'block' : 'none';
        }

        fetchPlaceDetails(token, placeId);
    } else if (currentPage.endsWith('add_review.html')) {
        if (!token) {
            window.location.href = 'index.html';
        }
    }
}

function getCookie(name) {
    let split_cookie = document.cookie.split(';')
    for (const param of split_cookie) {
        if (param.trim().startsWith(`${name}=`)) {
            let cookie = param.substring(param.indexOf('=') + 1)
            return cookie
        }
    }
    return null
}

async function fetchPlaces(token) {
    try {
        const URL = "http://127.0.0.1:5000/api/places"

        const response = await fetch(URL, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            }
        })

        if (response.ok) {
            const data = await response.json()
            displayPlaces(data)
        } else {
            alert("Error fetching places: " + response.statusText);
        }
    } catch (error) {
        alert('Network error: ' + error);
    }
}


function displayPlaces(places) {    
    const place_list = document.getElementById('places-list');
    place_list.innerHTML = ""
    for (const place of places) {
        const new_div = document.createElement('div');
        new_div.classList.add("place-card")

        const name = document.createElement('h3')
        name.textContent = place.name

        const price = document.createElement('p')
        price.textContent = `Price per night: ${place.price}`

        const view_details_button = document.createElement('a')
        view_details_button.classList.add('details-button')
        view_details_button.textContent = `View Details`
        view_details_button.href = "place.html?id=" + place.id
        
        new_div.appendChild(name)
        new_div.appendChild(price)
        new_div.appendChild(view_details_button)
        place_list.appendChild(new_div)
    };
}

function getPlaceIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

function displayPlaceDetails(place) {
    const container = document.getElementById('place-details');
    container.innerHTML = "";

    const name = document.createElement('h2');
    name.textContent = place.name;

    const price = document.createElement('p');
    price.textContent = `Price per night: $${place.price_by_night}`;

    const description = document.createElement('p');
    description.textContent = place.description;

    const amenities = document.createElement('ul');
    for (const amenity of place.amenities || []) {
        const li = document.createElement('li');
        li.textContent = amenity;
        amenities.appendChild(li);
    }

    const reviews = document.createElement('div');
    for (const review of place.reviews || []) {
        const card = document.createElement('div');
        card.classList.add('review-card');
        card.innerHTML = `<strong>${review.user}</strong>: ${review.comment} (${review.rating}/5)`;
        reviews.appendChild(card);
    }

    container.appendChild(name);
    container.appendChild(price);
    container.appendChild(description);
    container.appendChild(amenities);
    container.appendChild(reviews);
}

async function fetchPlaceDetails(token, placeId) {
    try {
        const URL = `http://127.0.0.1:5000/api/places/${placeId}`

        const response = await fetch(URL, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            }
        })

        if (response.ok) {
            const data = await response.json()
            displayPlaceDetails(data)
        } else {
            alert("Error fetching place details: " + response.statusText);
        }
    } catch (error) {
        alert('Network error: ' + error);
    }
}
