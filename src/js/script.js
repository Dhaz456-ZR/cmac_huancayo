// =========================
// TRANSICIONES CON VIDEO
// =========================

const transitionLinks = document.querySelectorAll(".transition-link");
const loadingScreen = document.getElementById("loadingScreen");
const loadingVideo = document.getElementById("loadingVideo");

transitionLinks.forEach((link) => {

    link.addEventListener("click", function(e){

        const url = this.getAttribute("href");

        if(!url || url === "#"){
            return;
        }

        e.preventDefault();

        loadingScreen.style.display = "flex";

        loadingVideo.currentTime = 0;
        loadingVideo.play();

        loadingVideo.onended = () => {
            window.location.href = url;
        };

        setTimeout(() => {
            window.location.href = url;
        }, 5000);

    });

});