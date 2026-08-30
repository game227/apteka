import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { RoleGuard } from './components/RoleGuard'
import { AuthProvider } from './context/AuthContext'
import { AdminPanelPage } from './pages/AdminPanelPage'
import { DrugPricesPage } from './pages/DrugPricesPage'
import { LoginPage } from './pages/LoginPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { PharmacyPanelPage } from './pages/PharmacyPanelPage'
import { PrescriptionUploadPage } from './pages/PrescriptionUploadPage'
import { SearchPage } from './pages/SearchPage'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<SearchPage />} />
            <Route path="/dorilar/:drugId" element={<DrugPricesPage />} />
            <Route path="/retsept" element={<PrescriptionUploadPage />} />
            <Route path="/kirish" element={<LoginPage />} />
            <Route
              path="/dorixona"
              element={
                <RoleGuard allow={['pharmacy_staff']}>
                  <PharmacyPanelPage />
                </RoleGuard>
              }
            />
            <Route
              path="/admin"
              element={
                <RoleGuard allow={['admin']}>
                  <AdminPanelPage />
                </RoleGuard>
              }
            />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
