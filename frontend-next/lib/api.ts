import type { AuthResponse, Company, RAT, DashboardStats, AuditLog, User, UserCompany, RolEmpresa, SecurityBreach, Rubro, RATSugerido } from '@/types';
import { API_BASE } from './constants';



function getToken(): string {
  if (typeof window === 'undefined') return '';
  return localStorage.getItem('custodio_token') || '';
}

export { getToken };

function authHeaders(): HeadersInit {
  return {
    Authorization: `Bearer ${getToken()}`,
    'Content-Type': 'application/json',
  };
}

let isRefreshing = false;
let refreshSubscribers: Array<(token: string) => void> = [];

function subscribeTokenRefresh(cb: (token: string) => void) {
  refreshSubscribers.push(cb);
}

function onTokenRefreshed(newToken: string) {
  refreshSubscribers.forEach((cb) => cb(newToken));
  refreshSubscribers = [];
}

async function tryRefreshToken(): Promise<string | null> {
  if (isRefreshing) {
    return new Promise((resolve) => {
      subscribeTokenRefresh((token) => resolve(token));
    });
  }
  isRefreshing = true;
  try {
    const res = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      credentials: 'include',
    });
    if (!res.ok) return null;
    const data = await res.json();
    if (data.access_token) {
      localStorage.setItem('custodio_token', data.access_token);
      onTokenRefreshed(data.access_token);
      return data.access_token;
    }
    return null;
  } catch {
    return null;
  } finally {
    isRefreshing = false;
  }
}

export async function apiFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const headers = { ...(options.headers || {}), ...authHeaders() };
  const init: RequestInit = { ...options, headers, credentials: 'include' };
  let res = await fetch(url, init)  // internal use;
  if (res.status === 401) {
    const newToken = await tryRefreshToken();
    if (newToken) {
      const retryHeaders = { ...headers, Authorization: `Bearer ${newToken}` };
      res = await fetch(url, { ...init, headers: retryHeaders })  // internal use;
    } else {
      localStorage.removeItem('custodio_token');
      localStorage.removeItem('custodio_user');
      localStorage.removeItem('custodio_company');
      window.location.replace('/login');
    }
  }
  return res;
}

async function handle<T>(res: Response): Promise<T> {
  if (res.status === 204) return {} as T;
  if (res.status === 401) {
    localStorage.removeItem('custodio_token');
    localStorage.removeItem('custodio_user');
    localStorage.removeItem('custodio_company');
    window.location.replace('/login');
    throw new Error('Sesión expirada');
  }
  if (!res.ok) {
    let detail = 'Error desconocido';
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      detail = res.statusText;
    }
    throw new Error(detail);
  }
  return res.json();
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export async function login(username: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ username, password }),
  });
  return handle<AuthResponse>(res);
}

export async function logout(): Promise<void> {
  localStorage.removeItem('custodio_token');
  localStorage.removeItem('custodio_user');
  localStorage.removeItem('custodio_company');
  await fetch(`${API_BASE}/auth/logout`, {
    method: 'POST',
    credentials: 'include',
  });
}

// ── Empresas ──────────────────────────────────────────────────────────────────

export async function listarEmpresas(): Promise<Company[]> {
  const res = await apiFetch(`${API_BASE}/companies/`);
  const data = await handle<{ empresas: Company[]; total: number; skip: number; limit: number }>(res);
  return data.empresas;
}

export async function crearEmpresa(data: Partial<Company>): Promise<Company> {
  const res = await apiFetch(`${API_BASE}/companies/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  return handle<Company>(res);
}

export async function actualizarEmpresa(id: number, data: Partial<Company>): Promise<Company> {
  const res = await apiFetch(`${API_BASE}/companies/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  return handle<Company>(res);
}

export async function eliminarEmpresa(id: number): Promise<void> {
  const res = await apiFetch(`${API_BASE}/companies/${id}`, { method: 'DELETE', });
  return handle<void>(res);
}

// ── RAT ───────────────────────────────────────────────────────────────────────

export async function listarRats(companyId?: number): Promise<RAT[]> {
  const url = companyId
    ? `${API_BASE}/rats/?company_id=${companyId}`
    : `${API_BASE}/rats/`;
  const res = await apiFetch(url);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Error al listar RATs');
  }
  const data = await res.json();
  return Array.isArray(data) ? data : (data.rats || []);
}

export interface ReportesResponse {
  total: number;
  skip: number;
  limit: number;
  sort_by: string;
  sort_order: string;
  filtros_aplicados: {
    company_id: number | null;
    search: string | null;
    estado: string | null;
    base_legal: string | null;
    categoria_titulares: string | null;
    datos_sensibles: boolean | null;
    evaluacion_impacto: boolean | null;
    transferencia_internacional: boolean | null;
    created_by: string | null;
  };
  rats: RAT[];
}

export interface ReportesParams {
  company_id?: number;
  search?: string;
  estado?: string;
  base_legal?: string;
  categoria_titulares?: string;
  datos_sensibles?: boolean;
  evaluacion_impacto?: boolean;
  transferencia_internacional?: boolean;
  created_by?: string;
  sort_by?: string;
  sort_order?: string;
  skip?: number;
  limit?: number;
}

export async function getReportes(params: ReportesParams): Promise<ReportesResponse> {
  const searchParams = new URLSearchParams();
  if (params.company_id) searchParams.set('company_id', String(params.company_id));
  if (params.search) searchParams.set('search', params.search);
  if (params.estado) searchParams.set('estado', params.estado);
  if (params.base_legal) searchParams.set('base_legal', params.base_legal);
  if (params.categoria_titulares) searchParams.set('categoria_titulares', params.categoria_titulares);
  if (params.datos_sensibles !== undefined) searchParams.set('datos_sensibles', String(params.datos_sensibles));
  if (params.evaluacion_impacto !== undefined) searchParams.set('evaluacion_impacto', String(params.evaluacion_impacto));
  if (params.transferencia_internacional !== undefined) searchParams.set('transferencia_internacional', String(params.transferencia_internacional));
  if (params.created_by) searchParams.set('created_by', params.created_by);
  if (params.sort_by) searchParams.set('sort_by', params.sort_by);
  if (params.sort_order) searchParams.set('sort_order', params.sort_order);
  if (params.skip !== undefined) searchParams.set('skip', String(params.skip));
  if (params.limit !== undefined) searchParams.set('limit', String(params.limit));

  const res = await apiFetch(`${API_BASE}/rats/reportes?${searchParams.toString()}`);
  return handle<ReportesResponse>(res);
}

export async function askAI(question: string, context?: string): Promise<{ answer: string }> {
  const res = await apiFetch(`${API_BASE}/ai/ask`, {
      method: 'POST',
      body: JSON.stringify({ question, context
    }),
  });
  return handle<{ answer: string }>(res);
}

export async function obtenerRat(id: number): Promise<RAT> {
  const res = await apiFetch(`${API_BASE}/rats/${id}`);
  return handle<RAT>(res);
}

export async function crearRat(data: Partial<RAT>): Promise<RAT> {
  const res = await apiFetch(`${API_BASE}/rats/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  return handle<RAT>(res);
}

export async function actualizarRat(id: number, data: Partial<RAT>): Promise<RAT> {
  const res = await apiFetch(`${API_BASE}/rats/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  return handle<RAT>(res);
}

export async function eliminarRat(id: number): Promise<void> {
  const res = await apiFetch(`${API_BASE}/rats/${id}`, { method: 'DELETE', });
  return handle<void>(res);
}

export async function getDashboardStats(companyId: number): Promise<DashboardStats> {
  const res = await apiFetch(`${API_BASE}/rats/dashboard/${companyId}`);
  return handle<DashboardStats>(res);
}

export async function sugerirRat(tipoProceso: string): Promise<Record<string, unknown>> {
  const res = await apiFetch(`${API_BASE}/rats/sugerencias`, {
      method: 'POST',
      body: JSON.stringify({ tipo_proceso: tipoProceso
    }),
  });
  return handle<Record<string, unknown>>(res);
}

export async function listarTiposProceso(): Promise<string[]> {
  const res = await apiFetch(`${API_BASE}/rats/sugerencias/tipos`);
  const data = await handle<{ tipos: string[] }>(res);
  return data.tipos || [];
}

export async function getAuditoria(ratId: number): Promise<AuditLog[]> {
  const res = await apiFetch(`${API_BASE}/rats/${ratId}/auditoria`);
  return handle<AuditLog[]>(res);
}

export async function getAuditoriaGlobal(companyId: number): Promise<Array<{
  id: number;
  rat_id: number;
  accion: string;
  usuario: string;
  timestamp: string;
  detalle?: string;
}>> {
  const res = await apiFetch(`${API_BASE}/rats/auditoria/${companyId}`);
  return handle<Array<{
    id: number;
    rat_id: number;
    accion: string;
    usuario: string;
    timestamp: string;
    detalle?: string;
  }>>(res);
}

export async function exportarCsv(companyId: number): Promise<Blob> {
  const res = await apiFetch(`${API_BASE}/rats/export/csv?company_id=${companyId}`);
  if (!res.ok) throw new Error('Error al exportar CSV');
  return res.blob();
}

export async function exportarPdf(companyId: number): Promise<Blob> {
  const res = await apiFetch(`${API_BASE}/rats/export/pdf?company_id=${companyId}`);
  if (!res.ok) throw new Error('Error al exportar PDF');
  return res.blob();
}

export async function exportarRatPdf(ratId: number): Promise<Blob> {
  const res = await apiFetch(`${API_BASE}/rats/${ratId}/export/pdf`);
  if (!res.ok) throw new Error('Error al exportar PDF');
  return res.blob();
}

export async function exportarCni(companyId: number): Promise<Blob> {
  const res = await apiFetch(`${API_BASE}/rats/export/cni?company_id=${companyId}`);
  if (!res.ok) throw new Error('Error al exportar CNI');
  return res.blob();
}

export async function duplicarRat(rat: RAT): Promise<RAT> {
  const payload = {
    company_id:                  rat.company_id,
    nombre_proceso:              `Copia de ${rat.nombre_proceso}`,
    categoria_datos:             rat.categoria_datos ?? '',
    categoria_titulares:         rat.categoria_titulares,
    finalidad:                   rat.finalidad ?? '',
    base_legal:                  rat.base_legal ?? 'Otra',
    fuente_datos:                rat.fuente_datos ?? '',
    plazo_retencion:             rat.plazo_retencion ?? '',
    transferencia_datos:         rat.transferencia_datos,
    medidas_seguridad:           rat.medidas_seguridad,
    destinatarios:               rat.destinatarios,
    nombre_encargado:            rat.nombre_encargado,
    tiene_contrato_encargado:    rat.tiene_contrato_encargado,
    transferencia_internacional: rat.transferencia_internacional,
    pais_destino:                rat.pais_destino,
    garantias_transferencia_int: rat.garantias_transferencia_int,
    datos_sensibles:             rat.datos_sensibles,
    tipo_dato_sensible:          rat.tipo_dato_sensible,
    evaluacion_impacto:          rat.evaluacion_impacto,
    estado_eipd:                 rat.evaluacion_impacto ? 'pendiente' : 'no_requerida',
    decisiones_automatizadas:    rat.decisiones_automatizadas,
    test_interes_legitimo:       rat.test_interes_legitimo,
  };
  return crearRat(payload);
}

export async function marcarRevisado(ratId: number): Promise<AuditLog> {
  const res = await apiFetch(`${API_BASE}/rats/${ratId}/revision`, { method: 'POST', });
  return handle<AuditLog>(res);
}

export async function aprobarRat(ratId: number): Promise<RAT> {
  const res = await apiFetch(`${API_BASE}/rats/${ratId}/aprobar`, { method: 'POST', });
  return handle<RAT>(res);
}

// ── Brechas de seguridad ──────────────────────────────────────────────────────

export async function listarBrechas(companyId: number): Promise<SecurityBreach[]> {
  const res = await apiFetch(`${API_BASE}/brechas/?company_id=${companyId}`);
  const data = await handle<{ brechas: SecurityBreach[]; total: number; skip: number; limit: number }>(res);
  return data.brechas;
}

export async function crearBrecha(data: Partial<SecurityBreach>): Promise<SecurityBreach> {
  const res = await apiFetch(`${API_BASE}/brechas/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  return handle<SecurityBreach>(res);
}

export async function actualizarBrecha(id: number, data: Partial<SecurityBreach>): Promise<SecurityBreach> {
  const res = await apiFetch(`${API_BASE}/brechas/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  return handle<SecurityBreach>(res);
}

export async function eliminarBrecha(id: number): Promise<void> {
  const res = await apiFetch(`${API_BASE}/brechas/${id}`, { method: 'DELETE', });
  return handle<void>(res);
}

export async function cambiarPassword(currentPassword: string, newPassword: string): Promise<void> {
  const res = await apiFetch(`${API_BASE}/auth/me/password`, {
      method: 'PUT',
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword
    }),
  });
  return handle<void>(res);
}

// ── Accesos por empresa ───────────────────────────────────────────────────────

export async function listarAccesos(companyId: number): Promise<UserCompany[]> {
  const res = await apiFetch(`${API_BASE}/companies/${companyId}/usuarios/`);
  return handle<UserCompany[]>(res);
}

export async function agregarAcceso(companyId: number, username: string, rol: RolEmpresa): Promise<UserCompany> {
  const res = await apiFetch(`${API_BASE}/companies/${companyId}/usuarios/`, {
      method: 'POST',
      body: JSON.stringify({ username, rol
    }),
  });
  return handle<UserCompany>(res);
}

export async function actualizarRolAcceso(companyId: number, userId: number, rol: RolEmpresa): Promise<UserCompany> {
  const res = await apiFetch(`${API_BASE}/companies/${companyId}/usuarios/${userId}`, {
      method: 'PUT',
      body: JSON.stringify({ rol
    }),
  });
  return handle<UserCompany>(res);
}

export async function removerAcceso(companyId: number, userId: number): Promise<void> {
  const res = await apiFetch(`${API_BASE}/companies/${companyId}/usuarios/${userId}`, { method: 'DELETE', });
  return handle<void>(res);
}

// ── Usuarios (solo admin) ─────────────────────────────────────────────────────

export async function listarUsuarios(): Promise<User[]> {
  const res = await apiFetch(`${API_BASE}/auth/users`);
  const data = await handle<{ usuarios: User[]; total: number; skip: number; limit: number }>(res);
  return data.usuarios;
}

export async function crearUsuario(data: {
  username: string;
  email: string;
  full_name: string;
  password: string;
  rol_global?: string;
  company_id?: number;
}): Promise<User> {
  const res = await apiFetch(`${API_BASE}/auth/users`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  return handle<User>(res);
}

export async function actualizarUsuario(userId: number, data: {
  email?: string;
  full_name?: string;
  rol_global?: string;
}): Promise<User> {
  const res = await apiFetch(`${API_BASE}/auth/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  return handle<User>(res);
}

export async function eliminarUsuario(userId: number): Promise<void> {
  const res = await apiFetch(`${API_BASE}/auth/users/${userId}`, { method: 'DELETE', });
  return handle<void>(res);
}

export async function cambiarPasswordOtro(userId: number, newPassword: string): Promise<void> {
  const res = await apiFetch(`${API_BASE}/auth/users/${userId}/password`, {
      method: 'PUT',
      body: JSON.stringify({ new_password: newPassword
    }),
  });
  return handle<void>(res);
}

// ── Rubros ────────────────────────────────────────────────────────────────────

export async function listarRubros(): Promise<Rubro[]> {
  const res = await apiFetch(`${API_BASE}/rubros`);
  return handle<Rubro[]>(res);
}

export async function sugerenciasPorRubro(rubroId: number): Promise<RATSugerido[]> {
  const res = await apiFetch(`${API_BASE}/rubros/${rubroId}/sugerencias`);
  return handle<RATSugerido[]>(res);
}

export async function crearSolicitudDerecho(data: {
  company_id: number;
  tipo: string;
  nombre_titular: string;
  email_titular: string;
  rut_titular?: string;
  descripcion?: string;
}): Promise<void> {
  const res = await apiFetch(`${API_BASE}/solicitudes-derecho/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handle<void>(res);
}

export async function listarSolicitudesDerecho(companyId: number, estado?: string): Promise<unknown[]> {
  const params = new URLSearchParams({ company_id: String(companyId) });
  if (estado) params.set('estado', estado);
  const res = await apiFetch(`${API_BASE}/solicitudes-derecho/?${params}`);
  const data = await handle<{ solicitudes: unknown[]; total: number; skip: number; limit: number }>(res);
  return data.solicitudes;
}

export async function actualizarSolicitudDerecho(
  id: number,
  data: { estado: string; respuesta: string; descripcion_accion?: string; usuario_nombre?: string }
): Promise<void> {
  const res = await apiFetch(`${API_BASE}/solicitudes-derecho/${id}/responder`, {
    method: 'PATCH',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handle<void>(res);
}

export async function actualizarRubro(rubroId: number, data: { nombre?: string; orden?: number }): Promise<void> {
  const res = await apiFetch(`${API_BASE}/rubros/${rubroId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  return handle<void>(res);
}

export interface DbHealth {
  engine: string;
  url: string;
  status: string;
  latency_ms?: number;
  error?: string;
}

export async function getDbHealth(): Promise<DbHealth> {
  const res = await apiFetch(`${API_BASE}/health/db`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  if (!res.ok) throw new Error('Error al obtener estado de BD');
  return res.json();
}

export interface TktTicket {
  id: number;
  company_id: number;
  tipo: string;
  estado: string;
  prioridad: string;
  origen: string;
  titular_nombre: string;
  titular_email: string;
  titular_rut?: string;
  descripcion?: string;
  fecha_recepcion?: string;
  fecha_vencimiento?: string;
  responsable_id?: number;
  respuesta_texto?: string;
  respuesta_fecha?: string;
  created_by?: string;
  created_at?: string;
  dias_restantes?: number;
  sla_color?: string;
  estado_sla?: string;
}

export interface TktDashboard {
  total: number;
  abiertos: number;
  en_proceso: number;
  pendientes: number;
  resueltos: number;
  vencidos: number;
  cumplimiento_sla: number;
  tiempo_promedio_horas: number;
}

export interface TktListResponse {
  tickets: TktTicket[];
  total: number;
  skip: number;
  limit: number;
  stats?: TktDashboard;
}

export async function listarTktTickets(companyId: number, estado?: string, prioridad?: string): Promise<TktListResponse> {
  const params = new URLSearchParams({ company_id: String(companyId) });
  if (estado) params.set('estado', estado);
  if (prioridad) params.set('prioridad', prioridad);
  const res = await apiFetch(`${API_BASE}/tkt-solicitud-derecho/?${params}`);
  const data = await handle<TktListResponse>(res);
  return data;
}

export async function getTktDashboard(companyId?: number): Promise<TktDashboard> {
  const params = new URLSearchParams();
  if (companyId) params.set('company_id', String(companyId));
  const res = await apiFetch(`${API_BASE}/tkt-solicitud-derecho/dashboard?${params}`);
  return handle<TktDashboard>(res);
}

export async function crearTktTicket(data: {
  company_id: number;
  tipo: string;
  prioridad?: string;
  origen?: string;
  titular_nombre: string;
  titular_email: string;
  titular_rut?: string;
  descripcion?: string;
}): Promise<TktTicket> {
  const res = await apiFetch(`${API_BASE}/tkt-solicitud-derecho/`, {
    method: 'POST',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handle<TktTicket>(res);
}

export async function getTktTicket(id: number): Promise<TktTicket> {
  const res = await apiFetch(`${API_BASE}/tkt-solicitud-derecho/${id}`);
  return handle<TktTicket>(res);
}

export async function actualizarTktTicket(id: number, data: { estado?: string; prioridad?: string; responsable_id?: number; respuesta_texto?: string }): Promise<TktTicket> {
  const res = await apiFetch(`${API_BASE}/tkt-solicitud-derecho/${id}`, {
    method: 'PATCH',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handle<TktTicket>(res);
}

export async function agregarTktNota(ticketId: number, nota: string): Promise<void> {
  const res = await apiFetch(`${API_BASE}/tkt-solicitud-derecho/${ticketId}/notas`, {
    method: 'POST',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify({ nota }),
  });
  return handle<void>(res);
}

export async function listarTktNotas(ticketId: number): Promise<{ id: number; nota: string; user_id: number; created_at: string }[]> {
  const res = await apiFetch(`${API_BASE}/tkt-solicitud-derecho/${ticketId}/notas`);
  return handle<{ id: number; nota: string; user_id: number; created_at: string }[]>(res);
}

export async function listarTktHistorial(ticketId: number): Promise<{ id: number; estado_anterior?: string; estado_nuevo: string; descripcion?: string; user_id: number; created_at: string }[]> {
  const res = await apiFetch(`${API_BASE}/tkt-solicitud-derecho/${ticketId}/historial`);
  return handle<{ id: number; estado_anterior?: string; estado_nuevo: string; descripcion?: string; user_id: number; created_at: string }[]>(res);
}

// ── B-01: Bloqueo temporal ─────────────────────────────────────────────────────

export async function bloquearSolicitud(solicitudId: number, ratId: number, plazoDias: number): Promise<void> {
  const res = await apiFetch(`${API_BASE}/solicitudes-derecho/${solicitudId}/bloquear`, {
    method: 'POST',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify({ rat_id: ratId, plazo_dias: plazoDias }),
  });
  return handle<void>(res);
}

export async function desbloquearSolicitud(solicitudId: number): Promise<void> {
  const res = await apiFetch(`${API_BASE}/solicitudes-derecho/${solicitudId}/desbloquear`, {
    method: 'POST',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
  });
  return handle<void>(res);
}

// ── B-04: Portabilidad ─────────────────────────────────────────────────────────

export async function exportarPortabilidad(solicitudId: number): Promise<Blob> {
  const res = await apiFetch(`${API_BASE}/solicitudes-derecho/${solicitudId}/portabilidad/export`);
  if (!res.ok) throw new Error('Error al exportar portabilidad');
  return res.blob();
}

// ── B-05: Evaluacion de riesgo de brecha ───────────────────────────────────────

export async function evaluarRiesgoBrecha(
  breachId: number,
  data: {
    volumen_titulares_afectados: number;
    incluye_datos_sensibles: boolean;
    incluye_datos_nna: boolean;
    incluye_datos_financieros: boolean;
  }
): Promise<SecurityBreach> {
  const res = await apiFetch(`${API_BASE}/brechas/${breachId}/evaluar-riesgo`, {
    method: 'POST',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handle<SecurityBreach>(res);
}

// ── B-06: Consentimientos ──────────────────────────────────────────────────────

export interface ConsentimientoCreate {
  rat_id: number;
  nombre_titular: string;
  email_titular: string;
  canal: string;
  texto_consentimiento: string;
  datos_sensibles: boolean;
}

export async function registrarConsentimiento(data: ConsentimientoCreate): Promise<void> {
  const res = await apiFetch(`${API_BASE}/rats/${data.rat_id}/consentimientos`, {
    method: 'POST',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handle<void>(res);
}

// ── B-03: Contratos de Encargado ────────────────────────────────────────────────

export interface EncargadoContrato {
  id: number;
  company_id: number;
  rat_id?: number;
  nombre_encargado: string;
  objeto: string;
  duracion_inicio: string;
  duracion_fin?: string;
  finalidad: string;
  tipo_datos: string;
  categorias_titulares: string;
  derechos_obligaciones: string;
  activo: boolean;
  fecha_alerta_vencimiento?: string;
  created_at?: string;
}

export async function listarEncargadosContrato(companyId: number): Promise<EncargadoContrato[]> {
  const res = await apiFetch(`${API_BASE}/encargados-contrato/?company_id=${companyId}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Error al listar contratos');
  }
  const data = await res.json();
  return Array.isArray(data) ? data : (data.contratos || []);
}

export async function crearEncargadoContrato(data: Omit<EncargadoContrato, 'id' | 'created_at'>): Promise<EncargadoContrato> {
  const res = await apiFetch(`${API_BASE}/encargados-contrato/`, {
    method: 'POST',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handle<EncargadoContrato>(res);
}

export async function actualizarEncargadoContrato(id: number, data: Partial<EncargadoContrato>): Promise<EncargadoContrato> {
  const res = await apiFetch(`${API_BASE}/encargados-contrato/${id}`, {
    method: 'PUT',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handle<EncargadoContrato>(res);
}

export async function eliminarEncargadoContrato(id: number): Promise<void> {
  const res = await apiFetch(`${API_BASE}/encargados-contrato/${id}`, { method: 'DELETE', });
  return handle<void>(res);
}

// ── B-02: Politica de Transparencia ────────────────────────────────────────────

export interface PoliticaTransparencia {
  company_id: number;
  nombre_empresa: string;
  rut_empresa: string;
  rubro?: string;
  contacto_dpo: string;
  email_dpo: string;
  domicilio?: string;
  version: string;
  fecha_generacion: string;
  hash_sha256: string;
  item_a_politica: string;
  item_b_responsable: string;
  item_c_domicilio: string;
  item_d_categorias: string;
  item_e_medidas: string;
  item_f_derechos_arco: string;
  item_g_recurir_apdc: string;
  item_h_transferencias: string;
  item_i_conservacion: string;
  item_j_fuente: string;
  item_k_retirar_consentimiento: string;
  item_l_decisiones_automatizadas: string;
}

export async function getPoliticaTransparencia(companyId: number): Promise<PoliticaTransparencia> {
  const res = await apiFetch(`${API_BASE}/publico/transparencia/${companyId}`);
  return handle<PoliticaTransparencia>(res);
}

// ── Consentimientos ─────────────────────────────────────────────────────────────

export interface ConsentimientoItem {
  id: number;
  company_id: number;
  rat_id: number | null;
  nombre_titular: string;
  email_titular: string | null;
  canal: string;
  texto_consentimiento: string;
  fecha_obtencion: string;
  fecha_revocacion: string | null;
  activo: boolean;
  ip_origen: string | null;
  created_at: string;
}

export interface ConsentimientoListResponse {
  consentimientos: ConsentimientoItem[];
  total: number;
  skip: number;
  limit: number;
}

export async function listarConsentimientos(companyId: number, ratId?: number, soloActivos?: boolean): Promise<ConsentimientoItem[]> {
  const params = new URLSearchParams({ company_id: String(companyId) });
  if (ratId) params.set('rat_id', String(ratId));
  if (soloActivos) params.set('solo_activos', 'true');
  const res = await apiFetch(`${API_BASE}/consentimientos/?${params}`);
  const data = await handle<ConsentimientoListResponse>(res);
  return data.consentimientos || [];
}

export async function crearConsentimiento(data: {
  rat_id: number;
  nombre_titular: string;
  email_titular?: string;
  canal: string;
  texto_consentimiento: string;
  fecha_obtencion: string;
}): Promise<ConsentimientoItem> {
  const res = await apiFetch(`${API_BASE}/consentimientos/`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return handle<ConsentimientoItem>(res);
}

export async function revocarConsentimiento(id: number): Promise<ConsentimientoItem> {
  const res = await apiFetch(`${API_BASE}/consentimientos/${id}/revocar`, { method: 'POST' });
  return handle<ConsentimientoItem>(res);
}

// ── EIPD ────────────────────────────────────────────────────────────────────────

export interface EIPDItem {
  id: number;
  rat_id: number;
  metodologia: string | null;
  objetivos: string | null;
  necesidad_proporcionalidad: string | null;
  riesgos_identificados: string | null;
  medidas_propuestas: string | null;
  parecer_dpo: string | null;
  fecha_elaboracion: string | null;
  fecha_aprobacion: string | null;
  resultado: 'completada' | 'no_requerida' | 'en_proceso';
  created_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface EIPDListResponse {
  eipds: EIPDItem[];
  total: number;
  skip: number;
  limit: number;
}

export async function listarEipds(companyId: number): Promise<EIPDItem[]> {
  const res = await apiFetch(`${API_BASE}/eipd/?company_id=${companyId}`);
  const data = await handle<EIPDListResponse>(res);
  return data.eipds || [];
}

export async function crearEipd(data: {
  rat_id: number;
  metodologia?: string;
  objetivos?: string;
  necesidad_proporcionalidad?: string;
  riesgos_identificados?: string;
  medidas_propuestas?: string;
  parecer_dpo?: string;
  fecha_elaboracion?: string;
  fecha_aprobacion?: string;
  resultado: string;
}): Promise<EIPDItem> {
  const res = await apiFetch(`${API_BASE}/eipd/`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return handle<EIPDItem>(res);
}

export async function actualizarEipd(id: number, data: Partial<EIPDItem>): Promise<EIPDItem> {
  const res = await apiFetch(`${API_BASE}/eipd/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
  return handle<EIPDItem>(res);
}
