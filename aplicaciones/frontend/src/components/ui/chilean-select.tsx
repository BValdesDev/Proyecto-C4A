import React from "react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./select"
import { Label } from "./label"
import { cn } from "../../utilidades/cn"
import { getChileanSectors, getCompanySizes, getChileanRegions } from "../../utilidades/localization"

interface ChileanSelectProps {
  type: "sector" | "size" | "region"
  value: string
  onValueChange: (value: string) => void
  placeholder?: string
  label?: string
  error?: string
  className?: string
  disabled?: boolean
  required?: boolean
}

export function ChileanSelect({
  type,
  value,
  onValueChange,
  placeholder,
  label,
  error,
  className,
  disabled = false,
  required = false,
}: ChileanSelectProps) {
  const getOptions = () => {
    switch (type) {
      case "sector":
        return getChileanSectors()
      case "size":
        return getCompanySizes()
      case "region":
        return getChileanRegions()
      default:
        return {}
    }
  }

  const getDefaultPlaceholder = () => {
    if (placeholder) return placeholder
    
    switch (type) {
      case "sector":
        return "Seleccionar sector económico"
      case "size":
        return "Seleccionar tamaño de empresa"
      case "region":
        return "Seleccionar región"
      default:
        return "Seleccionar opción"
    }
  }

  const options = getOptions()

  return (
    <div className={cn("space-y-2", className)}>
      {label && (
        <Label>
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </Label>
      )}
      
      <Select value={value} onValueChange={onValueChange} disabled={disabled}>
        <SelectTrigger className={cn(error && "border-red-500")}>
          <SelectValue placeholder={getDefaultPlaceholder()} />
        </SelectTrigger>
        <SelectContent>
          {Object.entries(options).map(([key, label]) => (
            <SelectItem key={key} value={key}>
              {label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      
      {error && (
        <p className="text-sm text-red-500">{error}</p>
      )}
    </div>
  )
}
















