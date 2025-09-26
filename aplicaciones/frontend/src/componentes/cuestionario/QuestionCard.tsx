import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Progress } from '../../components/ui/progress'
import { Badge } from '../../components/ui/badge'
import { RadioGroup, RadioGroupItem } from '../../components/ui/radio-group'
import { Label } from '../../components/ui/label'
import { Checkbox } from '../../components/ui/checkbox'
import { Textarea } from '../../components/ui/textarea'
import { Pregunta, Respuesta } from '../../tipos'

interface QuestionCardProps {
  pregunta: Pregunta
  respuesta?: Respuesta
  onAnswer: (preguntaId: string, valor: any) => void
  currentIndex: number
  totalQuestions: number
  isLast?: boolean
  onNext?: () => void
  onPrevious?: () => void
  onSave?: () => void
}

export const QuestionCard: React.FC<QuestionCardProps> = ({
  pregunta,
  respuesta,
  onAnswer,
  currentIndex,
  totalQuestions,
  isLast = false,
  onNext,
  onPrevious,
  onSave
}) => {
  const [localAnswer, setLocalAnswer] = useState(respuesta?.valor || '')

  const handleAnswerChange = (value: any) => {
    setLocalAnswer(value)
    onAnswer(pregunta.id, value)
  }

  const handleNext = () => {
    if (onNext) onNext()
  }

  const handlePrevious = () => {
    if (onPrevious) onPrevious()
  }

  const handleSave = () => {
    if (onSave) onSave()
  }

  const renderQuestionInput = () => {
    switch (pregunta.tipo_respuesta) {
      case 'opcion_unica':
        return (
          <RadioGroup
            value={localAnswer}
            onValueChange={handleAnswerChange}
            className="space-y-3"
          >
            {pregunta.opciones?.map((opcion, index) => (
              <div key={index} className="flex items-center space-x-2">
                <RadioGroupItem value={opcion.valor} id={`${pregunta.id}-${index}`} />
                <Label htmlFor={`${pregunta.id}-${index}`} className="flex-1">
                  {opcion.texto}
                </Label>
              </div>
            ))}
          </RadioGroup>
        )

      case 'opcion_multiple':
        return (
          <div className="space-y-3">
            {pregunta.opciones?.map((opcion, index) => (
              <div key={index} className="flex items-center space-x-2">
                <Checkbox
                  id={`${pregunta.id}-${index}`}
                  checked={Array.isArray(localAnswer) ? localAnswer.includes(opcion.valor) : false}
                  onCheckedChange={(checked) => {
                    const currentValues = Array.isArray(localAnswer) ? localAnswer : []
                    if (checked) {
                      handleAnswerChange([...currentValues, opcion.valor])
                    } else {
                      handleAnswerChange(currentValues.filter(v => v !== opcion.valor))
                    }
                  }}
                />
                <Label htmlFor={`${pregunta.id}-${index}`} className="flex-1">
                  {opcion.texto}
                </Label>
              </div>
            ))}
          </div>
        )

      case 'escala':
        return (
          <div className="space-y-4">
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>Muy bajo</span>
              <span>Muy alto</span>
            </div>
            <div className="flex space-x-2">
              {[1, 2, 3, 4, 5].map((value) => (
                <Button
                  key={value}
                  variant={localAnswer === value ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => handleAnswerChange(value)}
                  className="flex-1"
                >
                  {value}
                </Button>
              ))}
            </div>
            <div className="text-center text-sm text-muted-foreground">
              {localAnswer && `Seleccionado: ${localAnswer}`}
            </div>
          </div>
        )

      case 'texto_libre':
        return (
          <Textarea
            placeholder="Escribe tu respuesta aquí..."
            value={localAnswer}
            onChange={(e) => handleAnswerChange(e.target.value)}
            className="min-h-[100px]"
          />
        )

      default:
        return (
          <div className="text-muted-foreground">
            Tipo de pregunta no soportado: {pregunta.tipo_respuesta}
          </div>
        )
    }
  }

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <div className="flex items-center justify-between mb-4">
          <Badge variant="outline">
            Pregunta {currentIndex + 1} de {totalQuestions}
          </Badge>
          <div className="text-sm text-muted-foreground">
            {pregunta.categoria}
          </div>
        </div>
        
        <div className="mb-4">
          <Progress 
            value={(currentIndex / totalQuestions) * 100} 
            className="h-2"
          />
        </div>

        <CardTitle className="text-xl leading-relaxed">
          {pregunta.texto}
        </CardTitle>
        
        {pregunta.descripcion && (
          <p className="text-muted-foreground mt-2">
            {pregunta.descripcion}
          </p>
        )}
      </CardHeader>

      <CardContent>
        <div className="space-y-6">
          {renderQuestionInput()}
        </div>

        <div className="flex justify-between items-center mt-8 pt-6 border-t">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={currentIndex === 0}
          >
            Anterior
          </Button>

          <div className="flex space-x-2">
            <Button
              variant="outline"
              onClick={handleSave}
            >
              Guardar Progreso
            </Button>
            
            {isLast ? (
              <Button onClick={handleSave}>
                Finalizar Evaluación
              </Button>
            ) : (
              <Button onClick={handleNext}>
                Siguiente
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}


