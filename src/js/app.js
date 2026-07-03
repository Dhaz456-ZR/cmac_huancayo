// =========================
// PARTICULAS DEL FONDO
// =========================

function crearParticula(){

    const particle = document.createElement("div");

    particle.classList.add("particle");

    const size = Math.random() * 5 + 2;

    particle.style.width = size + "px";
    particle.style.height = size + "px";

    particle.style.left = Math.random() * window.innerWidth + "px";

    particle.style.animationDuration = Math.random() * 4 + 4 + "s";

    particle.style.opacity = Math.random();

    document.body.appendChild(particle);

    setTimeout(() => {
        particle.remove();
    }, 8000);
}

setInterval(crearParticula, 250);