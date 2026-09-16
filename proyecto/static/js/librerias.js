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
