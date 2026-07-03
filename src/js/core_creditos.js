const forms = document.querySelectorAll(".actions form");

forms.forEach((form) => {

    form.addEventListener("submit", (e) => {

        const button = form.querySelector("button");
        const action = button.textContent.trim();

        let message = "¿Confirmas esta acción?";

        if(action === "Aprobar"){
            message = "¿Deseas aprobar esta solicitud de crédito?";
        }

        if(action === "Rechazar"){
            message = "¿Deseas rechazar esta solicitud de crédito?";
        }

        if(action === "Desembolsar"){
            message = "¿Deseas desembolsar este crédito y enviarlo al saldo del cliente?";
        }

        const confirmacion = confirm(message);

        if(!confirmacion){
            e.preventDefault();
        }

    });

});