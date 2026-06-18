let ultimoResultado = null;
let archivoActual   = null;
const EJEMPLOS = {
  valido: `HDR|ORD-2026-001|20100055237|20481559927|10062026|VENTA|PEN\nITM|001|aceite-vegetal|100|KG|15.50\nITM|002|harina-preparada|50|SAC|45.00\nITM|003|leche-evaporada|200|CAJA|32.00\nFTR|3|10200.00|PENDIENTE`,
  error_lexico: `HDR|ORD-2026-002|20100055237|20481559927|10062026|VENTA|PEN\nITM|001|aceite@vegetal|100|KG|15.50\nFTR|1|1550.00|PENDIENTE`,
  error_sem: `HDR|ORD-2026-003|2010005523|20481559927|10062026|VENTA|PEN\nITM|001|aceite-vegetal|100|KG|15.50\nFTR|1|1550.00|PENDIENTE`,
};

document.getElementById('file-input').addEventListener('change', e => {
  const f = e.target.files[0];
  if (f) setFile(f);
});

const zone = document.getElementById('upload-zone');
zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
zone.addEventListener('drop', e => {
  e.preventDefault();
  zone.classList.remove('drag-over');
  const f = e.dataTransfer.files[0];
  if (f) setFile(f);
});

function setFile(file) {
  archivoActual = file;
  const sel = document.getElementById('file-selected');
  sel.textContent = file.name;
  sel.style.display = 'block';
  document.getElementById('btn-procesar').disabled = false;
}

function cargarEjemplo(tipo) {
  const contenido = EJEMPLOS[tipo];
  const nombre = tipo === 'valido' ? 'ORD-2026-001.txt' :
                    tipo === 'error_lexico' ? 'ORD-ERROR-LEX.txt' : 'ORD-ERROR-SEM.txt';
  archivoActual = new File([contenido], nombre, {type: 'text/plain'});
  const sel = document.getElementById('file-selected');
  sel.textContent = nombre;
  sel.style.display = 'block';
  document.getElementById('btn-procesar').disabled = false;
}

async function procesar() {
  if (!archivoActual) return;
  document.getElementById('loading').style.display = 'flex';
  resetUI();

  const fd = new FormData();
  fd.append('archivo', archivoActual);

  try {
    const res = await fetch('/procesar', { method: 'POST', body: fd });
    const data = await res.json();
    ultimoResultado = data;
    renderResultado(data);
  } catch(e) {
    alert('Error de conexión: ' + e.message);
  } finally {
    document.getElementById('loading').style.display = 'none';
  }
}

function resetUI() {
  document.getElementById('empty-state').style.display  = 'none';
  document.getElementById('result-banner').style.display = 'none';
  document.getElementById('download-section').style.display = 'none';
  ['lexico','sintactico','semantico','traduccion'].forEach(f => {
    document.getElementById('card-' + f).style.display = 'none';
  });
}

function renderResultado(data) {
  renderLexico(data);

  if (data.sintactico) renderSintactico(data);
  else skipPhase('sintactico');

  if (data.semantico) renderSemantico(data);
  else skipPhase('semantico');

  if (data.sql) renderTraduccion(data);
  else skipPhase('traduccion');

  const banner = document.getElementById('result-banner');
  banner.style.display = 'block';
  if (data.valido) {
    banner.className = 'result-banner result-ok';
    banner.textContent = 'Archivo procesado y traducido correctamente. SQL generado listo para ejecutar';
    document.getElementById('download-section').style.display = 'block';
    document.getElementById('btn-sql').style.display = 'flex';
    document.getElementById('btn-pdf').style.display = 'flex';
  } else {
    banner.className = 'result-banner result-err';
    banner.textContent = `Procesamiento detenido en fase ${data.fase_fallo}, corregir el archivo de entrada`;
  }
}

function renderLexico(data) {
  const card  = document.getElementById('card-lexico');
  const badge = document.getElementById('badge-lexico');
  const lex   = data.lexico;

  card.style.display = 'block';
  badge.textContent  = lex.valido ? '✅ Válido' : '❌ Error';
  badge.className  = 'phase-badge ' + (lex.valido ? 'badge-ok' : 'badge-err');
  let html = '';
  if (lex.errores.length) {
    html += '<div class="error-list" style="margin-bottom:1rem">';
    lex.errores.forEach(e => { html += `<div class="error-item">⚠ ${e}</div>`; });
    html += '</div>';
  }
  html += '<table class="data-table"><thead><tr><th>Línea</th><th>Pos</th><th>Lexema</th><th>Token</th></tr></thead><tbody>';
  lex.lineas.forEach(l => {
    l.tokens.forEach(t => {
      html += `<tr><td>${t.linea}</td><td>${t.posicion}</td>
        <td style="font-family:var(--mono)">${t.lexema}</td>
        <td><span class="tok tok-${t.token}">${t.token}</span></td></tr>`;
    });
  });
  html += '</tbody></table>';
  document.getElementById('tab-lexico-tokens').innerHTML = html;

  if (data.expresiones) {
    let er = '<table class="data-table"><thead><tr><th>Token</th><th>Expresión regular</th><th>Ejemplos</th></tr></thead><tbody>';
    data.expresiones.forEach(e => {
      er += `<tr><td><span class="tok tok-${e.token}">${e.token}</span></td>
             <td style="font-family:var(--mono);color:var(--orange)">${escHtml(e.expresion)}</td>
             <td style="color:var(--text-dim)">${e.ejemplos}</td></tr>`;
    });
    er += '</tbody></table>';
    document.getElementById('tab-lexico-er').innerHTML = er;
  }

  if (data.automatas) {
    document.getElementById('tab-lexico-afnd').innerHTML = renderAutomata(data.automatas.afnd, 'AFND');
    document.getElementById('tab-lexico-afd').innerHTML  = renderAutomata(data.automatas.afd,  'AFD');
    document.getElementById('tab-lexico-tabla').innerHTML = renderTablaTransiciones(data.automatas.tabla);
  }
}

function renderAutomata(aut, tipo) {
  const estados = aut.estados;
  const n = estados.length;
  const cx = 520, cy = 200;
  const radio = 150;
  const r_nodo = 28;

  const pos = {};
  estados.forEach((e, i) => {
    const angle = (2 * Math.PI * i / n) - Math.PI / 2;
    pos[e] = {
      x: cx + radio * Math.cos(angle),
      y: cy + radio * Math.sin(angle)
    };
  });

  let svg = `<div class="diagram-container"><p style="font-size:0.7rem;color:var(--text-dim);margin-bottom:0.75rem;letter-spacing:1px;text-transform:uppercase">${tipo} — ${aut.descripcion}</p>
<svg viewBox="0 0 ${cx*2} ${cy*2+40}" style="width:100%;max-height:360px" xmlns="http://www.w3.org/2000/svg">
<defs>
  <marker id="arr-${tipo}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
    <path d="M0,1L9,5L0,9" fill="none" stroke="#3B82F6" stroke-width="1.5"/>
  </marker>
  <marker id="arr-err-${tipo}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
    <path d="M0,1L9,5L0,9" fill="none" stroke="#5C7094" stroke-width="1.5"/>
  </marker>
</defs>`;

  aut.transiciones.forEach(t => {
    const from = pos[t.desde], to = pos[t.hacia];
    if (!from || !to) return;
    const isErr = t.hacia === 'qE';
    const color = isErr ? '#5C7094' : '#3B82F6';
    const markId = isErr ? `arr-err-${tipo}` : `arr-${tipo}`;

    if (t.desde === t.hacia) {
      svg += `<path d="M${from.x-10},${from.y-r_nodo} Q${from.x-40},${from.y-70} ${from.x+10},${from.y-r_nodo}"
        fill="none" stroke="${color}" stroke-width="1.2" marker-end="url(#${markId})"/>
        <text x="${from.x-20}" y="${from.y-72}" font-size="9" fill="${color}" font-family="JetBrains Mono">${escHtml(t.con)}</text>`;
    } else {
      const dx = to.x - from.x, dy = to.y - from.y;
      const len = Math.sqrt(dx*dx + dy*dy);
      const ux = dx/len, uy = dy/len;
      const x1 = from.x + ux*r_nodo, y1 = from.y + uy*r_nodo;
      const x2 = to.x   - ux*r_nodo, y2 = to.y   - uy*r_nodo;
      const mx = (x1+x2)/2 - uy*20, my = (y1+y2)/2 + ux*20;
      svg += `<path d="M${x1},${y1} Q${mx},${my} ${x2},${y2}"
        fill="none" stroke="${color}" stroke-width="1.2" marker-end="url(#${markId})"/>
        <text x="${mx}" y="${my-4}" font-size="9" fill="${color}" font-family="JetBrains Mono" text-anchor="middle">${escHtml(t.con)}</text>`;
    }
  });

  estados.forEach(e => {
    const {x, y} = pos[e];
    const isAcept = aut.estados_aceptacion.includes(e);
    const isInicio = e === aut.estado_inicial;
    const isErr2   = e === 'qE';
    const fill  = isErr2 ? '#2d1e1e' : isAcept ? '#1a2d1e' : '#131E33';
    const stroke= isErr2 ? '#EF4444' : isAcept ? '#10B981' : '#3B82F6';
    const tc    = isErr2 ? '#EF4444' : isAcept ? '#10B981' : '#79c0ff';

    if (isInicio) {
      svg += `<line x1="${x-r_nodo-25}" y1="${y}" x2="${x-r_nodo-2}" y2="${y}" stroke="#5C7094" stroke-width="1.2" marker-end="url(#arr-err-${tipo})"/>`;
    }
    svg += `<circle cx="${x}" cy="${y}" r="${r_nodo}" fill="${fill}" stroke="${stroke}" stroke-width="${isAcept?2:1.5}"/>`;
    if (isAcept) svg += `<circle cx="${x}" cy="${y}" r="${r_nodo-5}" fill="none" stroke="${stroke}" stroke-width="1"/>`;
    svg += `<text x="${x}" y="${y+4}" text-anchor="middle" font-size="11" font-weight="600" fill="${tc}" font-family="JetBrains Mono">${e}</text>`;
  });

  svg += `</svg></div>`;
  return svg;
}

function renderTablaTransiciones(tabla) {
  const {estados, simbolos, transiciones} = tabla;
  let html = `<div class="diagram-container">
  <p style="font-size:0.7rem;color:var(--text-dim);margin-bottom:0.75rem;letter-spacing:1px;text-transform:uppercase">Tabla de transiciones — ${tabla.descripcion}</p>
  <div style="overflow-x:auto">
  <table class="data-table"><thead><tr>
  <th>Estado</th>`;
  simbolos.forEach(s => { html += `<th>${escHtml(s)}</th>`; });
  html += `</tr></thead><tbody>`;
  estados.forEach(est => {
    const isAcept = ['q2','q3','q4','q5','q6'].includes(est);
    html += `<tr${isAcept?' class="tr-accept"':''}>
      <td style="font-family:var(--mono);font-weight:500;color:${est==='qE'?'var(--red)':'var(--blue)'}">${est}${isAcept?' *':''}</td>`;
    simbolos.forEach(s => {
      const dest = transiciones[est]?.[s] || '—';
      const cls  = dest === 'qE' ? 'tr-err' : dest === '—' ? '' : 'tr-ok';
      html += `<td class="${cls}" style="font-family:var(--mono)">${dest}</td>`;
    });
    html += `</tr>`;
  });
  html += `</tbody></table></div>
  <p style="font-size:0.68rem;color:var(--text-dim);margin-top:0.5rem">* Estado de aceptación</p>
  </div>`;
  return html;
}

function renderSintactico(data) {
  const card  = document.getElementById('card-sintactico');
  const badge = document.getElementById('badge-sintactico');
  const sint  = data.sintactico;

  card.style.display = 'block';
  badge.textContent = sint.valido ? '✅ Válido' : '❌ Error';
  badge.className = 'phase-badge ' + (sint.valido ? 'badge-ok' : 'badge-err');
  let gram = '';
  if (sint.errores.length) {
    gram += '<div class="error-list" style="margin-bottom:1rem">';
    sint.errores.forEach(e => { gram += `<div class="error-item">⚠ ${e}</div>`; });
    gram += '</div>';
  }
  gram += '<div class="prod-list">';
  (sint.producciones || []).forEach(p => {
    const parts = p.split('→');
    const lhs = parts[0].trim();
    const rhs = (parts[1]||'').trim();
    gram += `<div class="prod-item">
      <span class="kw">${lhs}</span>
      <span class="arrow"> → </span>
      <span class="sym">${rhs}</span>
    </div>`;
  });
  gram += '</div>';
  document.getElementById('tab-sintactico-gram').innerHTML = gram;

  document.getElementById('tab-sintactico-arbol').innerHTML = renderArbolSintactico(sint.arbol || []);
}

function renderArbolSintactico(arbol) {
  if (!arbol.length) return '<p style="color:var(--text-dim);font-size:0.8rem">Sin datos de árbol</p>';

  const W = 900, nW = 110, nH = 32, gapX = 20, gapY = 55;
  let svg = `<div class="diagram-container"><p style="font-size:0.7rem;color:var(--text-dim);margin-bottom:0.75rem;letter-spacing:1px;text-transform:uppercase">Árbol sintáctico — estructura jerárquica del documento</p>
<svg viewBox="0 0 ${W} ${arbol.length * (nH + gapY) + 100}" style="width:100%" xmlns="http://www.w3.org/2000/svg">`;

  const rootX = W/2 - nW/2, rootY = 20;
  svg += nodoSVG(rootX, rootY, nW, nH, 'documento', '#1f3a5f', '#79c0ff');

  const total = arbol.length;
  arbol.forEach((seg, si) => {
    const segX = (W / (total+1)) * (si+1) - nW/2;
    const segY = rootY + nH + gapY;

    svg += `<line x1="${rootX + nW/2}" y1="${rootY + nH}" x2="${segX + nW/2}" y2="${segY}" stroke="#1E2D47" stroke-width="1.2"/>`;

    const colors = {
      HDR: ['#1f3a5f','#79c0ff'],
      ITM: ['#1c2d1e','#56d364'],
      FTR: ['#2d2a1e','#e3b341']
    };
    const [bg, tc] = colors[seg.segmento] || ['#131E33','#CDD5E0'];
    svg += nodoSVG(segX, segY, nW, nH, seg.segmento + ' (' + seg.nombre + ')', bg, tc);

    const campos = seg.campos || [];
    const campoW = Math.min(nW, (W - 40) / Math.max(campos.length, 1));
    const startX = Math.max(20, segX + nW/2 - (campos.length * (campoW + 8))/2);

    campos.forEach((c, ci) => {
      const cx2 = startX + ci * (campoW + 8);
      const cy2 = segY + nH + gapY;
      svg += `<line x1="${segX + nW/2}" y1="${segY + nH}" x2="${cx2 + campoW/2}" y2="${cy2}" stroke="#1E2D47" stroke-width="1"/>`;
      svg += nodoSVG(cx2, cy2, campoW, nH-4, c.lexema, '#0F1729', '#CDD5E0', true);
    });
  });

  svg += '</svg></div>';
  return svg;
}

function nodoSVG(x, y, w, h, label, bg, tc, small=false) {
  const fs = small ? 8 : 10;
  const txt = label.length > 14 ? label.slice(0,12)+'…' : label;
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="5" fill="${bg}" stroke="${tc}" stroke-width="1.2"/>
  <text x="${x+w/2}" y="${y+h/2+fs/3}" text-anchor="middle" font-size="${fs}" fill="${tc}" font-family="JetBrains Mono" font-weight="500">${escHtml(txt)}</text>`;
}

function renderSemantico(data) {
  const card = document.getElementById('card-semantico');
  const badge = document.getElementById('badge-semantico');
  const sem  = data.semantico;

  card.style.display = 'block';
  badge.textContent = sem.valido ? '✅ Válido' : '❌ Error';
  badge.className = 'phase-badge ' + (sem.valido ? 'badge-ok' : 'badge-err');
  let html = '';
  if (sem.errores.length) {
    html += '<div class="error-list" style="margin-bottom:1rem">';
    sem.errores.forEach(e => { html += `<div class="error-item">⚠ ${e}</div>`; });
    html += '</div>';
  }
  html += '<div class="rules-grid">';
  (sem.reglas_aplicadas || []).forEach(r => {
    const ok = r.estado === '✅';
    html += `<div class="rule-item ${ok?'ok':'err'}">
      <span class="rule-code">${r.regla}</span>
      <div>
        <div class="rule-desc">${r.descripcion}</div>
        <div class="rule-val">${r.valor}</div>
      </div>
      <span>${r.estado}</span>
    </div>`;
  });
  html += '</div>';
  document.getElementById('body-semantico').innerHTML = html;
}

function renderTraduccion(data) {
  const card  = document.getElementById('card-traduccion');
  const badge = document.getElementById('badge-traduccion');
  card.style.display = 'block';
  badge.textContent = '✅ Generado';
  badge.className = 'phase-badge badge-ok';

  const sql = data.sql || '';
  const colored = sql
    .split('\n')
    .map(line => {
      if (line.startsWith('--')) return `<span class="sql-comment">${escHtml(line)}</span>`;
      let l = escHtml(line);
      l = l.replace(/\b(INSERT|INTO|VALUES|SELECT|FROM|WHERE|UPDATE|DELETE|CREATE|TABLE|SET)\b/g, '<span class="sql-keyword">$1</span>');
      l = l.replace(/'([^']*)'/g, "<span class=\"sql-string\">'$1'</span>");
      l = l.replace(/\b(\d+\.?\d*)\b/g, '<span class="sql-number">$1</span>');
      return l;
    })
    .join('\n');

  document.getElementById('body-traduccion').innerHTML =
    `<div class="code-block">${colored}</div>`;
}

function skipPhase(fase) {
  const card = document.getElementById('card-' + fase);
  card.style.display = 'block';
  const badge = document.getElementById('badge-' + fase);
  badge.textContent = '— Omitido';
  badge.className = 'phase-badge badge-skip';
}

function togglePhase(fase) {
  const body   = document.getElementById('body-' + fase);
  const toggle = document.getElementById('toggle-' + fase);
  const open   = !body.classList.contains('collapsed');
  body.classList.toggle('collapsed', open);
  toggle.classList.toggle('open', !open);
}

function showTab(phase, tab, btn) {
  const prefix  = `tab-${phase}-`;
  document.querySelectorAll(`[id^="${prefix}"]`).forEach(p => p.classList.remove('active'));
  document.getElementById(prefix + tab).classList.add('active');
  btn.closest('.tabs').querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}

async function descargarSQL() {
  if (!ultimoResultado?.sql) return;
  const res = await fetch('/descargar-sql', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({sql: ultimoResultado.sql})
  });
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'logiparse_output.sql';
  a.click(); URL.revokeObjectURL(url);
}

async function descargarPDF() {
  if (!ultimoResultado) return;
  const res = await fetch('/descargar-pdf', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({
      lexico: ultimoResultado.lexico,
      sintactico: ultimoResultado.sintactico,
      semantico: ultimoResultado.semantico,
      sql: ultimoResultado.sql || ''
    })
  });
  const blob = await res.blob();
  const ext = blob.type.includes('pdf') ? 'pdf' : 'html';
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = `reporte_logiparse.${ext}`;
  a.click(); URL.revokeObjectURL(url);
}

function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
