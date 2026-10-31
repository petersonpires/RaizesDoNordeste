
/*
========================================
RAÍZES DO NORDESTE
PAINEL ADMINISTRATIVO
========================================
*/

// Aguarda o carregamento da página.
document.addEventListener("DOMContentLoaded", async function () {

    // Recupera o token de autenticação.
    const token = sessionStorage.getItem("token");

    // Se não existir token, retorna ao login.
    if (!token) {
        window.location.replace("/");
        return;
    }

    try {
        // Consulta a API para identificar o usuário.
        const resposta = await fetch("/auth/me", {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        // Se a autenticação falhar, encerra a sessão.
        if (!resposta.ok) {
            sessionStorage.removeItem("token");
            window.location.replace("/");
            return;
        }

        const usuario = await resposta.json();

        // Somente administradores podem usar o painel.
        if (usuario.perfil !== "ADMIN") {
            sessionStorage.removeItem("token");

            alert(
                "Acesso permitido somente para administradores."
            );

            window.location.replace("/");
            return;
        }

        // Atualiza a identificação do usuário.
        const elementoUsuario =
            document.querySelector(".usuario");

        if (elementoUsuario) {
            elementoUsuario.textContent =
                "👤 " + usuario.nome;
        }

    } catch (erro) {

        console.error(
            "Erro ao verificar autenticação:",
            erro
        );

        alert(
            "Não foi possível verificar sua sessão."
        );

        window.location.replace("/");
        return;
    }

    // Configura o botão de saída.
    const botaoSair =
        document.getElementById("botao-sair");

    if (botaoSair) {

        botaoSair.addEventListener("click", function () {

            sessionStorage.removeItem("token");

            window.location.replace("/");

        });

    }

});
