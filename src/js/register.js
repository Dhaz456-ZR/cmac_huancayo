(function() {
    'use strict';

    var form = document.getElementById('registerForm');

    var nombreInput = document.getElementById('nombre');
    var dniInput = document.getElementById('dni');
    var tarjetaInput = document.getElementById('tarjeta');
    var passwordInput = document.getElementById('password');
    var confirmPasswordInput = document.getElementById('confirmPassword');

    var pinInputs = document.querySelectorAll('#pinBoxes .pin-input');
    var confirmPinInputs = document.querySelectorAll('#confirmPinBoxes .pin-input');

    var nombreError = document.getElementById('nombreError');
    var dniError = document.getElementById('dniError');
    var tarjetaError = document.getElementById('tarjetaError');
    var passwordError = document.getElementById('passwordError');
    var confirmPasswordError = document.getElementById('confirmPasswordError');
    var pinError = document.getElementById('pinError');
    var confirmPinError = document.getElementById('confirmPinError');

    var loadingScreen = document.getElementById('loadingScreen');

    function setupPinBehavior(inputs) {
        inputs.forEach(function(input, index) {
            input.addEventListener('input', function() {
                this.value = this.value.replace(/[^0-9]/g, '');
                if (this.value.length === 1 && index < inputs.length - 1) {
                    inputs[index + 1].focus();
                }
                if (this.closest('#pinBoxes')) {
                    pinError.textContent = '';
                } else if (this.closest('#confirmPinBoxes')) {
                    confirmPinError.textContent = '';
                }
            });

            input.addEventListener('keydown', function(e) {
                if (e.key === 'Backspace' && this.value === '' && index > 0) {
                    inputs[index - 1].focus();
                }
            });

            input.addEventListener('paste', function(e) {
                e.preventDefault();
                var paste = (e.clipboardData || window.clipboardData).getData('text');
                var digits = paste.replace(/[^0-9]/g, '').slice(0, 4);
                if (digits.length === 0) return;
                for (var i = 0; i < digits.length && i < inputs.length; i++) {
                    inputs[i].value = digits[i];
                }
                if (digits.length === 4) {
                    inputs[3].focus();
                } else {
                    inputs[digits.length].focus();
                }
            });
        });
    }

    setupPinBehavior(pinInputs);
    setupPinBehavior(confirmPinInputs);

    function getPinValue(inputs) {
        var pin = '';
        inputs.forEach(function(inp) { pin += inp.value; });
        return pin;
    }

    function validateForm() {
        var isValid = true;

        var nombre = nombreInput.value.trim();
        if (nombre.length < 2) {
            nombreError.textContent = 'Ingresa tu nombre completo.';
            isValid = false;
        } else {
            nombreError.textContent = '';
        }

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

        var confirmPassword = confirmPasswordInput.value.trim();
        if (confirmPassword !== password) {
            confirmPasswordError.textContent = 'Las contraseñas no coinciden.';
            isValid = false;
        } else {
            confirmPasswordError.textContent = '';
        }

        var pin = getPinValue(pinInputs);
        if (!/^[0-9]{4}$/.test(pin)) {
            pinError.textContent = 'El PIN debe tener 4 dígitos numéricos.';
            isValid = false;
        } else {
            pinError.textContent = '';
        }

        var confirmPin = getPinValue(confirmPinInputs);
        if (!/^[0-9]{4}$/.test(confirmPin)) {
            confirmPinError.textContent = 'El PIN de confirmación debe tener 4 dígitos.';
            isValid = false;
        } else if (confirmPin !== pin) {
            confirmPinError.textContent = 'Los PINs no coinciden.';
            isValid = false;
        } else {
            confirmPinError.textContent = '';
        }

        return isValid;
    }

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        if (!validateForm()) {
            if (nombreError.textContent) { nombreInput.focus(); }
            else if (dniError.textContent) { dniInput.focus(); }
            else if (tarjetaError.textContent) { tarjetaInput.focus(); }
            else if (passwordError.textContent) { passwordInput.focus(); }
            else if (confirmPasswordError.textContent) { confirmPasswordInput.focus(); }
            else if (pinError.textContent) { pinInputs[0].focus(); }
            else if (confirmPinError.textContent) { confirmPinInputs[0].focus(); }
            return;
        }

        loadingScreen.style.display = 'flex';
        form.submit();
    });

    document.getElementById('loginLink').addEventListener('click', function(e) {
        e.preventDefault();
        loadingScreen.style.display = 'flex';
        setTimeout(function() { window.location.href = '/'; }, 600);
    });

})();