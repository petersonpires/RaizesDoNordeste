
/*
========================================
RAÍZES DO NORDESTE
CADASTRO, LISTAGEM, EDIÇÃO E STATUS
DOS PRODUTOS
========================================
*/

document.addEventListener("DOMContentLoaded", async function () {

    // =====================================
    // ELEMENTOS DA PÁGINA
    // =====================================

    const corpoTabela = document.getElementById(
        "corpo-tabela-produtos"
    );

    const mensagemProdutos = document.getElementById(
        "mensagem-produtos"
    );

    const botaoAtualizar = document.getElementById(
        "botao-atualizar"
    );

    const botaoNovoProduto = document.getElementById(
        "botao-novo-produto"
    );

    const areaCadastro = document.getElementById(
        "area-cadastro-produto"
    );

    const formulario = document.getElementById(
        "form-cadastro-produto"
    );

    const tituloFormulario = document.getElementById(
        "titulo-formulario-produto"
    );

    const descricaoFormulario = document.getElementById(
        "descricao-formulario-produto"
    );

    const campoId = document.getElementById(
        "produto-id"
    );

    const campoNome = document.getElementById(
        "produto-nome"
    );

    const campoDescricao = document.getElementById(
        "produto-descricao"
    );

    const campoCategoria = document.getElementById(
        "produto-categoria"
    );

    const campoPreco = document.getElementById(
        "produto-preco"
    );

    const botaoSalvar = document.getElementById(
        "botao-salvar-produto"
    );

    const botaoCancelar = document.getElementById(
        "botao-cancelar-produto"
    );

    const mensagemCadastro = document.getElementById(
        "mensagem-cadastro-produto"
    );

    const botaoSair = document.getElementById(
        "botao-sair"
    );


    // =====================================
    // AUTENTICAÇÃO
    // =====================================

    const token = sessionStorage.getItem("token");

    if (!token) {
        window.location.replace("/");
        return;
    }

    function encerrarSessao() {

        sessionStorage.removeItem("token");

        window.location.replace("/");

    }

    botaoSair.addEventListener(
        "click",
        encerrarSessao
    );


    // =====================================
    // MENSAGENS
    // =====================================

    function mostrarMensagemProdutos(texto, tipo = "") {

        mensagemProdutos.textContent = texto;

        mensagemProdutos.className = "mensagem-produtos";

        if (tipo) {
            mensagemProdutos.classList.add(tipo);
        }

    }

    function mostrarMensagemCadastro(texto, tipo = "") {

        mensagemCadastro.textContent = texto;

        mensagemCadastro.className = "";

        if (tipo) {
            mensagemCadastro.classList.add(tipo);
        }

    }


    // =====================================
    // FORMATAÇÃO DE PREÇO
    // =====================================

    function formatarPreco(valor) {

        const numero = Number(valor);

        if (!Number.isFinite(numero)) {
            return "Preço indisponível";
        }

        return numero.toLocaleString("pt-BR", {
            style: "currency",
            currency: "BRL"
        });

    }


    // =====================================
    // CRIAR CÉLULA DA TABELA
    // =====================================

    function criarCelula(texto, classe = "") {

        const celula = document.createElement("td");

        celula.textContent = String(texto ?? "");

        if (classe) {
            celula.className = classe;
        }

        return celula;

    }


    // =====================================
    // ABRIR FORMULÁRIO DE CADASTRO
    // =====================================

    function abrirCadastro() {

        formulario.reset();

        campoId.value = "";

        tituloFormulario.textContent =
            "➕ Cadastrar novo produto";

        descricaoFormulario.textContent =
            "Preencha os dados do novo produto.";

        botaoSalvar.textContent =
            "Salvar produto";

        mostrarMensagemCadastro("");

        areaCadastro.hidden = false;

        campoNome.focus();

        areaCadastro.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    }


    // =====================================
    // ABRIR FORMULÁRIO DE EDIÇÃO
    // =====================================

    function abrirEdicao(produto) {

        formulario.reset();

        campoId.value = String(produto.id);

        campoNome.value = produto.nome ?? "";

        campoDescricao.value = produto.descricao ?? "";

        campoCategoria.value = produto.categoria ?? "";

        campoPreco.value = produto.preco ?? "";

        tituloFormulario.textContent =
            "✏️ Editar produto";

        descricaoFormulario.textContent =
            "Altere os dados do produto e salve.";

        botaoSalvar.textContent =
            "Salvar alterações";

        mostrarMensagemCadastro("");

        areaCadastro.hidden = false;

        areaCadastro.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

        campoNome.focus();

    }


    // =====================================
    // FECHAR FORMULÁRIO
    // =====================================

    function fecharFormulario() {

        formulario.reset();

        campoId.value = "";

        mostrarMensagemCadastro("");

        areaCadastro.hidden = true;

        botaoSalvar.textContent =
            "Salvar produto";

    }


    // =====================================
    // ALTERAR STATUS DO PRODUTO
    // =====================================

    async function alterarStatusProduto(produto, botao) {

        const novoStatus = !produto.ativo;

        const acao = novoStatus
            ? "ativar"
            : "desativar";

        const mensagemConfirmacao = novoStatus
            ? "Deseja ativar o produto \"" +
              produto.nome + "\"?"
            : "Deseja desativar o produto \"" +
              produto.nome + "\"?";

        const confirmado = window.confirm(
            mensagemConfirmacao
        );

        if (!confirmado) {
            return;
        }

        botao.disabled = true;

        mostrarMensagemProdutos(
            "Aguarde, estamos tentando " +
            acao + " o produto..."
        );

        try {

            const resposta = await fetch(
                "/produtos/" +
                encodeURIComponent(produto.id) +
                "/status",
                {
                    method: "PATCH",

                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + token
                    },

                    body: JSON.stringify({
                        ativo: novoStatus
                    })
                }
            );

            // Sessão expirada.

            if (resposta.status === 401) {

                alert(
                    "Sua sessão expirou. Faça login novamente."
                );

                encerrarSessao();

                return;

            }

            // Usuário sem permissão.

            if (resposta.status === 403) {

                throw new Error(
                    "Você não tem permissão para alterar o status."
                );

            }

            // Outros erros.

            if (!resposta.ok) {

                let detalhe = "Erro HTTP " + resposta.status;

                try {

                    const dadosErro = await resposta.json();

                    if (typeof dadosErro.detail === "string") {
                        detalhe = dadosErro.detail;
                    }

                } catch (erroLeitura) {

                    console.error(
                        "Erro ao ler resposta:",
                        erroLeitura
                    );

                }

                throw new Error(detalhe);

            }

            // Atualiza a tabela.

            const atualizou = await carregarProdutos();

            if (atualizou) {

                mostrarMensagemProdutos(
                    novoStatus
                        ? "Produto \"" + produto.nome +
                          "\" ativado com sucesso!"
                        : "Produto \"" + produto.nome +
                          "\" desativado com sucesso!",
                    "sucesso"
                );

            } else {

                mostrarMensagemProdutos(
                    "Status alterado, mas não foi possível " +
                    "atualizar a tabela. Clique em Atualizar lista.",
                    "erro"
                );

            }

        } catch (erro) {

            console.error(
                "Erro ao alterar status do produto:",
                erro
            );

            mostrarMensagemProdutos(
                "Não foi possível alterar o status: " +
                erro.message,
                "erro"
            );

        } finally {

            botao.disabled = false;

        }

    }


    // =====================================
    // PREENCHER TABELA DE PRODUTOS
    // =====================================

    function preencherTabela(produtos) {

        corpoTabela.replaceChildren();

        if (produtos.length === 0) {

            const linha = document.createElement("tr");

            const celula = criarCelula(
                "Nenhum produto cadastrado."
            );

            celula.colSpan = 6;

            celula.className = "lista-vazia";

            linha.appendChild(celula);

            corpoTabela.appendChild(linha);

            return;

        }

        produtos.forEach(function (produto) {

            const linha = document.createElement("tr");

            // ID

            linha.appendChild(
                criarCelula(produto.id)
            );

            // Nome

            linha.appendChild(
                criarCelula(
                    produto.nome,
                    "nome-produto"
                )
            );

            // Categoria

            linha.appendChild(
                criarCelula(produto.categoria)
            );

            // Preço

            linha.appendChild(
                criarCelula(
                    formatarPreco(produto.preco),
                    "preco-produto"
                )
            );

            // Situação

            const celulaStatus = document.createElement("td");

            const etiqueta = document.createElement("span");

            etiqueta.className = produto.ativo
                ? "status-produto status-ativo"
                : "status-produto status-inativo";

            etiqueta.textContent = produto.ativo
                ? "Ativo"
                : "Inativo";

            celulaStatus.appendChild(etiqueta);

            linha.appendChild(celulaStatus);


            // =====================================
            // BOTÕES DE AÇÃO
            // =====================================

            const celulaAcoes = document.createElement("td");

            celulaAcoes.style.whiteSpace = "nowrap";


            // BOTÃO EDITAR

            const botaoEditar = document.createElement("button");

            botaoEditar.type = "button";

            botaoEditar.textContent = "✏️ Editar";

            botaoEditar.className = "botao-editar-produto";

            botaoEditar.addEventListener(
                "click",
                function () {
                    abrirEdicao(produto);
                }
            );

            celulaAcoes.appendChild(botaoEditar);


            // BOTÃO ATIVAR / DESATIVAR

            const botaoStatus = document.createElement("button");

            botaoStatus.type = "button";

            botaoStatus.textContent = produto.ativo
                ? "⛔ Desativar"
                : "✅ Ativar";

            botaoStatus.className = produto.ativo
                ? "botao-desativar-produto"
                : "botao-ativar-produto";

            // Estilo básico, mesmo antes de
            // atualizar o arquivo CSS.

            botaoStatus.style.marginLeft = "8px";

            botaoStatus.style.padding = "8px 12px";

            botaoStatus.style.border = "none";

            botaoStatus.style.borderRadius = "6px";

            botaoStatus.style.cursor = "pointer";

            botaoStatus.style.fontWeight = "600";

            if (produto.ativo) {

                botaoStatus.style.backgroundColor = "#b45309";

                botaoStatus.style.color = "#ffffff";

            } else {

                botaoStatus.style.backgroundColor = "#15803d";

                botaoStatus.style.color = "#ffffff";

            }

            botaoStatus.addEventListener(
                "click",
                function () {
                    alterarStatusProduto(produto, botaoStatus);
                }
            );

            celulaAcoes.appendChild(botaoStatus);

            linha.appendChild(celulaAcoes);

            corpoTabela.appendChild(linha);

        });

    }


    // =====================================
    // VERIFICAR ADMINISTRADOR
    // =====================================

    async function verificarAdministrador() {

        try {

            const resposta = await fetch("/auth/me", {

                method: "GET",

                headers: {
                    "Authorization": "Bearer " + token
                }

            });

            if (!resposta.ok) {

                encerrarSessao();
                return false;

            }

            const usuario = await resposta.json();

            if (usuario.perfil !== "ADMIN") {

                alert(
                    "Acesso permitido somente para administradores."
                );

                encerrarSessao();
                return false;

            }

            const elementoUsuario = document.querySelector(
                ".usuario"
            );

            if (elementoUsuario) {

                elementoUsuario.textContent =
                    "👤 " + usuario.nome;

            }

            return true;

        } catch (erro) {

            console.error(
                "Erro ao verificar usuário:",
                erro
            );

            mostrarMensagemProdutos(
                "Não foi possível verificar sua sessão.",
                "erro"
            );

            return false;

        }

    }


    // =====================================
    // CARREGAR PRODUTOS
    // =====================================

    async function carregarProdutos() {

        botaoAtualizar.disabled = true;

        mostrarMensagemProdutos(
            "Carregando produtos..."
        );

        try {

            const resposta = await fetch("/produtos/", {

                method: "GET",

                cache: "no-store"

            });

            if (!resposta.ok) {

                throw new Error(
                    "Erro HTTP " + resposta.status
                );

            }

            const produtos = await resposta.json();

            if (!Array.isArray(produtos)) {

                throw new Error(
                    "Formato inesperado da API."
                );

            }

            preencherTabela(produtos);

            mostrarMensagemProdutos(
                produtos.length +
                " produto(s) encontrado(s).",
                "sucesso"
            );

            return true;

        } catch (erro) {

            console.error(
                "Erro ao carregar produtos:",
                erro
            );

            mostrarMensagemProdutos(
                "Não foi possível carregar os produtos.",
                "erro"
            );

            return false;

        } finally {

            botaoAtualizar.disabled = false;

        }

    }


    // =====================================
    // SALVAR CADASTRO OU EDIÇÃO
    // =====================================

    async function salvarProduto(evento) {

        evento.preventDefault();

        const idProduto = campoId.value.trim();

        const editando = idProduto !== "";

        const nome = campoNome.value.trim();

        const descricao = campoDescricao.value.trim();

        const categoria = campoCategoria.value.trim();

        const preco = Number(campoPreco.value);


        // Validação dos campos.

        if (!nome || !categoria) {

            mostrarMensagemCadastro(
                "Preencha o nome e a categoria.",
                "erro"
            );

            return;

        }

        if (!Number.isFinite(preco) || preco <= 0) {

            mostrarMensagemCadastro(
                "Informe um preço maior que zero.",
                "erro"
            );

            return;

        }


        // Dados enviados para a API.

        const dadosProduto = {
            nome: nome,
            descricao: descricao,
            preco: preco,
            categoria: categoria
        };


        // Define a rota e o método HTTP.

        const endereco = editando
            ? "/produtos/" + encodeURIComponent(idProduto)
            : "/produtos/";

        const metodo = editando
            ? "PUT"
            : "POST";


        botaoSalvar.disabled = true;

        botaoCancelar.disabled = true;

        botaoNovoProduto.disabled = true;

        mostrarMensagemCadastro(
            editando
                ? "Salvando alterações..."
                : "Cadastrando produto..."
        );


        try {

            const resposta = await fetch(endereco, {

                method: metodo,

                headers: {

                    "Content-Type": "application/json",

                    "Authorization": "Bearer " + token

                },

                body: JSON.stringify(dadosProduto)

            });


            // Sessão expirada.

            if (resposta.status === 401) {

                alert(
                    "Sua sessão expirou. Faça login novamente."
                );

                encerrarSessao();

                return;

            }


            // Sem permissão.

            if (resposta.status === 403) {

                mostrarMensagemCadastro(
                    "Você não tem permissão para realizar esta operação.",
                    "erro"
                );

                return;

            }


            // Outros erros da API.

            if (!resposta.ok) {

                let detalhe = "Erro HTTP " + resposta.status;

                try {

                    const dadosErro = await resposta.json();

                    if (typeof dadosErro.detail === "string") {

                        detalhe = dadosErro.detail;

                    }

                } catch (erroLeitura) {

                    console.error(
                        "Erro ao ler resposta:",
                        erroLeitura
                    );

                }

                throw new Error(detalhe);

            }


            // Sucesso.

            mostrarMensagemCadastro(
                editando
                    ? "Produto atualizado com sucesso!"
                    : "Produto cadastrado com sucesso!",
                "sucesso"
            );

            // Atualiza a tabela.

            await carregarProdutos();

            // Limpa o formulário e mantém a
            // mensagem de sucesso visível.

            formulario.reset();

            campoId.value = "";

            tituloFormulario.textContent =
                "➕ Cadastrar novo produto";

            descricaoFormulario.textContent =
                "Preencha os dados do novo produto.";

            botaoSalvar.textContent =
                "Salvar produto";


        } catch (erro) {

            console.error(
                "Erro ao salvar produto:",
                erro
            );

            mostrarMensagemCadastro(
                "Não foi possível salvar: " +
                erro.message,
                "erro"
            );

        } finally {

            botaoSalvar.disabled = false;

            botaoCancelar.disabled = false;

            botaoNovoProduto.disabled = false;

        }

    }


    // =====================================
    // EVENTOS DOS BOTÕES
    // =====================================

    botaoNovoProduto.addEventListener(
        "click",
        abrirCadastro
    );

    botaoCancelar.addEventListener(
        "click",
        fecharFormulario
    );

    formulario.addEventListener(
        "submit",
        salvarProduto
    );

    botaoAtualizar.addEventListener(
        "click",
        carregarProdutos
    );


    // =====================================
    // INICIAR A PÁGINA
    // =====================================

    const autorizado = await verificarAdministrador();

    if (!autorizado) {
        return;
    }

    await carregarProdutos();

});
