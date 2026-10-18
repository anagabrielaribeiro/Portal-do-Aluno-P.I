from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Boleto
from django.views.decorators.cache import never_cache
from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, Http404
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from alunos.models import Aluno
from io import BytesIO  # permite montar o PDF na memória, sem gravar em disco


@never_cache
@login_required # garante que só usuário autenticado acessa
def financeiro(request): 
    hoje = timezone.localdate() # o template compara o vencimento com essa data

    try: 
        aluno = request.user.aluno
    except Aluno.DoesNotExist:
        # colaborador vê tela sem boletos (evita o erro 500)
        return render(request, 'financeiro/financeiro.html', {'boletos': Boleto.objects.none(), 'hoje': hoje})

    boletos = Boleto.objects.filter(aluno=aluno) # só os boletos desse aluno
    return render(request, 'financeiro/financeiro.html', {'boletos': boletos, 'hoje': hoje})


@never_cache
@login_required
def baixar_boleto(request, boleto_id):
    # gera o PDF na hora, só para o dono do boleto
    try: 
        aluno = request.user.aluno
    except Aluno.DoesNotExist:
        raise Http404 # colaborador não tem boleto

    boleto = get_object_or_404(Boleto, id=boleto_id, aluno=aluno)


    buffer = BytesIO() # cria um espaço de armazenamento temporário na memória RAM que simula um arquivo físico.
    pdf = canvas.Canvas(buffer, pagesize=A4) # cria a "tela" de desenho do PDF
    largura, altura = A4

    # titulo
    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(50, altura - 80, 'Demonstrativo de Boleto')

    # dados do boleto
    pdf.setFont('Helvetica', 12)
    pdf.drawString(50, altura - 120, f'Aluno:  {aluno}')
    pdf.drawString(50, altura - 140, f'Referência: {boleto.mes_referencia}')
    pdf.drawString(50, altura - 160, f'Vencimento: {boleto.vencimento:%d/%m/%Y}')
    pdf.drawString(50, altura - 180, f'Valor: R$ {boleto.valor:.2f}')
    pdf.drawString(50, altura - 200, f'Situação: {'Pgao' if boleto.pago else 'Em aberto'}')

    pdf.showPage()
    pdf.save()
    buffer.seek(0) # volta ao inciio para poder enviar

    return FileResponse(buffer, content_type='application/pdf', filename=f'boleto-{boleto.id}.pdf')