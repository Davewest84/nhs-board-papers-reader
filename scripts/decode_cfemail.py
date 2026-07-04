#!/usr/bin/env python
"""Decode Cloudflare email-obfuscated (cfemail) addresses from a page or hex string.

Cloudflare's "Email Address Obfuscation" replaces mailto: addresses in the
served HTML with a placeholder like:

    <a href="/cdn-cgi/l/email-protection#a1c4ccc0c8cde1..." class="__cf_email__"
       data-cfemail="a1c4ccc0c8cde1...">[email&#160;protected]</a>

The real address is NOT encrypted -- it's a trivially reversible XOR where the
first hex byte is the key. This recovers it without needing JavaScript/Playwright.

Usage:
    py scripts/decode_cfemail.py https://www.example.nhs.uk/contact/   # fetch + decode all
    py scripts/decode_cfemail.py a1c4ccc0c8cde1                        # decode one hex string
    py scripts/decode_cfemail.py --stdin < page.html                  # decode piped HTML

Exit codes: 0 = at least one address recovered (or a valid hex decoded);
            1 = fetch/parse error; 2 = fetched OK but found no cfemail tokens.
"""
import re
import sys

CF_HEX_RE = re.compile(r'(?:data-cfemail=|/cdn-cgi/l/email-protection#)"?([0-9a-fA-F]{4,})')
HEX_ONLY_RE = re.compile(r'^[0-9a-fA-F]{4,}$')


def decode_one(hexstr):
    """XOR-decode a single cfemail hex token. Returns the email, or '' on failure."""
    try:
        key = int(hexstr[:2], 16)
        return ''.join(
            chr(int(hexstr[i:i + 2], 16) ^ key)
            for i in range(2, len(hexstr), 2)
        )
    except (ValueError, IndexError):
        return ''


def decode_html(html):
    """Find every cfemail token in HTML and decode it. Returns a deduped list."""
    seen, out = set(), []
    for m in CF_HEX_RE.finditer(html):
        email = decode_one(m.group(1))
        if email and '@' in email and email not in seen:
            seen.add(email)
            out.append(email)
    return out


def fetch(url):
    """Fetch raw HTML with a browser-like UA so servers return the real page."""
    import urllib.request
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/125.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', errors='replace')


def main(argv):
    if not argv:
        print(__doc__.strip())
        return 1

    if argv[0] == '--stdin':
        emails = decode_html(sys.stdin.read())
    elif HEX_ONLY_RE.match(argv[0]) and not argv[0].lower().startswith('http'):
        email = decode_one(argv[0])
        if not email:
            sys.stderr.write('Could not decode hex string.\n')
            return 1
        print(email)
        return 0
    else:
        try:
            html = fetch(argv[0])
        except Exception as e:  # noqa: BLE001 -- report any fetch failure plainly
            sys.stderr.write(f'Fetch failed: {e}\n')
            return 1
        emails = decode_html(html)

    if not emails:
        sys.stderr.write('No cfemail-obfuscated addresses found on the page.\n')
        return 2
    for e in emails:
        print(e)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
