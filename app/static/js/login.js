
/*
========================================
RAÍZES DO NORDESTE
LOGIN DO SISTEMA
========================================
*/

const formulario = document.getElementById("form-login");
const mensagem = document.getElementById("mensagem-login");

formulario.addEventListener("submit", async function (evento) {

    evento.preventDefault();

    const email = document.getElementById("email").value.trim();
    const senha = document.getElementById("senha").value;

    mensagem.textContent = "Verificando seus dados...";
    mensagem.style.color = "#697d3c";

    // Prepara os dados no formato aceito pelo FastAPI.
    const dadosLogin = new URLSearchParams();

    dadosLogin.append("username", email);
    dadosLogin.append("password", senha);

    try {

        // Envia o e-mail e a senha para a API.
        const resposta = await fetch("/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: dadosLogin
        });

        const dados = await resposta.json();

        // Verifica se o login foi recusado.
        if (!resposta.ok) {

            mensagem.textContent =
                typeof dados.detail === "string"
                    ? dados.detail
                    : "E-mail ou senha incorretos.";

            mensagem.style.color = "#b42318";
            return;
        }

        // Confere se a API retornou o token.
        if (!dados.access_token) {

            mensagem.textContent =
                "A API não retornou o token de acesso.";

            mensagem.style.color = "#b42318";
            return;
        }

        // Consulta a API para identificar o perfil do usuário.
        const respostaUsuario = await fetch("/auth/me", {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + dados.access_token
            }
        });

        if (!respostaUsuario.ok) {

            mensagem.textContent =
                "Não foi possível verificar seu perfil.";

            mensagem.style.color = "#b42318";
            return;
        }

        const usuario = await respostaUsuario.json();

        // O painel atual é exclusivo para administradores.
        if (usuario.perfil !== "ADMIN") {

            mensagem.textContent =
                "Este painel é exclusivo para administradores.";

            mensagem.style.color = "#b42318";
            return;
        }

        // Guarda o token temporariamente nesta aba.
        sessionStorage.setItem(
            "token",
            dados.access_token
        );

        mensagem.textContent =
            "Login realizado com sucesso! Abrindo o painel...";

        mensagem.style.color = "#247a38";

        // Abre o painel administrativo.
        window.location.replace("/painel");

    } catch (erro) {

        mensagem.textContent =
            "Não foi possível conectar ao servidor.";

        mensagem.style.color = "#b42318";

        console.error("Erro no login:", erro);

    }

});
