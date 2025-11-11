import React, { useState, useEffect } from "react"
import { Input } from "./input"
import { Label } from "./label"
import { cn } from "../../utilidades/cn"
import { formatRUT, validateRUT, formatPhone } from "../../utilidades/localization"

interface ChileanInputProps {
  type: "rut" | "phone" | "currency"
  value: string
  onChange: (value: string) => void
  placeholder?: string
  label?: string
  error?: string
  className?: string
  disabled?: boolean
  required?: boolean
}

export function ChileanInput({
  type,
  value,
  onChange,
  placeholder,
  label,
  error,
  className,
  disabled = false,
  required = false,
}: ChileanInputProps) {
  const [displayValue, setDisplayValue] = useState("")
  const [isValid, setIsValid] = useState(true)

  useEffect(() => {
    if (type === "rut") {
      const formatted = formatRUT(value)
      setDisplayValue(formatted)
      setIsValid(validateRUT(value))
    } else if (type === "phone") {
      const formatted = formatPhone(value)
      setDisplayValue(formatted)
      setIsValid(true) // Phone validation can be added later
    } else if (type === "currency") {
      const numericValue = parseFloat(value) || 0
      setDisplayValue(numericValue.toLocaleString('es-CL'))
      setIsValid(true)
    } else {
      setDisplayValue(value)
      setIsValid(true)
    }
  }, [value, type])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let newValue = e.target.value

    if (type === "rut") {
      // Solo permitir números, K y k
      newValue = newValue.replace(/[^0-9kK]/g, "")
    } else if (type === "phone") {
      // Solo permitir números
      newValue = newValue.replace(/[^0-9]/g, "")
    } else if (type === "currency") {
      // Solo permitir números y punto decimal
      newValue = newValue.replace(/[^0-9.]/g, "")
    }

    onChange(newValue)
  }

  const getPlaceholder = () => {
    if (placeholder) return placeholder
    
    switch (type) {
      case "rut":
        return "12.345.678-9"
      case "phone":
        return "9 1234 5678"
      case "currency":
        return "1000000"
      default:
        return ""
    }
  }

  const getInputType = () => {
    switch (type) {
      case "currency":
        return "number"
      default:
        return "text"
    }
  }

  return (
    <div className={cn("space-y-2", className)}>
      {label && (
        <Label htmlFor={type}>
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </Label>
      )}
      <Input
        id={type}
        type={getInputType()}
        value={displayValue}
        onChange={handleChange}
        placeholder={getPlaceholder()}
        disabled={disabled}
        className={cn(
          error && "border-red-500",
          !isValid && type === "rut" && "border-red-500"
        )}
      />
      {error && (
        <p className="text-sm text-red-500">{error}</p>
      )}
      {!isValid && type === "rut" && (
        <p className="text-sm text-red-500">RUT inválido</p>
      )}
    </div>
  )
}

