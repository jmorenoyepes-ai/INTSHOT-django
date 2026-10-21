function modal_eliminar(tabla, mensaje, url){
    // modificar modal de bootsrapt segun tabla en cuestión.
    let titulo = document.getElementById("modal_title");
    let body = document.getElementById("modal_body");
    let form = document.getElementById("modal_form_eliminar");

    titulo.innerHTML = `Eliminar ${tabla}`;
    body.innerHTML = mensaje;

    // La eliminación se envía por POST (con token CSRF) y no por un simple
    // enlace, para que un link externo no pueda borrar registros.
    form.setAttribute("action", url);
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


// Evitar envíos duplicados
// En producción (PythonAnywhere) el servidor a veces tarda un momento en
// responder y la gente vuelve a pulsar el botón, con lo que se crea dos veces
// un pedido, se agrega dos veces un producto al carrito, etc. Aquí, al enviar
// cualquier formulario o pulsar un botón-enlace, se bloquea el botón y se le
// pone un spinner hasta que llegue la siguiente página. No hay que tocar las
// plantillas: funciona para todo el sitio.
//
// Si algún formulario no debe bloquearse, basta con ponerle data-sin-bloqueo.
(function () {
    var SPINNER = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    var SPINNER_CON_TEXTO = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>';

    // Un botón que solo tiene un icono (p. ej. el carrito del catálogo) cambia
    // el icono por el spinner; uno con texto conserva el texto y antepone el spinner.
    function soloIcono(boton) {
        var copia = boton.cloneNode(true);
        copia.querySelectorAll('.material-symbols-outlined').forEach(function (i) { i.remove(); });
        return copia.textContent.trim() === '';
    }

    function bloquear(boton) {
        if (!boton || boton.dataset.bloqueado) return;
        boton.dataset.bloqueado = '1';
        boton.setAttribute('aria-busy', 'true');

        // Mantener el ancho para que el botón no "salte" al cambiar su contenido.
        boton.style.minWidth = boton.getBoundingClientRect().width + 'px';

        if (boton.tagName === 'A') {
            boton.classList.add('disabled');
            boton.setAttribute('aria-disabled', 'true');
        } else {
            boton.disabled = true;
        }

        if (boton.tagName === 'INPUT') return; // <input type="submit"> no tiene innerHTML
        boton.dataset.htmlOriginal = boton.innerHTML;
        boton.innerHTML = soloIcono(boton) ? SPINNER : SPINNER_CON_TEXTO + boton.innerHTML;
    }

    function desbloquear(boton) {
        if (!boton.dataset.bloqueado) return;
        delete boton.dataset.bloqueado;
        boton.removeAttribute('aria-busy');
        boton.style.minWidth = '';
        if (boton.tagName === 'A') {
            boton.classList.remove('disabled');
            boton.removeAttribute('aria-disabled');
        } else {
            boton.disabled = false;
        }
        if (boton.dataset.htmlOriginal !== undefined) {
            boton.innerHTML = boton.dataset.htmlOriginal;
            delete boton.dataset.htmlOriginal;
        }
    }

    function desbloquearTodo() {
        document.querySelectorAll('[data-bloqueado]').forEach(desbloquear);
        document.querySelectorAll('form[data-enviando]').forEach(function (f) { delete f.dataset.enviando; });
    }

    // --- Formularios ---------------------------------------------------------
    // El evento submit solo llega si la validación HTML5 (required, min, max…)
    // pasó, así que un formulario incompleto nunca queda bloqueado.
    document.addEventListener('submit', function (event) {
        var form = event.target;
        if (event.defaultPrevented || form.hasAttribute('data-sin-bloqueo')) return;

        // Segundo envío (Enter repetido, doble clic) mientras el primero va en camino.
        if (form.dataset.enviando) {
            event.preventDefault();
            return;
        }
        form.dataset.enviando = '1';

        // Un botón deshabilitado no viaja con el formulario; si el botón pulsado
        // tenía name/value, se conserva en un campo oculto para que el servidor
        // lo reciba igual.
        var pulsado = event.submitter;
        if (pulsado && pulsado.name) {
            var oculto = document.createElement('input');
            oculto.type = 'hidden';
            oculto.name = pulsado.name;
            oculto.value = pulsado.value;
            form.appendChild(oculto);
        }

        form.querySelectorAll('button[type="submit"], button:not([type]), input[type="submit"]').forEach(bloquear);
        if (form.id) {
            document.querySelectorAll('button[form="' + form.id + '"]').forEach(bloquear);
        }
    });

    // --- Botones que son enlaces (<a class="btn">) ---------------------------
    // Por ejemplo "Agregar al carrito", que es un enlace y no un formulario.
    document.addEventListener('click', function (event) {
        var enlace = event.target.closest('a.btn[href]');
        if (!enlace || event.defaultPrevented) return;

        // Casos en los que la página actual NO cambia: no hay que bloquear nada.
        if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        if (enlace.target === '_blank' || enlace.hasAttribute('download')) return;
        if (enlace.hasAttribute('data-bs-toggle') || enlace.hasAttribute('data-bs-dismiss')) return;
        var href = enlace.getAttribute('href');
        if (!href || href.charAt(0) === '#' || href.indexOf('javascript:') === 0) return;

        if (enlace.dataset.bloqueado) {
            event.preventDefault();
            return;
        }
        bloquear(enlace);
    });

    // --- Volver a dejar todo como estaba -------------------------------------
    // pagehide: justo antes de salir de la página. Así, si el navegador guarda
    // la página (caché de atrás/adelante o Firefox recordando el estado de los
    // botones), al volver con "Atrás" los botones están activos de nuevo.
    // pageshow: por si la página se restaura desde esa caché.
    window.addEventListener('pagehide', desbloquearTodo);
    window.addEventListener('pageshow', desbloquearTodo);
})();
