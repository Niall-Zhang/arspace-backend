document.addEventListener('DOMContentLoaded', (event) => {
    var appRoot = document.getElementById('root');

    // Create a new div element for the welcome message
    var welcomeDiv = document.createElement('div');
    welcomeDiv.className = 'welcome-message';
    welcomeDiv.textContent = 'Welcome to arspace, the premier event ticketing and networking platform!';

    // Append the welcome message to the root div
    appRoot.appendChild(welcomeDiv);

    // You can add more content dynamically here using JavaScript
});

document.querySelector('.menu-icon').addEventListener('click', function() {
    this.classList.toggle('active');
    document.querySelector('.nav-items').classList.toggle('show');
});