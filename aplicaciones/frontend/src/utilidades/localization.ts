/**
 * Utilidades de localización para Chile
 */

export interface ChileanDate {
  day: number;
  month: number;
  year: number;
  hour?: number;
  minute?: number;
}

export interface ChileanCurrency {
  amount: number;
  symbol: string;
  formatted: string;
}

export interface ChileanRUT {
  number: string;
  dv: string;
  formatted: string;
  valid: boolean;
}

export class ChileLocalization {
  private timezone = 'America/Santiago';
  private locale = 'es-CL';
  private currency = 'CLP';

  /**
   * Formatear moneda chilena
   */
  formatCurrency(amount: number, showSymbol: boolean = true): string {
    const formatter = new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    });

    if (showSymbol) {
      return formatter.format(amount);
    } else {
      return new Intl.NumberFormat('es-CL').format(amount);
    }
  }

  /**
   * Formatear número con separadores de miles chilenos
   */
  formatNumber(number: number, decimals: number = 0): string {
    return new Intl.NumberFormat('es-CL', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(number);
  }

  /**
   * Formatear fecha en formato chileno
   */
  formatDate(date: Date, formatType: 'short' | 'long' | 'datetime' | 'datetime_long' = 'short'): string {
    const options: Intl.DateTimeFormatOptions = {
      timeZone: this.timezone,
    };

    switch (formatType) {
      case 'short':
        options.day = '2-digit';
        options.month = '2-digit';
        options.year = 'numeric';
        break;
      case 'long':
        options.day = 'numeric';
        options.month = 'long';
        options.year = 'numeric';
        break;
      case 'datetime':
        options.day = '2-digit';
        options.month = '2-digit';
        options.year = 'numeric';
        options.hour = '2-digit';
        options.minute = '2-digit';
        break;
      case 'datetime_long':
        options.day = 'numeric';
        options.month = 'long';
        options.year = 'numeric';
        options.hour = '2-digit';
        options.minute = '2-digit';
        break;
    }

    return new Intl.DateTimeFormat('es-CL', options).format(date);
  }

  /**
   * Formatear RUT chileno
   */
  formatRUT(rut: string): string {
    if (!rut) return rut;

    // Limpiar RUT
    const rutClean = rut.replace(/[^0-9kK]/g, '');

    if (rutClean.length < 2) return rut;

    // Separar número y dígito verificador
    const number = rutClean.slice(0, -1);
    const dv = rutClean.slice(-1).toUpperCase();

    // Formatear con puntos
    const numberFormatted = this.formatNumberWithDots(number);

    return `${numberFormatted}-${dv}`;
  }

  /**
   * Formatear número con puntos cada 3 dígitos
   */
  private formatNumberWithDots(number: string): string {
    if (number.length <= 3) return number;

    return number.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  }

  /**
   * Validar RUT chileno
   */
  validateRUT(rut: string): boolean {
    if (!rut) return false;

    // Limpiar RUT
    const rutClean = rut.replace(/[^0-9kK]/g, '');

    if (rutClean.length < 2) return false;

    // Separar número y dígito verificador
    const number = rutClean.slice(0, -1);
    const dv = rutClean.slice(-1).toUpperCase();

    // Validar que el número sea válido
    if (!/^\d+$/.test(number)) return false;

    // Calcular dígito verificador
    const dvCalculated = this.calculateRUTDV(number);

    return dv === dvCalculated;
  }

  /**
   * Calcular dígito verificador de RUT
   */
  private calculateRUTDV(number: string): string {
    let sum = 0;
    let multiplier = 2;

    for (let i = number.length - 1; i >= 0; i--) {
      sum += parseInt(number[i]) * multiplier;
      multiplier++;
      if (multiplier > 7) {
        multiplier = 2;
      }
    }

    const remainder = sum % 11;
    const dv = 11 - remainder;

    if (dv === 11) return '0';
    if (dv === 10) return 'K';
    return dv.toString();
  }

  /**
   * Obtener hora actual de Chile
   */
  getCurrentChileanTime(): Date {
    return new Date(new Date().toLocaleString('en-US', { timeZone: this.timezone }));
  }

  /**
   * Parsear fecha en formato chileno
   */
  parseChileanDate(dateString: string, formatType: 'short' | 'long' | 'datetime' = 'short'): Date | null {
    try {
      let date: Date;

      switch (formatType) {
        case 'short':
          // DD/MM/YYYY
          const [day, month, year] = dateString.split('/');
          date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
          break;
        case 'long':
          // DD de MMMM de YYYY
          const longMatch = dateString.match(/(\d+)\s+de\s+(\w+)\s+de\s+(\d+)/);
          if (!longMatch) return null;
          const [, dayStr, monthStr, yearStr] = longMatch;
          const monthIndex = this.getMonthNames().indexOf(monthStr);
          if (monthIndex === -1) return null;
          date = new Date(parseInt(yearStr), monthIndex, parseInt(dayStr));
          break;
        case 'datetime':
          // DD/MM/YYYY HH:MM
          const [datePart, timePart] = dateString.split(' ');
          const [day2, month2, year2] = datePart.split('/');
          const [hour, minute] = timePart.split(':');
          date = new Date(parseInt(year2), parseInt(month2) - 1, parseInt(day2), parseInt(hour), parseInt(minute));
          break;
        default:
          return null;
      }

      return date;
    } catch (error) {
      return null;
    }
  }

  /**
   * Obtener nombres de meses en español
   */
  getMonthNames(): string[] {
    return [
      'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];
  }

  /**
   * Obtener nombres de días de la semana en español
   */
  getWeekdayNames(): string[] {
    return ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
  }

  /**
   * Formatear número de teléfono chileno
   */
  formatPhone(phone: string): string {
    if (!phone) return phone;

    // Limpiar número
    const phoneClean = phone.replace(/[^0-9]/g, '');

    if (phoneClean.length === 9) {
      // Móvil: 9 1234 5678
      return `${phoneClean[0]} ${phoneClean.slice(1, 5)} ${phoneClean.slice(5)}`;
    } else if (phoneClean.length === 8) {
      // Fijo: 2 1234 5678
      return `${phoneClean[0]} ${phoneClean.slice(1, 5)} ${phoneClean.slice(5)}`;
    }

    return phone;
  }

  /**
   * Obtener sectores económicos chilenos
   */
  getChileanSectors(): Record<string, string> {
    return {
      agricultura: 'Agricultura, Silvicultura y Pesca',
      mineria: 'Minería',
      manufactura: 'Manufactura',
      construccion: 'Construcción',
      comercio: 'Comercio',
      transporte: 'Transporte y Almacenamiento',
      alojamiento: 'Alojamiento y Servicios de Comida',
      informacion: 'Información y Comunicaciones',
      financiero: 'Actividades Financieras y de Seguros',
      inmobiliario: 'Actividades Inmobiliarias',
      profesional: 'Actividades Profesionales, Científicas y Técnicas',
      administrativo: 'Actividades de Servicios Administrativos',
      publico: 'Administración Pública',
      educacion: 'Educación',
      salud: 'Actividades de Atención de la Salud',
      arte: 'Artes, Entretenimiento y Recreación',
      otro: 'Otras Actividades de Servicios',
      hogares: 'Actividades de los Hogares',
      organizaciones: 'Organizaciones y Órganos Extraterritoriales'
    };
  }

  /**
   * Obtener tamaños de empresa chilenos
   */
  getCompanySizes(): Record<string, string> {
    return {
      micro: 'Microempresa (1-9 empleados)',
      pequena: 'Pequeña empresa (10-49 empleados)',
      mediana: 'Mediana empresa (50-199 empleados)',
      grande: 'Gran empresa (200+ empleados)'
    };
  }

  /**
   * Obtener regiones de Chile
   */
  getChileanRegions(): Record<string, string> {
    return {
      arica: 'Región de Arica y Parinacota',
      tarapaca: 'Región de Tarapacá',
      antofagasta: 'Región de Antofagasta',
      atacama: 'Región de Atacama',
      coquimbo: 'Región de Coquimbo',
      valparaiso: 'Región de Valparaíso',
      metropolitana: 'Región Metropolitana',
      ohiggins: 'Región del Libertador General Bernardo O\'Higgins',
      maule: 'Región del Maule',
      nuble: 'Región de Ñuble',
      biobio: 'Región del Biobío',
      araucania: 'Región de La Araucanía',
      rios: 'Región de Los Ríos',
      lagos: 'Región de Los Lagos',
      aysen: 'Región Aysén del General Carlos Ibáñez del Campo',
      magallanes: 'Región de Magallanes y de la Antártica Chilena'
    };
  }

  /**
   * Obtener zona horaria de Chile
   */
  getChileanTimezone(): string {
    return this.timezone;
  }

  /**
   * Obtener locale de Chile
   */
  getChileanLocale(): string {
    return this.locale;
  }

  /**
   * Obtener moneda de Chile
   */
  getChileanCurrency(): string {
    return this.currency;
  }
}

// Instancia global del servicio de localización
export const chileLocalization = new ChileLocalization();

// Funciones de conveniencia
export const formatCLP = (amount: number, showSymbol: boolean = true): string => {
  return chileLocalization.formatCurrency(amount, showSymbol);
};

export const formatChileanDate = (date: Date, formatType: 'short' | 'long' | 'datetime' | 'datetime_long' = 'short'): string => {
  return chileLocalization.formatDate(date, formatType);
};

export const formatRUT = (rut: string): string => {
  return chileLocalization.formatRUT(rut);
};

export const validateRUT = (rut: string): boolean => {
  return chileLocalization.validateRUT(rut);
};

export const getChileanTime = (): Date => {
  return chileLocalization.getCurrentChileanTime();
};

export const formatPhone = (phone: string): string => {
  return chileLocalization.formatPhone(phone);
};

export const getChileanSectors = (): Record<string, string> => {
  return chileLocalization.getChileanSectors();
};

export const getCompanySizes = (): Record<string, string> => {
  return chileLocalization.getCompanySizes();
};

export const getChileanRegions = (): Record<string, string> => {
  return chileLocalization.getChileanRegions();
};
















