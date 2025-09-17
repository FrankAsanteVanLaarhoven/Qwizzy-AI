# Railway Deployment

1. Create a new Railway project → Deploy from GitHub → select Qwizzy-AI.
2. Variables:
   - PORT: provided by Railway automatically
   - CLOUD_DEPLOYMENT=1
3. Build & Start Commands:
   - Build: pip install -r requirements.txt
   - Start: gunicorn -w 2 -k gthread -t 120 -b 0.0.0.0: wsgi:app
4. After deploy, copy the public URL and update vercel.json proxy target, then redeploy Vercel.
