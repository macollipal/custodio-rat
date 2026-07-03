// Tests unitarios del Design System
import { describe, it, expect } from 'vitest';
import {
  inputCls,
  inputStyle,
  selectCls,
  textareaCls,
  labelCls,
  labelStyle,
  btnPrimaryCls,
  btnPrimaryStyle,
  btnSecondaryCls,
  btnSecondaryStyle,
  btnDangerCls,
  btnDangerStyle,
  btnSuccessCls,
  btnSuccessStyle,
  btnWarningCls,
  btnWarningStyle,
  panelStyles,
  panelTitleStyles,
  panelWrapperCls,
  modalHeaderStyle,
  modalHeaderCls,
  modalContentCls,
  formFooterCls,
  gridResponsive1to2,
  gridResponsive1to3,
  badgeBaseCls,
  alertInfoStyle,
  alertWarningStyle,
  alertErrorStyle,
  alertSuccessStyle,
  tableHeaderStyle,
  tableBorderStyle,
  cardCls,
  cardBorderStyle,
  kpiCardCls,
  drawerCls,
  cx,
} from '../lib/styles';

describe('Design System - lib/styles.ts', () => {
  describe('Inputs', () => {
    it('inputCls tiene padding y focus ring correctos', () => {
      expect(inputCls).toContain('px-3.5');
      expect(inputCls).toContain('py-2.5');
      expect(inputCls).toContain('rounded-lg');
      expect(inputCls).toContain('focus:ring-2');
      expect(inputCls).toContain('focus:ring-blue-500');
      expect(inputCls).toContain('focus:border-transparent');
      expect(inputCls).toContain('transition');
    });

    it('inputStyle tiene border gris claro y fondo blanco', () => {
      expect(inputStyle.borderColor).toBe('#D1D5DB');
      expect(inputStyle.backgroundColor).toBe('#FFFFFF');
    });

    it('selectCls incluye appearance-none para control del icono', () => {
      expect(selectCls).toContain('appearance-none');
      expect(selectCls).toContain('bg-white');
    });

    it('textareaCls == inputCls', () => {
      expect(textareaCls).toBe(inputCls);
    });
  });

  describe('Labels', () => {
    it('labelCls tiene font-medium y mb-1.5', () => {
      expect(labelCls).toContain('text-sm');
      expect(labelCls).toContain('font-medium');
      expect(labelCls).toContain('mb-1.5');
      expect(labelCls).toContain('block');
    });

    it('labelStyle usa color gris 374151', () => {
      expect(labelStyle.color).toBe('#374151');
    });
  });

  describe('Botones', () => {
    it('btnPrimary: padding, font-semibold, transition, disabled', () => {
      expect(btnPrimaryCls).toContain('px-5');
      expect(btnPrimaryCls).toContain('py-2.5');
      expect(btnPrimaryCls).toContain('font-semibold');
      expect(btnPrimaryCls).toContain('transition');
      expect(btnPrimaryCls).toContain('disabled:opacity-50');
    });

    it('btnPrimaryStyle usa azul 2563EB', () => {
      expect(btnPrimaryStyle.background).toBe('#2563EB');
    });

    it('btnSecondary: border + hover gris', () => {
      expect(btnSecondaryCls).toContain('border');
      expect(btnSecondaryCls).toContain('hover:bg-gray-50');
    });

    it('btnSecondaryStyle: color gris y border gris claro', () => {
      expect(btnSecondaryStyle.color).toBe('#6B7280');
      expect(btnSecondaryStyle.borderColor).toBe('#E5E7EB');
    });

    it('btnDanger, btnSuccess, btnWarning tienen backgrounds distintivos', () => {
      expect(btnDangerStyle.background).toBe('#DC2626');
      expect(btnSuccessStyle.background).toBe('#059669');
      expect(btnWarningStyle.background).toBe('#D97706');
    });
  });

  describe('Paneles coloreados', () => {
    it('panelStyles tiene los 6 colores esperados', () => {
      expect(panelStyles).toHaveProperty('gray');
      expect(panelStyles).toHaveProperty('blue');
      expect(panelStyles).toHaveProperty('red');
      expect(panelStyles).toHaveProperty('green');
      expect(panelStyles).toHaveProperty('amber');
      expect(panelStyles).toHaveProperty('purple');
    });

    it('cada panel tiene background y border 1px solid', () => {
      Object.values(panelStyles).forEach(p => {
        expect(p.background).toBeDefined();
        expect(p.border).toMatch(/^1px solid #[A-F0-9]{6}$/i);
      });
    });

    it('panelTitleStyles tiene los mismos 6 colores que panelStyles', () => {
      expect(Object.keys(panelTitleStyles).sort()).toEqual(Object.keys(panelStyles).sort());
    });

    it('panelWrapperCls es rounded-xl p-5', () => {
      expect(panelWrapperCls).toContain('rounded-xl');
      expect(panelWrapperCls).toContain('p-5');
    });
  });

  describe('Modales/Drawer', () => {
    it('modalHeaderStyle usa gradiente azul institucional', () => {
      expect(modalHeaderStyle.background).toContain('linear-gradient');
      expect(modalHeaderStyle.background).toContain('#1E3A5F');
      expect(modalHeaderStyle.background).toContain('#2563EB');
    });

    it('modalHeaderCls es rounded-t-xl px-6 py-4', () => {
      expect(modalHeaderCls).toContain('rounded-t-xl');
      expect(modalHeaderCls).toContain('px-6');
      expect(modalHeaderCls).toContain('py-4');
    });

    it('modalContentCls y formFooterCls son responsive', () => {
      expect(modalContentCls).toContain('space-y-5');
      expect(formFooterCls).toContain('flex-col');
      expect(formFooterCls).toContain('sm:flex-row');
      expect(formFooterCls).toContain('justify-between');
    });

    it('drawerCls es 95vw mobile, 60vw desktop', () => {
      expect(drawerCls).toContain('w-[95vw]');
      expect(drawerCls).toContain('sm:w-[60vw]');
      expect(drawerCls).toContain('max-w-[640px]');
    });
  });

  describe('Grid responsive', () => {
    it('gridResponsive1to2: 1 col mobile, 2 cols sm+', () => {
      expect(gridResponsive1to2).toContain('grid-cols-1');
      expect(gridResponsive1to2).toContain('sm:grid-cols-2');
    });

    it('gridResponsive1to3: 1 col mobile, 2 cols sm, 3 cols lg', () => {
      expect(gridResponsive1to3).toContain('grid-cols-1');
      expect(gridResponsive1to3).toContain('sm:grid-cols-2');
      expect(gridResponsive1to3).toContain('lg:grid-cols-3');
    });
  });

  describe('Alertas', () => {
    it('hay 4 estilos de alerta (info, warning, error, success)', () => {
      expect(alertInfoStyle.background).toBe('#EFF6FF');
      expect(alertWarningStyle.background).toBe('#FEF3C7');
      expect(alertErrorStyle.background).toBe('#FEE2E2');
      expect(alertSuccessStyle.background).toBe('#D1FAE5');
    });

    it('cada alerta tiene border 1px solid', () => {
      [alertInfoStyle, alertWarningStyle, alertErrorStyle, alertSuccessStyle].forEach(a => {
        expect(a.border).toMatch(/^1px solid #[A-F0-9]{6}$/);
      });
    });
  });

  describe('Tablas y cards', () => {
    it('tableHeaderStyle y tableBorderStyle usan gris claro', () => {
      expect(tableHeaderStyle.background).toBe('#F9FAFB');
      expect(tableBorderStyle.borderColor).toBe('#E5E7EB');
    });

    it('cardCls y cardBorderStyle son para cards estandar', () => {
      expect(cardCls).toContain('rounded-xl');
      expect(cardBorderStyle.border).toBe('1px solid #E5E7EB');
    });

    it('kpiCardCls es p-4 rounded-lg', () => {
      expect(kpiCardCls).toContain('p-4');
      expect(kpiCardCls).toContain('rounded-lg');
    });

    it('badgeBaseCls es px-2 py-0.5 rounded', () => {
      expect(badgeBaseCls).toContain('px-2');
      expect(badgeBaseCls).toContain('py-0.5');
      expect(badgeBaseCls).toContain('rounded');
    });
  });

  describe('Helper cx', () => {
    it('une clases válidas', () => {
      expect(cx('a', 'b', 'c')).toBe('a b c');
    });

    it('filtra valores falsy', () => {
      expect(cx('a', false, 'b', null, undefined, 'c')).toBe('a b c');
    });

    it('retorna string vacío si no hay clases', () => {
      expect(cx()).toBe('');
      expect(cx(false, null, undefined)).toBe('');
    });
  });
});