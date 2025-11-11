// src/pages/admin/GestionCuestionarios.tsx
/**
 * Panel de administración para gestionar cuestionarios
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCuestionarios, Cuestionario } from '../../hooks/useCuestionarios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Plus,
  Search,
  Edit,
  Copy,
  Trash2,
  Eye,
  FileText,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';

export default function GestionCuestionarios() {
  const navigate = useNavigate();
  const { 
    cuestionarios, 
    loading, 
    error,
    listarCuestionarios,
    eliminarCuestionario,
    clonarCuestionario
  } = useCuestionarios();

  const [searchTerm, setSearchTerm] = useState('');
  const [cuestionarioEliminar, setCuestionarioEliminar] = useState<Cuestionario | null>(null);
  const [cuestionarioClonar, setCuestionarioClonar] = useState<Cuestionario | null>(null);
  const [nombreClon, setNombreClon] = useState('');
  const [procesando, setProcesando] = useState(false);

  useEffect(() => {
    listarCuestionarios(undefined, false); // Cargar todos incluyendo inactivos
  }, []);

  const cuestionariosFiltrados = cuestionarios.filter(c =>
    c.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.codigo.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleEliminar = async () => {
    if (!cuestionarioEliminar) return;

    setProcesando(true);
    try {
      await eliminarCuestionario(cuestionarioEliminar.id);
      toast.success('Cuestionario eliminado exitosamente');
      setCuestionarioEliminar(null);
    } catch (err: any) {
      toast.error(err.response?.data?.mensaje || 'Error al eliminar cuestionario');
    } finally {
      setProcesando(false);
    }
  };

  const handleClonar = async () => {
    if (!cuestionarioClonar || !nombreClon.trim()) {
      toast.error('Debe ingresar un nombre para el clon');
      return;
    }

    setProcesando(true);
    try {
      await clonarCuestionario(cuestionarioClonar.id, nombreClon);
      toast.success('Cuestionario clonado exitosamente');
      setCuestionarioClonar(null);
      setNombreClon('');
    } catch (err: any) {
      toast.error(err.response?.data?.mensaje || 'Error al clonar cuestionario');
    } finally {
      setProcesando(false);
    }
  };

  const getNivelBadge = (nivel: string) => {
    const configs: Record<string, string> = {
      'basico': 'bg-green-100 text-green-800',
      'intermedio': 'bg-blue-100 text-blue-800',
      'avanzado': 'bg-purple-100 text-purple-800'
    };
    
    return (
      <Badge className={configs[nivel] || 'bg-gray-100 text-gray-800'}>
        {nivel.charAt(0).toUpperCase() + nivel.slice(1)}
      </Badge>
    );
  };

  if (loading && cuestionarios.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando cuestionarios...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Cuestionarios</h1>
          <p className="text-gray-600 mt-2">
            Administra los cuestionarios de diagnóstico del sistema
          </p>
        </div>
        
        <Button onClick={() => navigate('/admin/cuestionarios/crear')}>
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Cuestionario
        </Button>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-gray-900">{cuestionarios.length}</p>
              <p className="text-sm text-gray-600 mt-1">Total Cuestionarios</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-green-600">
                {cuestionarios.filter(c => c.esta_activo).length}
              </p>
              <p className="text-sm text-gray-600 mt-1">Activos</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-blue-600">
                {cuestionarios.reduce((sum, c) => sum + c.total_evaluaciones, 0)}
              </p>
              <p className="text-sm text-gray-600 mt-1">Evaluaciones</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-purple-600">
                {cuestionarios.reduce((sum, c) => sum + c.total_items, 0)}
              </p>
              <p className="text-sm text-gray-600 mt-1">Total Preguntas</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Búsqueda */}
      <Card>
        <CardContent className="pt-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Buscar cuestionarios por nombre o código..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Lista de Cuestionarios */}
      <div className="grid grid-cols-1 gap-4">
        {cuestionariosFiltrados.map(cuestionario => (
          <Card key={cuestionario.id} className={!cuestionario.esta_activo ? 'opacity-60' : ''}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <CardTitle className="text-xl">{cuestionario.nombre}</CardTitle>
                    {getNivelBadge(cuestionario.nivel)}
                    <Badge variant="outline" className="text-xs">
                      v{cuestionario.version}
                    </Badge>
                    {!cuestionario.esta_activo && (
                      <Badge variant="destructive">
                        <XCircle className="h-3 w-3 mr-1" />
                        Inactivo
                      </Badge>
                    )}
                  </div>
                  <CardDescription>
                    Código: {cuestionario.codigo}
                  </CardDescription>
                </div>
                
                <div className="flex items-center gap-2">
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => navigate(`/app/diagnosticos/${cuestionario.id}`)}
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => navigate(`/admin/cuestionarios/${cuestionario.id}/editar`)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => {
                      setCuestionarioClonar(cuestionario);
                      setNombreClon(`${cuestionario.nombre} (Copia)`);
                    }}
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => setCuestionarioEliminar(cuestionario)}
                    disabled={!cuestionario.es_editable_por_admin}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>

            <CardContent>
              <div className="grid grid-cols-3 gap-6">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <FileText className="h-4 w-4 text-gray-400" />
                  <span>{cuestionario.total_items} preguntas</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Clock className="h-4 w-4 text-gray-400" />
                  <span>~{cuestionario.tiempo_estimado_minutos} minutos</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <CheckCircle2 className="h-4 w-4 text-gray-400" />
                  <span>{cuestionario.total_evaluaciones} evaluaciones</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}

        {cuestionariosFiltrados.length === 0 && (
          <Card>
            <CardContent className="py-12">
              <div className="text-center">
                <AlertCircle className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-600">
                  {searchTerm ? 'No se encontraron cuestionarios que coincidan con la búsqueda' : 'No hay cuestionarios disponibles'}
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Dialog de Eliminación */}
      <Dialog open={!!cuestionarioEliminar} onOpenChange={() => setCuestionarioEliminar(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirmar Eliminación</DialogTitle>
            <DialogDescription>
              ¿Está seguro que desea eliminar el cuestionario "{cuestionarioEliminar?.nombre}"?
              Esta acción no se puede deshacer.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCuestionarioEliminar(null)} disabled={procesando}>
              Cancelar
            </Button>
            <Button variant="destructive" onClick={handleEliminar} disabled={procesando}>
              {procesando ? 'Eliminando...' : 'Eliminar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog de Clonación */}
      <Dialog open={!!cuestionarioClonar} onOpenChange={() => {
        setCuestionarioClonar(null);
        setNombreClon('');
      }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Clonar Cuestionario</DialogTitle>
            <DialogDescription>
              Cree una copia del cuestionario "{cuestionarioClonar?.nombre}" que podrá personalizar.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <label className="text-sm font-medium mb-2 block">
              Nombre del nuevo cuestionario:
            </label>
            <Input
              value={nombreClon}
              onChange={(e) => setNombreClon(e.target.value)}
              placeholder="Ingrese el nombre..."
              disabled={procesando}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setCuestionarioClonar(null);
              setNombreClon('');
            }} disabled={procesando}>
              Cancelar
            </Button>
            <Button onClick={handleClonar} disabled={procesando || !nombreClon.trim()}>
              {procesando ? 'Clonando...' : 'Clonar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

