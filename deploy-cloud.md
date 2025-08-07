# Cloud Deployment Guide for HyperLiquid MCP Server

## ⚠️ SECURITY WARNING
**NEVER commit your `.env` file with private keys to GitHub!** Always use environment variables or secrets management.

## Option 1: Deploy to Railway (Recommended - Easiest)

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and Initialize**:
   ```bash
   railway login
   railway init
   ```

3. **Set Environment Variables**:
   ```bash
   railway variables set HYPERLIQUID_PRIVATE_KEY=0x196018e7602e0bfdd6b2cfe466e9e9d8762dc40d58d10e726420e969d91447ed
   railway variables set HYPERLIQUID_ACCOUNT_ADDRESS=0xBD30A0Bb71B7Bb9ba0C2B8c6DdeAC689a6415625
   railway variables set HYPERLIQUID_TESTNET=false
   railway variables set PORT=8080
   railway variables set HOST=0.0.0.0
   ```

4. **Deploy**:
   ```bash
   railway up
   ```

5. **Get Your URL**:
   ```bash
   railway domain
   ```

## Option 2: Deploy to Render

1. **Create account** at https://render.com

2. **Connect GitHub** repository

3. **Create New Web Service**:
   - Environment: Docker
   - Region: Choose closest to you
   - Instance Type: Free tier works fine

4. **Environment Variables**:
   Add these in Render dashboard:
   - `HYPERLIQUID_PRIVATE_KEY`
   - `HYPERLIQUID_ACCOUNT_ADDRESS`
   - `HYPERLIQUID_TESTNET`
   - `PORT=8080`
   - `HOST=0.0.0.0`

5. **Deploy** - Automatic on git push

## Option 3: Deploy to DigitalOcean App Platform

1. **Install doctl**:
   ```bash
   # Windows (using scoop)
   scoop install doctl
   ```

2. **Authenticate**:
   ```bash
   doctl auth init
   ```

3. **Create app.yaml**:
   ```yaml
   name: hyperliquid-mcp
   services:
   - name: web
     dockerfile_path: Dockerfile
     source_dir: .
     http_port: 8080
     instance_size_slug: basic-xxs
     instance_count: 1
     envs:
     - key: HYPERLIQUID_PRIVATE_KEY
       value: "YOUR_KEY"
       type: SECRET
     - key: HYPERLIQUID_ACCOUNT_ADDRESS
       value: "YOUR_ADDRESS"
     - key: HYPERLIQUID_TESTNET
       value: "false"
   ```

4. **Deploy**:
   ```bash
   doctl apps create --spec app.yaml
   ```

## Option 4: Deploy to Google Cloud Run

1. **Install gcloud CLI** and authenticate

2. **Build and push to Google Container Registry**:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR-PROJECT-ID/hyperliquid-mcp
   ```

3. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy hyperliquid-mcp \
     --image gcr.io/YOUR-PROJECT-ID/hyperliquid-mcp \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars HYPERLIQUID_PRIVATE_KEY=YOUR_KEY,HYPERLIQUID_ACCOUNT_ADDRESS=YOUR_ADDRESS
   ```

## Option 5: Deploy to AWS (EC2 with Docker)

1. **Launch EC2 instance** (t2.micro for free tier)

2. **SSH into instance**:
   ```bash
   ssh -i your-key.pem ec2-user@your-instance-ip
   ```

3. **Install Docker**:
   ```bash
   sudo yum update -y
   sudo yum install docker -y
   sudo service docker start
   sudo usermod -a -G docker ec2-user
   ```

4. **Clone and deploy**:
   ```bash
   git clone https://github.com/landoskyy/landotrade.git
   cd landotrade
   
   # Create .env file with your credentials
   nano .env
   
   # Build and run
   docker-compose up -d
   ```

5. **Configure Security Group**:
   - Add inbound rule for port 8080

## Connecting to Claude Desktop

Once deployed, add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hyperliquid-trader": {
      "command": "curl",
      "args": ["https://YOUR-DEPLOYED-URL.com"],
      "env": {}
    }
  }
}
```

Or for better integration, use the MCP HTTP client:

```json
{
  "mcpServers": {
    "hyperliquid-trader": {
      "url": "https://YOUR-DEPLOYED-URL.com",
      "transport": "http"
    }
  }
}
```

## Mobile Access

Once deployed:
1. Access Claude Desktop on mobile via web browser
2. The MCP server will be available through your cloud URL
3. All trading functions accessible from anywhere

## Security Best Practices

1. **Use HTTPS** - Most cloud providers provide this automatically
2. **Add Authentication** - Consider adding API key authentication:
   ```python
   # In main.py, add:
   API_KEY = os.getenv("API_KEY")
   
   @app.middleware("http")
   async def auth_middleware(request, call_next):
       if request.headers.get("X-API-Key") != API_KEY:
           return JSONResponse(status_code=401, content={"error": "Unauthorized"})
       return await call_next(request)
   ```

3. **Rate Limiting** - Prevent abuse
4. **IP Whitelisting** - If using from fixed locations
5. **Use Secrets Management** - AWS Secrets Manager, Google Secret Manager, etc.

## Monitoring

Add health check endpoint (already included in main.py):
- `GET /health` - Returns server status

## Estimated Costs

- **Railway**: Free tier available, ~$5/month for hobby
- **Render**: Free tier available, ~$7/month for starter
- **DigitalOcean**: ~$5/month for basic droplet
- **Google Cloud Run**: Pay per request, ~$0-5/month for light use
- **AWS EC2**: Free tier for 1 year, then ~$5-10/month for t2.micro

## Quick Test

After deployment, test your endpoint:

```bash
curl https://YOUR-DEPLOYED-URL.com/health
```

Should return: `{"status": "ok"}`