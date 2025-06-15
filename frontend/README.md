# CERES Frontend

Modern React dashboard for the CERES compliance and risk management system.

## 🚀 Quick Start

### Development
```bash
npm install --legacy-peer-deps
npm run dev
```

### Production Build
```bash
npm run build
npm run preview
```

## 🌐 Deploy Options

### Option 1: Vercel (Recommended)
1. Connect your GitHub repository to Vercel
2. Set root directory to `frontend`
3. Build command: `npm run build`
4. Output directory: `dist`
5. Environment variables will be loaded from `vercel.json`

**Deploy URL**: `https://ceres-frontend.vercel.app`

### Option 2: Netlify
1. Connect your GitHub repository to Netlify
2. Set base directory to `frontend`
3. Build command: `npm run build`
4. Publish directory: `dist`
5. Configuration loaded from `netlify.toml`

**Deploy URL**: `https://ceres-frontend.netlify.app`

### Option 3: Railway
1. Create new project on Railway
2. Connect GitHub repository
3. Set root directory to `frontend`
4. Configuration loaded from `railway.json`

**Deploy URL**: `https://ceres-frontend.up.railway.app`

## 🔧 Configuration

### Environment Variables
- `VITE_API_BASE_URL`: Backend API base URL
- `VITE_API_AUTH_URL`: Authentication API URL
- `VITE_APP_NAME`: Application name
- `VITE_APP_VERSION`: Application version
- `VITE_APP_ENVIRONMENT`: Environment (development/production)

### API Connection
The frontend connects to the CERES backend API:
- **Production**: `https://ceres-production-8d0c.up.railway.app/api/v1`
- **Development**: `http://localhost:8000/api/v1`

## 📱 Features

### Pages
- **Dashboard**: Overview with metrics and charts
- **Enrollment**: Customer registration and management
- **Documents**: Document processing and management
- **Screening**: Sanctions screening and compliance
- **Reports**: Analytics and reporting
- **Settings**: System configuration

### Components
- Modern UI with Radix UI components
- Responsive design (mobile-friendly)
- Dark/light theme support
- Multi-language support (EN/PT-BR)
- Real-time notifications
- Interactive charts and graphs

### Authentication
- JWT-based authentication
- Automatic token refresh
- Protected routes
- Role-based access control

## 🛠️ Tech Stack

- **Framework**: React 18 + Vite
- **UI Library**: Radix UI + Tailwind CSS
- **Charts**: Recharts
- **Forms**: React Hook Form + Zod
- **Routing**: React Router
- **HTTP Client**: Fetch API with custom service
- **State Management**: React Context
- **Icons**: Lucide React

## 📦 Build Output

After running `npm run build`, the following files are generated:
- `dist/index.html` - Main HTML file
- `dist/assets/` - CSS, JS, and other assets
- Total size: ~1MB (gzipped: ~300KB)

## 🔍 Troubleshooting

### Build Issues
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps

# Clear Vite cache
rm -rf .vite
npm run build
```

### API Connection Issues
1. Check environment variables
2. Verify backend is running
3. Check CORS configuration
4. Verify API endpoints in browser dev tools

### Deploy Issues
1. Ensure build completes successfully
2. Check environment variables on platform
3. Verify routing configuration
4. Check platform-specific logs

## 📚 Documentation

- [API Documentation](https://ceres-production-8d0c.up.railway.app/api/docs/)
- [Component Library](./src/components/ui/)
- [Configuration Guide](./src/config/)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## 📄 License

This project is part of the CERES compliance system.

