# Evidências de Adequação à LGPD - Projeto Portal do Aluno

Este documento detalha tecnicamente como os recursos integrados ao Portal do Aluno atendem aos requisitos da Lei Geral de Proteção de Dados (LGPD), focando no princípio da minimização e no fluxo de atendimento aos direitos do titular.

## 1. Princípio da Minimização (Art. 6º, III)
No Portal do Aluno, a coleta e exibição de dados operam estritamente com o necessário para o contexto acadêmico e administrativo:
* **Persistência de Dados:** O model `Aluno` no banco de dados foi estruturado para armazenar apenas atributos cruciais para a secretaria e comunicação legal (Nome, Nome Social, CPF, RG, contato). 
* **Mascaramento no Front-end:** Na view de "Dados Pessoais", dados críticos de identificação não são expostos em texto pleno de forma desnecessária. Utilizamos properties do model (`cpf_mascarado`, `rg_mascarado`) para exibir apenas os últimos dígitos da string na interface, garantindo a confidencialidade contra visualizações acidentais em tela.

## 2. Fluxo de Direitos do Titular (Art. 18)
Implementamos um módulo de autoatendimento (dashboard de Privacidade) para o aluno gerenciar seus dados com as seguintes implementações técnicas:

* **Transparência e Acesso Expandido:** A view de dados pessoais (`dados_pessoais`) foi projetada para varrer o banco e trazer o histórico completo de relacionamentos (matrículas passadas e ativas via `select_related`), unificando a visibilidade do titular sobre o que a instituição retém.
* **Portabilidade (Exportação em JSON):** Criamos o endpoint `/meus-dados/exportar/`. Essa view faz o parser dos dados do aluno e seu vínculo acadêmico para um dicionário Python, retornando um `JsonResponse`. O cabeçalho da resposta HTTP (`Content-Disposition: attachment`) força o download de um arquivo JSON estruturado e legível por máquina diretamente no client-side.
* **Solicitação de Exclusão e Anonimização:** Como instituições de ensino possuem obrigações legais e regulatórias de retenção de histórico escolar (MEC), não executamos um `delete()` em cascata no banco de dados. O fluxo implementado permite que o aluno acione a solicitação via front-end. O sistema registra a intenção e notifica a secretaria acadêmica, que fica responsável por executar a **anonimização irreversível** do cadastro via painel administrativo, quebrando o vínculo do CPF com o histórico sem comprometer a integridade relacional do banco.