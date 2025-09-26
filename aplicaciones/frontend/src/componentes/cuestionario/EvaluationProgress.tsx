import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { Progress } from '../../components/ui/progress'
import { Badge } from '../../components/ui/badge'
import { Clock, CheckCircle, FileText } from 'lucide-react'

interface EvaluationProgressProps {
  currentQuestion: number
  totalQuestions: number
  completedQuestions: number
  timeElapsed?: number
  isCompleted?: boolean
  className?: string
}

export const EvaluationProgress: React.FC<EvaluationProgressProps> = ({
  currentQuestion,
  totalQuestions,
  completedQuestions,
  timeElapsed,
  isCompleted = false,
  className = ''
}) => {
  const progressPercentage = (completedQuestions / totalQuestions) * 100
  const remainingQuestions = totalQuestions - completedQuestions

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60

    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`
    } else {
      return `${secs}s`
    }
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          {isCompleted ? (
            <CheckCircle className="w-5 h-5 text-green-600" />
          ) : (
            <FileText className="w-5 h-5 text-c4a-blue-600" />
          )}
          <span>Progreso de Evaluación</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Barra de progreso principal */}
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>Progreso General</span>
              <span>{progressPercentage.toFixed(0)}%</span>
            </div>
            <Progress value={progressPercentage} className="h-3" />
          </div>

          {/* Estadísticas detalladas */}
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-c4a-blue-600">
                {completedQuestions}
              </div>
              <div className="text-sm text-muted-foreground">
                Completadas
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-muted-foreground">
                {remainingQuestions}
              </div>
              <div className="text-sm text-muted-foreground">
                Restantes
              </div>
            </div>
          </div>

          {/* Estado actual */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {isCompleted ? (
                <Badge className="bg-green-100 text-green-800">
                  <CheckCircle className="w-3 h-3 mr-1" />
                  Completada
                </Badge>
              ) : (
                <Badge className="bg-yellow-100 text-yellow-800">
                  <Clock className="w-3 h-3 mr-1" />
                  En Progreso
                </Badge>
              )}
            </div>
            
            {timeElapsed !== undefined && (
              <div className="text-sm text-muted-foreground">
                Tiempo: {formatTime(timeElapsed)}
              </div>
            )}
          </div>

          {/* Pregunta actual */}
          {!isCompleted && (
            <div className="text-center text-sm text-muted-foreground">
              Pregunta {currentQuestion} de {totalQuestions}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}


