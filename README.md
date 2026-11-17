# Portal do Aluno P.I

![Python](https://img.shields.io/badge/Python-3.14-blue.svg)
![Django](https://img.shields.io/badge/Django-6.1-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-blue.svg)
![Vercel](https://img.shields.io/badge/Deploy-Vercel-black.svg)

Sistema web de autoatendimento acadêmico e financeiro, desenvolvido como Projeto Integrador de Políticas de Segurança da Informação (UMC).

## Integrantes

- Ana Gabriela Gonçalves Ribeiro - RGM: 11221103784 - Eng. Software 7°B
- Vitória Rodrigues de Souza - RGM: 11232100574 - Eng. Software 7°B

Orientador: Prof. Fabiano Bezerra Menegidio

## Acessar o sistema

- Versão online: [portalalunopi.vercel.app](https://portalalunopi.vercel.app/)
- Kanban: [GitHub Projects](https://github.com/anagabrielaribeiro/Portal-do-Aluno-P.I/projects)

Nenhum login, senha ou chave fica no repositório. As contas são criadas pela área administrativa.

## O que foi implementado

- hash de senha com PBKDF2-SHA256 e salt (1.500.000 iterações);
- 2FA (TOTP) obrigatório, com QR Code e bloqueio por tentativas inválidas;
- bloqueio de força bruta no login (15 minutos após 5 erros na conta ou 20 no IP);
- sessão com cookies seguros e expiração após 30 minutos sem uso;
- recuperação de senha com token de 1 hora, uso único e limite de pedidos;
- criptografia em repouso (Fernet) de CPF, RG, telefone, endereço e chave do 2FA;
- LGPD: consentimento, revogação, exportação dos dados em JSON e anonimização;
- logs de auditoria imutáveis, protegidos no código e por triggers no PostgreSQL;
- esteira DevSecOps no GitHub Actions com TruffleHog, Trivy, Semgrep, OWASP ZAP e Bearer.

## Documentação

| Documento | Conteúdo |
|---|---|
| [Requisitos](docs/Requisitos%20-%20Projeto%20Integrador%20-%2012.08.2026.docx) | Requisitos funcionais e não funcionais |
| [Documentação Técnico-Científica](docs/Documenta%C3%A7%C3%A3o%20T%C3%A9cnico-Cient%C3%ADfica%20-%20Portal%20do%20Aluno%20P.I..docx) | Documento principal do projeto |
| [Login e Autenticação](docs/Documenta%C3%A7%C3%A3o%20T%C3%A9cnica%20-%20Login%20e%20Autentifica%C3%A7%C3%A3o.docx) | Hash, 2FA, sessão e força bruta |
| [Recuperação de Senha](docs/Documenta%C3%A7%C3%A3o%20T%C3%A9cnica%20-%20Recupera%C3%A7%C3%A3o%20de%20senha.docx) | Token e limite de pedidos |
| [LGPD](docs/Documenta%C3%A7%C3%A3o%20T%C3%A9cnica%20-%20Lei%20Geral%20de%20Prote%C3%A7%C3%A3o%20de%20Dados%20Pessoais.docx) | Consentimento, exportação e anonimização |
| [Logs de Segurança](docs/Documenta%C3%A7%C3%A3o%20T%C3%A9cnica%20-%20Logs%20de%20Seguran%C3%A7a.docx) | Auditoria e logs imutáveis |
| [Relatório DevSecOps](docs/Relat%C3%B3rio%20T%C3%A9cnico%20DevSecOps%20-%20Portal%20do%20ALuno%20PI.docx) e [Relatório DevSecOps 2](docs/Relat%C3%B3rio%20T%C3%A9cnico%20DevSecOps%202%20-%20Portal%20do%20Aluno%20PI.docx) | Esteiras de segurança |
| [Pôster](docs/Poster%20-%20Portal%20do%20Aluno%20PI.pdf) e [Resumo](docs/Resumo%20-%20Portal%20do%20Aluno%20PI.pdf) | Apresentação no UMC Summit |

## Stack tecnológica

| Categoria | Tecnologia | Versão |
| :--- | :--- | :--- |
| Linguagem | Python | 3.14 |
| Framework web | Django | 6.1 |
| Banco de dados | PostgreSQL (Neon) | 18 |
| Segundo fator (TOTP) | `pyotp` + `qrcode` | 2.10 + 8.2 |
| Criptografia em repouso | `cryptography` (Fernet) | 50.0.2 |
| Arquivos estáticos | `whitenoise` | 6.7 |
| Hospedagem | Vercel | - |

## Arquitetura

O sistema usa a arquitetura **MVT (Model, View, Template)** do Django e é dividido em apps:

```text
Portal-do-Aluno-P.I/
├── .github/workflows/
│   ├── devsecops-pipeline.yml  # TruffleHog, Trivy e Semgrep
│   └── devsecops-avancado.yml  # OWASP ZAP e Bearer
├── .zap/rules.tsv            # alertas do ZAP aceitos, com justificativa
├── config/                   # settings, urls e hasher PBKDF2
├── autenticacao/             # login, 2FA, sessões, colaboradores e logs
├── recuperacao_senha/        # recuperação de senha
├── alunos/                   # dados pessoais cifrados
├── privacidade_lgpd/         # consentimentos, exportação e anonimização
├── matriculas/ notas/ financeiro/
├── calendario_horarios/ agenda/ tarefas/
├── documentos_certificados/
├── templates/ static/
├── docs/                     # documentação, pôster e resumo
└── .env.example
```

## Para rodar o projeto localmente

Precisa de Python 3.12 ou superior e de um PostgreSQL (local ou no Neon). Não roda com SQLite, porque os triggers dos logs de auditoria são do PostgreSQL. Os comandos para gerar as chaves do `.env` estão no próprio `.env.example`.

```bash
git clone https://github.com/anagabrielaribeiro/Portal-do-Aluno-P.I.git
cd Portal-do-Aluno-P.I
python -m venv venv
venv\Scripts\activate      # Windows (no Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env     # preencha, incluindo a DATABASE_URL
python manage.py migrate
python manage.py createcachetable
python manage.py runserver
```

### Primeiro acesso

O painel `/gestao-portal/` só aceita colaboradores com 2FA. Crie um superusuário e vincule ele a um colaborador:

```bash
python manage.py createsuperuser
python manage.py shell -c "from autenticacao.models import Usuario, Colaborador; Colaborador.objects.create(usuario=Usuario.objects.get(email='SEU_EMAIL'), cargo='Secretaria')"
```

Depois entre em `/login/colaborador/`, configure o 2FA e cadastre os alunos pelo painel. No primeiro login o aluno também configura o 2FA.

## Testes

```bash
python manage.py test
```

## Organização do trabalho

As tarefas foram acompanhadas no Kanban do GitHub Projects e o desenvolvimento foi feito com branches, pull requests e releases. Alguns commits aparecem com nomes diferentes por causa da configuração do Git em computadores diferentes: "Vitor", "vitoria souza", "Vitoria Rodrigues de Souza" e "Vitória Rodrigues" são da Vitória; "Ana Gabriela" e "Ana Gabriela Ribeiro" são da Ana.

## Uso de IA

Usamos ferramentas de IA como apoio para tirar dúvidas, entender conceitos, sugerir trechos de código e revisar textos. As decisões de segurança seguiram a OWASP, a documentação do Django, a RFC 6238 (TOTP) e a LGPD (Lei 13.709/2018). Todo código sugerido foi lido, adaptado e testado, e passa pelos testes automatizados e pela esteira de segurança antes de entrar na `main`.

## Licença

MIT. Veja [LICENSE](LICENSE).
