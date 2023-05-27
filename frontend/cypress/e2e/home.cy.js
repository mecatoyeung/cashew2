describe('homepage', () => {
  it('should contains h1, header, nav, ads, signup btn, signin btn, ads action btn, footer', () => {
    cy.viewport(1920 , 1080)
    cy.visit('/')
    cy.get('h1[class*=h1]').contains('Cashew Docparser')
    cy.get('header[class*=header]').should('exist')
    cy.get('nav[class*=nav]').should('exist')
    cy.get('div[class*=ad]').should('exist')
    cy.get('button[class*=signupBtn]').should('exist')
    cy.get('button[class*=signinBtn]').should('exist')
    cy.get('div[class*=sideAd] button[class*=talkToOurSales]').should('exist')
    cy.get('footer[class*=footer]').should('exist')
  })
})