# Detox (React Native)

## Setup
```bash
npm install -D detox jest-circus
npx detox init
```

## Selectors
```typescript
// Preferred
element(by.id('login-button'))          // testID prop
element(by.label('Submit'))             // accessibilityLabel
element(by.text('Welcome'))             // visible text

// Avoid
element(by.type('RCTView'))             // implementation detail
```

## Waits
```typescript
await waitFor(element(by.id('result')))
  .toBeVisible()
  .withTimeout(5000)

await device.disableSynchronization()  // for animations
// NEVER: await new Promise(r => setTimeout(r, 3000))
```

## Test Pattern
```typescript
describe('<CHECKPOINT_ID>: <description>', () => {
  beforeAll(async () => {
    await device.launchApp()
  })

  it('should <expected behavior>', async () => {
    // Arrange
    await element(by.id('tab-name')).tap()

    // Act
    await element(by.id('action-button')).tap()

    // Assert
    await expect(element(by.text('Result'))).toBeVisible()
  })
})
```

## Screenshots
```typescript
await device.takeScreenshot('<checkpoint-id>')
```

## Common Commands
| Action | Command |
|--------|---------|
| Build | `npx detox build -c ios.sim.debug` |
| Run all | `npx detox test -c ios.sim.debug` |
| Run one | `npx detox test -c ios.sim.debug e2e/<file>.test.ts` |
