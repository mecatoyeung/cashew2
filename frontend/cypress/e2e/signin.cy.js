describe('signin page', () => {
  it('should contains h1, displayName, email, password, confirm password, signup btn, signin btn, back to homepage btn', () => {
    cy.viewport(1920 , 1080)
    cy.visit('/signin')
    cy.get('h1[class*=h1]').contains('Sign in')
    cy.get('input[name=email]').should('exist')
    cy.get('input[name=password]').should('exist')
    cy.get('button[type=submit]').should('exist')
    cy.get('button[class*=signInBtn]').should('exist')
    cy.get('button[class*=signUpBtn]').should('exist')
    cy.get('i[class*=backBtn]').should('exist')
  })
})

describe('signin validations', () => {
  it('should display error message if "Email" is empty', () => {
    cy.viewport(1920 , 1080)
    cy.visit('/signin')
    cy.get('input[name=email]').clear()
    cy.get('button[class*=signInBtn]').click()
    cy.get('div[class*=formErrorMessage]').should('exist').contains("Email' cannot be empty.")
  })
})

describe('signin validations', () => {
  it('should display error message if "Password" is empty', () => {
    cy.viewport(1920 , 1080)
    cy.visit('/signin')
    cy.get('input[name=email]').clear()
    cy.get('button[class*=signInBtn]').click()
    cy.get('div[class*=formErrorMessage]').should('exist').contains("Password' cannot be empty.")
  })
})

describe('signin mock response', () => {
  it('should return valid response if everything fine', () => {
    cy.viewport(1920 , 1080)
    cy.visit('/signin')
    let user = {
      email: "me@catoyeung.com",
      password: "123",
    }
    cy.get('input[name=email]').type(user.email)
    cy.get('input[name=password]').type(user.password)
    cy.intercept('POST', Cypress.env('apiUrl') + '/api/account/signin/', {
      statusCode: 200,
      body: {
        displayName: user.displayName,
        email: user.email
      },
    })
    cy.get('button[class*=signInBtn]').click()
    cy.url()
      .should('be.equal', Cypress.config().baseUrl + '/admin/parsers')
  })
})