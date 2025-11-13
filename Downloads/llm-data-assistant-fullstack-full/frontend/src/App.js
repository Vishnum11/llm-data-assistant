import React, { useState, useEffect } from "react";
import axios from "axios";
const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000";
function App() {
  const [token, setToken] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [projects, setProjects] = useState([]);
  const [projName, setProjName] = useState("");
  const [selectedProject, setSelectedProject] = useState(null);
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [chatResp, setChatResp] = useState(null);
  const authHeader = () => ({ Authorization: `Bearer ${token}` });
  const register = async () => {
    try {
      const resp = await axios.post(`${API_BASE}/register`, null, { params: { username, password }});
      setToken(resp.data.access_token);
      alert("Registered and logged in");
    } catch (e) { alert("Register error: " + e.response?.data?.detail || e.message); }
  };
  const login = async () => {
    try {
      const params = new URLSearchParams();
      params.append("username", username);
      params.append("password", password);
      const resp = await axios.post(`${API_BASE}/token`, params);
      setToken(resp.data.access_token);
      alert("Logged in");
    } catch (e) { alert("Login error: " + e.response?.data?.detail || e.message); }
  };
  const fetchProjects = async () => {
    try { const resp = await axios.get(`${API_BASE}/projects`, { headers: authHeader() }); setProjects(resp.data); }
    catch (e) { console.error(e); }
  };
  useEffect(() => { if (token) fetchProjects(); }, [token]);
  const createProject = async () => {
    try {
      const resp = await axios.post(`${API_BASE}/projects`, null, { params: { name: projName, description: "" }, headers: authHeader() });
      setProjects([...projects, resp.data]);
      setProjName("");
    } catch (e) { alert("Error creating project: " + e.message); }
  };
  const uploadFile = async () => {
    if (!selectedProject || !file) { alert("Choose project and file"); return; }
    const fd = new FormData();
    fd.append("file", file);
    try {
      const resp = await axios.post(`${API_BASE}/projects/${selectedProject.id}/upload`, fd, { headers: {...authHeader(), "Content-Type": "multipart/form-data"}});
      alert("Ingested: " + JSON.stringify(resp.data.ingest));
    } catch (e) { alert("Upload error: " + e.response?.data?.detail || e.message); }
  };
  const askQuestion = async () => {
    if (!selectedProject) { alert("Select project"); return; }
    try {
      const resp = await axios.post(`${API_BASE}/projects/${selectedProject.id}/query`, null, { params: { question }, headers: authHeader() });
      setChatResp(resp.data);
    } catch (e) { alert("Query error: " + e.response?.data?.detail || e.message); }
  };
  return (
    <div style={{ padding: 20 }}>
      <h1>LLM Data Assistant (Fullstack)</h1>
      <section style={{ border: "1px solid #ddd", padding: 10, marginBottom: 10 }}>
        <h3>Auth</h3>
        <input placeholder="username" value={username} onChange={e=>setUsername(e.target.value)} />
        <input placeholder="password" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        <button onClick={register}>Register</button>
        <button onClick={login}>Login</button>
      </section>
      <section style={{ border: "1px solid #ddd", padding: 10, marginBottom: 10 }}>
        <h3>Projects</h3>
        <input placeholder="project name" value={projName} onChange={e=>setProjName(e.target.value)} />
        <button onClick={createProject}>Create</button>
        <div>
          {projects.map(p => (
            <div key={p.id} style={{ marginTop: 6 }}>
              <input type="radio" checked={selectedProject?.id === p.id} onChange={()=>setSelectedProject(p)} /> {p.name} (id:{p.id})
            </div>
          ))}
        </div>
      </section>
      <section style={{ border: "1px solid #ddd", padding: 10, marginBottom: 10 }}>
        <h3>Upload & Ingest</h3>
        <input type="file" onChange={e=>setFile(e.target.files[0])} />
        <button onClick={uploadFile}>Upload & Ingest</button>
      </section>
      <section style={{ border: "1px solid #ddd", padding: 10 }}>
        <h3>Chat</h3>
        <input placeholder="Ask a question" value={question} onChange={e=>setQuestion(e.target.value)} style={{ width: "60%" }} />
        <button onClick={askQuestion}>Ask</button>
        {chatResp && (
          <div style={{ marginTop: 10 }}>
            <h4>Answer</h4>
            <div>{chatResp.answer}</div>
            <h5>Source docs (metadata snippets)</h5>
            <pre>{JSON.stringify(chatResp.source_documents?.map(d => d.metadata || d), null, 2)}</pre>
          </div>
        )}
      </section>
    </div>
  );
}
export default App;
