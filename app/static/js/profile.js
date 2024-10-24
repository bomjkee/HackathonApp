document.addEventListener('DOMContentLoaded', function () {
    const profileButton = document.getElementById("profile-btn");
    const hackathonButton = document.getElementById("hackathon-btn");

    profileButton.addEventListener('click', function () {
        window.location.href = '/profile';
    });

    hackathonButton.addEventListener('click', function () {
        window.location.href = '/hackathon';
    });

    const regButton = document.getElementById("reg-btn");

    regButton.addEventListener('click', function () {
        window.location.href = '/reg';
    });
});