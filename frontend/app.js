/* =====================================================================
   Frontend - Sistema de Tarjetas de Circulación
   Comunicación con la API REST de Flask
===================================================================== */

const API = '/api';

// =====================================================================
// Helpers
// =====================================================================
async function api(path, options = {}) {
  const res = await fetch(API + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: 'Error desconocido' }));
    throw new Error(err.error || 'Error en la petición');
  }
  return res.json();
}

function toast(msg, type = 'success') {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = `toast ${type}`;
  setTimeout(() => el.classList.add('hidden'), 3500);
}

function badge(estado) {
  if (!estado) return '<em style="color:#a0aec0">N/A</em>';
  return `<span class="badge ${estado.toLowerCase()}">${estado}</span>`;
}

function fmtDate(d) {
  if (!d) return '-';
  return new Date(d).toLocaleDateString('es-GT');
}

// =====================================================================
// Tabs
// =====================================================================
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(btn.dataset.tab).classList.add('active');
  });
});

// =====================================================================
// Carga inicial
// =====================================================================
async function checkConnection() {
  const el = document.getElementById('db-status');
  try {
    const r = await api('/health');
    el.textContent = '✅ Conectado a PostgreSQL';
    el.classList.add('ok');
  } catch (e) {
    el.textContent = '❌ Sin conexión a la base de datos';
    el.classList.add('error');
  }
}

async function cargarDashboard() {
  try {
    const stats = await api('/estadisticas');
    document.getElementById('stats').innerHTML = `
      <div class="stat-card"><div class="label">Vehículos registrados</div><div class="value">${stats.total_vehiculos}</div></div>
      <div class="stat-card"><div class="label">Propietarios</div><div class="value">${stats.total_propietarios}</div></div>
      <div class="stat-card"><div class="label">Tarjetas activas</div><div class="value">${stats.tarjetas_activas}</div></div>
      <div class="stat-card warn"><div class="label">Tarjetas vencidas</div><div class="value">${stats.tarjetas_vencidas}</div></div>
      <div class="stat-card err"><div class="label">Desactivadas / Impago</div><div class="value">${stats.tarjetas_desactiv}</div></div>
    `;

    const tarjetas = await api('/tarjetas');
    const tbody = document.querySelector('#tbl-recientes tbody');
    // Solo mostrar registros que SÍ tengan tarjeta (id_tarjeta no null)
    const conTarjeta = tarjetas.filter(t => t.id_tarjeta);
    tbody.innerHTML = conTarjeta.slice(0, 10).map(t => `
      <tr>
        <td>${t.id_tarjeta}</td>
        <td><strong>${t.numero_placa}</strong></td>
        <td>${t.nombre_marca} ${t.nombre_modelo}</td>
        <td>${t.nombre_propietario || '-'}</td>
        <td>${fmtDate(t.fecha_vencimiento)}</td>
        <td>${badge(t.estado_tarjeta)}</td>
      </tr>
    `).join('');
  } catch (e) {
    toast('Error al cargar dashboard: ' + e.message, 'error');
  }
}

// =====================================================================
// Catálogos (para los <select>)
// =====================================================================
async function cargarCatalogos() {
  const [modelos, tipos, propietarios, usuarios, vehiculos, tarjetas, marcas] = await Promise.all([
    api('/modelos'),
    api('/tipos-uso'),
    api('/propietarios'),
    api('/usuarios'),
    api('/tarjetas'),
    api('/tarjetas'),
    api('/marcas'),
  ]);

  // Marcas (para crear modelo)
  const marcaOpts = marcas.map(m =>
    `<option value="${m.id_marca}">${m.nombre_marca}</option>`
  ).join('');
  const selMarca = document.getElementById('nm-marca-existente');
  if (selMarca) selMarca.innerHTML = '<option value="">-- Seleccione --</option>' + marcaOpts;

  // Modelos
  const modOpts = modelos.map(m =>
    `<option value="${m.id_modelo}">${m.nombre_marca} - ${m.nombre_modelo}</option>`
  ).join('');
  document.getElementById('sel-modelo').innerHTML = modOpts;
  document.getElementById('nv-modelo').innerHTML = modOpts;

  // Tipos de uso
  const tipoOpts = tipos.map(t =>
    `<option value="${t.id_tipo_uso}">${t.descripcion}</option>`
  ).join('');
  document.getElementById('sel-tipo-uso').innerHTML = tipoOpts;
  document.getElementById('nv-tipo-uso').innerHTML = tipoOpts;

  // Propietarios
  const propOpts = propietarios.map(p =>
    `<option value="${p.id_propietario}">${p.nombre} (DPI: ${p.dpi})</option>`
  ).join('');
  document.getElementById('sel-propietario').innerHTML = propOpts;
  document.getElementById('cd-nuevo').innerHTML = propOpts;
  document.getElementById('nv-propietario').innerHTML = propOpts;

  // Usuarios SAT
  document.getElementById('sel-usuario').innerHTML = usuarios.map(u =>
    `<option value="${u.id_usuario}">${u.nombre} (Lic. ${u.licencia})</option>`
  ).join('');

  // Vehículos (modificar, cambio color/motor/dueño)
  const vehOpts = vehiculos.map(v =>
    `<option value="${v.id_vehiculo}">${v.numero_placa} - ${v.nombre_marca} ${v.nombre_modelo}</option>`
  ).join('');
  document.getElementById('mod-vehiculo').innerHTML = '<option value="">Selecciona...</option>' + vehOpts;
  document.getElementById('cc-vehiculo').innerHTML  = '<option value="">Selecciona...</option>' + vehOpts;
  document.getElementById('cm-vehiculo').innerHTML  = '<option value="">Selecciona...</option>' + vehOpts;
  document.getElementById('cd-vehiculo').innerHTML  = '<option value="">Selecciona...</option>' + vehOpts;
  document.getElementById('nc-vehiculo').innerHTML  = '<option value="">Selecciona...</option>' + vehOpts;

  // Tarjetas para desactivar
  document.getElementById('ds-tarjeta').innerHTML = '<option value="">Selecciona...</option>' +
    tarjetas.filter(t => t.estado_tarjeta === 'ACTIVA').map(t =>
      `<option value="${t.id_tarjeta}">#${t.id_tarjeta} - ${t.numero_placa} (${t.nombre_propietario || 'sin dueño'})</option>`
    ).join('');

  // Listeners para mostrar color/motor/dueño actual
  document.getElementById('cc-vehiculo').addEventListener('change', async e => {
    const v = vehiculos.find(x => x.id_vehiculo == e.target.value);
    document.getElementById('cc-actual').value = v ? v.color : '';
  });
  document.getElementById('cm-vehiculo').addEventListener('change', async e => {
    const v = vehiculos.find(x => x.id_vehiculo == e.target.value);
    document.getElementById('cm-actual').value = v ? v.numero_motor : '';
  });
  document.getElementById('cd-vehiculo').addEventListener('change', async e => {
    const v = vehiculos.find(x => x.id_vehiculo == e.target.value);
    document.getElementById('cd-actual').value = v ? (v.nombre_propietario || 'Sin dueño') : '';
  });
}

// =====================================================================
// Consultar tarjetas
// =====================================================================
// =====================================================================
// Consultar tarjetas (incluye vehículos sin tarjeta)
// =====================================================================
async function buscarTarjetas() {
  const q = document.getElementById('q-busqueda').value.trim();
  const estado = document.getElementById('q-estado').value;
  const params = new URLSearchParams();
  if (q) params.append('q', q);
  if (estado) params.append('estado', estado);

  try {
    const rows = await api('/tarjetas?' + params.toString());
    const tbody = document.querySelector('#tbl-consulta tbody');
    tbody.innerHTML = rows.length === 0
      ? `<tr><td colspan="11" style="text-align:center;color:#718096;padding:1.5rem;">Sin resultados</td></tr>`
      : rows.map(t => {
          const tarjetaCell = t.id_tarjeta
            ? `#${t.id_tarjeta}`
            : `<em style="color:#a0aec0">Sin tarjeta</em>`;
          const vencCell = t.fecha_vencimiento ? fmtDate(t.fecha_vencimiento) : '-';
          const estadoCell = t.estado_tarjeta ? badge(t.estado_tarjeta) : '<em style="color:#a0aec0">N/A</em>';
          const propCell = t.nombre_propietario || '<em style="color:#a0aec0">Sin dueño</em>';
          const detalleBtn = t.id_tarjeta
            ? `<button class="btn-detail" onclick="verDetalle(${t.id_tarjeta},${t.id_vehiculo})">Ver</button>`
            : `<button class="btn-detail" onclick="verHistorialVehiculo(${t.id_vehiculo})">Ver</button>`;
          return `
            <tr>
              <td>${t.id_vehiculo}</td>
              <td><strong>${t.numero_placa}</strong></td>
              <td>${t.nombre_marca}</td>
              <td>${t.nombre_modelo}</td>
              <td>${t.anio}</td>
              <td>${t.color}</td>
              <td>${propCell}</td>
              <td>${tarjetaCell}</td>
              <td>${vencCell}</td>
              <td>${estadoCell}</td>
              <td>${detalleBtn}</td>
            </tr>
          `;
        }).join('');
  } catch (e) {
    toast('Error: ' + e.message, 'error');
  }
}

// Ver historial de un vehículo que no tiene tarjeta aún
async function verHistorialVehiculo(idVehiculo) {
  try {
    const hist = await api('/vehiculos/' + idVehiculo + '/historial');
    document.getElementById('detalle-body').innerHTML = `
      <p style="color:#718096">Este vehículo aún no tiene tarjeta de circulación emitida.</p>
    `;
    renderHistorial(hist);
    document.getElementById('modal-detalle').classList.remove('hidden');
  } catch (e) {
    toast('Error al cargar historial: ' + e.message, 'error');
  }
}

async function verDetalle(idTarjeta, idVehiculo) {
  try {
    const [t, hist] = await Promise.all([
      api('/tarjetas/' + idTarjeta),
      api('/vehiculos/' + idVehiculo + '/historial'),
    ]);

    document.getElementById('detalle-body').innerHTML = `
      <div class="detalle-fields">
        <div><strong>Placa</strong>${t.numero_placa}</div>
        <div><strong>Tipo de placa</strong>${t.tipo_placa}</div>
        <div><strong>Marca / Modelo</strong>${t.nombre_marca} ${t.nombre_modelo}</div>
        <div><strong>Año</strong>${t.anio}</div>
        <div><strong>Color</strong>${t.color}</div>
        <div><strong>Tipo de uso</strong>${t.tipo_uso}</div>
        <div><strong>Motor</strong>${t.numero_motor}</div>
        <div><strong>Chasis</strong>${t.numero_chasis}</div>
        <div><strong>Propietario</strong>${t.nombre_propietario || '-'}</div>
        <div><strong>DPI Propietario</strong>${t.dpi_propietario || '-'}</div>
        <div><strong>Usuario SAT</strong>${t.nombre_usuario_sat}</div>
        <div><strong>Licencia</strong>${t.licencia}</div>
        <div><strong>Emisión</strong>${fmtDate(t.fecha_emision)}</div>
        <div><strong>Vencimiento</strong>${fmtDate(t.fecha_vencimiento)}</div>
        <div><strong>Estado</strong>${badge(t.estado_tarjeta)}</div>
        <div><strong>Motivo desact.</strong>${t.motivo_desactivacion || '-'}</div>
      </div>
    `;

    renderHistorial(hist);
    document.getElementById('modal-detalle').classList.remove('hidden');
  } catch (e) {
    toast('Error al cargar detalle: ' + e.message, 'error');
  }
}

function renderHistorial(hist) {
  let histHtml = '';

  // Tarjetas anteriores del vehículo
  if (hist.tarjetas && hist.tarjetas.length) {
    histHtml += '<h5>📄 Tarjetas de circulación de este vehículo:</h5>';
    histHtml += '<div class="table-wrapper" style="margin-bottom:1rem;"><table><thead><tr>';
    histHtml += '<th>ID</th><th>Emisión</th><th>Vencimiento</th><th>Estado</th><th>Motivo</th></tr></thead><tbody>';
    hist.tarjetas.forEach(card => {
      histHtml += `<tr>
        <td>#${card.id_tarjeta}</td>
        <td>${fmtDate(card.fecha_emision)}</td>
        <td>${fmtDate(card.fecha_vencimiento)}</td>
        <td>${badge(card.estado)}</td>
        <td>${card.motivo_desactivacion || '-'}</td>
      </tr>`;
    });
    histHtml += '</tbody></table></div>';
  }

  // Propietarios
  if (hist.propietarios.length) {
    histHtml += '<h5>👥 Propietarios:</h5><ul>';
    hist.propietarios.forEach(p => {
      histHtml += `<li><strong>${p.nombre}</strong> (DPI ${p.dpi}) - desde ${fmtDate(p.fecha_inicio)} hasta ${p.es_actual ? '<strong style="color:#38a169">ACTUAL</strong>' : fmtDate(p.fecha_fin)}</li>`;
    });
    histHtml += '</ul>';
  }

  // Cambios de color
  if (hist.cambios_color.length) {
    histHtml += '<h5>🎨 Cambios de color:</h5><ul>';
    hist.cambios_color.forEach(c => {
      histHtml += `<li>${c.color_anterior} → <strong>${c.color_nuevo}</strong> (${fmtDate(c.fecha_cambio)})${c.observaciones ? ' — ' + c.observaciones : ''}</li>`;
    });
    histHtml += '</ul>';
  }

  // Cambios de motor
  if (hist.cambios_motor.length) {
    histHtml += '<h5>⚙️ Cambios de motor:</h5><ul>';
    hist.cambios_motor.forEach(c => {
      histHtml += `<li>${c.motor_anterior} → <strong>${c.motor_nuevo}</strong> (${fmtDate(c.fecha_cambio)})${c.observaciones ? ' — ' + c.observaciones : ''}</li>`;
    });
    histHtml += '</ul>';
  }

  if (!histHtml) histHtml = '<p style="color:#718096">Sin historial registrado.</p>';
  document.getElementById('historial-body').innerHTML = histHtml;
}

function cerrarModal() {
  document.getElementById('modal-detalle').classList.add('hidden');
}

// =====================================================================
// Registrar nueva tarjeta
// =====================================================================
async function registrarTarjeta(ev) {
  ev.preventDefault();
  const form = ev.target;
  const fd = new FormData(form);

  const payload = {
    vehiculo: {
      anio:          parseInt(fd.get('anio')),
      color:         fd.get('color'),
      numero_motor:  fd.get('numero_motor'),
      numero_chasis: fd.get('numero_chasis'),
      numero_placa:  fd.get('numero_placa'),
      tipo_placa:    fd.get('tipo_placa'),
      id_modelo:     parseInt(fd.get('id_modelo')),
      id_tipo_uso:   parseInt(fd.get('id_tipo_uso')),
    },
    id_propietario:    parseInt(fd.get('id_propietario')),
    id_usuario:        parseInt(fd.get('id_usuario')),
    fecha_emision:     fd.get('fecha_emision'),
    fecha_vencimiento: fd.get('fecha_vencimiento'),
  };

  try {
    const r = await api('/tarjetas', { method: 'POST', body: JSON.stringify(payload) });
    toast(`Tarjeta #${r.id_tarjeta} registrada correctamente`);
    form.reset();
    cargarCatalogos();
    cargarDashboard();
  } catch (e) {
    toast('Error: ' + e.message, 'error');
  }
}

// =====================================================================
// Modificar vehículo
// =====================================================================
async function cargarVehiculoParaModificar() {
  const id = document.getElementById('mod-vehiculo').value;
  if (!id) {
    document.getElementById('form-modificar').classList.add('hidden');
    return;
  }
  const vehiculos = await api('/tarjetas');
  const v = vehiculos.find(x => x.id_vehiculo == id);
  if (!v) return;

  const form = document.getElementById('form-modificar');
  form.classList.remove('hidden');
  form.dataset.idVehiculo = id;
  form.anio.value          = v.anio;
  form.color.value         = v.color;
  form.numero_motor.value  = v.numero_motor;
  form.numero_chasis.value = v.numero_chasis;
  form.numero_placa.value  = v.numero_placa;
  form.tipo_placa.value    = v.tipo_placa;
}

async function modificarVehiculo(ev) {
  ev.preventDefault();
  const form = ev.target;
  const id = form.dataset.idVehiculo;
  const payload = {
    anio:          parseInt(form.anio.value),
    color:         form.color.value,
    numero_motor:  form.numero_motor.value,
    numero_chasis: form.numero_chasis.value,
    numero_placa:  form.numero_placa.value,
    tipo_placa:    form.tipo_placa.value,
  };
  try {
    await api('/vehiculos/' + id, { method: 'PUT', body: JSON.stringify(payload) });
    toast('Vehículo actualizado');
    cargarCatalogos();
    cargarDashboard();
  } catch (e) {
    toast('Error: ' + e.message, 'error');
  }
}

// =====================================================================
// Cambio de color
// =====================================================================
async function hacerCambioColor(ev) {
  ev.preventDefault();
  const id = document.getElementById('cc-vehiculo').value;
  const payload = {
    color_nuevo:   document.getElementById('cc-nuevo').value,
    observaciones: document.getElementById('cc-obs').value,
  };
  try {
    const r = await api(`/vehiculos/${id}/cambio-color`, { method: 'POST', body: JSON.stringify(payload) });
    let msg = `Color cambiado de ${r.color_anterior} a ${r.color_nuevo}`;
    if (r.tarjeta) msg += ` • ${r.tarjeta}`;
    toast(msg);
    ev.target.reset();
    cargarCatalogos();
    cargarDashboard();
  } catch (e) {
    toast('Error: ' + e.message, 'error');
  }
}

// =====================================================================
// Cambio de motor
// =====================================================================
async function hacerCambioMotor(ev) {
  ev.preventDefault();
  const id = document.getElementById('cm-vehiculo').value;
  const payload = {
    motor_nuevo:   document.getElementById('cm-nuevo').value,
    observaciones: document.getElementById('cm-obs').value,
  };
  try {
    const r = await api(`/vehiculos/${id}/cambio-motor`, { method: 'POST', body: JSON.stringify(payload) });
    let msg = `Motor cambiado: ${r.motor_anterior} → ${r.motor_nuevo}`;
    if (r.tarjeta) msg += ` • ${r.tarjeta}`;
    toast(msg);
    ev.target.reset();
    cargarCatalogos();
    cargarDashboard();
  } catch (e) {
    toast('Error: ' + e.message, 'error');
  }
}

// =====================================================================
// Cambio de dueño
// =====================================================================
async function hacerCambioDueno(ev) {
  ev.preventDefault();
  const id = document.getElementById('cd-vehiculo').value;
  const payload = {
    id_propietario_nuevo: parseInt(document.getElementById('cd-nuevo').value),
  };
  try {
    const r = await api(`/vehiculos/${id}/cambio-dueno`, { method: 'POST', body: JSON.stringify(payload) });
    let msg = `Cambio de dueño: ${r.propietario_anterior || 'sin dueño'} → ${r.propietario_nuevo}`;
    if (r.tarjeta) msg += ` • ${r.tarjeta}`;
    toast(msg);
    ev.target.reset();
    cargarCatalogos();
    cargarDashboard();
  } catch (e) {
    toast('Error: ' + e.message, 'error');
  }
}

// =====================================================================
// Desactivar tarjeta
// =====================================================================
async function hacerDesactivacion(ev) {
  ev.preventDefault();
  const id = document.getElementById('ds-tarjeta').value;
  const payload = {
    motivo:      document.getElementById('ds-motivo').value,
    observacion: document.getElementById('ds-obs').value,
  };
  try {
    const r = await api(`/tarjetas/${id}/desactivar`, { method: 'POST', body: JSON.stringify(payload) });
    toast(`Tarjeta marcada como ${r.estado}`);
    ev.target.reset();
    cargarCatalogos();
    cargarDashboard();
  } catch (e) {
    toast('Error: ' + e.message, 'error');
  }
}

// =====================================================================
// Crear nuevo propietario
// =====================================================================
async function crearPropietario(ev) {
  ev.preventDefault();
  const fd = new FormData(ev.target);
  const payload = {
    nombre:    fd.get('nombre'),
    dpi:       fd.get('dpi'),
    direccion: fd.get('direccion'),
    telefono:  fd.get('telefono'),
  };
  try {
    const r = await api('/propietarios', { method: 'POST', body: JSON.stringify(payload) });
    toast(`Propietario #${r.id_propietario} registrado correctamente`);
    ev.target.reset();
    cargarCatalogos();
    cargarDashboard();
  } catch (e) {
    toast('Error: ' + e.message, 'error');
  }
}

// =====================================================================
// Crear nuevo vehículo
// =====================================================================
async function crearVehiculo(ev) {
  ev.preventDefault();
  const fd = new FormData(ev.target);
  const payload = {
    vehiculo: {
      numero_placa:  fd.get('numero_placa'),
      tipo_placa:    fd.get('tipo_placa'),
      anio:          parseInt(fd.get('anio')),
      color:         fd.get('color'),
      numero_motor:  fd.get('numero_motor'),
      numero_chasis: fd.get('numero_chasis'),
      id_modelo:     parseInt(fd.get('id_modelo')),
      id_tipo_uso:   parseInt(fd.get('id_tipo_uso')),
    },
    id_propietario: parseInt(fd.get('id_propietario')),
  };
  try {
    const r = await api('/vehiculos', { method: 'POST', body: JSON.stringify(payload) });
    toast(`Vehículo #${r.id_vehiculo} registrado correctamente`);
    ev.target.reset();
    cargarCatalogos();
    cargarDashboard();
  } catch (e) {
    toast('Error: ' + e.message, 'error');
  }
}

// =====================================================================
// Crear nueva calcomanía
// =====================================================================
async function crearCalcomania(ev) {
  ev.preventDefault();
  const fd = new FormData(ev.target);
  const payload = {
    id_vehiculo: parseInt(fd.get('id_vehiculo')),
    anio:        parseInt(fd.get('anio')),
    estado:      fd.get('estado'),
  };
  try {
    const r = await api('/calcomanias', { method: 'POST', body: JSON.stringify(payload) });
    toast(`Calcomanía #${r.id_calcomania} registrada correctamente`);
    ev.target.reset();
  } catch (e) {
    toast('Error: ' + e.message, 'error');
  }
}

// =====================================================================
// Crear nueva marca
// =====================================================================
async function crearMarca(ev) {
  ev.preventDefault();
  const fd = new FormData(ev.target);
  const payload = { nombre_marca: fd.get('nombre_marca') };
  try {
    const r = await api('/marcas', { method: 'POST', body: JSON.stringify(payload) });
    toast(`Marca #${r.id_marca} registrada correctamente`);
    ev.target.reset();
    cargarCatalogos();   // refresca todos los selects que dependen de marcas
  } catch (e) {
    toast('Error: ' + e.message, 'error');
  }
}

// =====================================================================
// Crear nuevo modelo (con marca existente o nueva)
// =====================================================================
async function crearModelo(ev) {
  ev.preventDefault();
  const nombreModelo = document.getElementById('nm-nombre-modelo').value.trim();
  const idMarca      = document.getElementById('nm-marca-existente').value;
  const nombreMarca  = document.getElementById('nm-marca-nueva').value.trim();

  if (!nombreModelo) {
    toast('Debe escribir el nombre del modelo', 'error');
    return;
  }
  if (!idMarca && !nombreMarca) {
    toast('Seleccione una marca existente o escriba una nueva', 'error');
    return;
  }

  const payload = { nombre_modelo: nombreModelo };
  if (idMarca)      payload.id_marca = parseInt(idMarca);
  if (nombreMarca)  payload.nombre_marca = nombreMarca;

  try {
    const r = await api('/modelos', { method: 'POST', body: JSON.stringify(payload) });
    toast(`Modelo #${r.id_modelo} registrado (marca #${r.id_marca})`);
    ev.target.reset();
    cargarCatalogos();   // refresca los selects de toda la app
  } catch (e) {
    toast('Error: ' + e.message, 'error');
  }
}

// =====================================================================
// Inicialización
// =====================================================================
(async function init() {
  await checkConnection();
  await cargarCatalogos();
  await cargarDashboard();
  await buscarTarjetas();

  // Fecha por defecto: hoy + 3 años
  const hoy = new Date();
  const tres = new Date(); tres.setFullYear(tres.getFullYear() + 3);
  document.querySelector('[name="fecha_emision"]').value     = hoy.toISOString().slice(0, 10);
  document.querySelector('[name="fecha_vencimiento"]').value = tres.toISOString().slice(0, 10);
})();
