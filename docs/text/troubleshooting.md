# AuroraAI Troubleshooting Guide

## Common Issues & Fixes

### 1. Assistant Not Responding
**Symptoms:** Long delays or no output.

**Possible Causes & Fixes:**
- Network issue → Check VPN/firewall.
- Expired API key → Run `aurora auth refresh`.
- Large file uploads throttled → Compress or split files.

### 2. Incorrect or Irrelevant Answers
**Symptoms:** Hallucinations, outdated info.

**Fixes:**
- Re-index documentation: `aurora connect ./docs --force`.
## Troubleshooting Connection Issues

### Symptoms
- Failed API requests or timeouts
- Unable to connect to external services (GitHub, Jira, etc.)
- Network-related error messages

### Common Causes and Solutions

#### Network Connectivity
- **Check internet connection**: Verify your network is stable and accessible
- **Firewall settings**: Ensure Aurora is allowed through your firewall
- **Proxy configuration**: If behind a corporate proxy, configure proxy settings in Aurora's config file

#### DNS Resolution
- **Verify domain resolution**: Test connectivity to API endpoints using `ping` or `nslookup`
- **DNS cache**: Clear system DNS cache if experiencing intermittent issues
- **Alternative DNS**: Try switching to public DNS servers (e.g., 8.8.8.8)

#### SSL/TLS Errors
- **Certificate validation**: Update system certificates or use `--insecure` flag for testing only
- **Protocol version**: Ensure TLS 1.2+ is supported on your system
- **Corporate SSL inspection**: Request certificate authority (CA) certificate from IT if applicable

#### Timeout Issues
- **Increase timeout values**: Use `--timeout=60` flag to extend wait time
- **Check service status**: Verify third-party service availability at their status pages
- **Reduce payload size**: Break large requests into smaller batches

#### Debug Mode
Enable verbose logging to diagnose connection problems:
- Add explicit context to prompts.
- Enable strict retrieval with: `--retrieval=strict`.

### 3. Authentication Errors
| Code | Meaning | Fix |
|------|---------|------|
| 401 | Invalid token | Re-enter API key |
| 403 | Permission denied | Check role settings |
| 429 | Rate limit exceeded | Reduce request size or upgrade plan |

### 4. Integration Sync Failures
**Fixes:**
- Validate GitHub/Jira tokens.
- Re-auth via: `aurora integrate github --reset`.
- Clear cache: `aurora cache purge`.

### 5. Advanced Connection Diagnostics

#### Network Layer Analysis
**TCP/IP Stack Verification:**
- Run `netstat -an | grep ESTABLISHED` to check active connections
- Monitor packet loss: `ping -c 100 api.aurora.ai` and analyze statistics
- Use `traceroute api.aurora.ai` to identify routing bottlenecks
- Check MTU settings: `ping -M do -s 1472 api.aurora.ai` to test fragmentation

**Port Availability:**
- Verify required ports are open: 443 (HTTPS), 80 (HTTP fallback)
- Test with `telnet api.aurora.ai 443` or `nc -zv api.aurora.ai 443`
- Check for port conflicts: `lsof -i :443` (Linux/macOS) or `netstat -ano | findstr :443` (Windows)

#### Protocol-Level Debugging
**HTTP/HTTPS Traffic Inspection:**
- Capture traffic with `tcpdump -i any -w aurora.pcap host api.aurora.ai`
- Analyze with Wireshark to inspect TLS handshakes and HTTP headers
- Use `curl -vvv https://api.aurora.ai/health` for detailed handshake output
- Enable request/response logging: `export AURORA_DEBUG_HTTP=1`

**TLS Handshake Failures:**
- Check cipher suite compatibility: `openssl s_client -connect api.aurora.ai:443 -tls1_2`
- Verify certificate chain: `openssl s_client -showcerts -connect api.aurora.ai:443`
- Test SNI (Server Name Indication): `openssl s_client -servername api.aurora.ai -connect api.aurora.ai:443`
- Inspect client certificate requirements if mutual TLS is enabled

#### DNS Deep Dive
**Resolution Path Analysis:**
- Query authoritative nameservers: `dig @8.8.8.8 api.aurora.ai +trace`
- Check DNS response times: `dig api.aurora.ai | grep "Query time"`
- Verify DNSSEC validation: `dig api.aurora.ai +dnssec`
- Test DNS-over-HTTPS: Configure DoH provider in system settings

**DNS Cache Management:**
- Linux: `sudo systemd-resolve --flush-caches` or `sudo service nscd restart`
- macOS: `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`
- Windows: `ipconfig /flushdns`
- Verify `/etc/hosts` (Unix) or `C:\Windows\System32\drivers\etc\hosts` (Windows) for override entries

#### Proxy and VPN Troubleshooting
**Proxy Configuration Validation:**
- Check environment variables: `echo $HTTP_PROXY $HTTPS_PROXY $NO_PROXY`
- Test proxy authentication: `curl -x http://proxy.corp.com:8080 --proxy-user user:pass https://api.aurora.ai`
- Configure in Aurora config: `aurora config set proxy.url http://proxy.corp.com:8080`
- Bypass proxy for testing: `export NO_PROXY=api.aurora.ai`

**VPN-Specific Issues:**
- Check split-tunneling configuration
- Verify VPN MTU: `ip link show` and adjust if < 1500
- Test with VPN disabled to isolate issue
- Check for IPv6 leakage: `curl -6 https://api.aurora.ai` vs `curl -4 https://api.aurora.ai`

#### Application-Level Diagnostics
**Aurora Internal Logs:**
- Enable maximum verbosity: `aurora --log-level=trace <command>`
- Tail log file in real-time: `tail -f ~/.aurora/logs/aurora.log`
- Filter connection events: `grep -i "connection\|socket\|timeout" ~/.aurora/logs/aurora.log`
- Structured JSON logging: `aurora --log-format=json <command> | jq '.level="error"'`

**Request/Response Inspection:**
- Capture full HTTP exchange: `AURORA_DUMP_REQUESTS=1 aurora <command>`
- Measure round-trip time: `time aurora api healthcheck`
- Test with minimal request: `aurora api raw --method GET --endpoint /v1/health`
- Verify request headers: Check `User-Agent`, `Authorization`, `Content-Type` in debug output

#### System Resource Constraints
**Connection Pool Exhaustion:**
- Check open file descriptors: `ulimit -n` and increase if needed
- Monitor active sockets: `lsof -p $(pgrep aurora) | grep TCP`
- Review connection pool settings: `aurora config get http.max_connections`
- Adjust keep-alive timeout: `aurora config set http.keepalive_timeout 30`

**Memory and CPU Impact:**
- Profile resource usage: `top -p $(pgrep aurora)` or `htop`
- Check for memory leaks during long-running operations
- Monitor thread count: `ps -eLf | grep aurora | wc -l`
- Enable profiling: `aurora --profile=cpu <command>`

#### Enterprise Environment Considerations
**Corporate Security Appliances:**
- SSL/TLS Inspection: Export CA certificate and install system-wide
- Web Application Firewalls: Whitelist Aurora user-agent string
- DLP (Data Loss Prevention): Configure exceptions for Aurora traffic
- CASB (Cloud Access Security Broker): Add Aurora domains to allowlist

**Authentication Mechanisms:**
- NTLM proxy authentication: `aurora config set proxy.auth ntlm`
- Kerberos/SPNEGO: Ensure valid ticket with `klist`
- Client certificates: Specify with `--client-cert=/path/to/cert.pem --client-key=/path/to/key.pem`
- OAuth token refresh: `aurora auth token --refresh`

#### Advanced Debugging Techniques
**Packet Capture and Analysis:**
```bash
# Capture on specific interface
sudo tcpdump -i eth0 -s 0 -w aurora_debug.pcap 'host api.aurora.ai'

# Filter by port and decode HTTP
sudo tcpdump -i any -A 'tcp port 443 and host api.aurora.ai'

# Real-time monitoring with timestamps
sudo tcpdump -i any -tttt 'host api.aurora.ai'
```

**SystemTap/eBPF Tracing (Linux):**
- Trace system calls: `strace -f -e trace=network aurora <command>`
- Monitor DNS queries: `sudo tcpdump -i any port 53`
- Track connection states: Use `ss -tan state established`

**Performance Profiling:**
- Generate flame graph: `aurora --profile=cpu --profile-output=profile.pb.gz <command>`
- Analyze with pprof: `go tool pprof -http=:8080 profile.pb.gz`
- Network timing breakdown: Use browser DevTools Network tab for web UI

#### Configuration File Troubleshooting
**Verify Configuration Syntax:**
```bash
# Validate config file
aurora config validate

# Show effective configuration
aurora config show --resolved

# Reset to defaults
aurora config reset --confirm

# Override specific setting
aurora --config=/tmp/test.yaml <command>
```

**Common Configuration Issues:**
- Incorrect endpoint URLs: Verify `api.base_url` setting
- Timeout values too low: Increase `http.timeout` and `http.read_timeout`
- Retry logic disabled: Enable with `http.retry.enabled=true`
- Connection limits: Adjust `http.max_connections_per_host`

#### External Service Integration Testing
**GitHub Connectivity:**
```bash
# Test GitHub API access
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user

# Verify webhook endpoint
curl -X POST https://api.aurora.ai/webhooks/github/test

# Check SSH access
ssh -T git@github.com
```

**Jira Connectivity:**
```bash
# Test Jira REST API
curl -u user@domain.com:api_token https://your-domain.atlassian.net/rest/api/3/myself

# Verify webhook delivery
aurora integrate jira test-webhook --project KEY
```

#### Logging and Monitoring
**Continuous Monitoring Setup:**
- Configure log aggregation: Ship logs to ELK, Splunk, or Datadog
- Set up alerts for connection failures
- Monitor error rates: `grep -c "connection refused\|timeout" aurora.log`
- Track success rates over time

**Metrics Collection:**
- Enable Prometheus metrics: `aurora serve --metrics-port=9090`
- Export connection statistics: `aurora metrics export --format=json`
- Dashboard visualization: Import Aurora Grafana dashboard

#### Emergency Workarounds
**Temporary Fixes:**
- Use alternative endpoint: `aurora --api-url=https://backup.aurora.ai`
- Offline mode (if supported): `aurora --offline <command>`
- Fallback to local processing: `aurora --no-remote <command>`
- Manual API calls: Use `curl` with stored authentication token

**Escalation Path:**
1. Collect diagnostic bundle: `aurora diagnostic collect --output=aurora-diag.zip`
2. Include system information: `aurora version --verbose`
3. Attach relevant logs and packet captures
4. Submit to support with issue details