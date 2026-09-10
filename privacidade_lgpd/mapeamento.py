# lista os dados pessoais coletados pelo sistema, a finalidade de cada um
# e uma descrição curta do que é feito com o dado


DADOS_PESSOAIS = [
    {
        'campo': 'nome',
        'app': 'alunos',
        'finalidade': 'identificação escolar',
        'descricao': 'usado para identificar o aluno em documentos, boletins e sistemas internos',
    },
    {
        'campo': 'cpf',
        'app': 'alunos',
        'finalidade': 'matrícula obrigatória por lei',
        'descricao': 'exigido por norma do MEC para validar a matrícula do aluno na instituição',
    },
    {
        'campo': 'email',
        'app': 'autenticacao',
        'finalidade': 'comunicação institucional',
        'descricao': 'usado para login, recuperação de senha e envio de avisos da instituição',
    },
    {
        'campo': 'dados_bancarios',
        'app': 'financeiro',
        'finalidade': 'cobrança',
        'descricao': 'usado para gerar boletos e registrar pagamentos de mensalidade',
    },
    {
        'campo': 'notas',
        'app': 'notas',
        'finalidade': 'registro acadêmico obrigatório',
        'descricao': 'usado para calcular aprovação/reprovação e compor o histórico escolar',
    },
    # ztem que adicionar os proximos campos quando os outros apps forem criados
]

