# CRUD Lava Jato

Projeto desktop em Python para controle simples de um lava jato.

Foi feito com PySide6, telas `.ui` do Qt Designer e banco MySQL/MariaDB usando o XAMPP.

## Banco de dados

1. Abra o XAMPP.
2. Inicie o MySQL.
3. Abra o phpMyAdmin.
4. Importe o arquivo:

```text
database/schema.sql
```

Esse arquivo cria o banco `lava_jato`, monta as tabelas e coloca alguns dados para teste.

Login inicial:

```text
Usuario: admin
Senha: admin123
```

## Como rodar

Na pasta do projeto:

```bash
pip install -r requirements.txt
python main.py
```

Se o seu MySQL tiver senha, informe antes de abrir:

```powershell
$env:LAVA_JATO_DB_USER="root"
$env:LAVA_JATO_DB_PASSWORD="sua_senha"
python main.py
```

## Pastas principais

```text
assets/       icones e estilo
controllers/  regras das telas
database/     conexao e SQL do banco
views/        telas feitas em .ui
main.py       arquivo principal
```
