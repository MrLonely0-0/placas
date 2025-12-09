"""
Main entry point for the Plate Validator application.
This serves the web interface with plate validators.
For CLI usage, see main.py
"""

from flask import Flask, jsonify, render_template_string, request
from plate_validator import validate_plate
from vehicle_info import get_vehicle_info

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Validador de Placas</title>
  <style>
    body { font-family: "Segoe UI", Arial, sans-serif; max-width: 720px; margin: 32px auto; padding: 0 16px; background: #f5f7fb; color: #1f2a44; }
    h1 { margin-bottom: 8px; }
    .card { background: #fff; border: 1px solid #dbe2f3; border-radius: 12px; padding: 20px; box-shadow: 0 10px 30px rgba(31, 42, 68, 0.08); }
    label { display: block; margin-bottom: 8px; font-weight: 600; }
    input { width: 100%; padding: 12px; border: 1px solid #c8d3e6; border-radius: 8px; font-size: 16px; }
    button { margin-top: 12px; padding: 12px 16px; border: none; border-radius: 8px; background: linear-gradient(135deg, #1f5bff, #1bc8ff); color: #fff; font-size: 15px; font-weight: 700; cursor: pointer; box-shadow: 0 10px 24px rgba(31, 91, 255, 0.2); }
    button:disabled { opacity: 0.6; cursor: not-allowed; }
    .result { margin-top: 16px; padding: 12px; border-radius: 8px; border: 1px solid #dbe2f3; background: #f9fbff; }
    .ok { color: #0f8a2f; font-weight: 700; }
    .erro { color: #c62828; font-weight: 700; }
    .chips { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
    .chip { padding: 8px 10px; background: #e9f1ff; border-radius: 999px; cursor: pointer; border: 1px solid #d0defa; }
    .info-box { margin-top: 20px; padding: 12px; background: #e8f4f8; border-left: 4px solid #1f5bff; border-radius: 4px; }
    .info-box code { background: #fff; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
  </style>
</head>
<body>
  <h1>Validador de Placas</h1>
  <p>Suporta formatos <strong>AAA-0000</strong> (antigo, com ou sem hífen digitado) e <strong>AAA0A00</strong> (Mercosul).</p>
  <div class="card">
    <label for="placa">Digite uma placa</label>
    <input id="placa" placeholder="Ex: ABC-1234 ou BRA2E19" />
    <div class="chips" id="chips"></div>
    <button id="btn">Validar</button>
    <div class="result" id="result" style="display:none"></div>
  </div>
  
  <div class="info-box">
    <strong>💡 Modo CLI disponível:</strong> Para usar via linha de comando, execute:<br>
    <code>python main.py "ABC-1234" "BRA2E19"</code>
  </div>
  
  <script>
    const samples = ["ABC-1234", "ABC1234", "BRA2E19", "GLS7D55", "A@A-1234", "BRA2E1", " abc-1234 ", "AAA 1234", "ABCD-123" ];
    const chipsContainer = document.getElementById('chips');
    samples.forEach(s => {
      const div = document.createElement('div');
      div.className = 'chip';
      div.textContent = s;
      div.onclick = () => { document.getElementById('placa').value = s; };
      chipsContainer.appendChild(div);
    });

    const btn = document.getElementById('btn');
    const resultEl = document.getElementById('result');
    btn.onclick = async () => {
      const placa = document.getElementById('placa').value;
      if (!placa) return;
      btn.disabled = true;
      resultEl.style.display = 'none';
      const resp = await fetch('/api/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ placa })
      });
      const data = await resp.json();
      btn.disabled = false;
      resultEl.style.display = 'block';
      const info = data.vehicle_info;
      const infoHtml = info ? `<div>Marca: <strong>${info.brand}</strong></div>
        <div>Modelo: <strong>${info.model}</strong></div>
        <div>Cor: <strong>${info.color}</strong></div>
        <div>Ano: <strong>${info.year}</strong></div>` : `<div>Veículo: n/d</div>`;
      resultEl.innerHTML = `<div class="${data.valid ? 'ok' : 'erro'}">${data.valid ? 'OK' : 'ERRO'}</div>` +
        `<div>Normalizada: <strong>${data.normalized}</strong></div>` +
        `<div>Tipo: <strong>${data.plate_type || '-'}</strong></div>` +
        infoHtml +
        `<div>Erros: ${data.errors.length ? data.errors.join('; ') : '-'}</div>`;
    };
  </script>
</body>
</html>
"""


@app.post("/api/validate")
def api_validate():
    payload = request.get_json(force=True, silent=True) or {}
    placa = payload.get("placa", "")
    result = validate_plate(placa)
    vehicle_info = get_vehicle_info(result.normalized) if result.valid else None
    return jsonify(
        valid=result.valid,
        plate_type=result.plate_type,
        normalized=result.normalized,
        errors=result.errors,
        vehicle_info=vehicle_info.__dict__ if vehicle_info else None,
    )


@app.get("/")
def index():
    return render_template_string(HTML_PAGE)


if __name__ == "__main__":
    # Debug mode for local dev; use a proper WSGI server in production.
    print("=" * 60)
    print("Validador de Placas - Web Interface")
    print("=" * 60)
    print("Servidor iniciado em: http://localhost:8000")
    print("Para modo CLI, use: python main.py <placa1> <placa2> ...")
    print("=" * 60)
    app.run(host="0.0.0.0", port=8000, debug=True)
