import React, { useState } from "react"
import { Button } from "./button"
import { Calendar } from "./calendar"
import { Popover, PopoverContent, PopoverTrigger } from "./popover"
import { CalendarIcon } from "lucide-react"
import { cn } from "../../utilidades/cn"
import { formatChileanDate } from "../../utilidades/localization"

interface ChileanDatePickerProps {
  date?: Date
  onDateChange?: (date: Date | undefined) => void
  placeholder?: string
  label?: string
  error?: string
  className?: string
  disabled?: boolean
  required?: boolean
  format?: "short" | "long" | "datetime" | "datetime_long"
}

export function ChileanDatePicker({
  date,
  onDateChange,
  placeholder = "Seleccionar fecha",
  label,
  error,
  className,
  disabled = false,
  required = false,
  format = "short",
}: ChileanDatePickerProps) {
  const [open, setOpen] = useState(false)

  const handleDateSelect = (selectedDate: Date | undefined) => {
    onDateChange?.(selectedDate)
    setOpen(false)
  }

  const formatDisplayDate = (date: Date) => {
    return formatChileanDate(date, format)
  }

  return (
    <div className={cn("space-y-2", className)}>
      {label && (
        <label className="text-sm font-medium">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className={cn(
              "w-full justify-start text-left font-normal",
              !date && "text-muted-foreground",
              error && "border-red-500"
            )}
            disabled={disabled}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {date ? formatDisplayDate(date) : <span>{placeholder}</span>}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            mode="single"
            selected={date}
            onSelect={handleDateSelect}
            initialFocus
            locale="es-CL"
          />
        </PopoverContent>
      </Popover>
      
      {error && (
        <p className="text-sm text-red-500">{error}</p>
      )}
    </div>
  )
}
















