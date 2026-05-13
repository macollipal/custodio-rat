export function validarRUT(rut: string): { valido: boolean; mensaje: string } {
  const limpio = rut.replace(/[^0-9kK]/gi, '').toUpperCase();
  if (limpio.length < 8) {
    return { valido: false, mensaje: 'El RUT debe tener al menos 8 caracteres (incluyendo DV).' };
  }

  const cuerpo = limpio.slice(0, -1);
  const dv = limpio.slice(-1);

  if (!/^\d+$/.test(cuerpo)) {
    return { valido: false, mensaje: 'El cuerpo del RUT debe contener solo números.' };
  }

  let suma = 0;
  let multiplo = 2;
  for (let i = cuerpo.length - 1; i >= 0; i--) {
    suma += parseInt(cuerpo[i], 10) * multiplo;
    multiplo = multiplo === 7 ? 2 : multiplo + 1;
  }

  const resto = suma % 11;
  const dvEsperado = resto === 0 ? '0' : resto === 1 ? 'K' : String(11 - resto);

  if (dv !== dvEsperado) {
    return { valido: false, mensaje: `El dígito verificador no corresponde. RUT inválido (esperado: ${dvEsperado}).` };
  }

  return { valido: true, mensaje: 'RUT válido.' };
}

export function formatearRUT(rut: string): string {
  const limpio = rut.replace(/[^0-9kK]/gi, '').toUpperCase();
  if (limpio.length < 2) return rut;
  const cuerpo = limpio.slice(0, -1);
  const dv = limpio.slice(-1);
  return `${cuerpo.replace(/\B(?=(\d{3})+(?!\d))/g, '.')}-${dv}`;
}