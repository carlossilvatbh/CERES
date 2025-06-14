import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  FileText, 
  Download, 
  Calendar, 
  TrendingUp,
  Users,
  Shield,
  AlertTriangle,
  CheckCircle,
  Filter,
  Search,
  BarChart3,
  PieChart
} from 'lucide-react'

const ReportsPage = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('30')
  const [selectedReport, setSelectedReport] = useState('compliance')

  const reports = [
    {
      id: 1,
      name: 'Relatório de Compliance Mensal',
      type: 'compliance',
      period: 'Maio 2025',
      status: 'ready',
      size: '2.3 MB',
      generated: '2025-06-01'
    },
    {
      id: 2,
      name: 'Análise de Risco Trimestral',
      type: 'risk',
      period: 'Q2 2025',
      status: 'generating',
      size: null,
      generated: null
    },
    {
      id: 3,
      name: 'Auditoria de Documentos',
      type: 'audit',
      period: 'Maio 2025',
      status: 'ready',
      size: '1.8 MB',
      generated: '2025-05-31'
    },
    {
      id: 4,
      name: 'Performance de Screening',
      type: 'performance',
      period: 'Últimos 30 dias',
      status: 'ready',
      size: '945 KB',
      generated: '2025-06-14'
    }
  ]

  const getStatusBadge = (status) => {
    switch (status) {
      case 'ready':
        return <Badge className="bg-green-100 text-green-800">Pronto</Badge>
      case 'generating':
        return <Badge className="bg-blue-100 text-blue-800">Gerando</Badge>
      case 'error':
        return <Badge className="bg-red-100 text-red-800">Erro</Badge>
      default:
        return <Badge>Desconhecido</Badge>
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gradient">Relatórios</h1>
        <p className="text-muted-foreground">Relatórios de compliance e análises</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="glass-effect">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Clientes Processados</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,247</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">+12%</span> vs mês anterior
            </p>
          </CardContent>
        </Card>

        <Card className="glass-effect">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Screenings Realizados</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,138</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">+8%</span> vs mês anterior
            </p>
          </CardContent>
        </Card>

        <Card className="glass-effect">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Alertas Gerados</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">61</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-red-600">+3%</span> vs mês anterior
            </p>
          </CardContent>
        </Card>

        <Card className="glass-effect">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Taxa de Resolução</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">94.2%</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">+2.1%</span> vs mês anterior
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Report Generation */}
      <Card className="glass-effect">
        <CardHeader>
          <CardTitle>Gerar Novo Relatório</CardTitle>
          <CardDescription>Configure e gere relatórios personalizados</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
            <div className="space-y-2">
              <Label htmlFor="report-type">Tipo de Relatório</Label>
              <Select value={selectedReport} onValueChange={setSelectedReport}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o tipo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="compliance">Compliance</SelectItem>
                  <SelectItem value="risk">Análise de Risco</SelectItem>
                  <SelectItem value="audit">Auditoria</SelectItem>
                  <SelectItem value="performance">Performance</SelectItem>
                  <SelectItem value="custom">Personalizado</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="period">Período</Label>
              <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o período" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7">Últimos 7 dias</SelectItem>
                  <SelectItem value="30">Últimos 30 dias</SelectItem>
                  <SelectItem value="90">Últimos 90 dias</SelectItem>
                  <SelectItem value="365">Último ano</SelectItem>
                  <SelectItem value="custom">Período personalizado</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="format">Formato</Label>
              <Select defaultValue="pdf">
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o formato" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pdf">PDF</SelectItem>
                  <SelectItem value="excel">Excel</SelectItem>
                  <SelectItem value="csv">CSV</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button>
              <FileText className="w-4 h-4 mr-2" />
              Gerar Relatório
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Charts Placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="glass-effect">
          <CardHeader>
            <CardTitle>Atividade de Compliance</CardTitle>
            <CardDescription>Screenings e alertas por mês</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] flex items-center justify-center border-2 border-dashed border-muted-foreground/25 rounded-lg">
              <div className="text-center">
                <BarChart3 className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">Gráfico de Barras - Atividade Mensal</p>
                <p className="text-sm text-muted-foreground mt-2">
                  Jan: 145 screenings, 12 alertas<br/>
                  Fev: 167 screenings, 8 alertas<br/>
                  Mar: 189 screenings, 15 alertas<br/>
                  Abr: 156 screenings, 6 alertas<br/>
                  Mai: 203 screenings, 11 alertas<br/>
                  Jun: 178 screenings, 9 alertas
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-effect">
          <CardHeader>
            <CardTitle>Distribuição de Risco</CardTitle>
            <CardDescription>Classificação dos clientes por nível de risco</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] flex items-center justify-center border-2 border-dashed border-muted-foreground/25 rounded-lg">
              <div className="text-center">
                <PieChart className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">Gráfico de Pizza - Distribuição de Risco</p>
                <div className="mt-4 space-y-2">
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-4 h-4 bg-green-500 rounded"></div>
                    <span className="text-sm">Baixo Risco: 78%</span>
                  </div>
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-4 h-4 bg-yellow-500 rounded"></div>
                    <span className="text-sm">Médio Risco: 18%</span>
                  </div>
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-4 h-4 bg-red-500 rounded"></div>
                    <span className="text-sm">Alto Risco: 4%</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Reports List */}
      <Card className="glass-effect">
        <CardHeader>
          <CardTitle>Relatórios Disponíveis</CardTitle>
          <CardDescription>Lista de relatórios gerados e em processamento</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {reports.map((report) => (
              <div key={report.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors">
                <div className="flex items-center space-x-4">
                  <FileText className="w-8 h-8 text-muted-foreground" />
                  <div>
                    <h4 className="font-medium">{report.name}</h4>
                    <p className="text-sm text-muted-foreground">
                      Período: {report.period}
                      {report.size && ` • Tamanho: ${report.size}`}
                    </p>
                    {report.generated && (
                      <p className="text-xs text-muted-foreground">
                        Gerado em: {new Date(report.generated).toLocaleDateString('pt-BR')}
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  {getStatusBadge(report.status)}
                  
                  {report.status === 'ready' && (
                    <div className="flex space-x-2">
                      <Button variant="ghost" size="icon">
                        <Download className="w-4 h-4" />
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Compliance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="glass-effect">
          <CardHeader>
            <CardTitle>Métricas de Compliance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Taxa de Detecção</span>
              <span className="text-sm font-bold">98.7%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Falsos Positivos</span>
              <span className="text-sm font-bold">2.1%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Tempo Médio de Resolução</span>
              <span className="text-sm font-bold">2.3h</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">SLA Compliance</span>
              <span className="text-sm font-bold text-green-600">99.2%</span>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-effect">
          <CardHeader>
            <CardTitle>Alertas por Categoria</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Sanções Financeiras</span>
              <Badge variant="outline">23</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">PEP (Pessoas Expostas)</span>
              <Badge variant="outline">18</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Lista de Terrorismo</span>
              <Badge variant="outline">12</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Outros</span>
              <Badge variant="outline">8</Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-effect">
          <CardHeader>
            <CardTitle>Próximas Ações</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center space-x-3">
              <Calendar className="w-4 h-4 text-blue-500" />
              <div>
                <p className="text-sm font-medium">Relatório Trimestral</p>
                <p className="text-xs text-muted-foreground">Vence em 15 dias</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <TrendingUp className="w-4 h-4 text-green-500" />
              <div>
                <p className="text-sm font-medium">Auditoria Interna</p>
                <p className="text-xs text-muted-foreground">Agendada para próxima semana</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <AlertTriangle className="w-4 h-4 text-orange-500" />
              <div>
                <p className="text-sm font-medium">Revisão de Políticas</p>
                <p className="text-xs text-muted-foreground">Pendente aprovação</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default ReportsPage

