describe('parsers page', () => {
  it('should contains h1, header, nav, ads, signup btn, signin btn, ads action btn, footer', () => {
    cy.viewport(1920 , 1080)
    cy.visit('/parsers')
    cy.get('h1[class*=h1]').contains('Parsers')
    cy.get('header[class*=header]').should('exist')
    cy.get('nav[class*=workspaceNav]').should('exist')
    cy.get('ul[class*=parsers]').should('exist')
    cy.get('footer[class*=footer]').should('exist')
  })

  it('should contains correct parser list', () => {
    cy.viewport(1920 , 1080)
    cy.intercept('GET', Cypress.env('apiUrl') + '/api/parsers/', {
      statusCode: 200,
      body: {
        parsers: [
          {
            id: 1,
            name: "KOHLS"
          },
          {
            id: 2,
            name: "Gaps & Old Navy"
          }
        ]
      },
    })
    cy.visit('/parsers')
    cy.get('ul[class*=parsers]').should('exist')
    cy.get('ul[class*=parsers]').children('li:contains("KOHLS")')
    cy.get('ul[class*=parsers]').children('li:contains("Gaps & Old Navy")')
  })
})