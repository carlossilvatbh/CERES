import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Upload, 
  FileText, 
  Image, 
  CheckCircle, 
  AlertCircle, 
  Clock,
  Eye,
  Download,
  Trash2,
  Search
} from 'lucide-react'

const DocumentsPage = () => {
  const [documents] = useState([
    {
      id: 1,
      name: 'RG - João Silva',
      type: 'RG',
      customer: 'João Silva',
      status: 'processed',
      uploadDate: '2025-06-14',
      size: '2.3 MB',
      confidence: 98
    },
    {
      id: 2,
      name: 'CPF - Maria Santos',
      type: 'CPF',
      customer: 'Maria Santos',
      status: 'processing',
      uploadDate: '2025-06-14',
      size: '1.8 MB',
      confidence: null
    },
    {
      id: 3,
      name: 'Passaporte - Pedro Costa',
      type: 'Passport',
      customer: 'Pedro Costa',
      status: 'pending',
      uploadDate: '2025-06-13',
      size: '3.1 MB',
      confidence: null
    },
    {
      id: 4,
      name: 'CNH - Ana Lima',
      type: 'CNH',
      customer: 'Ana Lima',
      status: 'processed',
      uploadDate: '2025-06-13',
      size: '2.7 MB',
      confidence: 95
    },
    {
      id: 5,
      name: 'RG - Carlos Oliveira',
      type: 'RG',
      customer: 'Carlos Oliveira',
      status: 'error',
      uploadDate: '2025-06-12',
      size: '1.2 MB',
      confidence: null
    }
  ])

  const [searchTerm, setSearchTerm] = useState('')
  const [selectedTab, setSelectedTab] = useState('all')

  const getStatusBadge = (status) => {
    switch (status) {
      case 'processed':
        return <Badge className="bg-green-100 text-green-800">Processado</Badge>
      case 'processing':
        return <Badge className="bg-blue-100 text-blue-800">Processando</Badge>
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
      case 'processed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'processing':
        return <Clock className="w-5 h-5 text-blue-500" />
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />
      default:
        return <FileText className="w-5 h-5 text-gray-500" />
    }
  }

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.customer.toLowerCase().includes(searchTerm.toLowerCase())
    
    if (selectedTab === 'all') return matchesSearch
    return matchesSearch && doc.status === selectedTab
  })

  const stats = {
    total: documents.length,
    processed: documents.filter(d => d.status === 'processed').length,
    processing: documents.filter(d => d.status === 'processing').length,
    pending: documents.filter(d => d.status === 'pending').length,
    error: documents.filter(d => d.status === 'error').length
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gradient">Documentos</h1>
        <p className="text-muted-foreground">Gestão e processamento de documentos</p>
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
              <FileText className="w-8 h-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-effect">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Processados</p>
                <p className="text-2xl font-bold text-green-600">{stats.processed}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-effect">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Processando</p>
                <p className="text-2xl font-bold text-blue-600">{stats.processing}</p>
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
                <p className="text-sm font-medium text-muted-foreground">Erros</p>
                <p className="text-2xl font-bold text-red-600">{stats.error}</p>
              </div>
              <AlertCircle className="w-8 h-8 text-red-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Upload Section */}
      <Card className="glass-effect">
        <CardHeader>
          <CardTitle>Upload de Documentos</CardTitle>
          <CardDescription>Faça upload de documentos para processamento automático</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
            <Upload className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Arraste arquivos aqui ou clique para selecionar</h3>
            <p className="text-muted-foreground mb-4">Suporte para PDF, JPG, PNG (máx. 10MB)</p>
            <Button>
              <Upload className="w-4 h-4 mr-2" />
              Selecionar Arquivos
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Search and Filters */}
      <Card className="glass-effect">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="Buscar documentos..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Tabs value={selectedTab} onValueChange={setSelectedTab}>
              <TabsList>
                <TabsTrigger value="all">Todos</TabsTrigger>
                <TabsTrigger value="processed">Processados</TabsTrigger>
                <TabsTrigger value="processing">Processando</TabsTrigger>
                <TabsTrigger value="pending">Pendentes</TabsTrigger>
                <TabsTrigger value="error">Erros</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </CardContent>
      </Card>

      {/* Documents List */}
      <Card className="glass-effect">
        <CardHeader>
          <CardTitle>Lista de Documentos</CardTitle>
          <CardDescription>
            {filteredDocuments.length} documento(s) encontrado(s)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredDocuments.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors">
                <div className="flex items-center space-x-4">
                  {getStatusIcon(doc.status)}
                  <div>
                    <h4 className="font-medium">{doc.name}</h4>
                    <p className="text-sm text-muted-foreground">
                      Cliente: {doc.customer} • Tipo: {doc.type} • {doc.size}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Upload: {new Date(doc.uploadDate).toLocaleDateString('pt-BR')}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  {doc.confidence && (
                    <div className="text-right">
                      <p className="text-sm font-medium">Confiança: {doc.confidence}%</p>
                      <Progress value={doc.confidence} className="w-20" />
                    </div>
                  )}
                  
                  {getStatusBadge(doc.status)}
                  
                  <div className="flex space-x-2">
                    <Button variant="ghost" size="icon">
                      <Eye className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon">
                      <Download className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" className="text-destructive hover:text-destructive">
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Processing Queue */}
      <Card className="glass-effect">
        <CardHeader>
          <CardTitle>Fila de Processamento</CardTitle>
          <CardDescription>Status do processamento de documentos</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <Clock className="w-5 h-5 text-blue-500" />
                <div>
                  <p className="font-medium">OCR em andamento</p>
                  <p className="text-sm text-muted-foreground">CPF - Maria Santos</p>
                </div>
              </div>
              <Progress value={65} className="w-32" />
            </div>

            <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <Clock className="w-5 h-5 text-yellow-500" />
                <div>
                  <p className="font-medium">Aguardando processamento</p>
                  <p className="text-sm text-muted-foreground">Passaporte - Pedro Costa</p>
                </div>
              </div>
              <Badge variant="outline">Na fila</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default DocumentsPage

