# CRUD Lava Jato - Python + PySide6 + MySQL/XAMPP

Sistema desktop para gerenciamento de lava jato, feito com Python 3, Qt Widgets/PySide6, interfaces `.ui` editaveis no Qt Designer e banco MySQL/MariaDB pelo XAMPP.

## Como executar

1. Abra o XAMPP Control Panel.
2. Inicie o servico `MySQL`.
3. No terminal, dentro da pasta do projeto:

```bash
pip install -r requirements.txt
python scripts/seed.py
python main.py
```

Login padrao:

- Usuario: `admin`
- Senha: `admin123`

O script `python scripts/seed.py` recria e popula o banco `lava_jato` no MySQL/MariaDB. Use ele quando quiser voltar aos dados iniciais.

## Configuracao do banco

Por padrao, o sistema usa a configuracao comum do XAMPP:

- Host: `127.0.0.1`
- Porta: `3306`
- Usuario: `root`
- Senha: vazia
- Banco: `lava_jato`

Se seu XAMPP estiver com outra configuracao, defina variaveis de ambiente antes de executar. No PowerShell:

```powershell
$env:LAVA_JATO_DB_HOST="127.0.0.1"
$env:LAVA_JATO_DB_PORT="3306"
$env:LAVA_JATO_DB_USER="root"
$env:LAVA_JATO_DB_PASSWORD="sua_senha"
$env:LAVA_JATO_DB_NAME="lava_jato"
python scripts/seed.py
python main.py
```

## Funcionalidades

- Login com senha armazenada por hash PBKDF2.
- Dashboard com indicadores de clientes, carros, ordens abertas, ordens concluidas e faturamento.
- CRUD completo de clientes, carros, servicos e ordens de servico.
- Ordem de servico com multiplos itens, quantidade e calculo automatico do total.
- Pesquisa de ordens por cliente, placa, status e periodo.
- Mensagens amigaveis com `QMessageBox`.
- Queries parametrizadas e camada de banco separada dos controllers.
- Banco MySQL/MariaDB criado automaticamente no XAMPP.

## Estrutura

```text
.
|-- main.py
|-- database/
|   |-- connection.py
|   `-- schema.sql
|-- controllers/
|-- models/
|-- views/
|-- assets/
|-- docs/
|-- scripts/
|-- tests/
|-- requirements.txt
`-- README.md
```

## Validacao tecnica

```bash
python -m compileall .
python tests/smoke_test.py
```

## Versionar no GitHub

```bash
git init
git add .
git commit -m "Projeto CRUD Lava Jato"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git push -u origin main
```
