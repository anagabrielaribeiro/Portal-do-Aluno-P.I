# Portal do Aluno P.I - Gestão Acadêmica e Autoatendimento do Estudante

Sistema web para autoatendimento, acompanhamento acadêmico, financeiro, documental e serviços integrados ao estudante.

## Stack tecnológica

A aplicação será desenvolvida utilizando **Python** como linguagem principal e **Django** como framework web. O banco de dados utilizado será o **PostgreSQL** para o ambiente de produção e **SQLite** para desenvolvimento e testes iniciais.

As versões foram selecionadas com base em distribuições estáveis e de suporte de longo prazo (LTS), garantindo compatibilidade com os requisitos de segurança, criptografia e conformidade com a LGPD.

| Categoria | Tecnologia | Versão |
|---|---|---|
| Linguagem de programação | Python | A definir |
| Framework web | Django | A definir |
| Banco de dados (Produção) | PostgreSQL | A definir |
| Banco de dados (Desenvolvimento) | SQLite | A definir |

### Escolha do Banco de Dados (PostgreSQL)
O **PostgreSQL** foi escolhido por ser um banco de dados relacional (RDBMS) de altíssimo desempenho, robusto e nativamente suportado pelo Django. Ele atende perfeitamente à necessidade de manter a integridade referencial entre alunos, matrículas, notas, parcelas, boletins e históricos acadêmicos, garantindo consultas isoladas por aluno, suporte nativo a campos JSON (ideal para preferências de acessibilidade e logs de consentimento da LGPD) e alto desempenho em transações.

## Arquitetura da aplicação

O sistema utilizará a arquitetura **MVT — Model, View e Template**, padrão nativo do framework Django. Essa arquitetura organiza a aplicação em responsabilidades separadas, facilitando a manutenção, a evolução, os testes e a auditoria do código.

### Model

Os **Models** representam as entidades de dados, as validações de integridade e as regras relacionadas à persistência das informações acadêmicas e pessoais do aluno. Eles serão responsáveis por mapear tabelas no PostgreSQL para alunos, matrículas, notas, faltas, mensalidades, boletins, calendários, tarefas, certificados, registros de consentimento (LGPD) e logs de auditoria.

### View

As **Views** serão responsáveis por processar as requisições HTTP, aplicar as regras de negócio do portal, validar a autenticação primária e o duplo fator (2FA), aplicar o isolamento estrito de dados por aluno (impedindo o acesso a registros de terceiros) e encaminhar os dados para os Templates ou respostas JSON.

As Views também garantirão que o aluno não possa realizar alterações em dados acadêmicos ou financeiros de responsabilidade exclusiva da instituição.

### Template

Os **Templates** serão responsáveis pela apresentação visual e interativa das informações ao estudante. Neles serão construídas as interfaces web responsivas (compatíveis com celulares, tablets e computadores), menus de navegação, dashboards com resumos de aulas/tarefas, tabelas de notas e formulários acessíveis.

Os Templates exibirão somente as funcionalidades, botões e documentos pertinentes ao perfil do aluno autenticado.

## Módulos e Aplicativos (Apps)

O sistema será dividido em aplicações independentes, chamadas de **apps**, seguindo a organização modular recomendada pelo Django. Cada app agrupamentos funcionais de um determinado domínio do portal.

### Principais Módulos do Portal do Aluno:
* **Autenticação & Segurança:** Fluxo de login, logout, recuperação de senha via token seguro, autenticação de dois fatores (2FA), controle de sessões e rate limit contra força bruta.
* **Minhas Matrículas:** Consulta de matrículas ativas, vínculo com cursos, turmas, períodos e histórico de matrículas inativas.
* **Notas, Faltas e Boletim:** Visualização de notas e frequências por disciplina/componente, acompanhamento do percentual de faltas e geração/impressão do boletim acadêmico.
* **Financeiro & Boletos:** Consulta de mensalidades (situação: paga, pendente ou vencida), código de pagamento, histórico financeiro e emissão de boletos.
* **Calendário & Horário de Aulas:** Calendário acadêmico com eventos/feriados por mês e grade de horários detalhada com nome da disciplina, docente responsável, sala, turma e curso.
* **Agenda & Tarefas:** Criação e acompanhamento de tarefas (pendentes/concluídas) e integração com datas de provas e trabalhos.
* **Documentos & Certificados:** Acesso e emissão da declaração de matrícula, visualização de documentos pessoais cadastrados (RG), download de arquivos institucionais e inclusão/consulta de certificados.
* **Privacidade & LGPD:** Painel para consulta de dados pessoais cadastrados, gestão/revogação de consentimento e solicitação de exportação ou exclusão de dados pessoais.

A estrutura de diretórios do projeto seguirá a organização abaixo:

```text
portal_aluno/
|-- settings.py manage.py
|-- settings.py config/
│   |-- settings.py
│   |-- urls.py
│   |-- asgi.py
│   |-- wsgi.py
|-- autenticacao/
|-- alunos/
|-- matriculas/
|-- notas/
|-- financeiro/
|-- calendario_horarios/
|-- agenda/
|-- documentos_certificados/
|-- tarefas/
|-- privacidade_lgpd/
|-- templates/
|-- static/
|-- requirements.txt
```


**Integrantes:**
- Ana Gabriela Gonçalves Ribeiro - RGM: 11221103784 - Eng. Software 7°B
- Vitória Rodrigues de Souza - RGM: 11232100574 - Eng. Software 7°B
