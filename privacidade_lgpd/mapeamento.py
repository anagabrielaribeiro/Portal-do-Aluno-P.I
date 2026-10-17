# lista os dados pessoais que o sistema guarda, pra que servem e em que base legal da LGPD cada um se apoia
# base_legal 'consentimento' = o aluno escolhe se aceita as outras não dependem do aceite dele


DADOS_PESSOAIS = [
    {'campo': 'nome', 'app': 'alunos', 'finalidade': 'identificação escolar',
     'base_legal': 'execução de contrato',
     'descricao': 'usado para identificar o aluno em documentos, boletins e sistemas internos'},
    {'campo': 'cpf', 'app': 'alunos', 'finalidade': 'matrícula obrigatória por lei',
     'base_legal': 'obrigação legal',
     'descricao': 'exigido por norma do MEC para validar a matrícula do aluno na instituição'},
    {'campo': 'rg', 'app': 'alunos', 'finalidade': 'matrícula obrigatória por lei',
     'base_legal': 'obrigação legal',
     'descricao': 'documento de identificação exigido na matrícula'},
    {'campo': 'data_nascimento', 'app': 'alunos', 'finalidade': 'identificação escolar',
     'base_legal': 'execução de contrato',
     'descricao': 'usada no cadastro do aluno e na geração do RA'},
    {'campo': 'endereco', 'app': 'alunos', 'finalidade': 'cadastro do aluno',
     'base_legal': 'execução de contrato',
     'descricao': 'usado no cadastro e no envio de correspondência da instituição'},
    {'campo': 'ultimo_ip_acesso', 'app': 'autenticacao', 'finalidade': 'segurança do acesso',
     'base_legal': 'legítimo interesse',
     'descricao': 'registrado para detectar acessos suspeitos à conta'},
    {'campo': 'curso, status e período', 'app': 'matriculas', 'finalidade': 'vida acadêmica',
     'base_legal': 'execução de contrato',
     'descricao': 'usados para manter o vínculo do aluno com o curso'},
    {'campo': 'notas', 'app': 'notas', 'finalidade': 'registro acadêmico obrigatório',
     'base_legal': 'obrigação legal',
     'descricao': 'usadas para calcular aprovação/reprovação e compor o histórico escolar'},
    {'campo': 'dados_bancarios', 'app': 'financeiro', 'finalidade': 'cobrança',
     'base_legal': 'execução de contrato',
     'descricao': 'usados para gerar boletos e registrar pagamentos de mensalidade'},
     # estes dois dependem do aceite do aluno
    {'campo': 'telefone', 'app': 'alunos', 'finalidade': 'contato por telefone',
     'base_legal': 'consentimento',
     'descricao': 'usado para a instituição entrar em contato por ligação ou mensagem'},
    {'campo': 'email', 'app': 'autenticacao', 'finalidade': 'envio de avisos e comunicados',
     'base_legal': 'consentimento',
     'descricao': 'usado para enviar avisos e novidades que não são essenciais ao curso'},
     
]

# só as finalidades que realmente precisam do aceite do aluno sem repetir
def finalidades_de_consentimento():
    return sorted(set(d['finalidade'] for d in DADOS_PESSOAIS if d['base_legal'] == 'consentimento'))

def dados_obrigatorios():
    return [d for d in DADOS_PESSOAIS if d['base_legal'] != 'consentimento']

