from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Aluno
from .forms import AlunoContatoForm
from django.views.decorators.cache import never_cache
from django.utils import timezone 

@never_cache #impede que o navegador guarde a pagina de cache
@login_required # se não estiver logado redireciona para a tela Login
def dados_pessoais(request):

    # tenta buscar o objeto Aluno relacionado ao usuário que está logado 
    try:
        aluno = request.user.aluno 
    except Aluno.DoesNotExist:
        if request.user.is_staff:
            return redirect('/gestao-portal/')
        messages.error(request, 'Não encontramos um cadastro de aluno vinculado a essa conta.')
        return redirect('login') 



    # busca a matricula ativa do aluno
    matricula_atual = aluno.matriculas.filter(status='ativa').select_related('curso', 'turma').first()

    # Busca todo o histórico acadêmico do aluno
    todas_matriculas = aluno.matriculas.all().order_by('-periodo_letivo')

    historico_notas = []
    historico_financeiro = []

    
    if request.method == 'POST': 

        if not aluno.pode_editar_contato:
            proxima = timezone.localtime(aluno.proxima_edicao_disponivel)
            messages.error(
                request,
                f'você pode editar de novo em {proxima:%d/%m/%Y as %H:%M}.',
            )
            return redirect('dados_pessoais')

        original = (aluno.telefone, aluno.endereco) # guarda valores antes de mexer

        form = AlunoContatoForm(request.POST, instance=aluno) # request.Post tem os dados digitados e o instance=aluno não deixa criar um aluno novo e sim atualizar
        if form.is_valid(): # is_valid() roda as validaões do form/model como campo origatório
            
            novo = (form.cleaned_data['telefone'], form.cleaned_data['endereco']) 

            if novo != original: # se mudou algo
                aluno = form.save(commit=False)
                aluno.data_ultima_alteracao_contato = ( timezone.now())
                aluno.save(
                    update_fields=[
                        'telefone',
                        'endereco',
                        'data_ultima_alteracao_contato'
                    ]
                )
                messages.success(request, 'Dados de contato atualizados com sucesso.')
            else: 
                messages.info(request, 'Nenhum dado foi alterado')
            return redirect('dados_pessoais')
    else: 
        form = AlunoContatoForm(instance=aluno)

    # dados que serão enviado para o html
    context = {
        'aluno': aluno,
        'matricula_atual': matricula_atual,
        'todas_matriculas': todas_matriculas,
        'historico_notas': historico_notas,
        'historico_financeiro': historico_financeiro,
        'form': form,
    }
    # renderiza a pagina 
    return render(request, 'alunos/dados_pessoais.html', context)