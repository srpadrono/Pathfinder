# Cypress (Web)

## Setup
```bash
npm install -D cypress
npx cypress open
```

## Selectors
```typescript
// Preferred
cy.get('[data-cy="login-form"]')
cy.findByRole('button', { name: 'Submit' })  // @testing-library/cypress
cy.contains('Welcome')

// Avoid
cy.get('.btn-primary')
cy.get('#submit')
```

## Waits
```typescript
cy.intercept('GET', '/api/data').as('loadData')
cy.wait('@loadData')
cy.get('[data-cy="result"]').should('be.visible')
// NEVER: cy.wait(3000)
```

## Test Pattern
```typescript
describe('<CHECKPOINT_ID>: <description>', () => {
  it('should <expected behavior>', () => {
    // Arrange
    cy.visit('/<route>')

    // Act
    cy.get('[data-cy="action-btn"]').click()

    // Assert
    cy.contains('Result').should('be.visible')
  })
})
```

## Visual Regression
```typescript
// With cypress-image-snapshot
cy.matchImageSnapshot('<checkpoint-id>.png')
```

## Common Commands
| Action | Command |
|--------|---------|
| Run all | `npx cypress run` |
| Run one | `npx cypress run --spec "cypress/e2e/<file>.cy.ts"` |
| Open UI | `npx cypress open` |
| Headless | `npx cypress run --headless` |
