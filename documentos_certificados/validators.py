import os
import uuid
from django.core.exceptions import ValidationError

# Define o tamanho máximo permitido para o arquivo 
TAMANHO_MAXIMO = 5 * 1024 * 1024   # 5 MB

# Mapeia as extensões permitidas para os seus respectivos bytes iniciais 
ASSINATURAS = {
    '.pdf': b'%PDF-',
    '.png': b'\x89PNG\r\n\x1a\n',
    '.jpg': b'\xff\xd8\xff',
    '.jpeg': b'\xff\xd8\xff',
}


# Gera um caminho e um nome único e seguro para o arquivo, descartando o nome original 
def caminho_certificado(instance, filename):
    # descarta o nome original e mantém só a extensão 
    ext = os.path.splitext(filename)[1].lower()
    return f'certificados/{uuid.uuid4().hex}{ext}'


# Valida se o arquivo enviado cumpre as regras de extensão, tamanho e integridade binária
def validar_arquivo_certificado(arquivo):
    ext = os.path.splitext(arquivo.name)[1].lower()
    
    # Verifica se a extensão do arquivo está na lista permitida
    if ext not in ASSINATURAS:
        raise ValidationError('Envie apenas arquivos PDF, JPG ou PNG.')

    # Verifica se o arquivo ultrapassa o limite máximo de tamanho de 5 MB
    if arquivo.size > TAMANHO_MAXIMO:
        raise ValidationError('O arquivo deve ter no máximo 5 MB.')

    # Lê os primeiros 8 bytes do arquivo e reseta o ponteiro para o início para validar o conteúdo real
    inicio = arquivo.read(8)
    arquivo.seek(0)
    
    # Confere se o conteúdo do arquivo bate com a extensão informada
    if not inicio.startswith(ASSINATURAS[ext]):
        raise ValidationError('O conteúdo do arquivo não corresponde à extensão.')