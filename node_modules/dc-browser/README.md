# dc-browser

Browser-compatible polyfill for Node.js's `diagnostics_channel` API. This package provides the core diagnostics channel functionality that works in browser environments, including integration with AsyncLocalStorage via `als-browser`.

## Features

- Full `diagnostics_channel` API compatibility
- Channel publish/subscribe mechanism
- TracingChannel for structured tracing
- Integration with AsyncLocalStorage via `bindStore`
- Zero runtime dependencies
- TypeScript support with full type definitions
- ESM and CommonJS builds
- Comprehensive test coverage

## Installation

```bash
npm install dc-browser
# or
pnpm add dc-browser
# or
yarn add dc-browser
```

For AsyncLocalStorage integration:
```bash
npm install als-browser
```

## Usage

### Basic Channel

```typescript
import { channel } from 'dc-browser';

const requestChannel = channel('http.request');

// Subscribe to messages
requestChannel.subscribe((message, name) => {
  console.log(`Received on ${name}:`, message);
});

// Publish a message
requestChannel.publish({ url: '/api/data', method: 'GET' });
```

### TracingChannel

TracingChannel provides structured tracing with start, end, asyncStart, asyncEnd, and error events:

```typescript
import { tracingChannel } from 'dc-browser';

const httpChannel = tracingChannel('http.request');

// Subscribe to events
httpChannel.subscribe({
  start: (context) => {
    console.log('Request started:', context);
  },
  end: (context) => {
    console.log('Request ended:', context);
  },
  error: (context) => {
    console.error('Request error:', context.error);
  }
});

// Trace a synchronous operation
const result = httpChannel.traceSync(() => {
  // Your sync code here
  return fetchData();
}, { requestId: 'req-123' });

// Trace a promise-based operation
const data = await httpChannel.tracePromise(async () => {
  // Your async code here
  return await fetch('/api/data');
}, { requestId: 'req-456' });
```

### AsyncLocalStorage Integration

Channels can be bound to AsyncLocalStorage instances to transform events into stored context:

```typescript
import { channel } from 'dc-browser';
import { AsyncLocalStorage } from 'als-browser';

const requestChannel = channel('http.request');
const requestContext = new AsyncLocalStorage();

// Bind the store to the channel
requestChannel.bindStore(requestContext);

// Now runStores will propagate context to the store
requestChannel.runStores({ requestId: 'req-789' }, () => {
  console.log(requestContext.getStore()); // { requestId: 'req-789' }

  // Context is available in the callback
  doWork();
});

function doWork() {
  const context = requestContext.getStore();
  console.log('Current request:', context.requestId);
}
```

### Transform Function

You can provide a transform function when binding a store to extract/transform the message:

```typescript
import { channel } from 'dc-browser';
import { AsyncLocalStorage } from 'als-browser';

const requestChannel = channel('http.request');
const userIdStore = new AsyncLocalStorage<string>();

// Extract just the userId from messages
requestChannel.bindStore(
  userIdStore,
  (message) => message.userId
);

requestChannel.runStores({ userId: 'user-123', url: '/api/data' }, () => {
  console.log(userIdStore.getStore()); // 'user-123'
});
```

### Multiple Stores

You can bind multiple AsyncLocalStorage instances to a single channel:

```typescript
const requestChannel = channel('http.request');
const requestIdStore = new AsyncLocalStorage<string>();
const userIdStore = new AsyncLocalStorage<string>();

requestChannel.bindStore(requestIdStore, (msg) => msg.requestId);
requestChannel.bindStore(userIdStore, (msg) => msg.userId);

requestChannel.runStores({ requestId: 'req-123', userId: 'user-456' }, () => {
  console.log(requestIdStore.getStore()); // 'req-123'
  console.log(userIdStore.getStore());    // 'user-456'
});
```

### Unbinding Stores

```typescript
const store = new AsyncLocalStorage();
const ch = channel('test');

ch.bindStore(store);
// ... later
ch.unbindStore(store); // Returns true if successfully unbound
```

## API

### Module Functions

#### `channel(name: string | symbol): Channel`

Get or create a channel by name.

#### `hasSubscribers(name: string | symbol): boolean`

Check if a channel has any subscribers.

#### `subscribe(name: string | symbol, callback: Function): void`

Subscribe to a channel.

#### `unsubscribe(name: string | symbol, callback: Function): boolean`

Unsubscribe from a channel.

#### `tracingChannel(name: string): TracingChannel`

Create a TracingChannel for structured tracing.

### Channel Class

#### `subscribe(callback: (message: any, name: string) => void): void`

Add a subscriber to this channel.

#### `unsubscribe(callback: Function): boolean`

Remove a subscriber from this channel.

#### `publish(message: any): void`

Publish a message to all subscribers.

#### `bindStore(store: AsyncLocalStorage, transform?: (message: any) => any): void`

Bind an AsyncLocalStorage instance to this channel. When `runStores` is called, the message (optionally transformed) will be set as the store value.

#### `unbindStore(store: AsyncLocalStorage): boolean`

Unbind an AsyncLocalStorage instance from this channel.

#### `runStores(context: any, fn: () => any): any`

Publish the context and run the function within all bound AsyncLocalStorage contexts.

### TracingChannel Class

A TracingChannel manages 5 individual channels:
- `start`: Published before operation begins
- `end`: Published after operation completes
- `asyncStart`: Published when async operation starts resolving
- `asyncEnd`: Published when async operation finishes resolving
- `error`: Published when operation throws/rejects

#### `subscribe(handlers: ChannelHandlers): void`

Subscribe to tracing events.

#### `unsubscribe(handlers: ChannelHandlers): boolean`

Unsubscribe from tracing events.

#### `traceSync<T>(fn: Function, context?: any, thisArg?: any, ...args: any[]): T`

Trace a synchronous operation.

#### `tracePromise<T>(fn: Function, context?: any, thisArg?: any, ...args: any[]): Promise<T>`

Trace a promise-based operation.

#### `traceCallback<T>(fn: Function, position?: number, context?: any, thisArg?: any, ...args: any[]): any`

Trace a callback-based operation.

## Integration with als-browser

When using `bindStore` with `als-browser`, the context will be preserved through:

1. **Synchronous code**: Full context propagation within the `runStores` callback
2. **Patched async APIs**: setTimeout, setInterval, requestAnimationFrame (via als-browser auto-patches)
3. **Manual propagation**: Use `AsyncLocalStorage.bind()` or `snapshot()` for other async operations

**Note**: Native Promise await boundaries will lose context unless you:
- Use the patched timer APIs (setTimeout, etc.)
- Manually bind callbacks with `AsyncLocalStorage.bind()`
- Use the capture/restore functions from `als-browser`

## Example: Request Tracing with Context

```typescript
import { tracingChannel } from 'dc-browser';
import { AsyncLocalStorage } from 'als-browser';

const httpChannel = tracingChannel('http.request');
const requestStore = new AsyncLocalStorage();

// Bind store to start channel for context propagation
httpChannel.start.bindStore(requestStore);

// Subscribe to events
httpChannel.subscribe({
  start: (ctx) => console.log('Started:', ctx.requestId),
  end: (ctx) => console.log('Ended:', ctx.requestId, 'result:', ctx.result),
  error: (ctx) => console.error('Error:', ctx.requestId, ctx.error)
});

// Make a traced request
const response = httpChannel.traceSync(() => {
  // Context is available throughout the operation
  console.log('Current request:', requestStore.getStore()?.requestId);

  return fetch('/api/data');
}, { requestId: 'req-123', url: '/api/data' });
```

## Testing

```bash
# Run tests
pnpm test

# Build
pnpm build
```

## License

MIT

## Credits

This implementation is based on Node.js's `diagnostics_channel` API from Node.js core.
