# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it by:

1. **Do NOT** open a public issue
2. Email: [Create an issue with security label if this were a real public repo]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work on a fix.

## Security Best Practices

### For Users

1. **Never commit `.env` files** - Always use environment variables
2. **Rotate API keys regularly** - Change your API keys every 90 days
3. **Use least privilege** - Only grant necessary permissions to API keys
4. **Monitor usage** - Check your API provider's usage dashboard regularly

### For Contributors

1. **No secrets in code** - Use environment variables
2. **Review dependencies** - Check for security updates regularly
3. **Test with mock data** - Don't use production credentials in tests

## Known Security Considerations

1. **API Keys in Environment**: This project requires API keys for embedding services. These should always be set via environment variables, never hardcoded.

2. **PostgreSQL Connection**: Database credentials should be protected. Use connection strings with passwords in environment variables.

3. **Local Storage**: Memories are stored locally in PostgreSQL. Ensure your database is properly secured.
