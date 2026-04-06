[![npm version](https://img.shields.io/npm/v/termi-link?logo=npm&labelColor=black&color=07293F)](https://npmjs.com/package/termi-link)

# termi-link

This library provides clickable terminal links for terminals that support them. It is designed to seamlessly replace popular [terminal-link](https://npmjs.com/package/terminal-link). In addition, it sanitizes the url to remove control characters.

### Reason


https://github.com/sindresorhus/terminal-link/issues/18 - terminal-link unfortunately adds a `%E2%80%8B` (Zero Width Space (ZWSP) character in Unicode, code point `U+200B`) to the start and end of the link in unsupported terminals, which makes links lead to 404 at least on Windows.

## Installation

```bash
npm install termi-link
```

## Usage

```ts
import { terminalLink } from 'termi-link';

terminalLink('example.com', 'https://example.com');
terminalLink('example.com', 'https://example.com', { fallback: (_text, url) => `${url}` });
```

## Credits  

- [terminal-link](https://npmjs.com/package/terminal-link)
- [termlink](https://github.com/savioxavier/termlink)
- [supports-hyperlinks](https://github.com/zkat/supports-hyperlinks)
  - 3.1.0
- [tty-link](https://github.com/piotrmurach/tty-link)

## License

MIT

