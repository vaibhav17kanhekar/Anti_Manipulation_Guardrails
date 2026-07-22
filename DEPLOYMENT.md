# Render Deployment

This project is deployed as one Render web service. Flask serves the API and all HTML, CSS, and JavaScript pages from the same service.

## Deploy from GitHub

1. Open [render.com](https://render.com) and sign in.
2. Select **New +** and choose **Web Service**.
3. Connect the `vaibhav17kanhekar/Anti_Manipulation_Guardrails` GitHub repository.
4. Use these settings:

   - **Runtime:** Python
   - **Build command:** `pip install -r requirements-deploy.txt`
   - **Start command:** `gunicorn api:app --bind 0.0.0.0:$PORT`
   - **Plan:** Free

5. Select **Create Web Service**.

Render will build the application and provide one public URL for the dashboard, analysis page, batch experiments, results visualizations, and about page. Future pushes to `main` will trigger automatic redeployments.

## Optional API keys

The current web demo uses simulated responses and works without provider API keys. Do not commit `config/api_keys.yaml`. If provider-backed features are added later, configure their secrets in Render's **Environment** settings instead of storing them in the repository.

## Local production check

From the project root, run:

```powershell
$env:PORT = "10000"
gunicorn api:app --bind 0.0.0.0:$env:PORT
```

Then open `http://localhost:10000`.