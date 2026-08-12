# Portal do Aluno P.I

Sistema web para autoatendimento, acompanhamento acadêmico e serviços ao estudante.

## Stack tecnológica

A aplicação será desenvolvida utilizando **Python** como linguagem principal e **Django** como framework web. O banco de dados utilizado será o **PostgreSQL** para o ambiente de produção e **SQLite** para desenvolvimento inicial.

As versões foram selecionadas com base nas versões LTS (Suporte de Longo Prazo) mais estáveis para garantir segurança, desempenho e suporte a longo prazo.

| Categoria | Tecnologia | Versão |
|---|---|---|
| Linguagem de programação | Python | 3.12.x |
| Framework web | Django | 5.0.x |
| Banco de dados | PostgreSQL | 16.x |

### Escolha do Banco de Dados (PostgreSQL)
O **PostgreSQL** foi escolhido por ser um banco de dados relacional (RDBMS) de altíssimo desempenho, robusto e nativamente suportado pelo Django. Ele atende perfeitamente à necessidade de manter a integridade referencial entre alunos, matrículas, notas, parcelas e históricos acadêmicos, garantindo consultas rápidas e suporte nativo a campos JSON (ideal para guardar preferências de acessibilidade e logs de LGPD).

## Arquitetura da aplicação

O sistema utilizará a arquitetura **MVT — Model, View e Template**, padrão do framework Django. Essa arquitetura organiza a aplicação em responsabilidades separadas, facilitando a manutenção, a evolução e a organização do código.

### Model

Os **Models** representam os dados e as regras relacionadas à persistência das informações acadêmicas do aluno. Eles serão responsáveis por definir as entidades do sistema, seus campos, relacionamentos e comportamentos associados ao banco de dados PostgreSQL.

Exemplos de entidades que poderão ser representadas por Models incluem dados do aluno, solicitações de matrícula, notas, boletos, tarefas do estudante e documentos.

### View

As **Views** serão responsáveis por processar as requisições, aplicar as regras de negócio do portal, consultar os dados restritos ao aluno autenticado e encaminhar as informações para os Templates apropriados.

As Views também deverão garantir a segurança e a privacidade dos dados, permitindo que cada estudante visualize estritamente os seus próprios registros acadêmicos e financeiros.

### Template

Os **Templates** serão responsáveis pela apresentação das informações ao estudante[cite: 2]. Neles serão construídas as interfaces web e mobile-friendly, menus, tabelas de notas, calendários e cartões visuais com foco em usabilidade e acessibilidade (UX/UI).

Os Templates deverão exibir somente as funcionalidades compatíveis com o perfil de acesso do aluno.

## Módulos e Aplicativos (Apps)

O sistema será dividido em aplicações independentes, chamadas de **apps**, seguindo a organização recomendada pelo Django[cite: 2]. Cada app deverá agrupar funcionalidades relacionadas a um determinado domínio do portal[cite: 2].

### Funcionalidades do Portal do Aluno:
* **Matrícula:** Consulta de matrículas ativas e controle de **matrícula inativa**.
* **Desempenho Acadêmico:** Visualização detalhada de **notas** e **frequência**.
* **Financeiro:** Consulta de mensalidades e **emissão do boleto** / cópia de chave Pix.
* **Calendário & Horários:** **Calendário** acadêmico e **horário de aulas** (exibindo nome do docente, disciplina e curso).
* **Documentação & Secretaria:** Consulta de **dados pessoais e documentação** (envio/visualização de RG, emissão de **declaração de matrícula**).
* **Certificados & Tarefas:** Emissão e validação de **certificados** e **lista de tarefas** integrada para gestão de estudos do aluno.

A divisão final dos apps seguirá uma estrutura semelhante à apresentada abaixo:

```text
portal_aluno/
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── autenticacao/
├── alunos/
├── matriculas/
├── notas/
├── financeiro/
├── calendario_horarios/
├── documentos_certificados/
├── tarefas/
├── templates/
├── static/
└── requirements.txt
