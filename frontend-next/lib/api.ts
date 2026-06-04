import type { AuthResponse, Company, RAT, DashboardStats, AuditLog, User, UserCompany, RolEmpresa, SecurityBreach, Rubro, RATSugerido } from '@/types';
import { API_BASE } from './constants';

console.log('[DEBUG] API_BASE =', API_BASE);

function getToken(): string {
  if (typeof window === 'undefined') return '';
  return localStorage.getItem('custodio_token') || '';
}

function authHeaders(): HeadersInit {
  return {
    Authorization: `Bearer ${getToken()}`,
    'Content-Type': 'application/json',
  };
}

async function handle<T>(res: Response): Promise<T> {
  if (res.status === 204) return {} as T;
  if (res.status === 401) {
    localStorage.removeItem('custodio_token');
    localStorage.removeItem('custodio_user');
    localStorage.removeItem('custodio_company');
    window.location.replace('/login');
    return {} as T;
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
  const res = await fetch(`${API_BASE}/companies/`, { headers: authHeaders() });
  const data = await handle<{ empresas: Company[]; total: number; skip: number; limit: number }>(res);
  return data.empresas;
}

export async function crearEmpresa(data: Partial<Company>): Promise<Company> {
  const res = await fetch(`${API_BASE}/companies/`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(data),
  });
  return handle<Company>(res);
}

export async function actualizarEmpresa(id: number, data: Partial<Company>): Promise<Company> {
  const res = await fetch(`${API_BASE}/companies/${id}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify(data),
  });
  return handle<Company>(res);
}

export async function eliminarEmpresa(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/companies/${id}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  return handle<void>(res);
}

// ── RAT ───────────────────────────────────────────────────────────────────────

export async function listarRats(companyId?: number): Promise<RAT[]> {
  const url = companyId
    ? `${API_BASE}/rats/?company_id=${companyId}`
    : `${API_BASE}/rats/`;
  const res = await fetch(url, { headers: authHeaders() });
  return handle<RAT[]>(res);
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

  const res = await fetch(`${API_BASE}/rats/reportes?${searchParams.toString()}`, { headers: authHeaders() });
  return handle<ReportesResponse>(res);
}

export async function askAI(question: string, context?: string): Promise<{ answer: string }> {
  const res = await fetch(`${API_BASE}/ai/ask`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ question, context }),
  });
  return handle<{ answer: string }>(res);
}

export async function obtenerRat(id: number): Promise<RAT> {
  const res = await fetch(`${API_BASE}/rats/${id}`, { headers: authHeaders() });
  return handle<RAT>(res);
}

export async function crearRat(data: Partial<RAT>): Promise<RAT> {
  const res = await fetch(`${API_BASE}/rats/`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(data),
  });
  return handle<RAT>(res);
}

export async function actualizarRat(id: number, data: Partial<RAT>): Promise<RAT> {
  const res = await fetch(`${API_BASE}/rats/${id}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify(data),
  });
  return handle<RAT>(res);
}

export async function eliminarRat(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/rats/${id}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  return handle<void>(res);
}

export async function getDashboardStats(companyId: number): Promise<DashboardStats> {
  const res = await fetch(`${API_BASE}/rats/dashboard/${companyId}`, {
    headers: authHeaders(),
  });
  return handle<DashboardStats>(res);
}

export async function sugerirRat(tipoProceso: string): Promise<Record<string, unknown>> {
  const res = await fetch(`${API_BASE}/rats/sugerencias`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ tipo_proceso: tipoProceso }),
  });
  return handle<Record<string, unknown>>(res);
}

export async function listarTiposProceso(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/rats/sugerencias/tipos`, {
    headers: authHeaders(),
  });
  const data = await handle<{ tipos: string[] }>(res);
  return data.tipos || [];
}

export async function getAuditoria(ratId: number): Promise<AuditLog[]> {
  const res = await fetch(`${API_BASE}/rats/${ratId}/auditoria`, {
    headers: authHeaders(),
  });
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
  const res = await fetch(`${API_BASE}/rats/auditoria/${companyId}`, {
    headers: authHeaders(),
  });
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
  const res = await fetch(`${API_BASE}/rats/export/csv?company_id=${companyId}`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('Error al exportar CSV');
  return res.blob();
}

export async function exportarPdf(companyId: number): Promise<Blob> {
  const res = await fetch(`${API_BASE}/rats/export/pdf?company_id=${companyId}`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('Error al exportar PDF');
  return res.blob();
}

export async function exportarRatPdf(ratId: number): Promise<Blob> {
  const res = await fetch(`${API_BASE}/rats/${ratId}/export/pdf`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('Error al exportar PDF');
  return res.blob();
}

export async function exportarCni(companyId: number): Promise<Blob> {
  const res = await fetch(`${API_BASE}/rats/export/cni?company_id=${companyId}`, {
    headers: authHeaders(),
  });
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
  const res = await fetch(`${API_BASE}/rats/${ratId}/revision`, {
    method: 'POST',
    headers: authHeaders(),
  });
  return handle<AuditLog>(res);
}

export async function aprobarRat(ratId: number): Promise<RAT> {
  const res = await fetch(`${API_BASE}/rats/${ratId}/aprobar`, {
    method: 'POST',
    headers: authHeaders(),
  });
  return handle<RAT>(res);
}

// ── Brechas de seguridad ──────────────────────────────────────────────────────

export async function listarBrechas(companyId: number): Promise<SecurityBreach[]> {
  const res = await fetch(`${API_BASE}/brechas/?company_id=${companyId}`, { headers: authHeaders() });
  const data = await handle<{ brechas: SecurityBreach[]; total: number; skip: number; limit: number }>(res);
  return data.brechas;
}

export async function crearBrecha(data: Partial<SecurityBreach>): Promise<SecurityBreach> {
  const res = await fetch(`${API_BASE}/brechas/`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(data),
  });
  return handle<SecurityBreach>(res);
}

export async function actualizarBrecha(id: number, data: Partial<SecurityBreach>): Promise<SecurityBreach> {
  const res = await fetch(`${API_BASE}/brechas/${id}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify(data),
  });
  return handle<SecurityBreach>(res);
}

export async function eliminarBrecha(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/brechas/${id}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  return handle<void>(res);
}

export async function cambiarPassword(currentPassword: string, newPassword: string): Promise<void> {
  const res = await fetch(`${API_BASE}/auth/me/password`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
  });
  return handle<void>(res);
}

// ── Accesos por empresa ───────────────────────────────────────────────────────

export async function listarAccesos(companyId: number): Promise<UserCompany[]> {
  const res = await fetch(`${API_BASE}/companies/${companyId}/usuarios/`, {
    headers: authHeaders(),
  });
  return handle<UserCompany[]>(res);
}

export async function agregarAcceso(companyId: number, username: string, rol: RolEmpresa): Promise<UserCompany> {
  const res = await fetch(`${API_BASE}/companies/${companyId}/usuarios/`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ username, rol }),
  });
  return handle<UserCompany>(res);
}

export async function actualizarRolAcceso(companyId: number, userId: number, rol: RolEmpresa): Promise<UserCompany> {
  const res = await fetch(`${API_BASE}/companies/${companyId}/usuarios/${userId}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify({ rol }),
  });
  return handle<UserCompany>(res);
}

export async function removerAcceso(companyId: number, userId: number): Promise<void> {
  const res = await fetch(`${API_BASE}/companies/${companyId}/usuarios/${userId}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  return handle<void>(res);
}

// ── Usuarios (solo admin) ─────────────────────────────────────────────────────

export async function listarUsuarios(): Promise<User[]> {
  const res = await fetch(`${API_BASE}/auth/users`, { headers: authHeaders() });
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
  const res = await fetch(`${API_BASE}/auth/users`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(data),
  });
  return handle<User>(res);
}

export async function actualizarUsuario(userId: number, data: {
  email?: string;
  full_name?: string;
  rol_global?: string;
}): Promise<User> {
  const res = await fetch(`${API_BASE}/auth/users/${userId}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify(data),
  });
  return handle<User>(res);
}

export async function eliminarUsuario(userId: number): Promise<void> {
  const res = await fetch(`${API_BASE}/auth/users/${userId}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  return handle<void>(res);
}

export async function cambiarPasswordOtro(userId: number, newPassword: string): Promise<void> {
  const res = await fetch(`${API_BASE}/auth/users/${userId}/password`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify({ new_password: newPassword }),
  });
  return handle<void>(res);
}

// ── Rubros ────────────────────────────────────────────────────────────────────

export async function listarRubros(): Promise<Rubro[]> {
  const res = await fetch(`${API_BASE}/rubros`, { headers: authHeaders() });
  return handle<Rubro[]>(res);
}

export async function sugerenciasPorRubro(rubroId: number): Promise<RATSugerido[]> {
  const res = await fetch(`${API_BASE}/rubros/${rubroId}/sugerencias`, { headers: authHeaders() });
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
  const res = await fetch(`${API_BASE}/solicitudes-derecho/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handle<void>(res);
}

export async function listarSolicitudesDerecho(companyId: number, estado?: string): Promise<unknown[]> {
  const params = new URLSearchParams({ company_id: String(companyId) });
  if (estado) params.set('estado', estado);
  const res = await fetch(`${API_BASE}/solicitudes-derecho/?${params}`, { headers: authHeaders() });
  const data = await handle<{ solicitudes: unknown[]; total: number; skip: number; limit: number }>(res);
  return data.solicitudes;
}

export async function actualizarSolicitudDerecho(
  id: number,
  data: { estado: string; respuesta: string; descripcion_accion?: string; usuario_nombre?: string }
): Promise<void> {
  const res = await fetch(`${API_BASE}/solicitudes-derecho/${id}/responder`, {
    method: 'PATCH',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handle<void>(res);
}

export async function actualizarRubro(rubroId: number, data: { nombre?: string; orden?: number }): Promise<void> {
  const res = await fetch(`${API_BASE}/rubros/${rubroId}`, {
    method: 'PUT',
    headers: authHeaders(),
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
  const res = await fetch(`${API_BASE}/health/db`, {
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
  const res = await fetch(`${API_BASE}/tkt-solicitud-derecho/?${params}`, { headers: authHeaders() });
  const data = await handle<TktListResponse>(res);
  return data;
}

export async function getTktDashboard(companyId?: number): Promise<TktDashboard> {
  const params = new URLSearchParams();
  if (companyId) params.set('company_id', String(companyId));
  const res = await fetch(`${API_BASE}/tkt-solicitud-derecho/dashboard?${params}`, { headers: authHeaders() });
  return handle<TktDashboard>(res);
}

export async function getTktTicket(id: number): Promise<TktTicket> {
  const res = await fetch(`${API_BASE}/tkt-solicitud-derecho/${id}`, { headers: authHeaders() });
  return handle<TktTicket>(res);
}

export async function actualizarTktTicket(id: number, data: { estado?: string; prioridad?: string; responsable_id?: number; respuesta_texto?: string }): Promise<TktTicket> {
  const res = await fetch(`${API_BASE}/tkt-solicitud-derecho/${id}`, {
    method: 'PATCH',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handle<TktTicket>(res);
}

export async function agregarTktNota(ticketId: number, nota: string): Promise<void> {
  const res = await fetch(`${API_BASE}/tkt-solicitud-derecho/${ticketId}/notas`, {
    method: 'POST',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify({ nota }),
  });
  return handle<void>(res);
}

export async function listarTktNotas(ticketId: number): Promise<{ id: number; nota: string; user_id: number; created_at: string }[]> {
  const res = await fetch(`${API_BASE}/tkt-solicitud-derecho/${ticketId}/notas`, { headers: authHeaders() });
  return handle<{ id: number; nota: string; user_id: number; created_at: string }[]>(res);
}

export async function listarTktHistorial(ticketId: number): Promise<{ id: number; estado_anterior?: string; estado_nuevo: string; descripcion?: string; user_id: number; created_at: string }[]> {
  const res = await fetch(`${API_BASE}/tkt-solicitud-derecho/${ticketId}/historial`, { headers: authHeaders() });
  return handle<{ id: number; estado_anterior?: string; estado_nuevo: string; descripcion?: string; user_id: number; created_at: string }[]>(res);
}
