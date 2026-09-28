"use client";

import React, { useState } from "react";

interface FlaggedTweet {
  id: string;
  text: string;
  created_at: string;
  category: string;
  confidence: number;
  reason: string;
  tweet_url: string;
}

const PERSONAS = [
  { id: "corporate", label: "Corporate & Recruiter", desc: "Flags rants, profanity, and career hazards." },
  { id: "anti_cringe", label: "Anti-Cringe", desc: "Flags teenage melodrama, oversharing, and edge." },
  { id: "naija_street", label: "Naija Banter Safe", desc: "Protects pidgin & banter; flags scams, hate, and threats." },
  { id: "sfw", label: "Safe For Work", desc: "Strict filter on explicit, vulgar, or adult content." },
  { id: "clumsy_takes", label: "Clumsy Hot Takes", desc: "Catches bad takes and arguments that aged poorly." },
];

export default function AuditPage() {
  const [file, setFile] = useState<File | null>(null);
  const [selectedPersona, setSelectedPersona] = useState<string>("corporate");
  const [sampleLimit, setSampleLimit] = useState<number>(10);
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [results, setResults] = useState<{
    totalAudited: number;
    totalFlagged: number;
    tweets: FlaggedTweet[];
  } | null>(null);

  // Validate and store the uploaded tweets.js file
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setErrorMessage("");
    if (e.target.files && e.target.files[0]) {
      const chosenFile = e.target.files[0];
      if (!chosenFile.name.endsWith(".js") && !chosenFile.name.endsWith(".json")) {
        setErrorMessage("Please select only the extracted 'tweets.js' file from your archive.");
        return;
      }
      setFile(chosenFile);
    }
  };

  // Send the file and persona selection to the backend API
  const handleStartAudit = async () => {
    if (!file) {
      setErrorMessage("Please select your tweets.js file first.");
      return;
    }

    setLoading(true);
    setErrorMessage("");
    setResults(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("persona", selectedPersona);
    formData.append("limit", sampleLimit.toString());

    try {
      const response = await fetch("http://127.0.0.1:8000/api/audit", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setResults({
        totalAudited: data.total_audited,
        totalFlagged: data.total_flagged,
        tweets: data.flagged_tweets || [],
      });
    } catch (err: any) {
      setErrorMessage(
        err.message || "Failed to reach backend. Make sure your FastAPI server is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  // Export flagged tweets directly into a downloadable CSV
  const handleDownloadCSV = () => {
    if (!results || results.tweets.length === 0) return;

    const headers = ["tweet_id", "tweet_url", "category", "confidence", "reason", "tweet_text"];
    const rows = results.tweets.map((t) => [
      `"${t.id}"`,
      `"${t.tweet_url}"`,
      `"${t.category}"`,
      t.confidence,
      `"${t.reason.replace(/"/g, '""')}"`,
      `"${t.text.replace(/"/g, '""')}"`,
    ]);

    const csvContent = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `flagged_tweets_${selectedPersona}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 py-10 px-4 sm:px-8">
      <div className="max-w-3xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="text-center space-y-2">
          <span className="inline-block bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs px-3 py-1 rounded-full font-medium">
            Free Local Testing Mode
          </span>
          <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
            TweetAudit
          </h1>
          <p className="text-slate-400 text-sm sm:text-base">
            Upload only your extracted <code className="text-emerald-400 font-mono">data/tweets.js</code> file to audit posts against custom personas.
          </p>
        </div>

        {/* Step 1: Upload Box */}
        <section className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-md space-y-3">
          <label className="block text-sm font-semibold text-slate-300">
            1. Select your tweets.js file
          </label>
          <div className="border-2 border-dashed border-slate-800 hover:border-slate-700 transition rounded-lg p-6 text-center bg-slate-950/50 cursor-pointer relative">
            <input
              type="file"
              accept=".js,.json"
              onChange={handleFileChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <div className="text-sm font-medium text-slate-200">
              {file ? file.name : "Click here or drop your tweets.js file"}
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Supports <code className="text-slate-400">tweets.js</code> directly from your unzipped archive.
            </p>
          </div>
          {errorMessage && (
            <p className="text-xs text-red-400 font-medium pt-1">{errorMessage}</p>
          )}
        </section>

        {/* Step 2: Persona Selection */}
        <section className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-md space-y-4">
          <div className="flex justify-between items-center">
            <label className="block text-sm font-semibold text-slate-300">
              2. Select Audit Persona
            </label>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span>Test batch limit:</span>
              <select
                value={sampleLimit}
                onChange={(e) => setSampleLimit(Number(e.target.value))}
                className="bg-slate-800 border border-slate-700 text-slate-200 rounded px-2 py-1"
              >
                <option value={5}>5 Tweets</option>
                <option value={10}>10 Tweets</option>
                <option value={20}>20 Tweets</option>
                <option value={50}>50 Tweets</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {PERSONAS.map((item) => {
              const isSelected = selectedPersona === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setSelectedPersona(item.id)}
                  className={`text-left p-4 rounded-lg border transition ${
                    isSelected
                      ? "border-emerald-500 bg-emerald-950/30 text-white"
                      : "border-slate-800 bg-slate-950/40 text-slate-400 hover:border-slate-700"
                  }`}
                >
                  <div className="font-semibold text-sm mb-1 text-slate-200">{item.label}</div>
                  <div className="text-xs text-slate-400 leading-relaxed">{item.desc}</div>
                </button>
              );
            })}
          </div>
        </section>

        {/* Start Button */}
        <button
          onClick={handleStartAudit}
          disabled={!file || loading}
          className="w-full py-3.5 px-6 rounded-xl font-semibold bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed transition text-white shadow-lg"
        >
          {loading ? "Auditing Posts..." : `Start Free Audit (${sampleLimit} Tweets)`}
        </button>

        {/* Results Section */}
        {results && (
          <section className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-md space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
              <div>
                <h2 className="text-lg font-bold text-white">Audit Complete</h2>
                <p className="text-xs text-slate-400">
                  Scanned {results.totalAudited} tweets | Flagged {results.totalFlagged} for deletion
                </p>
              </div>

              {results.tweets.length > 0 && (
                <button
                  onClick={handleDownloadCSV}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-4 py-2 rounded-lg transition"
                >
                  Download Cleanup CSV
                </button>
              )}
            </div>

            {results.tweets.length === 0 ? (
              <p className="text-sm text-slate-400 py-4 text-center">
                No tweets were flagged under this persona.
              </p>
            ) : (
              <div className="space-y-3">
                {results.tweets.map((tweet) => (
                  <div key={tweet.id} className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-red-400 uppercase tracking-wider">
                        {tweet.category}
                      </span>
                      <a
                        href={tweet.tweet_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-slate-500 hover:text-slate-300 underline"
                      >
                        View Post
                      </a>
                    </div>
                    <p className="text-sm text-slate-200">"{tweet.text}"</p>
                    <p className="text-xs text-slate-400">
                      <span className="font-semibold text-slate-300">Reason:</span> {tweet.reason}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

      </div>
    </main>
  );
}