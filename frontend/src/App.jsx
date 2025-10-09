import React, { useEffect, useRef, useState } from "react";
import axios from "axios";
import "./App.css";

const API_BASE = import.meta?.env?.VITE_API_URL || "http://localhost:8000";
const ENDPOINT = `${API_BASE}/api/colorize`;

function BeforeAfter({ beforeSrc, afterSrc }) {
  const [pos, setPos] = useState(50);
  return (
    <div className="ba">
      <img className="ba-img ba-after" src={afterSrc} alt="after" />
      <div className="ba-clip" style={{ width: `${pos}%` }}>
        <img className="ba-img ba-before" src={beforeSrc} alt="before" />
      </div>
      <input
        className="ba-range"
        type="range"
        min="0"
        max="100"
        value={pos}
        onChange={(e) => setPos(+e.target.value)}
        aria-label="Compare before/after"
      />
    </div>
  );
}

export default function App() {
  const [file, setFile] = useState(null);
  const [previewLocal, setPreviewLocal] = useState("");
  const [result, setResult] = useState(null); // { preview_url, download_url }
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  const dropRef = useRef(null);
  const fileInputRef = useRef(null);

  // drag & drop
  useEffect(() => {
    const el = dropRef.current;
    if (!el) return;
    const stop = (e) => { e.preventDefault(); e.stopPropagation(); };
    const onDrop = (e) => {
      stop(e);
      const f = e.dataTransfer?.files?.[0];
      if (f) handleFile(f);
      el.classList.remove("drop-hover");
    };
    const onOver  = (e) => { stop(e); el.classList.add("drop-hover"); };
    const onLeave = (e) => { stop(e); el.classList.remove("drop-hover"); };

    el.addEventListener("dragover", onOver);
    el.addEventListener("dragleave", onLeave);
    el.addEventListener("drop", onDrop);
    ["dragenter","dragover","dragleave","drop"].forEach(ev => window.addEventListener(ev, stop));
    return () => {
      el.removeEventListener("dragover", onOver);
      el.removeEventListener("dragleave", onLeave);
      el.removeEventListener("drop", onDrop);
      ["dragenter","dragover","dragleave","drop"].forEach(ev => window.removeEventListener(ev, stop));
    };
  }, []);

  const handleFile = (f) => {
    if (!f.type.startsWith("image/")) return setError("Загрузите изображение (JPG/PNG/WebP).");
    if (f.size > 15 * 1024 * 1024) return setError("Файл слишком большой (макс. 15 MB).");
    setError(null);
    setFile(f);
    setResult(null);
    setPreviewLocal(URL.createObjectURL(f));
  };

  const handleFileChange = (e) => {
    const f = e.target.files?.[0];
    if (f) handleFile(f);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) { setError("Выберите файл"); return; }

    setLoading(true);
    setProgress(0);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await axios.post(ENDPOINT, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 120000,
        onUploadProgress: (p) => {
          if (!p.total) return;
          setProgress(Math.round((p.loaded * 100) / p.total));
        },
      });
      setResult(res.data);
    } catch (err) {
      const msg = err?.response?.data?.detail || err?.message || "Не удалось обработать изображение";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const afterUrl = result ? `${API_BASE}${result.preview_url}` : "";
  const downloadUrl = result ? `${API_BASE}${result.download_url}` : "";

  return (
    <div className="page">
      {/* фон под стеклом */}
      <div className="bg-grid" aria-hidden />
      <div className="orbs" aria-hidden>
        <span className="orb orb-a" />
        <span className="orb orb-b" />
        <span className="orb orb-c" />
      </div>

      <div className="container">
        <header className="hdr">
          <div className="brand">
            <span className="logo-dot" />
            ColorAIze
          </div>
        </header>

        <main className="main">
          <section className="hero">
            <h1 className="hero-title">Колоризация чёрно-белых фото</h1>
            <p className="sub">Загрузите снимок — получите восстановление цвета с помощью ML.</p>
          </section>

          {/* Стеклянная карточка с фиксированным stage */}
          <section className="card glass">
            <span className="glass-border" aria-hidden />

            {!previewLocal ? (
              <div className="stack">
                {/* FIXED stage: drop-зона всегда одного размера */}
                <div
                  className="stage dropzone"
                  ref={dropRef}
                  role="button"
                  tabIndex={0}
                  aria-label="Перетащите изображение или нажмите, чтобы выбрать файл"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <div className="dz-graphic" aria-hidden>
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none">
                      <path d="M6 14.5a4 4 0 0 1 1.2-7.8 5.5 5.5 0 0 1 10.7 1.6 3.8 3.8 0 0 1 3.1 3.7c0 2.1-1.7 3.8-3.8 3.8H6.8"
                            stroke="url(#gcloud)" strokeWidth="1.6" opacity=".9" />
                      <defs>
                        <linearGradient id="gcloud" x1="2" y1="6" x2="22" y2="18">
                          <stop stopColor="#2bd3ff"/><stop offset="1" stopColor="#7cff6e"/>
                        </linearGradient>
                      </defs>
                    </svg>
                  </div>
                  <span className="sr-only">Перетащите изображение или нажмите для выбора</span>
                </div>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  hidden
                  onChange={handleFileChange}
                />

                <div className="actions">
                  <label className="btn primary">
                    Выбрать файл
                    <input type="file" accept="image/*" hidden onChange={handleFileChange} />
                  </label>
                </div>
              </div>
            ) : (
              <form className="preview" onSubmit={handleSubmit}>
                {/* FIXED stage: превью не меняет размер карточки */}
                <div className="stage">
                  <img className="stage-img" src={previewLocal} alt="preview" />
                </div>
                <div className="row">
                  <label className="btn secondary">
                    Заменить
                    <input type="file" accept="image/*" hidden onChange={handleFileChange} />
                  </label>
                  <button className="btn primary" type="submit" disabled={loading}>
                    {loading ? "Обработка…" : "Раскрасить"}
                  </button>
                </div>

                {loading && (
                  <div className="progress">
                    <div className="bar" style={{ width: `${progress}%` }} />
                    <span>{progress}%</span>
                  </div>
                )}
              </form>
            )}

            {!!error && <div className="error">{error}</div>}
          </section>

          {previewLocal && (
            <section className="result">
              {loading && (
                <div className="loading">
                  <div className="spinner" />
                  <div className="load-hint">Цветизируем изображение…</div>
                </div>
              )}
              {result && !loading && (
                <>
                  <BeforeAfter beforeSrc={previewLocal} afterSrc={afterUrl} />
                  <a className="btn primary dl" href={downloadUrl} download>
                    Скачать результат
                  </a>
                </>
              )}
            </section>
          )}
        </main>

        <footer className="ftr">© {new Date().getFullYear()} ColorAIze</footer>
      </div>
    </div>
  );
}