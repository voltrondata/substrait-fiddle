/// <reference types="cypress" />

describe('Substrait Fiddle Upload Test', ()=>{
    beforeEach(()=>{
        cy.visit('/')
    })


    it('upload binary file', ()=>{
        
        cy.get('button')
        .contains('Upload')
        .click()
        .url()
        .should('include','/upload')
        
        cy.get("#status")
        .should('have.text','// Status\n');

        cy.get("svg")
            .should('be.empty')
        
        cy.get('#file-upload').selectFile('cypress/e2e/plan.bin')
        
        cy.get('#status')
        .should('contain','Plan generation successful!');
        
        cy.get("svg")
        .should('not.be.empty')

    })

    it('upload sql file', ()=>{
        
        cy.get('button')
        .contains('Upload')
        .click()
        .url()
        .should('include','/upload')
        
        cy.get("#status")
        .should('have.text','// Status\n');

        cy.get("svg")
            .should('be.empty')
        
        cy.get('#file-upload').selectFile('cypress/e2e/query.sql')
        
        cy.get('#status')
        .should('contain','Plan generation successful!');
        
        cy.get("svg")
        .should('not.be.empty')

    })
}
);
