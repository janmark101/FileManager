describe('FileManager App', () => {
    it('Should load the home page', () => {
      cy.visit('http://localhost:4200/');

      
      cy.contains('ADD Team', { timeout: 20000 }).should('be.visible');
      cy.contains('ADD Team').click();

    //   cy.get('input[name="team-name"]').should('be.visible').type('Test Team');  
    // cy.get('textarea[name="team-description"]').should('be.visible').type('Description of the new team');  
    

    // cy.contains('OK').click();

    });
  });
  