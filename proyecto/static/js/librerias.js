function modal_eliminar(tabla, mensaje, url){
    // modificar modal de bootsrapt segun tabla en cuestión.
    let titulo = document.getElementById("modal_title");
    let body = document.getElementById("modal_body");
    let boton_aceptar = document.getElementById("modal_aceptar");
    
    titulo.innerHTML = `Eliminar ${tabla}`;
    body.innerHTML = mensaje;

    console.log(url);
    boton_aceptar.setAttribute("onclick",`location.href='${url}'`);
}

// Switch de modo oscuro/claro
// El tema ya viene aplicado desde tema.html (inline en el <head>); aqui solo
// se maneja el cambio. Se usa querySelectorAll y no un id porque hay un switch
// por plantilla base (topbar privada y navbar publica).
(function () {
    var switches = document.querySelectorAll('.theme-toggle');
    if (!switches.length) return;

    var esOscuro = document.documentElement.getAttribute('data-bs-theme') === 'dark';

    function pintarSwitches() {
        switches.forEach(function (boton) {
            boton.setAttribute('aria-pressed', esOscuro ? 'true' : 'false');
            boton.setAttribute('aria-label', esOscuro ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro');
            var icono = boton.querySelector('.theme-toggle-icon');
            if (icono) {
                icono.textContent = esOscuro ? 'dark_mode' : 'light_mode';
            }
        });
    }

    pintarSwitches();

    switches.forEach(function (boton) {
        boton.addEventListener('click', function () {
            esOscuro = !esOscuro;
            document.documentElement.setAttribute('data-bs-theme', esOscuro ? 'dark' : 'light');
            try {
                localStorage.setItem('intshot-theme', esOscuro ? 'dark' : 'light');
            } catch (e) {}
            pintarSwitches();

            // Avisa a quien necesite reaccionar al cambio (p. ej. los graficos
            // del dashboard, que se dibujan en <canvas> y no leen variables CSS).
            document.dispatchEvent(new CustomEvent('intshot:cambio-tema', {
                detail: { oscuro: esOscuro },
            }));
        });
    });
})();
