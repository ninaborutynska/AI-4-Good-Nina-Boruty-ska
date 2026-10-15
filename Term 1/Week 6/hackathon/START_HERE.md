# Start the submitted app

Project authors: Luuk and Nina.

This package contains the Next.js app, Python analysis source, tests, documentation,
presentation and a real saved dataset. It contains no personal access token.

## Run the dashboard

Install Node.js 22 or newer (including npm). Extract the entire ZIP first.
Open PowerShell in the extracted `Hackathon 6` folder and run:

```powershell
cd dashboard
npm.cmd ci
Copy-Item .env.example .env.local
npm.cmd run build
cd ..
& .\start-dashboard.ps1
```

Open http://localhost:3101 and http://localhost:3101/evaluation.
If PowerShell blocks scripts, start directly from the dashboard folder instead:

```powershell
npm.cmd run start
```

Internet is required to install dependencies. The packaged dashboard then reads
the included CSVs locally and requires no GitHub token or Python inference.
The data is a fixed snapshot synchronized at 2026-10-15T15:01:40.901985+00:00.
It is not a live feed. The original cloud collection operates independently.
The README explains optional live connection and Python analysis setup.

Use the walkthrough in README.md to demonstrate filters, source comments and
the human-label evaluation. The presentation is in outputs/presentation.
The collector itself is hosted in LuukAalders/Hackathons; this ZIP contains the
local app and analysis source, not a separate running cloud collector.
