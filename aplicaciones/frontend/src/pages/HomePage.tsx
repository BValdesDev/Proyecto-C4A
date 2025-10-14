import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { 
  Shield, 
  BarChart3, 
  Users, 
  CheckCircle, 
  ArrowRight, 
  Star,
  Lock,
  Zap,
  Target,
  Award,
  Globe,
  Building,
  Check,
  X
} from 'lucide-react'

export const HomePage: React.FC = () => {
  const navigate = useNavigate()

  const features = [
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Evaluaciones NIST CSF 2.0",
      description: "Cumplimiento con el marco de ciberseguridad más reconocido mundialmente"
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: "Reportes Detallados",
      description: "Análisis completo con recomendaciones específicas para tu organización"
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: "Gestión Multi-usuario",
      description: "Colabora con tu equipo en evaluaciones y seguimiento de mejoras"
    },
    {
      icon: <Target className="w-6 h-6" />,
      title: "Benchmarking Sectorial",
      description: "Compara tu postura de ciberseguridad con organizaciones similares"
    }
  ]

  const plans = [
    {
      name: "Gratuito",
      price: "$0",
      period: "/mes",
      description: "Perfecto para empezar",
      features: [
        "Hasta 3 evaluaciones",
        "Reportes básicos",
        "Soporte por email",
        "Acceso a dashboard"
      ],
      cta: "Comenzar Gratis",
      popular: false
    },
    {
      name: "Pro",
      price: "$32.000",
      period: "/mes",
      description: "Para equipos en crecimiento",
      features: [
        "Evaluaciones ilimitadas",
        "Reportes avanzados",
        "Benchmarking sectorial",
        "Soporte prioritario",
        "Integración API"
      ],
      cta: "Probar Pro",
      popular: true
    },
    {
      name: "Empresarial",
      price: "Personalizado",
      period: "",
      description: "Para grandes organizaciones",
      features: [
        "Todo lo de Pro",
        "Gestión multi-organización",
        "SLA garantizado",
        "Consultoría incluida",
        "Soporte 24/7"
      ],
      cta: "Contactar Ventas",
      popular: false
    }
  ]

  const comparisonFeatures = [
    {
      category: "Evaluaciones",
      features: [
        { name: "Evaluaciones por mes", gratuito: "1", pro: "Ilimitadas", empresarial: "Ilimitadas" },
        { name: "Preguntas disponibles", gratuito: "10 básicas", pro: "50 detalladas", empresarial: "100 completas" },
        { name: "Recomendaciones", gratuito: "3", pro: "15", empresarial: "50+" }
      ]
    },
    {
      category: "Reportes y Análisis",
      features: [
        { name: "Reportes básicos", gratuito: true, pro: true, empresarial: true },
        { name: "Reportes avanzados", gratuito: false, pro: true, empresarial: true },
        { name: "Benchmarking sectorial", gratuito: false, pro: true, empresarial: true },
        { name: "Marca de agua en reportes", gratuito: true, pro: false, empresarial: false },
        { name: "Marca blanca", gratuito: false, pro: false, empresarial: true }
      ]
    },
    {
      category: "Usuarios y Organización",
      features: [
        { name: "Usuarios máximos", gratuito: "1", pro: "10", empresarial: "Ilimitados" },
        { name: "Gestión multi-organización", gratuito: false, pro: false, empresarial: true },
        { name: "SSO (Single Sign-On)", gratuito: false, pro: false, empresarial: true },
        { name: "API completa", gratuito: false, pro: true, empresarial: true }
      ]
    },
    {
      category: "Soporte y Servicios",
      features: [
        { name: "Soporte por email", gratuito: true, pro: true, empresarial: true },
        { name: "Soporte prioritario", gratuito: false, pro: true, empresarial: true },
        { name: "Soporte 24/7", gratuito: false, pro: false, empresarial: true },
        { name: "Consultoría personalizada", gratuito: false, pro: false, empresarial: true },
        { name: "SLA garantizado", gratuito: false, pro: false, empresarial: true }
      ]
    }
  ]

  const testimonials = [
    {
      name: "María González",
      role: "CISO, Banco Nacional",
      content: "C4A nos ayudó a identificar vulnerabilidades críticas que no habíamos detectado. El proceso es muy intuitivo y los reportes son excelentes.",
      rating: 5
    },
    {
      name: "Carlos Rodríguez",
      role: "Director TI, RetailCorp",
      content: "La comparación sectorial nos dio una perspectiva valiosa. Ahora sabemos exactamente dónde estamos respecto a la competencia.",
      rating: 5
    },
    {
      name: "Ana Martínez",
      role: "Gerente de Riesgos, SaludCorp",
      content: "Implementamos las recomendaciones de C4A y mejoramos significativamente nuestra postura de ciberseguridad en solo 3 meses.",
      rating: 5
    }
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-white/95 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-c4a-purple-600 to-c4a-blue-600 rounded-lg flex items-center justify-center">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-foreground">C4A SaaS</span>
            </div>
            <nav className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-foreground hover:text-c4a-blue-600 transition-colors">Características</a>
              <a href="#pricing" className="text-foreground hover:text-c4a-blue-600 transition-colors">Precios</a>
              <a href="#testimonials" className="text-foreground hover:text-c4a-blue-600 transition-colors">Testimonios</a>
              <a href="#contact" className="text-foreground hover:text-c4a-blue-600 transition-colors">Contacto</a>
            </nav>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" onClick={() => navigate('/login')}>
                Iniciar Sesión
              </Button>
              <Button onClick={() => navigate('/registro')} className="c4a-button-primary">
                Comenzar Gratis
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center">
          <Badge className="mb-4 bg-c4a-blue-100 text-c4a-blue-800">
            <Zap className="w-4 h-4 mr-1" />
            Nuevo: NIST CSF 2.0
          </Badge>
          <h1 className="text-5xl md:text-6xl font-bold text-foreground mb-6">
            Evalúa y Mejora tu
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-c4a-purple-600 to-c4a-blue-600">
              {" "}Ciberseguridad
            </span>
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            Plataforma líder en evaluaciones de ciberseguridad basada en NIST CSF 2.0 y COBIT 2019. 
            Identifica vulnerabilidades, mejora tu postura de seguridad y cumple con estándares internacionales.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" onClick={() => navigate('/registro')} className="c4a-button-primary text-lg px-8 py-4">
              Comenzar Evaluación Gratis
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
            <Button size="lg" variant="outline" className="text-lg px-8 py-4">
              Ver Demo
            </Button>
          </div>
          <p className="text-sm text-muted-foreground mt-4">
            Sin tarjeta de crédito • Configuración en 2 minutos
          </p>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-muted/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Todo lo que necesitas para una ciberseguridad robusta
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Herramientas profesionales diseñadas para organizaciones que se toman en serio la ciberseguridad
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="text-center hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="w-12 h-12 bg-c4a-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    {feature.icon}
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-c4a-blue-600 mb-2">500+</div>
              <div className="text-muted-foreground">Organizaciones</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-c4a-blue-600 mb-2">50K+</div>
              <div className="text-muted-foreground">Evaluaciones</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-c4a-blue-600 mb-2">98%</div>
              <div className="text-muted-foreground">Satisfacción</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-c4a-blue-600 mb-2">24/7</div>
              <div className="text-muted-foreground">Soporte</div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-muted/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Planes que se adaptan a tu organización
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Desde startups hasta grandes corporaciones, tenemos el plan perfecto para ti
            </p>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
            {plans.map((plan, index) => (
              <Card key={index} className={`relative flex flex-col h-full transition-all duration-300 hover:shadow-lg ${plan.popular ? 'border-c4a-blue-500 shadow-lg scale-105' : ''}`}>
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-c4a-blue-600 text-white">Más Popular</Badge>
                  </div>
                )}
                <CardHeader className="text-center">
                  <CardTitle className="text-2xl">{plan.name}</CardTitle>
                  <div className="text-4xl font-bold text-foreground">
                    {plan.price}
                    <span className="text-lg text-muted-foreground">{plan.period}</span>
                  </div>
                  <CardDescription>{plan.description}</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-col h-full">
                  <div className="flex-1">
                    <ul className="space-y-3 mb-6">
                      {plan.features.map((feature, featureIndex) => (
                        <li key={featureIndex} className="flex items-center">
                          <CheckCircle className="w-5 h-5 text-green-500 mr-3" />
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="mt-auto">
                    <Button 
                      className={`w-full ${plan.popular ? 'c4a-button-primary' : ''}`}
                      variant={plan.popular ? 'default' : 'outline'}
                      onClick={() => navigate('/registro')}
                    >
                      {plan.cta}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Comparison Table Section */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Compara nuestros planes
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Encuentra el plan perfecto para tu organización
            </p>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full max-w-6xl mx-auto bg-white rounded-lg shadow-lg overflow-hidden">
              <thead>
                <tr className="bg-gradient-to-r from-c4a-blue-600 to-c4a-purple-600 text-white">
                  <th className="px-6 py-4 text-left font-semibold">Características</th>
                  <th className="px-6 py-4 text-center font-semibold">
                    <div className="flex flex-col items-center">
                      <span className="text-lg font-bold">Gratuito</span>
                      <span className="text-sm opacity-90">$0/mes</span>
                    </div>
                  </th>
                  <th className="px-6 py-4 text-center font-semibold bg-c4a-blue-500">
                    <div className="flex flex-col items-center">
                      <span className="text-lg font-bold">Pro</span>
                      <span className="text-sm opacity-90">$32.000/mes</span>
                      <Badge className="mt-1 bg-white text-c4a-blue-600 text-xs">Más Popular</Badge>
                    </div>
                  </th>
                  <th className="px-6 py-4 text-center font-semibold">
                    <div className="flex flex-col items-center">
                      <span className="text-lg font-bold">Empresarial</span>
                      <span className="text-sm opacity-90">Personalizado</span>
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                {comparisonFeatures.map((category, categoryIndex) => (
                  <React.Fragment key={categoryIndex}>
                    <tr className="bg-gray-50">
                      <td colSpan={4} className="px-6 py-3 font-semibold text-gray-700 border-b">
                        {category.category}
                      </td>
                    </tr>
                    {category.features.map((feature, featureIndex) => (
                      <tr key={featureIndex} className="border-b hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4 font-medium text-gray-900">
                          {feature.name}
                        </td>
                        <td className="px-6 py-4 text-center">
                          {typeof feature.gratuito === 'boolean' ? (
                            feature.gratuito ? (
                              <Check className="w-5 h-5 text-green-600 mx-auto" />
                            ) : (
                              <X className="w-5 h-5 text-red-500 mx-auto" />
                            )
                          ) : (
                            <span className="text-sm font-medium text-gray-700">{feature.gratuito}</span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-center bg-blue-50">
                          {typeof feature.pro === 'boolean' ? (
                            feature.pro ? (
                              <Check className="w-5 h-5 text-green-600 mx-auto" />
                            ) : (
                              <X className="w-5 h-5 text-red-500 mx-auto" />
                            )
                          ) : (
                            <span className="text-sm font-medium text-gray-700">{feature.pro}</span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-center">
                          {typeof feature.empresarial === 'boolean' ? (
                            feature.empresarial ? (
                              <Check className="w-5 h-5 text-green-600 mx-auto" />
                            ) : (
                              <X className="w-5 h-5 text-red-500 mx-auto" />
                            )
                          ) : (
                            <span className="text-sm font-medium text-gray-700">{feature.empresarial}</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
          
          <div className="text-center mt-8">
            <p className="text-muted-foreground mb-4">
              ¿No estás seguro de qué plan elegir?
            </p>
            <Button 
              onClick={() => navigate('/registro')}
              className="bg-c4a-blue-600 hover:bg-c4a-blue-700"
            >
              Comenzar con Plan Gratuito
            </Button>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Lo que dicen nuestros clientes
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Miles de organizaciones confían en C4A para proteger sus activos digitales
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="p-6">
                <div className="flex items-center mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <blockquote className="text-muted-foreground mb-4">
                  "{testimonial.content}"
                </blockquote>
                <div>
                  <div className="font-semibold text-foreground">{testimonial.name}</div>
                  <div className="text-sm text-muted-foreground">{testimonial.role}</div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-c4a-purple-600 to-c4a-blue-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            ¿Listo para mejorar tu ciberseguridad?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Únete a cientos de organizaciones que ya protegen sus activos con C4A
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="secondary" onClick={() => navigate('/registro')} className="text-lg px-8 py-4">
              Comenzar Evaluación Gratis
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
            <Button size="lg" variant="outline" className="text-lg px-8 py-4 border-white text-white hover:bg-white hover:text-c4a-blue-600">
              Contactar Ventas
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-muted py-12">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-c4a-purple-600 to-c4a-blue-600 rounded-lg flex items-center justify-center">
                  <Shield className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold text-foreground">C4A SaaS</span>
              </div>
              <p className="text-muted-foreground">
                Plataforma líder en evaluaciones de ciberseguridad para organizaciones modernas.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-foreground mb-4">Producto</h3>
              <ul className="space-y-2 text-muted-foreground">
                <li><a href="#" className="hover:text-foreground transition-colors">Características</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Precios</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">API</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Integraciones</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-foreground mb-4">Soporte</h3>
              <ul className="space-y-2 text-muted-foreground">
                <li><a href="#" className="hover:text-foreground transition-colors">Centro de Ayuda</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Documentación</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Contacto</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Estado del Sistema</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-foreground mb-4">Legal</h3>
              <ul className="space-y-2 text-muted-foreground">
                <li><a href="#" className="hover:text-foreground transition-colors">Términos de Servicio</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Política de Privacidad</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Cookies</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">GDPR</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t mt-8 pt-8 text-center text-muted-foreground">
            <p>&copy; 2024 C4A SaaS. Todos los derechos reservados.</p>
          </div>
        </div>
      </footer>

    </div>
  )
}
