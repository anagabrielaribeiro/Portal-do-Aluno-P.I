# Imagem do Portal do Aluno P.I para rodar localmente com Docker
# mesma versão do Python usada na esteira de CI (o Django 6.1 exige 3.12 ou superior)
FROM python:3.12-slim

# não gera arquivos .pyc e mostra os logs na hora
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# instala as dependências primeiro para aproveitar o cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copia o código (o que não deve entrar está no .dockerignore)
COPY . .

# roda com um usuário sem privilégios, e não como root
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# prepara o banco, a tabela de cache do rate limit e os estáticos, e sobe o servidor
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py createcachetable && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
