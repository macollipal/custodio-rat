export type RolGlobal = 'superadmin' | 'admin_empresa' | 'usuario';

export interface User {
  id: number;
  username: string;
  full_name: string;
  email: string;
  rol_global: RolGlobal;
  empresa_nombre?: string;
  empresa_id?: number;
}

export interface Company {
  id: number;
  nombre: string;
  rut: string;
  rubro?: string;
  rubro_id?: number;
  direccion?: string;
  contacto_dpo?: string;
  email_dpo?: string;
  descripcion?: string;
  canal_ejercicio_derechos?: string;
  total_rats?: number;
  mi_rol?: RolEmpresa | null;
}

export interface Rubro {
  id: number;
  nombre: string;
  orden: number;
  total_sugerencias?: number;
}

export interface RATSugerido {
  id: number;
  rubro_id: number;
  nombre_proceso: string;
  categoria_datos: string;
  categoria_titulares?: string;
  finalidad?: string;
  base_legal?: string;
  plazo_retencion?: string;
  datos_sensibles: boolean;
  evaluacion_impacto: boolean;
  decisiones_automatizadas: boolean;
}

export interface RAT {
  id: number;
  company_id: number;
  nombre_proceso: string;
  categoria_datos?: string;
  categoria_titulares?: string;
  finalidad?: string;
  base_legal?: string;
  fuente_datos?: string;
  plazo_retencion?: string;
  transferencia_datos?: string;
  medidas_seguridad?: string;
  destinatarios?: string;
  nombre_encargado?: string;
  tiene_contrato_encargado?: boolean;
  transferencia_internacional: boolean;
  pais_destino?: string;
  garantias_transferencia_int?: string;
  datos_sensibles: boolean;
  tipo_dato_sensible?: string;
  evaluacion_impacto: boolean;
  estado_eipd?: string;
  fecha_eipd?: string;
  decisiones_automatizadas: boolean;
  test_interes_legitimo?: string;
  estado: 'borrador' | 'completo' | 'en_revision' | 'aprobado';
  completitud: number;
  nivel_riesgo?: string;
  updated_at: string;
  created_at: string;
  created_by?: string;
  updated_by?: string;
  observaciones_auditoria?: string;
  aprobado_por?: string;
  fecha_aprobacion?: string;
  archivo_base_legal_nombre?: string;
  archivo_base_legal_tipo?: string;
  tiene_archivo_base_legal?: boolean;
}

export type EstadoEIPD = 'no_requerida' | 'pendiente' | 'en_proceso' | 'completada';

export interface SecurityBreach {
  id: number;
  company_id: number;
  descripcion: string;
  fecha_deteccion: string;
  rats_afectados?: string;
  datos_comprometidos?: string;
  medidas_adoptadas?: string;
  notificado_apdc: boolean;
  fecha_notificacion_apdc?: string;
  notificado_titulares: boolean;
  fecha_notificacion_titulares?: string;
  creado_por?: string;
  created_at: string;
  updated_at: string;
  horas_desde_deteccion?: number;
  plazo_apdc_vencido?: boolean;
}

export interface DashboardStats {
  total_procesos: number;
  completitud_promedio: number;
  procesos_con_datos_sensibles: number;
  requieren_eipd: number;
  transferencias_internacionales: number;
  por_estado: Record<string, number>;
  eipd_pendientes?: number;
  transferencias_sin_garantias?: number;
  interes_legitimo_sin_test?: number;
  encargados_sin_contrato?: number;
  rats_por_vencer?: number;
  rats_vencidos?: number;
}

export interface AuditLog {
  id: number;
  rat_id: number;
  accion: string;
  usuario: string;
  timestamp: string;
  detalle?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export type RolEmpresa = 'admin' | 'editor' | 'viewer';

export interface UserCompany {
  id: number;
  user_id: number;
  company_id: number;
  rol: RolEmpresa;
  created_at: string;
  username: string;
  full_name: string;
  email: string;
}

export interface ReportesResponse {
  total: number;
  skip: number;
  limit: number;
  sort_by: string;
  sort_order: string;
  filtros_aplicados: Record<string, unknown>;
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

export interface SavedFilter {
  id: string;
  name: string;
  filters: Partial<ReportesParams>;
  created_at: string;
}

export interface RATWizardData {
  nombre_proceso?: string;
  fuente_datos?: string;
  destinatarios?: string;
  nombre_encargado?: string;
  tiene_contrato_encargado?: boolean;
  categoria_datos?: string;
  categoria_titulares?: string;
  datos_sensibles?: boolean;
  tipo_dato_sensible?: string;
  evaluacion_impacto?: boolean;
  estado_eipd?: string;
  fecha_eipd?: string;
  decisiones_automatizadas?: boolean;
  finalidad?: string;
  base_legal?: string;
  test_interes_legitimo?: string;
  plazo_retencion?: string;
  medidas_seguridad?: string;
  transferencia_datos?: string;
  transferencia_internacional?: boolean;
  pais_destino?: string;
  garantias_transferencia_int?: string;
  _sug_observacion?: string;
  _testIL?: { paso1?: string; paso2?: string; paso3?: string };
  archivo_base_legal_base64?: string;
  archivo_base_legal_nombre?: string;
  archivo_base_legal_tipo?: string;
}
