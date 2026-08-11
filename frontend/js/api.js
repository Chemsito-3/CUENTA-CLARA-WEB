// =============================================================================
// api.js - Utilidades para consumir la API de Cuenta Clara
// Proyecto: Cuenta Clara | Evidencia: GA7-220501096-AA5-EV03
// Autor: Carlos Varón
// =============================================================================

const API_URL = 'http://localhost:5000';

// ── Obtener token guardado en localStorage ─────────────────────────────────
function getToken() {
    return localStorage.getItem('cc_token');
}

// ── Headers con token JWT ──────────────────────────────────────────────────
function authHeaders() {
    return {
        'Content-Type' : 'application/json',
        'Authorization': `Bearer ${getToken()}`
    };
}

// ── Verificar si el usuario está autenticado ───────────────────────────────
function verificarAuth() {
    const token = getToken();
    if (!token) {
        window.location.href = 'index.html';
        return false;
    }
    return true;
}

// ── Cerrar sesión ──────────────────────────────────────────────────────────
function cerrarSesion() {
    localStorage.removeItem('cc_token');
    localStorage.removeItem('cc_tendero');
    window.location.href = 'index.html';
}

// ── Obtener datos del tendero guardados ────────────────────────────────────
function getTendero() {
    const data = localStorage.getItem('cc_tendero');
    return data ? JSON.parse(data) : null;
}

// ── Función genérica para llamadas a la API ────────────────────────────────
async function apiCall(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: authHeaders()
    };
    if (body) options.body = JSON.stringify(body);

    const res  = await fetch(`${API_URL}${endpoint}`, options);
    const data = await res.json();
    return { ok: res.ok, status: res.status, data };
}

// ── Formatear moneda colombiana ────────────────────────────────────────────
function formatCOP(valor) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency', currency: 'COP',
        minimumFractionDigits: 0
    }).format(valor);
}

// ── Mostrar alerta UI ──────────────────────────────────────────────────────
function mostrarAlerta(id, tipo, mensaje) {
    const el = document.getElementById(id);
    if (!el) return;
    el.className = `alerta-ui ${tipo} show`;
    el.textContent = (tipo === 'exito' ? '✅ ' : '❌ ') + mensaje;
    setTimeout(() => el.classList.remove('show'), 4000);
}

// ── Pintar nombre del tendero en el navbar ─────────────────────────────────
function pintarNavbar() {
    const tendero = getTendero();
    const el = document.getElementById('nav-tienda');
    if (el && tendero) el.textContent = `🏪 ${tendero.nombre_tienda}`;
}
