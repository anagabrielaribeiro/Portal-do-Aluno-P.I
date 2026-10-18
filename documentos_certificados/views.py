from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from .models import SolicitacaoDocumento, TipoDocumento, Certificado
from .forms import CertificadoForm

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import FileResponse
from django.utils import timezone

@never_cache
@login_required
def meus_documentos(request):
    # Pega apenas os documentos do aluno logado
    if not hasattr(request.user, 'aluno'):
        return redirect('/gestao-portal/')
        
    documentos = SolicitacaoDocumento.objects.filter(aluno=request.user.aluno).order_by('-data_solicitacao')
    tipos_disponiveis = TipoDocumento.choices
    
    return render(request, 'documentos_certificados/lista.html', {
        'documentos': documentos,
        'tipos_disponiveis': tipos_disponiveis
    })

@never_cache
@login_required
def meus_certificados(request):
    try:
        aluno = request.user.aluno
    except AttributeError:
        return redirect('/gestao-portal/')

    # Busca os certificados já cadastrados do aluno
    lista_certificados = Certificado.objects.filter(aluno=aluno).order_by('-data')

    # Processa o formulário de envio de novo certificado
    if request.method == 'POST':
        form = CertificadoForm(request.POST, request.FILES) # request.FILES é obrigatório para upload de arquivos
        if form.is_valid():
            certificado = form.save(commit=False)
            certificado.aluno = aluno
            certificado.save()
            messages.success(request, 'Certificado anexado com sucesso!')
            return redirect('certificados')
    else:
        form = CertificadoForm()

    return render(request, 'documentos_certificados/certificados.html', {
        'certificados': lista_certificados,
        'form': form
    })

@never_cache
@login_required
@require_POST
def nova_solicitacao(request):
    if not hasattr(request.user, 'aluno'):
        return redirect('login')
        
    tipo_escolhido = request.POST.get('tipo')
    
    # Verifica se o aluno mandou um tipo válido
    tipos_validos = [escolha[0] for escolha in TipoDocumento.choices]
    if tipo_escolhido in tipos_validos:
        SolicitacaoDocumento.objects.create(
            aluno=request.user.aluno,
            tipo=tipo_escolhido
        )
        messages.success(request, "Documento solicitado com sucesso! Acompanhe o status.")
    else:
        messages.error(request, "Tipo de documento inválido.")
        
    return redirect('meus_documentos')

@never_cache
@login_required
def gerar_declaracao_matricula(request):
    if not hasattr(request.user, 'aluno'):
        return redirect('login')
    
    aluno = request.user.aluno
    matricula = aluno.matriculas.filter(status='ativa').first()
    
    buffer = BytesIO() # Cria PDF na memória
    pdf = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4
    
    pdf.setFont('Helvetica-Bold', 18)
    pdf.drawString(50, altura - 80, 'Declaração de Matrícula')
    
    pdf.setFont('Helvetica', 12)
    pdf.drawString(50, altura - 130, 'Certificamos para os devidos fins que o(a) aluno(a)')
    
    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawString(50, altura - 150, f'{aluno.nome_exibicao} (RGM: {aluno.ra})')
    
    pdf.setFont('Helvetica', 12)
    if matricula:
        pdf.drawString(50, altura - 180, f'está regularmente matriculado(a) no curso de {matricula.curso.nome}.')
        pdf.drawString(50, altura - 200, f'Período letivo: {matricula.periodo_letivo}')
    else:
        pdf.drawString(50, altura - 180, 'não possui matrícula ativa no momento.')
        
    pdf.drawString(50, altura - 250, f'São Paulo, {timezone.now().strftime("%d/%m/%Y")}.')
    
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    
    return FileResponse(buffer, as_attachment=True, filename=f'Declaracao_Matricula_{aluno.ra}.pdf')
