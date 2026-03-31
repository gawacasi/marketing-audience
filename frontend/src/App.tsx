import { NavLink, Route, Routes } from "react-router-dom";
import CampaignDetailPage from "./pages/CampaignDetailPage";
import CampaignsPage from "./pages/CampaignsPage";
import UploadPage from "./pages/UploadPage";
import UsersPage from "./pages/UsersPage";

function App() {
  return (
    <div className="layout">
      <header className="header">
        <div className="brand">Marketing Audience Campaign Builder</div>
        <nav className="nav">
          <NavLink to="/" end>
            Upload
          </NavLink>
          <NavLink to="/campaigns">Campanhas</NavLink>
          <NavLink to="/users">Usuários</NavLink>
        </nav>
      </header>
      <main className="main">
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/campaigns" element={<CampaignsPage />} />
          <Route path="/campaigns/:id" element={<CampaignDetailPage />} />
          <Route path="/users" element={<UsersPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
