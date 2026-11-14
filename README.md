# Portal do Aluno P.I – Gestão Acadêmica e Autoatendimento do Estudante

Sistema web de autoatendimento acadêmico e financeiro com foco em **Segurança da Informação** e **conformidade com a LGPD**, desenvolvido como Projeto Integrador da disciplina de Políticas de Segurança da Informação (UMC – Engenharia de Software).

**Integrantes:**
- Ana Gabriela Gonçalves Ribeiro – RGM: 11221103784 – Eng. Software 7°B
- Vitória Rodrigues de Souza – RGM: 11232100574 – Eng. Software 7°B

**Orientador:** Prof. Fabiano Bezerra Menegidio

| | |
|---|---|
| **Aplicação online (Vercel)** | https://portalalunopi.vercel.app/ |
| **Kanban do projeto** | [GitHub Projects do repositório](https://github.com/anagabrielaribeiro/Portal-do-Aluno-P.I/projects) |

---

## Sumário

1. [Como testar (avaliação)](#1-como-testar-avaliação)
2. [Como rodar localmente](#2-como-rodar-localmente)
3. [Variáveis de ambiente](#3-variáveis-de-ambiente)
4. [Stack tecnológica](#4-stack-tecnológica)
5. [Arquitetura](#5-arquitetura)
6. [Módulos do portal](#6-módulos-do-portal)
7. [Segurança implementada](#7-segurança-implementada)
8. [Conformidade com a LGPD](#8-conformidade-com-a-lgpd)
9. [Esteira DevSecOps](#9-esteira-devsecops)
10. [Testes automatizados](#10-testes-automatizados)
11. [Documentação](#11-documentação)
12. [Organização do trabalho e Kanban](#12-organização-do-trabalho-e-kanban)
13. [Uso de Inteligência Artificial no desenvolvimento](#13-uso-de-inteligência-artificial-no-desenvolvimento)
14. [Autoria dos commits](#14-autoria-dos-commits)
15. [Estrutura de diretórios](#15-estrutura-de-diretórios)
16. [Licença](#16-licença)

---

## 1. Como testar (avaliação)

A forma mais rápida de avaliar o sistema é pela versão publicada na Vercel:

1. Acesse https://portalalunopi.vercel.app/.
2. Clique em **Entrar no portal do aluno** e faça login com uma conta de aluno.

   > 🔒 **Por política de segurança do projeto, nenhuma credencial (e-mail, senha ou chave) é publicada neste repositório.** As contas são criadas pela área administrativa, e para testar localmente qualquer avaliador pode criar os próprios usuários seguindo a [seção 2](#criando-os-usuários-de-teste).
3. No primeiro acesso, o sistema pede a configuração do **2FA**: escaneie o QR Code com o Google Authenticator ou o Microsoft Authenticator e digite o código de 6 dígitos.
4. Aceite ou recuse as finalidades opcionais no pop-up de **consentimento LGPD**.
5. Navegue pelo menu lateral: Dados Pessoais (CPF/RG mascarados), Matrículas, Notas e Faltas, Financeiro, Calendário, Agenda, Tarefas, Documentos e Privacidade & LGPD.

**Fluxos de segurança que podem ser testados:**

| O que testar | Como |
|---|---|
| Bloqueio por força bruta | Errar a senha 5 vezes seguidas → conta bloqueada por 15 minutos |
| Bloqueio do 2FA | Errar o código de 6 dígitos 5 vezes |
| Recuperação de senha | "Esqueci minha senha" → link por e-mail válido por 1 hora e de uso único |
| Expiração de sessão | Ficar 30 minutos sem interagir → sessão encerrada |
| Exportação de dados (portabilidade) | Privacidade & LGPD → Exportar Meus Dados (JSON), com confirmação de senha |
| Revogação de consentimento | Privacidade & LGPD → botão **Revogar** |
| Área administrativa | `/login/colaborador/` (exige perfil de colaborador + 2FA) → `/gestao-portal/` |

---

## 2. Como rodar localmente

Há duas formas: **com Docker** (mais simples, não precisa instalar Python nem PostgreSQL) ou **manualmente**.

### Opção A: com Docker (recomendada)

Pré-requisito: [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e aberto.

```bash
git clone https://github.com/anagabrielaribeiro/Portal-do-Aluno-P.I.git
cd Portal-do-Aluno-P.I
cp .env.example .env        # no Windows: copy .env.example .env
```

Preencha no `.env` as chaves obrigatórias (`DJANGO_SECRET_KEY`, `CHAVE_CRIPTOGRAFIA`, `CHAVE_HASH_CPF`; os comandos para gerá-las estão no passo 6 da opção B) e escolha um `POSTGRES_USER` e um `POSTGRES_PASSWORD`. Depois:

```bash
docker compose up --build
```

O Docker sobe um PostgreSQL próprio, aplica as migrações, cria a tabela do rate limit e inicia o portal em **http://localhost:8000**. Para criar os usuários de teste ([veja abaixo](#criando-os-usuários-de-teste)), use os mesmos comandos com o prefixo `docker compose exec web`:

```bash
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py shell
docker compose exec web python manage.py test    # roda os testes automatizados
```

Para parar: `Ctrl + C` (ou `docker compose down`; para apagar também o banco, `docker compose down -v`).

> O `Dockerfile` roda a aplicação com um usuário sem privilégios (não root), e o `.dockerignore` impede que o `.env` e outros arquivos locais entrem na imagem. Nenhuma senha ou chave fica escrita nos arquivos do Docker: tudo vem do `.env`.

### Opção B: manualmente

#### Pré-requisitos

- **Python 3.12 ou superior** (o projeto foi desenvolvido em Python 3.14 e a esteira de CI roda em 3.12)
- **PostgreSQL 14 ou superior** (local, via Docker ou um banco gratuito no [Neon](https://neon.tech))
- Git

> O `settings.py` exige `DATABASE_URL` e usa o PostgreSQL como motor do banco. Isso é proposital: os **triggers de proteção dos logs de auditoria** (migração `autenticacao/0016_proteger_logs_no_banco.py`) só existem no PostgreSQL.

#### Passo a passo

```bash
# 1. Clonar o repositório
git clone https://github.com/anagabrielaribeiro/Portal-do-Aluno-P.I.git
cd Portal-do-Aluno-P.I

# 2. Criar e ativar o ambiente virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Criar o arquivo .env a partir do modelo
# Windows:
copy .env.example .env
# Linux/macOS:
cp .env.example .env
```

**5. Ter um PostgreSQL disponível** (instalado na máquina ou um banco gratuito no Neon) e colocar a URL dele em `DATABASE_URL` no `.env`.

**6. Gerar as chaves e preencher o `.env`** (veja a [seção 3](#3-variáveis-de-ambiente)):

```bash
# DJANGO_SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# CHAVE_CRIPTOGRAFIA (Fernet / AES-128)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# CHAVE_HASH_CPF
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**7. Preparar o banco e iniciar o servidor:**

```bash
python manage.py migrate
python manage.py createcachetable      # tabela usada pelo rate limit de login
python manage.py collectstatic --noinput
python manage.py runserver
```

Acesse **http://127.0.0.1:8000**.

### Criando os usuários de teste

O painel administrativo (`/gestao-portal/`) só aceita **colaboradores com 2FA**. Para criar o primeiro:

```bash
python manage.py createsuperuser
python manage.py shell
```

```python
from autenticacao.models import Usuario, Colaborador
u = Usuario.objects.get(email="SEU_EMAIL_DO_SUPERUSER")
Colaborador.objects.create(usuario=u, cargo="Secretaria")
exit()
```

Depois:

1. Entre em **http://127.0.0.1:8000/login/colaborador/** com esse e-mail e senha e configure o 2FA.
2. Em `/gestao-portal/`, cadastre um **Usuário** (com e-mail e senha de no mínimo 12 caracteres) e um **Aluno** vinculado a ele (nome, sexo, CPF, RG, data de nascimento, telefone e endereço).
3. Saia e entre com o aluno em **http://127.0.0.1:8000/entrar/**.

> **Recuperação de senha local:** o envio de e-mail usa SMTP do Gmail. Para testar localmente, preencha `EMAIL_HOST_USER` e `EMAIL_HOST_PASSWORD` com uma [senha de app do Google](https://support.google.com/accounts/answer/185833). Os demais fluxos funcionam sem isso.

---

## 3. Variáveis de ambiente

Todas as credenciais ficam fora do código, no arquivo `.env` (local) ou nas Environment Variables da Vercel (produção). O `.env` está no `.gitignore` e nunca é versionado. O modelo completo está em [`.env.example`](.env.example).

| Variável | Obrigatória | Descrição |
|---|---|---|
| `DJANGO_SECRET_KEY` | Sim | Chave secreta do Django |
| `DATABASE_URL` | Sim* | URL do PostgreSQL, ex.: `postgres://USUARIO:SENHA@localhost:5432/portal_aluno` (com Docker, é montada automaticamente) |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | Só com Docker | Banco criado pelo `docker-compose.yml` |
| `CHAVE_CRIPTOGRAFIA` | Sim | Chave Fernet usada para cifrar CPF, RG, telefone, endereço e chave do 2FA |
| `CHAVE_HASH_CPF` | Sim | Chave usada no hash do CPF (busca sem descriptografar) |
| `CHAVES_CRIPTOGRAFIA_ANTIGAS` | Não | Chaves anteriores, separadas por vírgula, usadas só durante a rotação (`python manage.py rotacionar_chaves`) |
| `DJANGO_DEBUG` | Não | `True` só em desenvolvimento (padrão: `False`) |
| `ALLOWED_HOSTS` | Não | Padrão: `.vercel.app,localhost,127.0.0.1` |
| `DATABASE_SSL_REQUIRE` | Não | `False` para Postgres local sem SSL (padrão: `True`) |
| `FORCE_HTTPS` | Não | `False` para rodar em `http://` local (padrão: `True`) |
| `BEHIND_PROXY` | Não | `False` fora da Vercel (padrão: `True`) |
| `PROXIES_CONFIAVEIS` | Não | Número de proxies confiáveis à frente da aplicação (padrão: `1`) |
| `HSTS_SECONDS` | Não | Duração do HSTS em segundos (padrão: `3600`) |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | Não* | Conta Gmail para enviar a recuperação de senha |

\* `DATABASE_URL` não precisa ser preenchida ao usar Docker. `EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD` são necessárias apenas para testar a recuperação de senha.

---

## 4. Stack tecnológica

| Categoria | Tecnologia | Versão |
|---|---|---|
| Linguagem | Python | 3.14 (compatível com 3.12+) |
| Framework web | Django | 6.1 |
| Banco de dados | PostgreSQL (Neon em produção) | 14+ |
| Hospedagem | Vercel (HTTPS forçado) | – |
| 2FA | PyOTP + qrcode | 2.10 / 8.2 |
| Criptografia | cryptography (Fernet) | 50.0.2 |
| Arquivos estáticos | WhiteNoise | 6.7 |

O **PostgreSQL** foi escolhido por ser um banco relacional robusto, nativamente suportado pelo Django, que garante integridade referencial entre alunos, matrículas, notas e parcelas, oferece campos JSON (usados nos registros de consentimento) e permite criar **triggers** que tornam os logs de auditoria imutáveis.

---

## 5. Arquitetura

O sistema é um **monólito modular** em Django, organizado no padrão **MVT (Model, View, Template)** e dividido em apps por domínio.

- **Models:** entidades e regras de persistência (alunos, matrículas, notas, parcelas, consentimentos e logs). Os dados sensíveis usam o campo `CampoCriptografado`, que cifra antes de salvar.
- **Views:** processam as requisições, validam autenticação + 2FA e aplicam o **isolamento por aluno**: cada aluno só acessa os próprios registros.
- **Templates:** interfaces responsivas que exibem apenas o que é pertinente ao perfil autenticado, com dados sensíveis mascarados.

---

## 6. Módulos do portal

| App | Responsabilidade |
|---|---|
| `autenticacao` | Login por e-mail, 2FA (TOTP), bloqueio por força bruta, sessões, login de colaborador, logs de autenticação e auditoria |
| `recuperacao_senha` | Recuperação de senha por token seguro com rate limit |
| `alunos` | Dados pessoais com criptografia em repouso e mascaramento |
| `privacidade_lgpd` | Mapeamento de dados, consentimentos, exportação e anonimização |
| `matriculas` | Matrículas ativas e históricas |
| `notas` | Notas, faltas e boletim |
| `financeiro` | Mensalidades e boletos |
| `calendario_horarios` | Calendário acadêmico e grade de horários |
| `agenda` / `tarefas` | Agenda do aluno e lista de tarefas |
| `documentos_certificados` | Declarações, documentos e certificados (com validação de upload) |

---

## 7. Segurança implementada

**Autenticação e credenciais**
- Senhas com **PBKDF2-SHA256 + salt, 1.500.000 iterações** (`config/hashers.py`), acima do mínimo recomendado pela OWASP (600.000).
- Validadores de senha: mínimo de 12 caracteres e bloqueio de senhas comuns, numéricas ou parecidas com os dados do usuário.
- **2FA obrigatório (TOTP)** com QR Code. A sessão só é criada depois do código de 6 dígitos.
- **Rate limit:** bloqueio de 15 minutos após 5 falhas na conta ou 20 falhas no mesmo IP; 2FA bloqueado após 5 códigos errados.
- Cookies `Secure`, `HttpOnly` e `SameSite=Lax`; sessão expira com 30 minutos de inatividade ou ao fechar o navegador.
- Mensagens de erro genéricas para impedir a enumeração de usuários.

**Recuperação de senha**
- Token do `default_token_generator`, válido por 1 hora e invalidado após a troca.
- Limite de 3 pedidos por hora por e-mail e 5 por hora por IP.
- E-mails mascarados nos logs (`_mascarar_email`).

**Comunicação e infraestrutura**
- HTTPS forçado e HSTS em produção; credenciais apenas em variáveis de ambiente.
- Rotação de chaves de criptografia com `python manage.py rotacionar_chaves`.

**Auditoria**
- `LogAutenticacao` (acessos, IP e resultado) e `LogAuditoria` (bloqueios, anonimizações, revogações, alterações de contato).
- Logs **append-only**: `save()`/`delete()` sobrescritos e QuerySet bloqueado no Django, além de **triggers no PostgreSQL** que impedem `UPDATE` e `DELETE` até mesmo por scripts.

---

## 8. Conformidade com a LGPD

- **Mapeamento de dados** (`privacidade_lgpd/mapeamento.py`) com finalidade e base legal de cada dado (obrigação legal, execução de contrato, consentimento).
- **Minimização:** CPF e RG exibidos mascarados (ex.: `529.***.***-25`).
- **Criptografia em repouso (Fernet/AES-128):** CPF, RG, telefone, endereço e chave do 2FA ilegíveis no banco.
- **Consentimento:** pop-up no primeiro acesso e painel para revogar a qualquer momento.
- **Portabilidade:** exportação completa em JSON, com confirmação de senha.
- **Direito à exclusão:** anonimização irreversível em uma única transação (`@transaction.atomic`), mantendo apenas o que a instituição é obrigada a guardar (histórico financeiro).

---

## 9. Esteira DevSecOps

A cada `push` e `pull request`, o GitHub Actions executa:

| Workflow | Ferramenta | Tipo | O que faz |
|---|---|---|---|
| `devsecops-pipeline.yml` | **TruffleHog** | Segredos | Bloqueia commits com credenciais expostas |
| `devsecops-pipeline.yml` | **Trivy** | SCA / SBOM | Analisa vulnerabilidades nas dependências e gera `sbom.json` (CycloneDX) |
| `devsecops-pipeline.yml` | **Semgrep** | SAST | Regras de Python e Django; bloqueia padrões inseguros |
| `devsecops-avancado.yml` | **OWASP ZAP** | DAST | Sobe a aplicação com PostgreSQL temporário e ataca em execução; exceções justificadas em `.zap/rules.tsv` |
| `devsecops-avancado.yml` | **Bearer** | Privacidade / SAST | Detecta vazamento de dados pessoais e segredos |

Os relatórios ficam disponíveis como artefatos na aba **Actions**.

---

## 10. Testes automatizados

O projeto tem **89 testes** cobrindo autenticação, 2FA, bloqueios, recuperação de senha, criptografia, LGPD e isolamento de dados entre alunos.

```bash
python manage.py test
```

---

## 11. Documentação

Toda a documentação está na pasta [`docs/`](docs/):

| Documento | Conteúdo |
|---|---|
| Poster - Portal do Aluno PI.pdf | Pôster apresentado no UMC Summit |
| Resumo - Portal do Aluno PI.pdf | Resumo científico (português, inglês e espanhol) |
| Documentação Técnico-Científica - Portal do Aluno P.I. | Documento principal do projeto |
| Requisitos - Projeto Integrador - 12.08.2026 | Requisitos funcionais e não funcionais |
| Documentação Técnica - Login e Autentificação | Login, 2FA, sessões e força bruta |
| Documentação Técnica - Recuperação de senha | Fluxo de recuperação e rate limit |
| Documentação Técnica - Lei Geral de Proteção de Dados Pessoais | Mapeamento, consentimento, portabilidade e anonimização |
| Documentação Técnica - Logs de Segurança | Auditoria e logs imutáveis |
| Relatório Técnico DevSecOps (1 e 2) | Esteiras de segurança no GitHub Actions |

---

## 12. Organização do trabalho e Kanban

A divisão e o andamento das tarefas foram acompanhados no Kanban do **GitHub Projects**, vinculado a este repositório: [GitHub Projects do repositório](https://github.com/anagabrielaribeiro/Portal-do-Aluno-P.I/projects).

O desenvolvimento seguiu um fluxo incremental com **branches, pull requests e releases versionadas** (de `v1.0.0`, em agosto, até a versão final), o que pode ser conferido no histórico de commits e na aba **Releases**.

---

## 13. Uso de Inteligência Artificial no desenvolvimento

<!-- REVISEM ESTA SEÇÃO para que descreva exatamente como vocês usaram a IA. -->

Ferramentas de IA generativa foram usadas como **apoio** ao desenvolvimento, e não como substitutas das decisões técnicas da equipe. O uso seguiu os seguintes princípios:

- **Decisões de arquitetura e segurança tomadas pela equipe**, com base em fontes oficiais: OWASP (Authentication, Password Storage e Session Management Cheat Sheets), documentação do Django, RFC 6238 (TOTP) e o texto da LGPD (Lei 13.709/2018).
- **A IA como apoio pontual:** tirar dúvidas, explicar conceitos, sugerir trechos de código e ajudar a revisar textos.
- **Todo código sugerido foi lido, adaptado e testado** antes de entrar no repositório. Nada foi aceito sem entendimento de como funciona.
- **Validação automática independente da IA:** 89 testes automatizados e uma esteira com cinco ferramentas de segurança (TruffleHog, Trivy, Semgrep, OWASP ZAP e Bearer) que barram código inseguro, tenha ele sido escrito por pessoas ou sugerido por IA.
- **Revisão em dupla** por pull requests antes do merge na `main`.

Essa abordagem segue a ideia de *vibe coding* com responsabilidade: a IA acelera a escrita, mas a fundamentação teórica, a revisão e a validação continuam humanas e verificáveis.

---

## 14. Autoria dos commits

Por causa de configurações diferentes do Git em computadores distintos, os commits aparecem com mais de um nome:

| Nome no commit | Integrante |
|---|---|
| Ana Gabriela / Ana Gabriela Ribeiro | Ana Gabriela Gonçalves Ribeiro |
| Vitor / vitoria souza / Vitoria Rodrigues de Souza / Vitória Rodrigues | Vitória Rodrigues de Souza |

---

## 15. Estrutura de diretórios

```text
Portal-do-Aluno-P.I/
├── manage.py
├── requirements.txt
├── README.md
├── LICENSE
├── .env.example                 # modelo das variáveis de ambiente
├── Dockerfile                   # imagem da aplicação (usuário sem privilégios)
├── docker-compose.yml           # aplicação + PostgreSQL local
├── .dockerignore
├── .gitignore
├── .github/workflows/
│   ├── devsecops-pipeline.yml   # TruffleHog, Trivy e Semgrep
│   └── devsecops-avancado.yml   # OWASP ZAP e Bearer
├── .zap/rules.tsv               # alertas do ZAP aceitos, com justificativa
├── config/                      # settings, urls, hasher PBKDF2 e admin protegido
├── docs/                        # documentação, pôster e resumo
├── autenticacao/                # login, 2FA, logs e comando rotacionar_chaves
├── recuperacao_senha/
├── alunos/                      # CampoCriptografado e validadores
├── privacidade_lgpd/            # mapeamento, consentimentos, exportação
├── matriculas/  notas/  financeiro/
├── calendario_horarios/  agenda/  tarefas/
├── documentos_certificados/
├── templates/                   # HTML por app
└── static/                      # CSS, JS e imagens
```

---

## 16. Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE).
