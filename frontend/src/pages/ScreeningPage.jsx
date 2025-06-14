import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Shield, 
  Search, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  User,
  Building,
  Globe,
  FileText,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react'

const ScreeningPage = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedTab, setSelectedTab] = useState('all')
  
  const [screenings] = useState([
    {
      id: 1,
      customer: 'João Silva',
      type: 'individual',
      status: 'completed',
      riskLevel: 'low',
      matches: 0,
      sources: ['OFAC', 'UN', 'EU'],
      lastRun: '2025-06-14T10:30:00',
      confidence: 98
    },
    {
      id: 2,
      customer: 'Maria Santos',
      type: 'individual',
      status: 'running',
      riskLevel: null,
      matches: null,
      sources: ['OFAC', 'UN'],
      lastRun: '2025-06-14T11:00:00',
      confidence: null
    },
    {
      id: 3,
      customer: 'Pedro Costa',
      type: 'individual',
      status: 'completed',
      riskLevel: 'high',
      matches: 2,
      sources: ['OFAC', 'UN', 'EU', 'OpenSanctions'],
      lastRun: '2025-06-14T09:15:00',
      confidence: 95
    },
    {
      id: 4,
      customer: 'TechCorp Ltda',
      type: 'company',
      status: 'completed',
      riskLevel: 'medium',
      matches: 1,
      sources: ['OpenCorporates', 'GLEIF', 'SEC'],
      lastRun: '2025-06-13T16:45:00',
      confidence: 87
    },
    {
      id: 5,
      customer: 'Ana Lima',
      type: 'individual',
      status: 'pending',
      riskLevel: null,
      matches: null,
      sources: [],
      lastRun: null,
      confidence: null
    }
  ])

  const [sources] = useState([
    { name: 'OFAC', status: 'active', lastUpdate: '2025-06-14', records: 12547 },
    { name: 'UN Consolidated List', status: 'active', lastUpdate: '2025-06-14', records: 8932 },
    { name: 'EU Financial Sanctions', status: 'active', lastUpdate: '2025-06-13', records: 5621 },
    { name: 'UK OFSI', status: 'active', lastUpdate: '2025-06-13', records: 3456 },
    { name: 'OpenSanctions', status: 'active', lastUpdate: '2025-06-14', records: 45123 },
    { name: 'Banco Central BR', status: 'active', lastUpdate: '2025-06-14', records: 2341 },
    { name: 'OpenCorporates', status: 'active', lastUpdate: '2025-06-14', records: 234567 },
    { name: 'GLEIF LEI', status: 'active', lastUpdate: '2025-06-13', records: 87654 }
  ])

  const getRiskBadge = (riskLevel) => {
    switch (riskLevel) {
      case 'low':
        return <Badge className="bg-green-100 text-green-800">Baixo Risco</Badge>
      case 'medium':
        return <Badge className="bg-yellow-100 text-yellow-800">Médio Risco</Badge>
      case 'high':
        return <Badge className="bg-red-100 text-red-800">Alto Risco</Badge>
      default:
        return <Badge variant="outline">Não avaliado</Badge>
    }
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return <Badge className="bg-green-100 text-green-800">Concluído</Badge>
      case 'running':
        return <Badge className="bg-blue-100 text-blue-800">Executando</Badge>
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800">Pendente</Badge>
      case 'error':
        return <Badge className="bg-red-100 text-red-800">Erro</Badge>
      default:
        return <Badge>Desconhecido</Badge>
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'running':
        return <Clock className="w-5 h-5 text-blue-500 animate-spin" />
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />
      case 'error':
        return <AlertTriangle className="w-5 h-5 text-red-500" />
      default:
        return <Shield className="w-5 h-5 text-gray-500" />
    }
  }

  const filteredScreenings = screenings.filter(screening => {
    const matchesSearch = screening.customer.toLowerCase().includes(searchTerm.toLowerCase())
    
    if (selectedTab === 'all') return matchesSearch
    return matchesSearch && screening.status === selectedTab
  })

  const stats = {
    total: screenings.length,
    completed: screenings.filter(s => s.status === 'completed').length,
    running: screenings.filter(s => s.status === 'running').length,
    pending: screenings.filter(s => s.status === 'pending').length,
    highRisk: screenings.filter(s => s.riskLevel === 'high').length
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gradient">Screening</h1>
        <p className="text-muted-foreground">Verificação de sanções e listas restritivas</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="glass-effect">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total</p>
                <p className="text-2xl font-bold">{stats.total}</p>
              </div>
              <Shield className="w-8 h-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-effect">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Concluídos</p>
                <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-effect">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Executando</p>
                <p className="text-2xl font-bold text-blue-600">{stats.running}</p>
              </div>
              <Clock className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-effect">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Pendentes</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.pending}</p>
              </div>
              <Clock className="w-8 h-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-effect">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Alto Risco</p>
                <p className="text-2xl font-bold text-red-600">{stats.highRisk}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-red-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card className="glass-effect">
        <CardHeader>
          <CardTitle>Ações Rápidas</CardTitle>
          <CardDescription>Iniciar novos screenings ou gerenciar execuções</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button className="h-20 flex flex-col items-center justify-center space-y-2">
              <Play className="w-6 h-6" />
              <span>Novo Screening Individual</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col items-center justify-center space-y-2">
              <Building className="w-6 h-6" />
              <span>Novo Screening Empresa</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col items-center justify-center space-y-2">
              <RotateCcw className="w-6 h-6" />
              <span>Atualizar Fontes</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Screenings List */}
        <Card className="glass-effect">
          <CardHeader>
            <CardTitle>Screenings Recentes</CardTitle>
            <CardDescription>Lista de verificações realizadas</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 mb-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                <Input
                  placeholder="Buscar screenings..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              
              <Tabs value={selectedTab} onValueChange={setSelectedTab}>
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="all">Todos</TabsTrigger>
                  <TabsTrigger value="completed">Concluídos</TabsTrigger>
                  <TabsTrigger value="running">Executando</TabsTrigger>
                  <TabsTrigger value="pending">Pendentes</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>

            <div className="space-y-3">
              {filteredScreenings.map((screening) => (
                <div key={screening.id} className="p-4 border rounded-lg hover:bg-accent/50 transition-colors">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(screening.status)}
                      <div>
                        <h4 className="font-medium">{screening.customer}</h4>
                        <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                          {screening.type === 'individual' ? (
                            <User className="w-4 h-4" />
                          ) : (
                            <Building className="w-4 h-4" />
                          )}
                          <span>{screening.type === 'individual' ? 'Pessoa Física' : 'Pessoa Jurídica'}</span>
                        </div>
                      </div>
                    </div>
                    {getStatusBadge(screening.status)}
                  </div>

                  {screening.riskLevel && (
                    <div className="flex items-center justify-between mb-2">
                      {getRiskBadge(screening.riskLevel)}
                      {screening.matches !== null && (
                        <span className="text-sm text-muted-foreground">
                          {screening.matches} match(es) encontrado(s)
                        </span>
                      )}
                    </div>
                  )}

                  {screening.confidence && (
                    <div className="mb-2">
                      <div className="flex justify-between text-sm mb-1">
                        <span>Confiança</span>
                        <span>{screening.confidence}%</span>
                      </div>
                      <Progress value={screening.confidence} />
                    </div>
                  )}

                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>Fontes: {screening.sources.join(', ')}</span>
                    {screening.lastRun && (
                      <span>
                        {new Date(screening.lastRun).toLocaleString('pt-BR')}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Data Sources */}
        <Card className="glass-effect">
          <CardHeader>
            <CardTitle>Fontes de Dados</CardTitle>
            <CardDescription>Status das fontes de sanções e listas restritivas</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {sources.map((source, index) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <div>
                      <h4 className="font-medium">{source.name}</h4>
                      <p className="text-sm text-muted-foreground">
                        {source.records.toLocaleString()} registros
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge variant="outline" className="mb-1">Ativo</Badge>
                    <p className="text-xs text-muted-foreground">
                      Atualizado: {new Date(source.lastUpdate).toLocaleDateString('pt-BR')}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center space-x-2 mb-2">
                <Globe className="w-5 h-5 text-blue-500" />
                <span className="font-medium">Cobertura Global</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Mais de 400.000 registros de 195+ jurisdições FATF
              </p>
              <Progress value={95} className="mt-2" />
              <p className="text-xs text-muted-foreground mt-1">95% de cobertura global</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Alerts */}
      <Card className="glass-effect">
        <CardHeader>
          <CardTitle>Alertas Recentes</CardTitle>
          <CardDescription>Matches encontrados que requerem atenção</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center space-x-3">
                <AlertTriangle className="w-5 h-5 text-red-500" />
                <div>
                  <h4 className="font-medium text-red-800">Pedro Costa</h4>
                  <p className="text-sm text-red-600">2 matches encontrados em OFAC e UN</p>
                </div>
              </div>
              <div className="flex space-x-2">
                <Button size="sm" variant="outline">Revisar</Button>
                <Button size="sm">Investigar</Button>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-center space-x-3">
                <AlertTriangle className="w-5 h-5 text-yellow-500" />
                <div>
                  <h4 className="font-medium text-yellow-800">TechCorp Ltda</h4>
                  <p className="text-sm text-yellow-600">1 match encontrado em OpenCorporates</p>
                </div>
              </div>
              <div className="flex space-x-2">
                <Button size="sm" variant="outline">Revisar</Button>
                <Button size="sm">Investigar</Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default ScreeningPage

