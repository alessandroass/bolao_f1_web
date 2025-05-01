function atualizarOpcoes() {
    const pilotos = JSON.parse(document.getElementById("pilotos-data").textContent);
    const selects = document.querySelectorAll("select:not([name='pole'])");

    const selecionados = Array.from(selects)
        .map(sel => sel.value)
        .filter(v => v !== "");

    selects.forEach(sel => {
        const valorAtual = sel.value;
        sel.innerHTML = '<option value="">-- Escolha --</option>';
        pilotos.forEach(piloto => {
            if (!selecionados.includes(piloto) || piloto === valorAtual) {
                const opt = document.createElement("option");
                opt.value = piloto;
                opt.textContent = piloto;
                if (piloto === valorAtual) opt.selected = true;
                sel.appendChild(opt);
            }
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const selects = document.querySelectorAll("select:not([name='pole'])");
    selects.forEach(sel => sel.addEventListener("change", atualizarOpcoes));
    atualizarOpcoes();
});
