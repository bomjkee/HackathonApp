document.addEventListener('DOMContentLoaded', function () {
    const regButton = document.getElementById("reg-btn");
    const hackathonButton = document.getElementById("back-btn");

    regButton.addEventListener('click', function () {
        window.location.href = '/profile';
    });

    hackathonButton.addEventListener('click', function () {
        window.location.href = '/hackathon';
    });
});