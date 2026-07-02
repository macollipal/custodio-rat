import { describe, it, expect } from 'vitest';
import { computeCompanyAlerts } from '@/components/companies/CompanyAlertsBanner';
import type { Company } from '@/types';

const baseCompany: Company = {
  id: 1,
  nombre: 'Test SpA',
  rut: '76.000.001-1',
  contacto_dpo: 'Juan Test',
  email_dpo: 'dpo@test.cl',
};

describe('CompanyAlertsBanner — computeCompanyAlerts', () => {
  it('retorna [] cuando no hay empresas', () => {
    expect(computeCompanyAlerts([])).toEqual([]);
  });

  it('retorna [] cuando todas las empresas estan sanas', () => {
    const companies: Company[] = [
      { ...baseCompany, id: 1, total_rats: 5, completitud_promedio: 80, rats_vencidos: 0, solicitudes_vencidas_sla: 0 },
      { ...baseCompany, id: 2, total_rats: 3, completitud_promedio: 90, rats_vencidos: 0, solicitudes_vencidas_sla: 0 },
    ];
    expect(computeCompanyAlerts(companies)).toEqual([]);
  });

  it('detecta RATs vencidos', () => {
    const companies: Company[] = [
      { ...baseCompany, id: 1, rats_vencidos: 3 },
      { ...baseCompany, id: 2, rats_vencidos: 2 },
    ];
    const alerts = computeCompanyAlerts(companies);
    expect(alerts.length).toBe(1);
    expect(alerts[0].titulo).toContain('5 RATs vencidos');
    expect(alerts[0].icon).toBe('⚠️');
  });

  it('singular cuando hay 1 RAT vencido', () => {
    const companies: Company[] = [{ ...baseCompany, rats_vencidos: 1 }];
    const alerts = computeCompanyAlerts(companies);
    expect(alerts[0].titulo).toContain('1 RAT vencido');
    expect(alerts[0].titulo).not.toContain('1 RATs');
  });

  it('detecta solicitudes ARCO vencidas', () => {
    const companies: Company[] = [{ ...baseCompany, solicitudes_vencidas_sla: 2 }];
    const alerts = computeCompanyAlerts(companies);
    expect(alerts.length).toBe(1);
    expect(alerts[0].titulo).toContain('2 solicitudes ARCO vencidas');
    expect(alerts[0].icon).toBe('📋');
  });

  it('detecta empresas con completitud < 50%', () => {
    const companies: Company[] = [
      { ...baseCompany, id: 1, total_rats: 5, completitud_promedio: 30 },
      { ...baseCompany, id: 2, total_rats: 10, completitud_promedio: 80 },
      { ...baseCompany, id: 3, total_rats: 4, completitud_promedio: 49 },
    ];
    const alerts = computeCompanyAlerts(companies);
    const completitudAlert = alerts.find((a) => a.icon === '📉');
    expect(completitudAlert).toBeDefined();
    expect(completitudAlert!.titulo).toContain('2 empresas con completitud < 50%');
  });

  it('ignora empresas con 0 RATs aunque completitud sea 0', () => {
    const companies: Company[] = [
      { ...baseCompany, id: 1, total_rats: 0, completitud_promedio: 0 },
    ];
    const alerts = computeCompanyAlerts(companies);
    const completitudAlert = alerts.find((a) => a.icon === '📉');
    expect(completitudAlert).toBeUndefined();
  });

  it('detecta empresas sin DPO', () => {
    const companies: Company[] = [
      { ...baseCompany, id: 1, contacto_dpo: 'Juan', email_dpo: 'j@t.cl' },
      { ...baseCompany, id: 2, contacto_dpo: undefined, email_dpo: 'b@t.cl' },
      { ...baseCompany, id: 3, contacto_dpo: 'Ana', email_dpo: undefined },
    ];
    const alerts = computeCompanyAlerts(companies);
    const dpoAlert = alerts.find((a) => a.icon === '👤');
    expect(dpoAlert).toBeDefined();
    expect(dpoAlert!.titulo).toContain('2 empresas sin DPO definido');
  });

  it('plural correcto segun conteo', () => {
    const c1: Company[] = [{ ...baseCompany, id: 1, rats_vencidos: 1 }];
    expect(computeCompanyAlerts(c1)[0].titulo).toContain('1 RAT vencido');

    const c5: Company[] = [{ ...baseCompany, id: 1, rats_vencidos: 5 }];
    expect(computeCompanyAlerts(c5)[0].titulo).toContain('5 RATs vencidos');
  });

  it('retorna multiples alertas simultaneamente', () => {
    const companies: Company[] = [
      {
        ...baseCompany,
        rats_vencidos: 2,
        solicitudes_vencidas_sla: 1,
        total_rats: 5,
        completitud_promedio: 30,
      },
    ];
    const alerts = computeCompanyAlerts(companies);
    expect(alerts.length).toBe(3);
    const icons = alerts.map((a) => a.icon);
    expect(icons).toContain('⚠️');
    expect(icons).toContain('📋');
    expect(icons).toContain('📉');
  });
});