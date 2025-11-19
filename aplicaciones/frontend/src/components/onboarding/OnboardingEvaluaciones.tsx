import React from 'react'
import { Link } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Compass, FilePlus2, Loader2, Users } from 'lucide-react'

type StepAction =
  | { tipo: 'link'; etiqueta: string; href: string }
  | { tipo: 'accion'; etiqueta: string; onClick: () => void }

interface PasoOnboarding {
  titulo: string
  descripcion: string
  icono: React.ReactNode
  accion: StepAction
}

interface OnboardingEvaluacionesProps {
  onCrearEvaluacion: () => void
  creandoEvaluacion?: boolean
}

export const OnboardingEvaluaciones: React.FC<OnboardingEvaluacionesProps> = ({ onCrearEvaluacion, creandoEvaluacion = false }) => {
  const pasos: PasoOnboarding[] = [
    {
      titulo: 'Explora el panel principal',
      descripcion:
        'Revisa métricas clave, atajos y recomendaciones que te orientarán en los primeros días de uso.',
      icono: <Compass className="h-6 w-6 text-c4a-blue-600" />,
      accion: {
        tipo: 'link',
        etiqueta: 'Ir al dashboard',
        href: '/app/dashboard'
      }
    },
    {
      titulo: 'Crea tu primera evaluación',
      descripcion:
        'Generar automáticamente el diagnóstico de 50 preguntas del Plan Pro.',
      icono: <FilePlus2 className="h-6 w-6 text-c4a-blue-600" />,
      accion: {
        tipo: 'accion',
        etiqueta: 'Crear evaluación',
        onClick: onCrearEvaluacion
      }
    },
    {
      titulo: 'Invita a tu equipo',
      descripcion:
        'Comparte la plataforma con tus colaboradores para avanzar en conjunto con el plan de acción.',
      icono: <Users className="h-6 w-6 text-c4a-blue-600" />,
      accion: {
        tipo: 'link',
        etiqueta: 'Gestionar invitaciones',
        href: '/app/suscripciones'
      }
    }
  ]

  return (
    <div className="space-y-8">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-semibold text-foreground">Comienza con tu diagnóstico</h2>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Aún no tienes evaluaciones registradas. Sigue estos pasos para configurar tu cuenta, crear la primera
          evaluación y sumar a tu equipo al proceso de mejora continua.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {pasos.map((paso, indice) => (
          <Card key={paso.titulo} className="h-full border-c4a-blue-100 bg-card">
            <CardHeader className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-c4a-blue-50 text-c4a-blue-600">
                  {paso.icono}
                </div>
                <span className="text-sm font-medium text-c4a-blue-500">Paso {indice + 1}</span>
              </div>
              <CardTitle className="text-lg leading-tight text-foreground">{paso.titulo}</CardTitle>
              <CardDescription className="text-sm text-muted-foreground">
                {paso.descripcion}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {paso.accion.tipo === 'link' ? (
                <Button variant="outline" className="w-full" asChild>
                  <Link to={paso.accion.href}>{paso.accion.etiqueta}</Link>
                </Button>
              ) : (
                <Button
                  className="w-full"
                  onClick={paso.accion.onClick}
                  disabled={creandoEvaluacion}
                >
                  {creandoEvaluacion ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creando evaluación...
                    </>
                  ) : (
                    paso.accion.etiqueta
                  )}
                </Button>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}



