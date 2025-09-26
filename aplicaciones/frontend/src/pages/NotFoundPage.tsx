import React from 'react'
import { Link } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { Card, CardContent } from '../components/ui/card'
import { Home, ArrowLeft } from 'lucide-react'

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="w-full max-w-md text-center">
        <CardContent className="pt-6">
          <div className="space-y-6">
            <div>
              <h1 className="text-6xl font-bold text-muted-foreground">404</h1>
              <h2 className="text-2xl font-semibold mt-4">Página no encontrada</h2>
              <p className="text-muted-foreground mt-2">
                La página que buscas no existe o ha sido movida.
              </p>
            </div>
            
            <div className="flex flex-col space-y-3">
              <Button asChild>
                <Link to="/app/dashboard">
                  <Home className="w-4 h-4 mr-2" />
                  Ir al Dashboard
                </Link>
              </Button>
              <Button variant="outline" onClick={() => window.history.back()}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Volver Atrás
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}


