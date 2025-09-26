import { useState, useEffect } from 'react'
import { chileLocalization, formatCLP, formatChileanDate, formatRUT, validateRUT, getChileanTime } from '../utilidades/localization'

export function useChileanLocalization() {
  const [currentTime, setCurrentTime] = useState<Date>(getChileanTime())

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(getChileanTime())
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  return {
    // Time utilities
    currentTime,
    getChileanTime,
    
    // Formatting utilities
    formatCLP,
    formatChileanDate,
    formatRUT,
    validateRUT,
    
    // Data utilities
    getChileanSectors: chileLocalization.getChileanSectors,
    getCompanySizes: chileLocalization.getCompanySizes,
    getChileanRegions: chileLocalization.getChileanRegions,
    getMonthNames: chileLocalization.getMonthNames,
    getWeekdayNames: chileLocalization.getWeekdayNames,
    
    // Configuration
    timezone: chileLocalization.getChileanTimezone(),
    locale: chileLocalization.getChileanLocale(),
    currency: chileLocalization.getChileanCurrency(),
  }
}
















