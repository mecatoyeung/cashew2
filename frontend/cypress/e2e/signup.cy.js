describe('signup page', () => {
  it('should contains h1, displayName, email, password, confirm password, signup btn, signin btn, back to homepage btn', () => {
    cy.viewport(1920 , 1080)
    cy.visit('/signup')
    cy.get('h1[class*=h1]').contains('Sign up now!')
    cy.get('input[name=displayName]').should('exist')
    cy.get('input[name=email]').should('exist')
    cy.get('input[name=password]').should('exist')
    cy.get('input[name=confirmPassword]').should('exist')
    cy.get('button[type=submit]').should('exist')
    cy.get('button[class*=signUpBtn]').should('exist')
    cy.get('button[class*=signInBtn]').should('exist')
    cy.get('i[class*=backBtn]').should('exist')
  })
})

describe('signup validations', () => {
  it('should display error message if "Display Name" is empty', () => {
    cy.viewport(1920 , 1080)
    cy.visit('/signup')
    cy.get('input[name=displayName]').clear()
    cy.get('button[class*=signUpBtn]').click()
    cy.get('div[class*=formErrorMessage]').should('exist').contains("Display Name' cannot be empty.")
  })
  it('should display error message if "Email" is empty', () => {
    cy.viewport(1920 , 1080)
    cy.visit('/signup')
    cy.get('input[name=email]').clear()
    cy.get('button[class*=signUpBtn]').click()
    cy.get('div[class*=formErrorMessage]').should('exist').contains("Display Name' cannot be empty.")
  })
})

describe('signup mock response', () => {
  it('should return valid response if everything fine', () => {
    cy.viewport(1920 , 1080)
    cy.visit('/signup')
    let user = {
      displayName: 'Cato Yeung',
      email: "me@catoyeung.com",
      password: "123",
      confirmPassword: "123"
    }
    cy.get('input[name=displayName]').type(user.displayName)
    cy.get('input[name=email]').type(user.email)
    cy.get('input[name=password]').type(user.password)
    cy.get('input[name=confirmPassword]').type(user.confirmPassword)
    cy.intercept('POST', Cypress.env('apiUrl') + '/api/account/create/', {
      statusCode: 201,
      body: {
        displayName: user.displayName,
        email: user.email
      },
    })
    cy.get('button[class*=signUpBtn]').click()
    cy.get('div[class*=formSuccessMessage]').should('exist').contains("Your account has been created. Please sign in.")
  })
  it('should return invalid response if existing email has already been registered', () => {
    cy.viewport(1920 , 1080)
    cy.visit('/signup')
    let user = {
      displayName: 'Cato Yeung',
      email: "me@catoyeung.com",
      password: "123",
      confirmPassword: "123"
    }
    cy.get('input[name=displayName]').type(user.displayName)
    cy.get('input[name=email]').type(user.email)
    cy.get('input[name=password]').type(user.password)
    cy.get('input[name=confirmPassword]').type(user.confirmPassword)

    let errorMessage = "Email has already been registered."

    cy.intercept('POST', Cypress.env('apiUrl') + '/api/account/create/', {
      statusCode: 400,
      body: {
        errorMessage: errorMessage
      },
    })
    cy.get('button[class*=signUpBtn]').click()
    cy.get('div[class*=formErrorSummaryMessage]').should('exist').contains(errorMessage)
  })
})