# Claude Desktop Integration Guide

## After Cloud Deployment

Once your HyperLiquid MCP server is deployed to the cloud, follow these steps to connect it to Claude Desktop.

## Step 1: Get Your Cloud URL

After deploying to your chosen cloud provider, you'll get a public URL like:
- Railway: `https://your-app.up.railway.app`
- Render: `https://your-app.onrender.com`
- DigitalOcean: `https://your-app.ondigitalocean.app`
- Google Cloud Run: `https://your-app-xxxxx.run.app`

## Step 2: Test Your Deployment

First, verify your server is running:

```bash
curl https://YOUR-CLOUD-URL/health
```

You should see:
```json
{"status": "ok", "service": "hyperliquid-mcp"}
```

## Step 3: Configure Claude Desktop

### Find Your Config File

**Windows:**
```
C:\Users\YOUR_USERNAME\AppData\Roaming\Claude\claude_desktop_config.json
```

**Mac:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### Add MCP Server Configuration

Edit the `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "hyperliquid-trader": {
      "url": "https://YOUR-CLOUD-URL",
      "transport": {
        "type": "http",
        "headers": {
          "X-API-Key": "YOUR-SECRET-API-KEY"
        }
      }
    }
  }
}
```

### Alternative Configuration (Using NPX)

If you prefer using the MCP client:

```json
{
  "mcpServers": {
    "hyperliquid-trader": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/client-http",
        "https://YOUR-CLOUD-URL"
      ],
      "env": {
        "API_KEY": "YOUR-SECRET-API-KEY"
      }
    }
  }
}
```

## Step 4: Restart Claude Desktop

After saving the configuration:
1. Completely quit Claude Desktop (not just close the window)
2. Restart Claude Desktop
3. Check the MCP connection icon in Claude Desktop

## Step 5: Test in Claude Desktop

Try these commands in Claude:

```
"What's my HyperLiquid account balance?"
"Show me my open positions"
"What's the current BTC price?"
```

## Mobile Access

### On iOS/Android:

1. **Using Claude Desktop Web Version:**
   - Access Claude Desktop through your mobile browser
   - The MCP server connection will work automatically

2. **Using Claude Mobile App:**
   - Currently, the Claude mobile app doesn't support MCP servers
   - Use the web version for trading functionality

## Security Configuration

### Basic Setup (Development)

For testing, deploy without authentication:

**.env file:**
```env
REQUIRE_AUTH=false
```

### Production Setup (Recommended)

Enable API authentication:

**.env file:**
```env
REQUIRE_AUTH=true
API_KEY=your-very-long-random-api-key-here
RATE_LIMIT=60
```

Generate a secure API key:
```bash
# Linux/Mac
openssl rand -hex 32

# Windows PowerShell
-join ((1..32) | ForEach {'{0:X}' -f (Get-Random -Max 256)})
```

## Troubleshooting

### Server Not Responding

1. Check server logs:
   ```bash
   # Railway
   railway logs
   
   # Docker
   docker logs hyperliquid-mcp
   ```

2. Verify environment variables are set correctly

3. Check firewall/security group allows port 8080

### Claude Desktop Not Connecting

1. Check Claude Desktop logs:
   - Windows: `%APPDATA%\Claude\logs`
   - Mac: `~/Library/Logs/Claude`

2. Verify JSON syntax in config file

3. Try the test command:
   ```bash
   npx @modelcontextprotocol/client-http https://YOUR-CLOUD-URL/health
   ```

### Authentication Issues

1. Verify API key matches in both .env and claude_desktop_config.json

2. Test with curl:
   ```bash
   curl -H "X-API-Key: YOUR-API-KEY" https://YOUR-CLOUD-URL/health
   ```

## Advanced Features

### Using Multiple Accounts

Deploy multiple instances with different configs:

```json
{
  "mcpServers": {
    "hyperliquid-main": {
      "url": "https://main-account.railway.app",
      "transport": {
        "type": "http",
        "headers": {"X-API-Key": "KEY1"}
      }
    },
    "hyperliquid-test": {
      "url": "https://test-account.railway.app",
      "transport": {
        "type": "http",
        "headers": {"X-API-Key": "KEY2"}
      }
    }
  }
}
```

### Custom Commands in Claude

You can create aliases in Claude:

"When I say 'check my positions', use the hyperliquid-trader to get my open positions and format them nicely"

"When I say 'quick buy [SYMBOL] $[AMOUNT]', use hyperliquid-trader to open a market buy position"

## Monitoring Your Server

### Add Uptime Monitoring

Use services like:
- UptimeRobot (free)
- Pingdom
- Better Uptime

Monitor endpoint: `https://YOUR-CLOUD-URL/health`

### View Logs

Most cloud providers offer log viewing:
- Railway: `railway logs`
- Render: Dashboard → Logs
- DigitalOcean: App Platform → Runtime Logs

## Example Trading Commands

Once connected, you can ask Claude:

### Account Management
- "What's my current balance?"
- "Show me all my open positions"
- "What's my total PnL?"

### Trading
- "Buy $1000 worth of BTC with 10x leverage"
- "Close my ETH position"
- "Set a stop loss at $3000 for my BTC position"

### Market Data
- "What's the current price of SOL?"
- "Show me the order book for DOGE"
- "What's the funding rate for BTC?"

### Order Management
- "Cancel all my open orders"
- "Place a limit buy order for ETH at $2000"
- "Show me my order history"

## Cost Optimization

### Free Tier Options

1. **Railway**: 500 hours free/month
2. **Render**: 750 hours free/month
3. **Google Cloud Run**: 2 million requests free/month

### Reducing Costs

1. Use serverless (Cloud Run, Lambda)
2. Enable auto-sleep on idle
3. Use smaller instance sizes
4. Implement caching

## Support

For issues:
1. Check server logs
2. Verify environment variables
3. Test endpoints with curl
4. Review Claude Desktop logs

Remember to NEVER share your private keys or API keys publicly!