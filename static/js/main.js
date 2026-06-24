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
    let er = '<div style="overflow-x:auto"><table class="data-table" style="min-width:1000px">';
    er += '<thead><tr>';
    er += '<th style="background:var(--blue-dim);color:var(--navy);font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;padding:0.5rem 0.75rem;min-width:190px">Token</th>';
    er += '<th style="background:var(--blue-dim);color:var(--navy);font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;padding:0.5rem 0.75rem;min-width:200px">Descripción</th>';
    er += '<th style="background:var(--blue-dim);color:var(--navy);font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;padding:0.5rem 0.75rem">Ejemplos de Lexemas</th>';
    er += '<th style="background:var(--blue-dim);color:var(--navy);font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;padding:0.5rem 0.75rem;min-width:160px">Expresión Regular</th>';
    er += '<th style="background:var(--blue-dim);color:var(--navy);font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;padding:0.5rem 0.75rem;min-width:200px">Lenguaje</th>';
    er += '<th style="background:var(--blue-dim);color:var(--navy);font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;padding:0.5rem 0.75rem;min-width:180px">Gramática</th>';
    er += '<th style="background:var(--blue-dim);color:var(--navy);font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;padding:0.5rem 0.75rem;min-width:200px">Producciones</th>';
    er += '</tr></thead><tbody>';

    data.expresiones.forEach((e, idx) => {
      const rowBg = idx % 2 === 1 ? 'background:rgba(28,43,58,0.03)' : '';
      const prods = (e.producciones || []).join('\n');
      er += `<tr style="${rowBg}">
        <td style="border:1px solid var(--border);padding:0.5rem 0.75rem;vertical-align:top">
          <span class="tok tok-${e.token}">${e.token}</span>
        </td>
        <td style="border:1px solid var(--border);padding:0.5rem 0.75rem;vertical-align:top;font-size:0.8rem;color:var(--text)">
          ${e.descripcion || ''}
        </td>
        <td style="border:1px solid var(--border);padding:0.5rem 0.75rem;vertical-align:top;font-family:JetBrains Mono,monospace;color:var(--text-dim)">
          ${e.ejemplos}
        </td>
        <td style="border:1px solid var(--border);padding:0.5rem 0.75rem;vertical-align:top;font-family:JetBrains Mono,monospace;color:var(--blue)">
          ${escHtml(e.expresion)}
        </td>
        <td style="border:1px solid var(--border);padding:0.5rem 0.75rem;vertical-align:top;color:var(--purple)">
          ${e.lenguaje || ''}
        </td>
        <td style="border:1px solid var(--border);padding:0.5rem 0.75rem;vertical-align:top;font-family:JetBrains Mono,monospace;color:var(--yellow)">
          ${e.gramatica || ''}
        </td>
        <td style="border:1px solid var(--border);padding:0.5rem 0.75rem;vertical-align:top;font-family:JetBrains Mono,monospace;font-size:0.7rem;color:var(--teal);white-space:pre-line">
          ${escHtml(prods)}
        </td>
      </tr>`;
    });

    er += '</tbody></table></div>';
    document.getElementById('tab-lexico-er').innerHTML = er;
  }

  if (data.automatas) {
    document.getElementById('afnd-global-content').innerHTML = renderAutomata(data.automatas.afnd, 'AFND');
    document.getElementById('afd-global-content').innerHTML  =
      renderAutomata(data.automatas.afd, 'AFD') +
      renderTuring(data.automatas.turing);
    document.getElementById('tab-lexico-tabla').innerHTML = renderTablaTransiciones(data.automatas.tabla);
  }
  if (data.automatas_token) {
    poblarSelectorTokens('afnd', data.automatas_token);
    poblarSelectorTokens('afd', data.automatas_token);
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
    const fill  = isErr2 ? '#FAD7D3' : isAcept ? '#D4EAE3' : '#D4E3F5';
    const stroke= isErr2 ? '#C0392B' : isAcept ? '#5D8B7A' : '#2E5E9E';
    const tc    = isErr2 ? '#C0392B' : isAcept ? '#5D8B7A' : '#2E5E9E';

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

  let plantillasHtml = '';
  if (data.plantillas_gramatica) {
    plantillasHtml = '<p style="font-size:0.7rem;color:#5C7094;margin-bottom:0.75rem;' +
      'letter-spacing:1px;text-transform:uppercase">Plantillas gramaticales (HDR / ITM / FTR)</p>' +
      '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem;margin-bottom:1.5rem">';
    data.plantillas_gramatica.forEach(p => {
      plantillasHtml += renderArbolSintactico([p]).replace(
        'Árbol sintáctico — estructura jerárquica del documento',
        'Plantilla: ' + p.segmento + ' (' + p.nombre + ')'
      );
    });
    plantillasHtml += '</div>';
  }
  plantillasHtml += '<p style="font-size:0.7rem;color:#5C7094;margin:1rem 0 0.75rem;' +
    'letter-spacing:1px;text-transform:uppercase">Árbol instanciado (documento real procesado)</p>';

  document.getElementById('tab-sintactico-arbol').innerHTML =
    plantillasHtml + renderArbolSintactico(sint.arbol || []);
}

function renderArbolSintactico(arbol) {
  if (!arbol.length) return '<p style="color:var(--text-dim);font-size:0.8rem">Sin datos de árbol</p>';

  const nW = 110, nH = 32, gapY = 55;
  const minCampoW = 60, campoGap = 8;

  // Calcular ancho necesario por cada segmento según su cantidad de campos
  const total = arbol.length;
  const anchosSegmento = arbol.map(seg => {
    const campos = seg.campos || [];
    const anchoCampos = campos.length > 0
      ? campos.length * (minCampoW + campoGap) - campoGap
      : 0;
    return Math.max(nW, anchoCampos);
  });

  const gapSegmento = 30;
  const anchoContenido = anchosSegmento.reduce((a,b)=>a+b,0) + gapSegmento * Math.max(0, total - 1);
  const W = Math.max(900, anchoContenido + 80);

  const rootY    = 20;
  const segY     = rootY + nH + gapY;
  const camposY  = segY + nH + gapY;
  const hayCampos = arbol.some(s => (s.campos || []).length > 0);
  const Hsvg = hayCampos ? (camposY + nH + 40) : (segY + nH + 40);

  let svg = `<div class="diagram-container">
    <p style="font-size:0.7rem;color:var(--text-dim);margin-bottom:0.75rem;letter-spacing:1px;text-transform:uppercase">Árbol sintáctico — estructura jerárquica del documento</p>
    <svg viewBox="0 0 ${W} ${Hsvg}" style="width:${W}px;max-width:none;display:block" xmlns="http://www.w3.org/2000/svg">`;

  const rootX = W/2 - nW/2;
  svg += nodoSVG(rootX, rootY, nW, nH, 'documento', '#D4E3F5', '#2E5E9E');

  // Calcular posición horizontal acumulada de cada segmento
  let cursorX = 0;
  const posiciones = [];
  anchosSegmento.forEach(ancho => {
    posiciones.push(cursorX);
    cursorX += ancho + gapSegmento;
  });
  const anchoUsado = cursorX - gapSegmento;
  const offsetCentrado = (W - anchoUsado) / 2;

  arbol.forEach((seg, si) => {
    const anchoSeg = anchosSegmento[si];
    const groupX   = posiciones[si] + offsetCentrado;
    const segX     = groupX + anchoSeg/2 - nW/2;

    svg += `<line x1="${rootX + nW/2}" y1="${rootY + nH}" x2="${segX + nW/2}" y2="${segY}" stroke="#1E2D47" stroke-width="1.2"/>`;

    const colors = {
      HDR: ['#D4E3F5','#2E5E9E'],
      ITM: ['#D4EAE3','#5D8B7A'],
      FTR: ['#F5E8CC','#B07D2E']
    };
    const [bg, tc] = colors[seg.segmento] || ['#EEF2F8','#1C2B3A'];
    svg += nodoSVG(segX, segY, nW, nH, seg.segmento + ' (' + seg.nombre + ')', bg, tc);

    const campos = seg.campos || [];
    if (campos.length) {
      const campoW = (anchoSeg - campoGap * (campos.length - 1)) / campos.length;
      campos.forEach((c, ci) => {
        const cx2 = groupX + ci * (campoW + campoGap);
        svg += `<line x1="${segX + nW/2}" y1="${segY + nH}" x2="${cx2 + campoW/2}" y2="${camposY}" stroke="#1E2D47" stroke-width="1"/>`;
        svg += nodoSVG(cx2, camposY, campoW, nH - 4, c.lexema, '#EEF2F8', '#1C2B3A', true);
      });
    }
  });

  svg += '</svg></div>';
  return svg;
}

function nodoSVG(x, y, w, h, label, bg, tc, small=false) {
  const fs = small ? 8 : 10;
  const maxChars = small ? Math.max(6, Math.floor(w / 7)) : 14;
  const txt = label.length > maxChars ? label.slice(0, maxChars - 1) + '…' : label;
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="5" fill="${bg}" stroke="${tc}" stroke-width="1.2"/>
  <text x="${x + w/2}" y="${y + h/2 + fs/3}" text-anchor="middle" font-size="${fs}" fill="${tc}" font-family="JetBrains Mono" font-weight="500">${escHtml(txt)}</text>`;
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

function renderTuring(turing) {
  if (!turing) return '';

  const cinta = turing.cinta_ejemplo || [];
  let cintaHtml = '<div style="display:flex;gap:2px;margin:0.75rem 0;flex-wrap:wrap">';
  cinta.forEach((sym, i) => {
    const isHead = i === 0;
    cintaHtml += `<div style="
      min-width:32px;height:32px;
      border:1px solid ${isHead ? 'var(--blue)' : 'var(--border)'};
      border-radius:4px;
      display:flex;align-items:center;justify-content:center;
      font-family:JetBrains Mono,monospace;font-size:0.8rem;
      background:${isHead ? 'rgba(46,94,158,0.15)' : 'var(--surface)'};
      color:${sym === '□' ? 'var(--text-dim)' : 'var(--text)'};
      position:relative;
    ">
      ${escHtml(sym)}
      ${isHead ? '<div style="position:absolute;top:-14px;font-size:0.6rem;color:var(--blue)">▼</div>' : ''}
    </div>`;
  });
  cintaHtml += '</div>';

  const t = turing.tabla;
  let tablaHtml = '<div style="overflow-x:auto;margin-top:1rem">';
  tablaHtml += '<p style="font-size:0.68rem;color:var(--text-dim);margin-bottom:0.5rem;letter-spacing:1px;text-transform:uppercase">Tabla de transiciones — Formato: estado_destino / símbolo_escribe / movimiento</p>';
  tablaHtml += '<table class="data-table" style="min-width:700px"><thead><tr>';
  tablaHtml += '<th>Estado</th>';
  (t.simbolos || []).forEach(s => { tablaHtml += `<th>${escHtml(s)}</th>`; });
  tablaHtml += '</tr></thead><tbody>';
  (t.estados || []).forEach((est, idx) => {
    const isAcept = est === 'qACEPT';
    const isReject = est === 'qREJECT';
    const rowBg = idx % 2 === 1 ? 'rgba(28,43,58,0.03)' : 'transparent';
    tablaHtml += `<tr style="background:${rowBg}">`;
    const color = isAcept ? 'var(--teal)' : isReject ? 'var(--red)' : 'var(--blue)';
    tablaHtml += `<td style="font-family:JetBrains Mono,monospace;font-weight:500;color:${color}">${est}</td>`;
    (t.simbolos || []).forEach(s => {
      const val = t.transiciones[est]?.[s] || '—';
      const isErr = val.includes('qR') || val === '—';
      const isOk  = val.includes('qA') || val.includes('SQL') || val.includes('✓');
      const tc = isErr ? 'var(--text-dim)' : isOk ? 'var(--teal)' : 'var(--text)';
      tablaHtml += `<td style="font-family:JetBrains Mono,monospace;font-size:0.72rem;color:${tc}">${escHtml(val)}</td>`;
    });
    tablaHtml += '</tr>';
  });
  tablaHtml += '</tbody></table></div>';

  let transHtml = '<div style="display:flex;flex-direction:column;gap:0.35rem;margin-top:1rem">';
  (turing.transiciones || []).forEach(tr => {
    const isOk = tr.hacia === 'qACEPT' || tr.escribe === 'SQL' || tr.escribe === '✓';
    const isErr = tr.hacia === 'qREJECT';
    const color = isErr ? 'var(--red)' : isOk ? 'var(--teal)' : 'var(--text)';
    transHtml += `<div style="
      background:var(--surface);border:1px solid var(--border);border-radius:5px;
      padding:0.4rem 0.75rem;font-size:0.75rem;
      display:flex;align-items:center;gap:0.75rem;
    ">
      <span style="font-family:JetBrains Mono,monospace;color:var(--blue);flex-shrink:0">${tr.desde}</span>
      <span style="color:var(--text-dim)">→</span>
      <span style="font-family:JetBrains Mono,monospace;color:${color};flex-shrink:0">${tr.hacia}</span>
      <span style="color:var(--text-dim);font-size:0.68rem">
        lee: <span style="color:var(--yellow)">${escHtml(tr.lee)}</span>
        escribe: <span style="color:var(--purple)">${escHtml(tr.escribe)}</span>
        mueve: <span style="color:var(--blue)">${tr.mueve}</span>
      </span>
      <span style="color:var(--text-dim);font-size:0.68rem;margin-left:auto">${tr.descripcion}</span>
    </div>`;
  });
  transHtml += '</div>';

  return `
    <div style="margin-top:1.5rem;padding-top:1.5rem;border-top:1px solid var(--border)">
      <p style="font-size:0.7rem;color:var(--text-dim);margin-bottom:0.75rem;
                letter-spacing:1px;text-transform:uppercase">
        Máquina de Turing — Modelo computacional del transpilador TXT→SQL
      </p>
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:1rem">
        <p style="font-size:0.78rem;color:var(--text);margin-bottom:0.5rem">
          <strong style="color:var(--blue)">Descripción:</strong> ${turing.descripcion}
        </p>
        <p style="font-size:0.75rem;color:var(--text-dim)">
          Estado inicial: <span style="color:var(--blue);font-family:JetBrains Mono,monospace">${turing.estado_inicial}</span> &nbsp;|&nbsp;
          Aceptación: <span style="color:var(--teal);font-family:JetBrains Mono,monospace">${turing.estado_aceptacion}</span> &nbsp;|&nbsp;
          Rechazo: <span style="color:var(--red);font-family:JetBrains Mono,monospace">${turing.estado_rechazo}</span>
        </p>
        <p style="font-size:0.72rem;color:var(--text-dim);margin-top:0.5rem">
          Cinta de ejemplo (cabezal en posición inicial ▼):
        </p>
        ${cintaHtml}
        <p style="font-size:0.72rem;color:var(--text-dim);margin-top:1rem">
          Función de transición δ(q, a) = (q', b, D):
        </p>
        ${transHtml}
        ${tablaHtml}
      </div>
    </div>`;
}

let automatasTokenGlobal = null;

function poblarSelectorTokens(tipo, automatasToken) {
  automatasTokenGlobal = automatasToken;
  const sel = document.getElementById('selector-token-' + tipo);
  if (!sel) return;
  sel.innerHTML = '<option value="">Selecciona un token...</option>';
  Object.keys(automatasToken).forEach(nombre => {
    sel.innerHTML += `<option value="${nombre}">${nombre}</option>`;
  });
}

function mostrarAutomataToken(tipo, nombreToken) {
  const cont = document.getElementById('resultado-token-' + tipo);
  if (!nombreToken || !automatasTokenGlobal) {
    cont.innerHTML = '';
    return;
  }
  const data = automatasTokenGlobal[nombreToken];
  if (!data) { cont.innerHTML = ''; return; }

  let html = `<div class="tok tok-${nombreToken}" style="display:inline-block;margin-bottom:0.75rem">${nombreToken}</div>`;

  if (tipo === 'afnd') {
    html += renderAutomata(data.afnd, 'AFND — ' + nombreToken);
  } else {
    html += renderAutomata(data.afd, 'AFD — ' + nombreToken);
  }
  html += renderTablaTransiciones(data.tabla);

  cont.innerHTML = html;
}

function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
