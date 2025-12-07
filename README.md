# Validador de Placas (Brasil)

Valida placas no formato antigo `AAA-0000` (com ou sem hífen digitado, será normalizado) e Mercosul `AAA0A00`, com CLI, app web (Flask), API e testes automatizados. Retorna também dados mockados de veículo (marca, modelo, cor, ano) para algumas placas de exemplo.

## Requisitos
- Python 3.8+
- Flask (instalação via `pip install -r requirements.txt`)
- requests (já no requirements)

## Instalação
```powershell
pip install -r requirements.txt
```

## Como usar (CLI)
```powershell
python main.py "ABC-1234" "BRA2E19" "ABC1234"
```
Saída exemplo:
```
ABC-1234 -> OK | tipo=ANTIGA | normalizada=ABC-1234 | veiculo=Volkswagen Gol 1.6 2018 cor=Prata |
BRA2E19  -> OK | tipo=MERCOSUL | normalizada=BRA2E19 | veiculo=Chevrolet Onix 1.0 2020 cor=Branco |
ABC1234  -> OK | tipo=ANTIGA | normalizada=ABC-1234 | veiculo=Volkswagen Gol 1.6 2018 cor=Prata |
```

## Como usar (Web)
```powershell
python app.py
```
Abra http://localhost:8000 e use o formulário. Também há endpoint JSON `POST /api/validate` com corpo `{"placa": "ABC-1234"}`.

### Versão estática (GitHub Pages)
- Arquivo: `static/index.html` (funciona apenas com HTML/JS, sem backend).
- Usa o mesmo `vehicle_db.json` na raiz do repositório para carregar marca/modelo/cor/ano (via fetch relativo `../vehicle_db.json`).
- Publicação no GitHub Pages: habilite Pages apontando para a branch e diretório `/static`; a URL será algo como `https://<user>.github.io/<repo>/` (ou `/static/` se usar root). Basta garantir que `vehicle_db.json` também esteja publicado na raiz.
- A versão estática não pode chamar APIs privadas sem CORS; se usar uma API pública, certifique-se de habilitar CORS ou usar um endpoint que permita origem `*`.

## Regras principais
- Aceita: `AAA-0000` (antiga) e `AAA0A00` (Mercosul).
- Para formato antigo, hífen é opcional: digitou `ABC1234`, o sistema normaliza para `ABC-1234`.
- Converte para maiúsculas e remove espaços no início/fim; espaços internos não são aceitos.
- Caracteres especiais ou comprimentos errados são rejeitados.

## Dados de veículo (mock)
- Mock interno em `vehicle_info.py` + arquivo `vehicle_db.json` que você pode editar/estender. Cada item: `plate`, `brand`, `model`, `color`, `year`.
- As chaves são normalizadas para maiúsculas; placas antigas sem hífen também funcionam. Adicione novas linhas no JSON conforme necessário.
- Integração automática com APIs públicas gratuitas (FIPE, Tabela de Preços, carroapi, etc.): tenta várias fontes automaticamente sem precisar de config. Ordem: (1) `VEHICLE_API_URL` (env var, suporta `{plate}`); (2) APIs FIPE/Denatran públicas; (3) Serviços genéricos; (4) fallback para `vehicle_db.json` local. Resposta esperada: JSON com campos `plate`, `brand`, `model`, `color`, `year`.

## Testes automatizados
```powershell
python -m unittest discover -s tests
```

## Estrutura
- `plate_validator.py`: funções de validação.
- `main.py`: CLI simples para validar uma ou mais placas.
- `app.py`: app Flask com página HTML e API `/api/validate`.
- `vehicle_info.py`: mock de dados do veículo (marca, modelo, cor, ano).
- `static/index.html`: versão 100% estática para GitHub Pages, usando o mesmo `vehicle_db.json`.
- `tests/`: casos de teste unitários.
- `requirements.txt`: dependências mínimas.
