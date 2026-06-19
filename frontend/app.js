const API = '';

function switchTab(name, el) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('panel-' + name).classList.add('active');
}

async function indexProject() {
  const name = document.getElementById('idx-name').value.trim();
  const url  = document.getElementById('idx-url').value.trim();
  const btn  = document.getElementById('idx-btn');
  const out  = document.getElementById('idx-result');

  if (!name || !url) { showStatus(out, 'Rellena los dos campos.', 'err'); return; }

  btn.disabled = true;
  btn.textContent = 'Indexando…';
  out.className = 'result';

  try {
    const res  = await fetch(`${API}/index`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_name: name, git_url: url }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail ?? JSON.stringify(data));
    showStatus(out, `Listo — ${data.files_indexed} archivos indexados (id: ${data.project_id}).`, 'ok');
    loadProjects();
  } catch (e) {
    showStatus(out, `Error: ${e.message}`, 'err');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Indexar';
  }
}

async function queryProject() {
  const name  = document.getElementById('q-project').value;
  const query = document.getElementById('q-query').value.trim();
  const btn   = document.getElementById('q-btn');
  const out   = document.getElementById('q-result');

  if (!name || !query) { showStatus(out, 'Rellena los dos campos.', 'err'); return; }

  btn.disabled = true;
  btn.textContent = 'Consultando…';
  out.className = 'result';

  try {
    const res  = await fetch(`${API}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_name: name, query }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail ?? JSON.stringify(data));
    renderAnswer(out, data);
  } catch (e) {
    showStatus(out, `Error: ${e.message}`, 'err');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Preguntar';
  }
}

function renderAnswer(container, data) {
  const sid = 'src-' + Date.now();
  container.innerHTML = `
    <div class="answer">${escHtml(data.answer)}</div>
    <button class="sources-toggle" onclick="toggleSources('${sid}', this)">Ver fuentes (${data.sources.length})</button>
    <div id="${sid}" class="sources">
      ${data.sources.map(s => `
        <div class="source-item">
          <div class="source-meta">${escHtml(s.chunk_type)} · líneas ${s.start_line}–${s.end_line}</div>
          <div class="source-code">${escHtml(s.code)}</div>
        </div>
      `).join('')}
    </div>
  `;
  container.className = 'result visible';
}

function toggleSources(id, btn) {
  const open = document.getElementById(id).classList.toggle('open');
  btn.textContent = (open ? 'Ocultar' : 'Ver') + btn.textContent.replace(/^(Ver|Ocultar)/, '');
}

function showStatus(container, msg, type) {
  container.innerHTML = `<div class="status ${type}">${escHtml(msg)}</div>`;
  container.className = 'result visible';
}

function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

async function loadProjects() {
  const sel = document.getElementById('q-project');
  try {
    const res = await fetch(`${API}/projects`);
    const projects = await res.json();
    if (projects.length === 0) {
      sel.innerHTML = '<option value="">Sin proyectos indexados</option>';
    } else {
      sel.innerHTML = projects.map(p =>
        `<option value="${escHtml(p.name)}" data-desc="${escHtml(p.description ?? '')}">${escHtml(p.name)}</option>`
      ).join('');
    }
  } catch {
    sel.innerHTML = '<option value="">Error al cargar proyectos</option>';
  }
  updateDescription();
}

function updateDescription() {
  const sel = document.getElementById('q-project');
  const desc = sel.selectedOptions[0]?.dataset.desc ?? '';
  const div = document.getElementById('q-description');
  div.textContent = desc;
  div.style.display = desc ? 'block' : 'none';
}

document.addEventListener('DOMContentLoaded', loadProjects);
