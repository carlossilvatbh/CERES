import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Users, 
  FileText, 
  Shield, 
  AlertTriangle, 
  TrendingUp, 
  Clock,
  CheckCircle,
  XCircle
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const DashboardPage = () => {
  // Memoize static data to prevent unnecessary re-renders
  const initialStats = useMemo(() => ({
    totalCustomers: 1247,
    pendingDocuments: 23,
    activeScreenings: 8,
    highRiskAlerts: 3,
    completedToday: 45,
    processingTime: '2.3min'
  }), [])

  const chartData = useMemo(() => [
    { name: 'Jan', customers: 65, screenings: 45 },
    { name: 'Fev', customers: 78, screenings: 52 },
    { name: 'Mar', customers: 90, screenings: 67 },
    { name: 'Abr', customers: 81, screenings: 58 },
    { name: 'Mai', customers: 95, screenings: 72 },
    { name: 'Jun', customers: 112, screenings: 89 }
  ], [])

  const riskData = useMemo(() => [
    { name: 'Baixo Risco', value: 78, color: '#22c55e' },
    { name: 'Médio Risco', value: 18, color: '#f59e0b' },
    { name: 'Alto Risco', value: 4, color: '#ef4444' }
  ], [])

  const initialActivities = useMemo(() => [
    {
      id: 1,
      type: 'customer',
      message: 'Novo cliente cadastrado: João Silva',
      time: '5 min atrás',
      status: 'success'
    },
    {
      id: 2,
      type: 'screening',
      message: 'Screening concluído para Maria Santos',
      time: '12 min atrás',
      status: 'success'
    },
    {
      id: 3,
      type: 'alert',
      message: 'Alerta de alto risco: Pedro Costa',
      time: '25 min atrás',
      status: 'warning'
    },
    {
      id: 4,
      type: 'document',
      message: 'Documento processado: RG - Ana Lima',
      time: '1 hora atrás',
      status: 'success'
    }
  ], [])

  const [stats, setStats] = useState(initialStats)
  const [recentActivities, setRecentActivities] = useState(initialActivities)
  const [loading, setLoading] = useState(false)

  // Memoized fetch function to prevent infinite re-renders
  const fetchDashboardData = useCallback(async () => {
    if (loading) return // Prevent multiple simultaneous requests
    
    setLoading(true)
    try {
      // Simulate API call - replace with actual API endpoint
      const response = await fetch('/api/dashboard/stats')
      if (response.ok) {
        const data = await response.json()
        setStats(prevStats => ({ ...prevStats, ...data.stats }))
        setRecentActivities(data.activities || initialActivities)
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
      // Keep existing data on error
    } finally {
      setLoading(false)
    }
  }, [loading, initialActivities])

  // Use effect with proper dependencies
  useEffect(() => {
    fetchDashboardData()
    
    // Set up periodic refresh (every 5 minutes)
    const interval = setInterval(fetchDashboardData, 5 * 60 * 1000)
    
    return () => clearInterval(interval)
  }, [fetchDashboardData])

  // Memoized components to prevent unnecessary re-renders
  const StatsCards = useMemo(() => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <Card className="glass-effect">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total de Clientes</CardTitle>
          <Users className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.totalCustomers.toLocaleString()}</div>
          <p className="text-xs text-muted-foreground">
            <span className="text-green-600">+12%</span> em relação ao mês anterior
          </p>
        </CardContent>
      </Card>

      <Card className="glass-effect">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Documentos Pendentes</CardTitle>
          <FileText className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.pendingDocuments}</div>
          <p className="text-xs text-muted-foreground">
            <span className="text-orange-600">-5%</span> em relação a ontem
          </p>
        </CardContent>
      </Card>

      <Card className="glass-effect">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Screenings Ativos</CardTitle>
          <Shield className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.activeScreenings}</div>
          <p className="text-xs text-muted-foreground">
            Em processamento
          </p>
        </CardContent>
      </Card>

      <Card className="glass-effect">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Alertas de Alto Risco</CardTitle>
          <AlertTriangle className="h-4 w-4 text-destructive" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-destructive">{stats.highRiskAlerts}</div>
          <p className="text-xs text-muted-foreground">
            Requer atenção imediata
          </p>
        </CardContent>
      </Card>
    </div>
  ), [stats])

  const Charts = useMemo(() => (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card className="glass-effect">
        <CardHeader>
          <CardTitle>Atividade Mensal</CardTitle>
          <CardDescription>Clientes cadastrados e screenings realizados</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="customers" fill="oklch(0.35 0.15 240)" name="Clientes" />
              <Bar dataKey="screenings" fill="oklch(0.25 0.18 45)" name="Screenings" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card className="glass-effect">
        <CardHeader>
          <CardTitle>Distribuição de Risco</CardTitle>
          <CardDescription>Classificação dos clientes por nível de risco</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={riskData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {riskData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  ), [chartData, riskData])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gradient">Dashboard</h1>
        <p className="text-muted-foreground">Visão geral do sistema de compliance</p>
      </div>

      {/* Stats Cards */}
      {StatsCards}

      {/* Charts */}
      {Charts}

      {/* Recent Activities and Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="glass-effect">
          <CardHeader>
            <CardTitle>Atividades Recentes</CardTitle>
            <CardDescription>Últimas ações no sistema</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivities.map((activity) => (
                <div key={activity.id} className="flex items-center space-x-3">
                  <div className={`w-2 h-2 rounded-full ${
                    activity.status === 'success' ? 'bg-green-500' :
                    activity.status === 'warning' ? 'bg-orange-500' : 'bg-red-500'
                  }`} />
                  <div className="flex-1">
                    <p className="text-sm font-medium">{activity.message}</p>
                    <p className="text-xs text-muted-foreground">{activity.time}</p>
                  </div>
                  {activity.status === 'success' && <CheckCircle className="w-4 h-4 text-green-500" />}
                  {activity.status === 'warning' && <AlertTriangle className="w-4 h-4 text-orange-500" />}
                  {activity.status === 'error' && <XCircle className="w-4 h-4 text-red-500" />}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="glass-effect">
          <CardHeader>
            <CardTitle>Ações Rápidas</CardTitle>
            <CardDescription>Acesso rápido às funcionalidades principais</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <Button className="h-20 flex flex-col items-center justify-center space-y-2">
                <Users className="w-6 h-6" />
                <span className="text-sm">Novo Cliente</span>
              </Button>
              <Button variant="outline" className="h-20 flex flex-col items-center justify-center space-y-2">
                <Shield className="w-6 h-6" />
                <span className="text-sm">Screening</span>
              </Button>
              <Button variant="outline" className="h-20 flex flex-col items-center justify-center space-y-2">
                <FileText className="w-6 h-6" />
                <span className="text-sm">Documentos</span>
              </Button>
              <Button variant="outline" className="h-20 flex flex-col items-center justify-center space-y-2">
                <TrendingUp className="w-6 h-6" />
                <span className="text-sm">Relatórios</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="glass-effect">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Processados Hoje</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.completedToday}</div>
            <p className="text-xs text-muted-foreground">
              Clientes processados nas últimas 24h
            </p>
          </CardContent>
        </Card>

        <Card className="glass-effect">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tempo Médio</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.processingTime}</div>
            <p className="text-xs text-muted-foreground">
              Por processo de screening
            </p>
          </CardContent>
        </Card>

        <Card className="glass-effect">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Taxa de Sucesso</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">98.7%</div>
            <p className="text-xs text-muted-foreground">
              Processos concluídos com sucesso
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default DashboardPage

