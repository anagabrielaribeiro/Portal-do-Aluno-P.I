# Portal do Aluno P.I - Gestão Acadêmica e Autoatendimento do Estudante

**Integrantes:**
- Ana Gabriela Gonçalves Ribeiro - RGM: 11221103784 - Eng. Software 7°B
- Vitória Rodrigues de Souza - RGM: 11232100574 - Eng. Software 7°B

**Orientador:** Prof. Fabiano Bezerra Menegidio

Sistema web para autoatendimento, acompanhamento acadêmico, financeiro, documental e serviços integrados ao estudante, desenvolvido como Projeto Integrador da disciplina de Políticas de Segurança da Informação. O foco do projeto é a autenticação segura, a proteção das credenciais e a conformidade com a LGPD.

- Aplicação publicada: https://portalalunopi.vercel.app/
- Kanban do projeto: [GitHub Projects](https://github.com/anagabrielaribeiro/Portal-do-Aluno-P.I/projects)
- Pôster, resumo e documentação técnica: pasta [docs](docs/)

## Como testar

O jeito mais simples de testar é pela versão publicada na Vercel. Ao entrar com uma conta de aluno, o sistema pede a configuração do 2FA no primeiro acesso (pelo QR Code, usando o Google Authenticator ou o Microsoft Authenticator) e depois mostra o pop-up de consentimento da LGPD. Em seguida o aluno tem acesso ao menu com dados pessoais, matrículas, notas e faltas, financeiro, calendário, agenda, tarefas, documentos e privacidade.

Por questão de segurança, não deixamos nenhum login, senha ou chave no repositório. As contas são criadas pela área administrativa, e quem quiser rodar o projeto na própria máquina consegue criar os usuários seguindo os passos abaixo.

Alguns fluxos de segurança que podem ser testados:

- Errar a senha 5 vezes seguidas bloqueia a conta por 15 minutos.
- Errar o código do 2FA 5 vezes também bloqueia a verificação.
- Em "Esqueci minha senha" o link chega por e-mail, vale por 1 hora e só pode ser usado uma vez.
- Depois de 30 minutos sem uso, a sessão expira.
- Em Privacidade e LGPD o aluno pode exportar os dados em JSON (pedindo a senha de novo) e revogar consentimentos.
- A área administrativa fica em `/gestao-portal/` e só aceita colaboradores que entraram por `/login/colaborador/` com 2FA.

## Como rodar localmente

### Com Docker

Essa é a forma mais fácil, porque não precisa instalar Python nem PostgreSQL. É preciso ter o [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e aberto.

```bash
git clone https://github.com/anagabrielaribeiro/Portal-do-Aluno-P.I.git
cd Portal-do-Aluno-P.I
cp .env.example .env
```

No Windows, o último comando é `copy .env.example .env`.

Depois é só preencher o `.env` (as chaves podem ser geradas com os comandos da seção "Gerando as chaves") e escolher um usuário e uma senha para o banco em `POSTGRES_USER` e `POSTGRES_PASSWORD`. Para subir:

```bash
docker compose up --build
```

O Docker cria um PostgreSQL só para o projeto, roda as migrações e deixa o portal em http://localhost:8000. Para os outros comandos do Django, basta colocar `docker compose exec web` na frente, por exemplo:

```bash
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py test
```

Para parar, use `Ctrl + C`. O comando `docker compose down -v` apaga também o banco local.

O Dockerfile roda a aplicação com um usuário sem privilégios, e o `.dockerignore` evita que o `.env` vá para dentro da imagem.

### Sem Docker

É preciso ter Python 3.12 ou superior (desenvolvemos em 3.14 e a esteira usa 3.12) e um PostgreSQL, que pode ser instalado na máquina ou criado de graça no [Neon](https://neon.tech). O projeto não roda com SQLite porque os triggers que protegem os logs de auditoria só existem no PostgreSQL.

```bash
git clone https://github.com/anagabrielaribeiro/Portal-do-Aluno-P.I.git
cd Portal-do-Aluno-P.I

python -m venv venv
venv\Scripts\activate          # no Linux/macOS: source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env         # no Linux/macOS: cp .env.example .env
```

Com o `.env` preenchido (incluindo a `DATABASE_URL` do seu PostgreSQL):

```bash
python manage.py migrate
python manage.py createcachetable
python manage.py collectstatic --noinput
python manage.py runserver
```

O portal fica em http://127.0.0.1:8000.

### Gerando as chaves

```bash
# DJANGO_SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# CHAVE_CRIPTOGRAFIA
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# CHAVE_HASH_CPF
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Criando os usuários de teste

O painel administrativo só aceita colaboradores com 2FA, então o primeiro precisa ser criado pelo terminal. Primeiro crie um superusuário com `python manage.py createsuperuser` e depois vincule ele a um colaborador:

```bash
python manage.py shell -c "from autenticacao.models import Usuario, Colaborador; Colaborador.objects.create(usuario=Usuario.objects.get(email='SEU_EMAIL'), cargo='Secretaria')"
```

Com isso, entre em http://127.0.0.1:8000/login/colaborador/, configure o 2FA e, em `/gestao-portal/`, cadastre um usuário (senha com pelo menos 12 caracteres) e um aluno vinculado a ele. Depois é só sair e entrar com o aluno em `/entrar/`.

A recuperação de senha envia e-mail pelo Gmail, então para testar ela localmente é preciso preencher `EMAIL_HOST_USER` e `EMAIL_HOST_PASSWORD` com uma senha de app do Google. O resto funciona sem isso.

## Variáveis de ambiente

Nenhuma credencial fica no código. Localmente elas ficam no `.env`, que está no `.gitignore`, e em produção ficam nas variáveis de ambiente da Vercel. O arquivo `.env.example` tem o modelo.

| Variável | Para que serve |
|---|---|
| `DJANGO_SECRET_KEY` | Chave secreta do Django (obrigatória) |
| `DATABASE_URL` | Endereço do PostgreSQL (obrigatória sem Docker) |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Banco criado pelo Docker |
| `CHAVE_CRIPTOGRAFIA` | Chave Fernet que cifra CPF, RG, telefone, endereço e a chave do 2FA (obrigatória) |
| `CHAVE_HASH_CPF` | Usada no hash do CPF, para buscar sem descriptografar (obrigatória) |
| `CHAVES_CRIPTOGRAFIA_ANTIGAS` | Chaves antigas, usadas só na rotação com `python manage.py rotacionar_chaves` |
| `DJANGO_DEBUG` | `True` apenas em desenvolvimento |
| `ALLOWED_HOSTS` | Domínios aceitos (padrão: `.vercel.app,localhost,127.0.0.1`) |
| `DATABASE_SSL_REQUIRE`, `FORCE_HTTPS`, `BEHIND_PROXY` | Colocar `False` para rodar local sem HTTPS |
| `PROXIES_CONFIAVEIS`, `HSTS_SECONDS` | Ajustes de proxy e HSTS em produção |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Conta do Gmail usada na recuperação de senha |

## Stack tecnológica

A aplicação foi desenvolvida em **Python** com o framework **Django**. Em produção usamos **PostgreSQL** hospedado no Neon, e o sistema fica publicado na **Vercel**, com HTTPS forçado.

| Categoria | Tecnologia | Versão |
|---|---|---|
| Linguagem | Python | 3.14 |
| Framework web | Django | 6.1 |
| Banco de dados | PostgreSQL (Neon) | 18 |
| 2FA | PyOTP e qrcode | 2.10 / 8.2 |
| Criptografia | cryptography (Fernet) | 50.0.2 |

### Escolha do banco de dados

O PostgreSQL foi escolhido por ser um banco relacional robusto e com suporte nativo no Django. Ele atende bem à necessidade de manter a integridade entre alunos, matrículas, notas e parcelas, tem suporte a campos JSON (que usamos nos registros de consentimento da LGPD) e permite criar triggers, que usamos para impedir que os logs de auditoria sejam alterados ou apagados.

## Arquitetura

O sistema usa a arquitetura **MVT (Model, View e Template)**, padrão do Django, e é dividido em apps por assunto.

Os **Models** representam os dados do sistema (alunos, matrículas, notas, parcelas, consentimentos e logs). Os dados sensíveis usam um campo próprio, o `CampoCriptografado`, que cifra a informação antes de salvar no banco.

As **Views** processam as requisições, conferem o login e o 2FA e garantem que cada aluno só veja os próprios dados. Também impedem que o aluno altere informações acadêmicas ou financeiras, que são de responsabilidade da instituição.

Os **Templates** montam as telas, que são responsivas e mostram só o que faz sentido para o perfil logado, com CPF e RG mascarados.

### Módulos

- `autenticacao`: login por e-mail, 2FA, bloqueio por força bruta, sessões, login de colaborador e logs
- `recuperacao_senha`: recuperação de senha por token com limite de pedidos
- `alunos`: dados pessoais com criptografia e mascaramento
- `privacidade_lgpd`: mapeamento dos dados, consentimentos, exportação e anonimização
- `matriculas`, `notas`, `financeiro`: matrículas, notas e faltas, mensalidades e boletos
- `calendario_horarios`, `agenda`, `tarefas`: calendário acadêmico, horários, agenda e lista de tarefas
- `documentos_certificados`: declarações, documentos e certificados

## Segurança

**Senhas.** As senhas são guardadas com PBKDF2-SHA256 e salt, com 1.500.000 iterações (`config/hashers.py`). A OWASP recomenda no mínimo 600.000. Também bloqueamos senhas com menos de 12 caracteres, senhas comuns, só numéricas ou parecidas com os dados do usuário.

**2FA.** Depois da senha, o usuário precisa digitar o código TOTP de 6 dígitos gerado pelo aplicativo autenticador. A sessão só é criada depois dessa etapa.

**Força bruta.** A conta fica bloqueada por 15 minutos após 5 tentativas erradas, e o IP após 20. O 2FA também é bloqueado depois de 5 códigos errados. As mensagens de erro são genéricas, para não revelar se o e-mail existe.

**Sessão.** Os cookies são `Secure`, `HttpOnly` e `SameSite=Lax`. A sessão expira com 30 minutos sem uso ou quando o navegador é fechado.

**Recuperação de senha.** O token dura 1 hora e deixa de valer depois que a senha é trocada. São aceitos no máximo 3 pedidos por hora para o mesmo e-mail e 5 por hora do mesmo IP, e o e-mail aparece mascarado nos logs.

**Logs de auditoria.** Temos o `LogAutenticacao`, que registra os acessos, e o `LogAuditoria`, que registra bloqueios, anonimizações, revogações e alterações de contato. Os dois só aceitam inserção: o `save()` e o `delete()` foram sobrescritos no Django e, além disso, triggers no PostgreSQL impedem `UPDATE` e `DELETE` direto no banco.

**Chaves.** As chaves de criptografia podem ser trocadas com o comando `python manage.py rotacionar_chaves`, que recifra os dados com a chave nova.

## LGPD

- Cada dado pessoal tem finalidade e base legal mapeadas em `privacidade_lgpd/mapeamento.py`.
- CPF e RG aparecem mascarados na tela (ex.: `529.***.***-25`).
- CPF, RG, telefone, endereço e a chave do 2FA ficam cifrados no banco com Fernet (AES-128).
- No primeiro acesso aparece o pop-up de consentimento, e o aluno pode revogar a qualquer momento.
- O aluno pode exportar todos os seus dados em JSON, confirmando a senha antes.
- O pedido de exclusão anonimiza os dados em uma única transação (`@transaction.atomic`). Não fazemos a exclusão física porque o histórico financeiro precisa ser mantido pela instituição.

## Esteira DevSecOps

A cada push e pull request o GitHub Actions roda duas esteiras:

- `devsecops-pipeline.yml`: TruffleHog (procura segredos no código), Trivy (vulnerabilidades nas dependências) e Semgrep (análise estática com regras de Python e Django).
- `devsecops-avancado.yml`: OWASP ZAP (sobe a aplicação com um PostgreSQL temporário e testa ela rodando) e Bearer (procura vazamento de dados pessoais). Os alertas do ZAP que aceitamos estão justificados em `.zap/rules.tsv`.

Se alguma ferramenta encontrar problema, a esteira falha. Os relatórios ficam na aba Actions.

## Testes

O projeto tem 89 testes automatizados, que cobrem login, 2FA, bloqueios, recuperação de senha, criptografia, LGPD e o isolamento entre alunos (um aluno não consegue ver nem alterar os dados de outro).

```bash
python manage.py test
```

## Documentação

Na pasta [docs](docs/) estão o pôster, o resumo, os requisitos, a documentação técnico-científica, as documentações técnicas de login, recuperação de senha, LGPD e logs, e os dois relatórios técnicos de DevSecOps.

## Organização do trabalho

As tarefas foram divididas e acompanhadas no [Kanban do GitHub Projects](https://github.com/anagabrielaribeiro/Portal-do-Aluno-P.I/projects). O desenvolvimento foi feito aos poucos, com branches, pull requests e releases desde a v1.0.0, em agosto.

Alguns commits aparecem com nomes diferentes por causa da configuração do Git em computadores diferentes. Os commits de "Vitor", "vitoria souza", "Vitoria Rodrigues de Souza" e "Vitória Rodrigues" são todos da Vitória, e os de "Ana Gabriela" e "Ana Gabriela Ribeiro" são da Ana.

## Uso de IA

Usamos ferramentas de IA como apoio durante o desenvolvimento, para tirar dúvidas, entender conceitos, sugerir trechos de código e revisar textos. As decisões de segurança foram baseadas nas recomendações da OWASP, na documentação do Django, na RFC 6238 (TOTP) e na própria LGPD (Lei 13.709/2018).

Todo código sugerido foi lido, adaptado e testado antes de ir para o repositório. Além disso, os testes automatizados e as ferramentas da esteira (TruffleHog, Trivy, Semgrep, ZAP e Bearer) verificam o código independentemente de quem escreveu, e as alterações passaram por pull request antes de entrar na `main`.

## Licença

MIT. Veja o arquivo [LICENSE](LICENSE).
