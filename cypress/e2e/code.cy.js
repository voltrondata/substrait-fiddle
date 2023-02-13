/// <reference types="cypress" />

describe('Substrait Fiddle Code Test', ()=>{
    beforeEach(()=>{
        cy.visit('/')
    })


    it('code sql query', ()=>{
        cy.get('select')
        .select('sql');
        
        cy.get("#status")
        .should('have.text','// Status\n');

        cy.get("svg")
            .should('be.empty')

        cy.get('#editor')
                .click()
                .focused()
                .type('{ctrl}a')
                .clear()
                .type('select * from lineitem;');
        
        cy.get('button')
            .contains('Generate')
            .click();
        
        cy.get('#status')
        .should('contain','Plan generation successful!');
        
        cy.get("svg")
        .should('not.be.empty')

    })
}
);
